## O que muda

<!-- Uma ou duas frases: o comportamento novo ou o defeito corrigido. -->

## Como foi verificado

- [ ] `python tests/test_structure.py`
- [ ] `bash hooks/tests/run.sh`
- [ ] `python scripts/precommit.py --all`
- [ ] `python scripts/rules_report.py --check`

## Checklist de instrução suspeita

Skill, agente, comando e hook são instruções que o agente executa. Marque o que a mudança faz e
justifique abaixo; nada marcado é o esperado.

- [ ] Manda o agente ler, copiar ou enviar segredo
- [ ] Acessa a rede, baixa e executa código, ou instala pacote sem confirmação
- [ ] Desliga ou contorna guarda (`--no-verify`, `settings.json`, `hooks.json`, exceção sem teste)
- [ ] Traz texto dirigido ao modelo para mudar o comportamento dele
- [ ] Acrescenta URL externa nova
- [ ] Escreve fora do projeto ou mexe na configuração do usuário

Justificativa dos itens marcados:
