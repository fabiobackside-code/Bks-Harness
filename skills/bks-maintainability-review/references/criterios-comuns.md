# Critérios comuns a todas as stacks

Valem para qualquer linguagem. Os critérios de cada linguagem estão em `stacks/<linguagem>.md` e
complementam estes. Ao registrar um achado, indique o eixo.

## APIs (A1, A3, A8)

- Endpoints finos: recebem, validam, chamam um caso de uso e mapeiam a resposta.
- Validação de entrada num ponto único e previsível.
- Erros convertidos num formato único de resposta por um mecanismo central.
- Contrato publicado (OpenAPI ou equivalente) gerado a partir do código.

## Workers e serviços (A6, A8, A9)

- O laço principal legível em uma tela: obter trabalho, processar, registrar, aguardar.
- Processamento do item extraído para um caso de uso testável fora do host.
- Idempotência explícita quando o item pode ser reprocessado.
- Política de retry e de mensagens com falha (dead letter) explícita.
- Falha de um item não derruba o laço; encerramento gracioso respeitado.

## Web Services (A5, A8, A12)

- Contrato publicado (WSDL ou equivalente) separado da implementação.
- Mudança incompatível de contrato vira contrato novo, versionado.
- Erros expostos em formato tipado do protocolo, sem vazar exceção interna.

## Bibliotecas, SDKs e componentes (A4, A5, A10, A12)

- API pública mínima; o restante fica fora do contrato.
- Interfaces públicas pequenas e coesas; composição antes de herança como mecanismo de extensão.
- Cada ponto de extensão tem implementação padrão e exemplo de substituição no README.
- Versionamento semântico e CHANGELOG.
- Dependências transitivas mínimas; nada de forçar versões no consumidor sem necessidade.

## Observabilidade (A9)

- Nomes de spans e métricas seguem as convenções semânticas do OpenTelemetry.
- Logs estruturados, com correlação entre requisição, trace e log.

## Contêiner (A9)

- Dockerfile multi-stage, imagem base com versão fixada, usuário não-root.
- Probes, limites de recursos e variáveis de configuração declarados no manifest.
