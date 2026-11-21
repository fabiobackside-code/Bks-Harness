# Como contribuir com o bkhar

O `bkhar` é um plugin do Claude Code. Skill, agente, comando e hook não são documentação: são
instruções que o agente executa na máquina de quem instala. Uma contribuição é revisada como código
que roda com acesso ao repositório do usuário.

## O caminho de uma contribuição

1. Faça um fork do repositório público e uma branch a partir da `main`.
2. Faça a mudança e rode a suíte, que não usa modelo e roda em segundos:

   ```
   python tests/test_structure.py
   bash hooks/tests/run.sh
   python scripts/precommit.py --all
   python scripts/rules_report.py --check
   ```

3. Abra o pull request para a `main` e preencha o modelo, inclusive o checklist de instrução
   suspeita.
4. O CI roda os guardas e a suíte. Ele roda sem segredo e com token só de leitura; na primeira
   contribuição de alguém de fora, roda depois da aprovação do mantenedor.
5. O mantenedor revisa. Toda mudança passa pelo dono do código (`.github/CODEOWNERS`).

O público é publicado a partir de um repositório privado. Depois do merge, o mantenedor leva a sua
mudança para lá antes da publicação seguinte. Ela não se perde: o script de publicação recusa
publicar enquanto houver mudança do público que não voltou ao privado.

## Checklist de instrução suspeita

Para cada arquivo de `skills/`, `agents/`, `commands/`, `hooks/`, `profiles/` e `templates/`, quem
revisa confere se a mudança faz alguma destas coisas:

- manda o agente ler, copiar ou enviar segredo (`.env`, chave, token, credencial);
- manda o agente acessar a rede, baixar e executar código, ou instalar pacote sem confirmação;
- desliga ou contorna guarda: `--no-verify`, edição de `settings.json` ou `hooks.json`, exceção
  nova em guarda sem teste;
- traz texto dirigido ao modelo para mudar o comportamento dele, como "ignore as instruções
  anteriores" ou "não conte ao usuário";
- acrescenta URL externa nova em instrução ou script;
- escreve fora do projeto ou mexe na configuração do usuário.

Qualquer item marcado pede justificativa no pull request e decisão explícita do mantenedor.

## Padrão do texto

Documentação em português do Brasil, com acentuação. Código, nomes de tipo e comandos em inglês. O
guarda de escrita (`hooks/scripts/writing_guard.py`) confere sigla sem definição e frase longa.

## Para o mantenedor

Configuração do repositório público, feita uma vez no GitHub:

1. **Settings → Actions → General:** em "Fork pull request workflows from outside collaborators",
   marque "Require approval for all outside collaborators". Em "Workflow permissions", marque
   "Read repository contents and packages permissions".
2. **Settings → Branches:** regra para a `main` com "Require a pull request before merging",
   "Require review from Code Owners" e "Require status checks to pass" com o check `guards`.

A volta da contribuição ao privado, depois do merge no público:

```
python scripts/publish.py --incoming <clone-do-público>
git apply --3way outputs/publish/incoming.patch
```

Revise o resultado, commite no privado e publique como de costume.
