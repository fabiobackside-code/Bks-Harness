#!/usr/bin/env python3
"""Medidor de tokens e custo de sessoes do Claude Code.

Le os transcripts JSONL em ~/.claude/projects/<slug>/<sessionId>.jsonl,
agrega uso por modelo e calcula custo em USD com base em pricing.json.

Uso:
  session_cost.py session [--session-id ID] [--project SLUG] [--json]
      Relatorio da sessao (por padrao, a mais recente do projeto atual).

  session_cost.py append --ledger PATH [--phase TEXTO] [--label TEXTO]
      Calcula a sessao atual e grava um snapshot no ledger JSONL.
      Idempotente por (session_id, phase): regravar substitui o snapshot.

  session_cost.py report --ledger PATH [--json]
      Consolida o ledger inteiro: total por modelo, por fase, e geral.

Saida humana em PT-BR; --json para consumo programatico.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Console do Windows usa cp1252 por padrao e mutila acentos/travessoes.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HOME = Path(os.path.expanduser("~"))
PROJECTS_DIR = HOME / ".claude" / "projects"
PRICING_PATH = Path(__file__).resolve().parent / "pricing.json"


# --------------------------------------------------------------------------- #
# Pricing
# --------------------------------------------------------------------------- #

def load_pricing():
    if not PRICING_PATH.exists():
        return {"models": {}, "aliases": {}}
    with open(PRICING_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def resolve_model(pricing, model):
    models = pricing.get("models", {})
    if model in models:
        return model
    alias = pricing.get("aliases", {}).get(model)
    if alias and alias in models:
        return alias
    # tenta prefixo (ex.: claude-opus-5-20260101 -> claude-opus-5)
    for known in models:
        if model.startswith(known):
            return known
    return None


def cost_of(pricing, model, usage):
    """Retorna (custo_usd, modelo_resolvido_ou_None)."""
    key = resolve_model(pricing, model)
    if key is None:
        return 0.0, None
    p = pricing["models"][key]
    c = (
        usage["input"] * p["input"]
        + usage["output"] * p["output"]
        + usage["cache_write_5m"] * p["cache_write_5m"]
        + usage["cache_write_1h"] * p["cache_write_1h"]
        + usage["cache_read"] * p["cache_read"]
    ) / 1_000_000
    return c, key


# --------------------------------------------------------------------------- #
# Localizacao do transcript
# --------------------------------------------------------------------------- #

def slug_for_cwd(cwd=None):
    """Replica o slug de diretorio usado pelo Claude Code."""
    p = Path(cwd or os.getcwd()).resolve()
    return str(p).replace(":", "-").replace("\\", "-").replace("/", "-")


def find_transcripts(project_slug=None, session_id=None):
    """Retorna lista de Paths de transcript, mais recente primeiro."""
    if not PROJECTS_DIR.is_dir():
        return []

    if session_id:
        hits = list(PROJECTS_DIR.glob("*/" + session_id + ".jsonl"))
        if hits:
            return hits

    if project_slug:
        slugs = [project_slug]
    else:
        s = slug_for_cwd()
        dirs = [d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()]
        # case-insensitive: Windows gera tanto "D--" quanto "d--"
        slugs = [d for d in dirs if d.lower() == s.lower()]
        if not slugs:
            # fallback: sessao aberta em subpasta do projeto
            slugs = [d for d in dirs if s.lower().startswith(d.lower())]

    files = []
    for sl in slugs:
        d = PROJECTS_DIR / sl
        if d.is_dir():
            files.extend(d.glob("*.jsonl"))
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files


# --------------------------------------------------------------------------- #
# Parse
# --------------------------------------------------------------------------- #

def empty_usage():
    return {
        "input": 0, "output": 0,
        "cache_write_5m": 0, "cache_write_1h": 0, "cache_read": 0,
        "messages": 0,
    }


def parse_transcript(path):
    """Agrega uso por modelo. Deduplica por message.id (retries repetem a linha).

    Retorna (por_modelo, meta) onde meta tem first_ts/last_ts/session_id.
    """
    by_model = {}
    seen = set()
    first_ts = last_ts = None
    session_id = Path(path).stem

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue
            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue

            mid = msg.get("id") or rec.get("uuid")
            if mid:
                if mid in seen:
                    continue
                seen.add(mid)

            ts = rec.get("timestamp")
            if ts:
                if first_ts is None or ts < first_ts:
                    first_ts = ts
                if last_ts is None or ts > last_ts:
                    last_ts = ts

            model = msg.get("model") or "desconhecido"
            acc = by_model.setdefault(model, empty_usage())

            cw = usage.get("cache_creation") or {}
            w5 = cw.get("ephemeral_5m_input_tokens")
            w1 = cw.get("ephemeral_1h_input_tokens")
            if w5 is None and w1 is None:
                # transcripts antigos: so o total agregado
                w5 = usage.get("cache_creation_input_tokens", 0) or 0
                w1 = 0

            acc["input"] += usage.get("input_tokens", 0) or 0
            acc["output"] += usage.get("output_tokens", 0) or 0
            acc["cache_write_5m"] += w5 or 0
            acc["cache_write_1h"] += w1 or 0
            acc["cache_read"] += usage.get("cache_read_input_tokens", 0) or 0
            acc["messages"] += 1

    meta = {
        "session_id": session_id,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "transcript": str(path),
    }
    return by_model, meta


AGENT_MODEL_DEFAULT = {
    "planner": "opus",
    "builder": "sonnet",
    "reviewer": "opus",
    "scribe": "haiku",
}


def parse_subagents(path):
    """Uso por invocacao de subagente, que nao aparece no bloco usage do transcript.

    O consumo do subagente vive na notificacao de conclusao (<subagent_tokens>),
    e o tipo dele na chamada da tool Agent. Os dois se ligam pelo tool-use-id.
    Ver docs/ARCHITECTURE.md.
    """
    chamadas = {}
    notif = {}

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue

            msg = rec.get("message")
            if isinstance(msg, dict):
                for blk in (msg.get("content") or []):
                    if not isinstance(blk, dict):
                        continue
                    if blk.get("type") == "tool_use" and blk.get("name") == "Agent":
                        inp = blk.get("input") or {}
                        chamadas[blk.get("id")] = {
                            "tipo": inp.get("subagent_type") or "geral",
                            "descricao": inp.get("description") or "",
                            "model_override": inp.get("model"),
                        }

            if "subagent_tokens" not in line:
                continue
            tid = re.search(r"<tool-use-id>([^<]+)</tool-use-id>", line)
            tok = re.search(r"<subagent_tokens>(\d+)</subagent_tokens>", line)
            if tid and tok:
                notif[tid.group(1)] = int(tok.group(1))

    por_agente = {}
    for tool_id, tokens in notif.items():
        info = chamadas.get(tool_id, {"tipo": "desconhecido", "model_override": None})
        tipo = info["tipo"]
        modelo = info.get("model_override") or AGENT_MODEL_DEFAULT.get(tipo, "?")
        chave = (tipo, modelo)
        acc = por_agente.setdefault(chave, {"invocacoes": 0, "tokens": 0})
        acc["invocacoes"] += 1
        acc["tokens"] += tokens
    return por_agente


def summarize(by_model, pricing):
    """Consolida em estrutura de relatorio."""
    models = []
    unknown = []
    total = empty_usage()
    total_cost = 0.0

    for model, u in sorted(by_model.items()):
        c, resolved = cost_of(pricing, model, u)
        if resolved is None:
            unknown.append(model)
        for k in total:
            total[k] += u[k]
        total_cost += c
        models.append({
            "model": model,
            "priced_as": resolved,
            "usage": dict(u),
            "billable_tokens": (u["input"] + u["output"] + u["cache_write_5m"]
                                + u["cache_write_1h"] + u["cache_read"]),
            "cost_usd": round(c, 6),
        })

    total["billable_tokens"] = (total["input"] + total["output"]
                                + total["cache_write_5m"] + total["cache_write_1h"]
                                + total["cache_read"])
    return {
        "models": models,
        "total": total,
        "total_cost_usd": round(total_cost, 6),
        "unknown_models": unknown,
    }


# --------------------------------------------------------------------------- #
# Formatacao
# --------------------------------------------------------------------------- #

def fmt_int(n):
    return "{:,}".format(n).replace(",", ".")


def fmt_usd(v):
    s = "{:,.4f}".format(v)
    return "US$ " + s.replace(",", "@").replace(".", ",").replace("@", ".")


DISCLAIMER = ("_Custo estimado a partir dos tokens do transcript e da tabela de precos "
              "local (`%s`). Nao e a fatura oficial; "
              "planos de assinatura com valor fixo nao cobram por token._"
              % PRICING_PATH.name)


def render_session(summary, meta, title="Consumo desta sessao"):
    out = []
    t = summary["total"]
    out.append("### " + title)
    out.append("")
    out.append("Sessao: `" + meta["session_id"] + "`")
    if meta.get("first_ts"):
        out.append("Periodo: " + str(meta["first_ts"]) + " -> " + str(meta["last_ts"]))
    out.append("")
    out.append("| Modelo | Input | Output | Cache write | Cache read | Total | Custo |")
    out.append("|---|---:|---:|---:|---:|---:|---:|")
    for m in summary["models"]:
        u = m["usage"]
        w = u["cache_write_5m"] + u["cache_write_1h"]
        flag = "" if m["priced_as"] else " (!)"
        out.append("| " + m["model"] + flag
                   + " | " + fmt_int(u["input"])
                   + " | " + fmt_int(u["output"])
                   + " | " + fmt_int(w)
                   + " | " + fmt_int(u["cache_read"])
                   + " | " + fmt_int(m["billable_tokens"])
                   + " | " + fmt_usd(m["cost_usd"]) + " |")
    w = t["cache_write_5m"] + t["cache_write_1h"]
    out.append("| **TOTAL** | **" + fmt_int(t["input"])
               + "** | **" + fmt_int(t["output"])
               + "** | **" + fmt_int(w)
               + "** | **" + fmt_int(t["cache_read"])
               + "** | **" + fmt_int(t["billable_tokens"])
               + "** | **" + fmt_usd(summary["total_cost_usd"]) + "** |")
    out.append("")
    out.append("Mensagens do assistente contabilizadas: " + str(t["messages"]))
    if summary["unknown_models"]:
        out.append("")
        out.append("(!) Modelo sem preco em `pricing.json` (custo contado como 0): "
                   + ", ".join(summary["unknown_models"])
                   + ". Atualize `%s`." % PRICING_PATH)
    agentes = summary.get("agentes") or {}
    if agentes:
        out.append("")
        out.append("**Subagentes** (tokens fora do thread principal):")
        out.append("")
        out.append("| Agente | Modelo | Invocacoes | Tokens |")
        out.append("|---|---|---:|---:|")
        tot_inv = tot_tok = 0
        for (tipo, modelo), d in sorted(agentes.items(), key=lambda x: -x[1]["tokens"]):
            out.append("| `%s` | %s | %d | %s |"
                       % (tipo, modelo, d["invocacoes"], fmt_int(d["tokens"])))
            tot_inv += d["invocacoes"]
            tot_tok += d["tokens"]
        out.append("| **TOTAL** | | **%d** | **%s** |" % (tot_inv, fmt_int(tot_tok)))
        out.append("")
        out.append("_Tokens de subagente vem da notificacao de conclusao, que nao traz o tier: "
                   "o modelo e o declarado no agente. Nao entram no custo acima._")

    out.append("")
    out.append(DISCLAIMER)
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Comandos
# --------------------------------------------------------------------------- #

def _load_session(args):
    pricing = load_pricing()
    files = find_transcripts(args.project, args.session_id)
    if not files:
        return None, None, None
    by_model, meta = parse_transcript(files[0])
    summary = summarize(by_model, pricing)
    summary["agentes"] = parse_subagents(files[0])
    return summary, meta, pricing


def cmd_session(args):
    summary, meta, _ = _load_session(args)
    if summary is None:
        print("Nenhum transcript encontrado para este projeto.", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"summary": summary, "meta": meta}, ensure_ascii=False, indent=2))
    else:
        print(render_session(summary, meta))
    return 0


def cmd_append(args):
    summary, meta, _ = _load_session(args)
    if summary is None:
        print("Nenhum transcript encontrado para este projeto.", file=sys.stderr)
        return 1

    ledger = Path(args.ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "session_id": meta["session_id"],
        "phase": args.phase or "",
        "label": args.label or "",
        "models": dict((m["model"], {"usage": m["usage"], "cost_usd": m["cost_usd"]})
                       for m in summary["models"]),
        "total": summary["total"],
        "total_cost_usd": summary["total_cost_usd"],
    }

    # Idempotencia: o snapshot e cumulativo por sessao, entao um novo /save
    # na mesma sessao+fase SUBSTITUI o registro anterior em vez de somar.
    kept = []
    if ledger.exists():
        with open(ledger, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    prev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if (prev.get("session_id") == entry["session_id"]
                        and (prev.get("phase") or "") == entry["phase"]):
                    continue
                kept.append(prev)
    kept.append(entry)

    with open(ledger, "w", encoding="utf-8") as fh:
        for rec in kept:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    if args.json:
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    else:
        print(render_session(summary, meta))
        print()
        msg = ("Ledger atualizado: `" + str(ledger) + "` (sessao `"
               + meta["session_id"] + "`")
        if entry["phase"]:
            msg += ", fase `" + entry["phase"] + "`"
        print(msg + ").")
    return 0


def cmd_report(args):
    ledger = Path(args.ledger)
    if not ledger.exists():
        print("Ledger nao encontrado: " + str(ledger), file=sys.stderr)
        return 1

    entries = []
    with open(ledger, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    by_model = {}
    by_phase = {}
    grand = empty_usage()
    grand_cost = 0.0

    for e in entries:
        for model, d in (e.get("models") or {}).items():
            acc = by_model.setdefault(model, dict(empty_usage(), cost_usd=0.0))
            for k, v in d.get("usage", {}).items():
                acc[k] = acc.get(k, 0) + v
            acc["cost_usd"] += d.get("cost_usd", 0.0)

        ph = e.get("phase") or "(sem fase)"
        pacc = by_phase.setdefault(ph, {"tokens": 0, "cost_usd": 0.0, "sessions": set()})
        tot = e.get("total") or {}
        pacc["tokens"] += tot.get("billable_tokens", 0)
        pacc["cost_usd"] += e.get("total_cost_usd", 0.0)
        pacc["sessions"].add(e.get("session_id"))

        for k in grand:
            grand[k] += tot.get(k, 0)
        grand_cost += e.get("total_cost_usd", 0.0)

    grand["billable_tokens"] = (grand["input"] + grand["output"]
                                + grand["cache_write_5m"] + grand["cache_write_1h"]
                                + grand["cache_read"])
    sessions = set(e.get("session_id") for e in entries)

    if args.json:
        print(json.dumps({
            "by_model": by_model,
            "by_phase": dict((k, {"tokens": v["tokens"],
                                  "cost_usd": round(v["cost_usd"], 6),
                                  "sessions": len(v["sessions"])})
                             for k, v in by_phase.items()),
            "total": grand,
            "total_cost_usd": round(grand_cost, 6),
            "sessions": len(sessions),
            "entries": len(entries),
        }, ensure_ascii=False, indent=2))
        return 0

    out = []
    out.append("### Consumo total do processo BKS-SDD")
    out.append("")
    out.append("Sessoes contabilizadas: " + str(len(sessions))
               + " | Registros no ledger: " + str(len(entries)))
    out.append("")
    out.append("**Por modelo**")
    out.append("")
    out.append("| Modelo | Input | Output | Cache write | Cache read | Total | Custo |")
    out.append("|---|---:|---:|---:|---:|---:|---:|")
    for model, u in sorted(by_model.items(), key=lambda kv: -kv[1]["cost_usd"]):
        w = u["cache_write_5m"] + u["cache_write_1h"]
        tot = u["input"] + u["output"] + w + u["cache_read"]
        out.append("| " + model
                   + " | " + fmt_int(u["input"])
                   + " | " + fmt_int(u["output"])
                   + " | " + fmt_int(w)
                   + " | " + fmt_int(u["cache_read"])
                   + " | " + fmt_int(tot)
                   + " | " + fmt_usd(u["cost_usd"]) + " |")
    out.append("")
    out.append("**Por fase**")
    out.append("")
    out.append("| Fase | Sessoes | Tokens | Custo | % do total |")
    out.append("|---|---:|---:|---:|---:|")
    for ph, v in sorted(by_phase.items(), key=lambda kv: -kv[1]["cost_usd"]):
        pct = (v["cost_usd"] / grand_cost * 100) if grand_cost else 0.0
        out.append("| " + ph
                   + " | " + str(len(v["sessions"]))
                   + " | " + fmt_int(v["tokens"])
                   + " | " + fmt_usd(v["cost_usd"])
                   + " | " + "{:.1f}%".format(pct) + " |")
    out.append("")
    out.append("**TOTAL GERAL: " + fmt_int(grand["billable_tokens"])
               + " tokens — " + fmt_usd(grand_cost) + "**")
    out.append("")
    out.append(DISCLAIMER)
    print("\n".join(out))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Medidor de tokens/custo do Claude Code")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("session", help="relatorio da sessao")
    p.add_argument("--session-id")
    p.add_argument("--project")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_session)

    p = sub.add_parser("append", help="grava a sessao no ledger")
    p.add_argument("--ledger", required=True)
    p.add_argument("--phase", default="")
    p.add_argument("--label", default="")
    p.add_argument("--session-id")
    p.add_argument("--project")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_append)

    p = sub.add_parser("report", help="consolida o ledger")
    p.add_argument("--ledger", required=True)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_report)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
