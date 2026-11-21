#!/usr/bin/env python3
"""Gera o HTML do Atlas, da Apresentação, do treinamento, do guia do Maestri, do guia para quem chega, do roteiro e do estudo do TXC.

Uso:
  python scripts/build_artefatos.py            gera os seis HTML
  python scripts/build_artefatos.py --check    falha se o HTML versionado estiver defasado

Requer o pacote Python `markdown` (3.x). Saída pronta para imprimir em PDF pelo navegador.
"""
import html
import io
import json
import os
import re
import sys

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, 'docs', 'artefatos')
ATLAS_MD = os.path.join(ART, 'atlas', 'atlas-bks-harness.md')
MANUAL_MD = os.path.join(ART, 'manual', 'manual-comandos.md')
FIGURES = os.path.join(ART, 'atlas', 'figuras')
DECK = os.path.join(ART, 'apresentacao')
ATLAS_HTML = os.path.join(ART, 'atlas', 'atlas-bks-harness.html')
DECK_HTML = os.path.join(DECK, 'apresentacao-bks-harness.html')
TRAINING = os.path.join(ART, 'treinamento')
TRAINING_MD = os.path.join(TRAINING, 'treinamento-bks-harness.md')
TRAINING_HTML = os.path.join(TRAINING, 'treinamento-bks-harness.html')
GUIDE = os.path.join(ART, 'maestri')
GUIDE_MD = os.path.join(GUIDE, 'guia-maestri.md')
GUIDE_HTML = os.path.join(GUIDE, 'guia-maestri.html')
STUDY = os.path.join(ROOT, 'docs', 'estudo')
STUDY_MD = os.path.join(STUDY, 'roteiro-7-dias.md')
STUDY_HTML = os.path.join(STUDY, 'roteiro-7-dias.html')
HARNESS_GUIDE = os.path.join(ART, 'guia')
HARNESS_GUIDE_MD = os.path.join(HARNESS_GUIDE, 'guia-bks-harness.md')
HARNESS_GUIDE_HTML = os.path.join(HARNESS_GUIDE, 'guia-bks-harness.html')
TXC_STUDY = os.path.join(STUDY, 'txc')
TXC_STUDY_MD = os.path.join(TXC_STUDY, 'estudo-txc.md')
TXC_STUDY_HTML = os.path.join(TXC_STUDY, 'estudo-txc.html')
TXC_STUDY_MOBILE_HTML = os.path.join(TXC_STUDY, 'estudo-txc-celular.html')

FONTS = ('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700'
         '&family=JetBrains+Mono:wght@400;600&display=swap')

ATLAS_CSS = """
:root{color-scheme:light dark;--bg:#FBF9F4;--paper:#FFFFFF;--ink:#1C2733;--soft:#3E4A57;--quiet:#6B7480;--line:#DDD6C8;--accent:#A84E18;--accent2:#D9682B;--codebg:#F2EEE5;--axis:#8A8F94;--grid:#CFCAC0;--tint:#F1ECE2}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0F1923;--paper:#13202E;--ink:#EDE9E1;--soft:#C9D3DC;--quiet:#8FA0B0;--line:#2D4257;--accent:#F0904F;--accent2:#F0904F;--codebg:#0C1620;--axis:#7D8C99;--grid:#2D4257;--tint:#1D2E40}}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);font-family:'IBM Plex Sans',Arial,sans-serif;font-size:16px;line-height:1.6}
main{max-width:860px;margin:0 auto;padding:48px 32px 96px}
.cover{min-height:92vh;display:flex;flex-direction:column;justify-content:space-between;padding:64px 0;border-bottom:1px solid var(--line)}
.eyebrow{font-family:'JetBrains Mono','Courier New',monospace;font-size:13px;letter-spacing:.06em;color:var(--accent)}
.cover h1{font-size:56px;line-height:1.05;margin:24px 0 16px;font-weight:600;border:none;padding:0}
.cover p.sub{font-size:20px;color:var(--soft);max-width:620px}
.meta{font-family:'JetBrains Mono','Courier New',monospace;font-size:13px;color:var(--quiet)}
nav.toc{padding:48px 0;border-bottom:1px solid var(--line)} nav.toc ol{padding-left:20px;columns:2;column-gap:40px} nav.toc li{margin:6px 0}
a{color:var(--accent)}
h2{font-size:32px;line-height:1.15;margin:72px 0 16px;padding-top:24px;border-top:3px solid var(--accent2);font-weight:600}
h3{font-size:22px;margin:40px 0 8px;font-weight:600}
h4{font-size:18px;margin:32px 0 6px;font-weight:600;color:var(--accent)}
h5{font-size:16px;margin:24px 0 4px;font-weight:600}
p,li{color:var(--soft)} strong,b{color:var(--ink)}
table{width:100%;border-collapse:collapse;font-size:14px;margin:16px 0 24px;display:block;overflow-x:auto}
th{text-align:left;border-bottom:2px solid var(--ink);padding:8px 10px} td{border-bottom:1px solid var(--line);padding:8px 10px;vertical-align:top;color:var(--soft)}
code{font-family:'JetBrains Mono','Courier New',monospace;font-size:.88em;background:var(--codebg);padding:1px 5px;border-radius:4px}
pre{background:var(--codebg);border:1px solid var(--line);border-radius:10px;padding:16px 18px;overflow-x:auto;font-size:13px;line-height:1.5;white-space:pre-wrap} pre code{background:none;padding:0}
blockquote{margin:16px 0;padding:8px 20px;border-left:3px solid var(--accent2);background:var(--paper);border-radius:0 10px 10px 0}
figure{margin:28px 0;padding:20px;background:var(--paper);border:1px solid var(--line);border-radius:12px}
figure svg{width:100%;height:auto;display:block} figcaption{font-size:13px;color:var(--quiet);margin-top:10px}
ul li::marker,ol li::marker{color:var(--accent)}
@page{size:A4;margin:18mm 16mm 20mm}
@media print{
 :root{--bg:#fff;--paper:#fff;--ink:#1C2733;--soft:#2E3A47;--quiet:#5A636E;--line:#D8D2C6;--accent:#A84E18;--accent2:#D9682B;--codebg:#F4F1EA;--axis:#7A7F84;--grid:#CFCAC0;--tint:#F3EFE7}
 html,body{font-size:11pt} main{max-width:none;padding:0}
 .cover{min-height:250mm;page-break-after:always;border:none} nav.toc{page-break-after:always;border:none}
 h2{page-break-before:always;margin-top:0} h3,h4,h5{page-break-after:avoid}
 figure,table,pre,blockquote{page-break-inside:avoid} table{display:table}
 a{color:var(--ink);text-decoration:none}
}
"""

DECK_CSS = """
:root{color-scheme:light dark;--bg:#E9E5DC} @media (prefers-color-scheme: dark){:root{--bg:#0B131B}}
html,body{margin:0;background:var(--bg)}
.deck{display:flex;flex-direction:column;align-items:center;gap:32px;padding:32px 0}
.frame{width:calc(min(100vw - 32px, 1920px));aspect-ratio:16/9;overflow:hidden;position:relative;box-shadow:0 2px 12px rgba(0,0,0,.15)}
.frame>section{width:1920px;height:1080px;box-sizing:border-box;position:absolute;left:0;top:0;transform-origin:0 0;overflow:hidden}
.frame>section aside{display:none}
section h1,section h2,section h3,section p,section ul,section table{margin:0} section ul{padding-left:1.2em} section *{box-sizing:border-box}
body.notes .frame>section aside{display:block;position:absolute;left:0;right:0;bottom:0;background:#13202ECC;color:#F5F2EB;font:28px/1.4 'IBM Plex Sans',Arial,sans-serif;padding:24px 128px}
@page{size:1920px 1080px;margin:0}
@media print{ html,body{background:none} .deck{display:block;padding:0} .frame{width:1920px;height:1080px;box-shadow:none;page-break-after:always;break-after:page} .frame>section{transform:none!important} .frame>section aside{display:none!important} }
"""

DECK_JS = """
function fit(){document.querySelectorAll('.frame').forEach(f=>{f.firstElementChild.style.transform='scale('+(f.clientWidth/1920)+')'})}
addEventListener('resize',fit);fit();
addEventListener('keydown',e=>{
 const frames=[...document.querySelectorAll('.frame')];
 const i=frames.findIndex(f=>f.getBoundingClientRect().top>=-10);
 if(e.key==='ArrowRight'||e.key==='PageDown'){frames[Math.min(i+1,frames.length-1)].scrollIntoView({behavior:'smooth'});e.preventDefault()}
 if(e.key==='ArrowLeft'||e.key==='PageUp'){frames[Math.max(i-1,0)].scrollIntoView({behavior:'smooth'});e.preventDefault()}
 if(e.key==='n'){document.body.classList.toggle('notes')}
});
"""

FIGURE_RX = re.compile(r'^&#91;embedded content: (.+?)\\\]\s*$', re.M)
SLUG_RX = re.compile(r'[^a-z0-9]+')


def read(path):
    with io.open(path, encoding='utf-8') as fh:
        return fh.read()


def strip_frontmatter(text):
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            return text[end + 4:].lstrip('\n')
    return text


def load_figures(folder):
    figures = {}
    if not os.path.isdir(folder):
        return figures
    for name in sorted(os.listdir(folder)):
        body = read(os.path.join(folder, name))
        caption = re.search(r'</b>\s*·\s*(.+?)(?:\s*·\s*comandos|</figcaption>)', body)
        key = re.sub(r'<[^>]+>', '', caption.group(1)).strip()
        figures[key] = re.sub(r'<p class="read">.*?</p>', '', body, flags=re.S).strip()
    return figures


def demote(text, levels):
    out, fence = [], False
    for line in text.split('\n'):
        if line.startswith('```'):
            fence = not fence
        if not fence and re.match(r'#{1,5} ', line):
            line = '#' * levels + line
        out.append(line)
    return '\n'.join(out)


def slugify(text):
    plain = html.unescape(re.sub(r'<[^>]+>', '', text)).lower()
    for a, b in (('áàâã', 'a'), ('éê', 'e'), ('í', 'i'), ('óôõ', 'o'), ('ú', 'u'), ('ç', 'c')):
        for ch in a:
            plain = plain.replace(ch, b)
    return SLUG_RX.sub('-', plain).strip('-')


def render_doc(source, figures_dir, eyebrow, blurb, meta, extra=None):
    title = re.match(r'# (.+)\n', source).group(1)
    version_line = re.search(r'^Versão (\d+\.\d+\.\d+).*$', source, re.M)
    version = version_line.group(1)
    body = source[version_line.end():]
    if extra:
        body = extra(body)

    figures = load_figures(figures_dir)
    missing = []

    def figure(match):
        key = match.group(1).strip()
        if key not in figures:
            missing.append(key)
            return match.group(0)
        return '\n<div markdown="0">%s</div>\n' % figures[key]

    body = FIGURE_RX.sub(figure, body)
    if missing:
        raise SystemExit('figura sem arquivo em %s: %s' % (
            os.path.relpath(figures_dir, ROOT), ', '.join(missing)))

    numbered = [0]

    def number_figure(match):
        numbered[0] += 1
        return '<b>Figura %d</b>' % numbered[0]

    body = re.sub(r'<b>Figura \d+</b>', number_figure, body)
    content = markdown.markdown(body, extensions=['tables', 'fenced_code', 'md_in_html'])

    toc = []

    def anchor(match):
        text = match.group(1)
        ident = slugify(text)
        toc.append((ident, text))
        return '<h2 id="%s">%s</h2>' % (ident, text)

    content = re.sub(r'<h2>(.*?)</h2>', anchor, content)
    toc_html = ''.join('<li><a href="#%s">%s</a></li>' % item for item in toc)
    main_title, _, subtitle = title.partition(' — ')

    page = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s · v%(version)s</title>
<link rel="stylesheet" href="%(fonts)s">
<style>%(css)s</style></head><body><main>
<section class="cover"><div class="eyebrow">%(eyebrow)s</div>
<div><h1>%(main)s</h1><p class="sub">%(sub)s: %(blurb)s</p></div>
<div class="meta">Versão %(version)s · %(meta)s</div></section>
<nav class="toc"><div class="eyebrow">SUMÁRIO</div><ol>%(toc)s</ol></nav>
%(content)s
</main></body></html>
""" % {'title': html.escape(title), 'version': version, 'fonts': FONTS, 'css': ATLAS_CSS,
       'eyebrow': eyebrow, 'blurb': blurb, 'meta': meta,
       'main': html.escape(main_title), 'sub': html.escape(subtitle or 'Manual'),
       'toc': toc_html, 'content': content}
    return page


def build_atlas():
    def with_manual(body):
        manual = strip_frontmatter(read(MANUAL_MD))
        manual = re.sub(r'^# .+\n', '', manual, count=1)
        manual_part = '## Parte X — Manual de comandos\n\n' + demote(manual, 1) + '\n\n'
        return body.replace('\n## Apêndices', '\n' + manual_part + '## Apêndices', 1)

    return render_doc(read(ATLAS_MD), FIGURES, 'FABIO · BKS · BKS HARNESS',
                      'conceitos, arquitetura, equipe, ritos, aprendizado, comandos com manual de uso, '
                      'skills e um case de ponta a ponta.',
                      'Claude primeiro, plugável a DeepSeek, Ollama e outros', with_manual)


def build_training():
    return render_doc(read(TRAINING_MD), os.path.join(TRAINING, 'figuras'), 'BKS HARNESS · TREINAMENTO',
                      'do zero à primeira sessão produtiva e a um ciclo completo com a equipe de agentes.',
                      'para quem instala pelo repositório público')


def build_guide():
    return render_doc(read(GUIDE_MD), os.path.join(GUIDE, 'figuras'), 'BKS HARNESS · MAESTRI',
                      'a equipe de agentes em terminais do Maestri, a delegação de comandos e o uso fora dele.',
                      'beta: integração em prova')


def build_harness_guide():
    return render_doc(read(HARNESS_GUIDE_MD), os.path.join(HARNESS_GUIDE, 'figuras'), 'BKS HARNESS · GUIA',
                      'o que orienta o agente, o que confere o trabalho, o que é proibido, o que fica guardado '
                      'e como se mede.',
                      'para quem chega')


def build_study():
    return render_doc(read(STUDY_MD), os.path.join(STUDY, 'figuras'), 'BKS HARNESS · ESTUDO',
                      'sete dias de leitura e prática na PoC, do vocabulário de Harness Engineering ao '
                      'ciclo completo com a equipe e ao esqueleto de um artigo.',
                      'privado: não sai para o público')


def build_txc_study():
    return render_doc(read(TXC_STUDY_MD), os.path.join(TXC_STUDY, 'figuras'), 'BKS HARNESS · ESTUDO DO TXC',
                      'o problema, os fundamentos, o caso de origem, onde o padrão aparece, a mesma transação '
                      'em C#, TypeScript e Go, e quando adotar.',
                      'sobre o txc-guidelines 2.2')


MOBILE_CSS = """
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
html,body{font-family:system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;font-size:17px;line-height:1.65}
code,pre,.eyebrow{font-family:ui-monospace,'SF Mono',Menlo,Consolas,monospace}
main{padding:16px 16px 72px}
.cover{min-height:auto;padding:40px 0 32px}
.cover h1{font-size:34px}
.cover p.sub{font-size:18px}
.toc{padding:24px 0}
nav.toc ol{columns:auto;column-count:1;list-style:none;padding-left:0}
p code,li code,td code{overflow-wrap:anywhere}
.toc li{margin:10px 0}
h2{font-size:25px;margin:48px 0 12px;scroll-margin-top:12px}
h3{font-size:20px;margin:32px 0 8px;scroll-margin-top:12px}
table{font-size:14px;-webkit-overflow-scrolling:touch}
th,td{min-width:120px}
pre{font-size:12.5px;padding:12px}
figure{padding:10px;margin:20px -8px}
a.top{position:fixed;right:14px;bottom:14px;width:44px;height:44px;border-radius:22px;display:flex;align-items:center;justify-content:center;background:var(--accent);color:#fff;text-decoration:none;font-size:20px;box-shadow:0 2px 8px rgba(0,0,0,.25)}
@media print{a.top{display:none}}
"""


def build_txc_study_mobile():
    page = build_txc_study()
    page = page.replace('<link rel="stylesheet" href="%s">\n' % FONTS, '')
    page = page.replace('</style>', MOBILE_CSS + '</style>', 1)
    page = page.replace('<nav class="toc">', '<nav class="toc" id="sumario">', 1)
    page = page.replace('</main>', '</main><a class="top" href="#sumario" aria-label="Voltar ao sumário">↑</a>', 1)
    return page


def build_deck():
    deck = json.loads(read(os.path.join(DECK, 'deck.json')))
    frames = []
    for slide in deck['order']:
        section = read(os.path.join(DECK, 'slides', slide + '.html')).strip()
        frames.append('<div class="frame">\n%s\n</div>' % section)
    page = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<link rel="stylesheet" href="%(fonts)s">
<style>%(css)s</style></head><body><div class="deck">
%(frames)s
</div>
<script>%(js)s</script>
</body></html>
""" % {'title': html.escape(deck['title']), 'fonts': FONTS, 'css': DECK_CSS,
       'frames': '\n'.join(frames), 'js': DECK_JS}
    return page


def main(argv):
    targets = [(ATLAS_HTML, ATLAS_MD, build_atlas), (DECK_HTML, DECK, build_deck),
               (TRAINING_HTML, TRAINING_MD, build_training), (GUIDE_HTML, GUIDE_MD, build_guide),
               (HARNESS_GUIDE_HTML, HARNESS_GUIDE_MD, build_harness_guide),
               (STUDY_HTML, STUDY_MD, build_study), (TXC_STUDY_HTML, TXC_STUDY_MD, build_txc_study),
               (TXC_STUDY_MOBILE_HTML, TXC_STUDY_MD, build_txc_study_mobile)]
    outputs = []
    for path, source, builder in targets:
        if not os.path.exists(source):
            print('pulado, fonte fora desta árvore: %s' % os.path.relpath(source, ROOT))
            continue
        outputs.append((path, builder()))
    if '--check' in argv:
        stale = [p for p, text in outputs if not os.path.exists(p) or read(p) != text]
        for p in stale:
            print('defasado: %s' % os.path.relpath(p, ROOT))
        return 1 if stale else 0
    for path, text in outputs:
        with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text)
        print('gerado: %s' % os.path.relpath(path, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
