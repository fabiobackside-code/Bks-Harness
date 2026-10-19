# Critérios condicionais

Só se aplicam quando o código ou o manifest mostram a tecnologia. Sem esse sinal, a seção inteira
fica fora do parecer e não penaliza.

## Cofre de credenciais (A4, A5, A8, A9)

**Sinal:** cliente de cofre no código ou na configuração: CyberArk, HashiCorp Vault, Azure Key
Vault, AWS Secrets Manager.

- Um único adapter conhece o cofre. O resto da solução recebe uma abstração (ex.:
  `ICredentialProvider`) ou uma connection string já resolvida.
- Política de cache, expiração e renovação visível no código e documentada.
- Comportamento definido quando o cofre está indisponível: falhar na inicialização, retry, ou usar
  a última credencial válida.
- Teste do adapter com o cofre simulado, sem dependência de ambiente.
- Nenhum log, trace ou exceção expõe o valor da credencial.

## OpenShift e Kubernetes (A9)

**Sinal:** manifests (`Deployment`, `DeploymentConfig`, `Route`), Helm chart ou Kustomize no
repositório.

- Liveness e readiness separados, cada um com o endpoint certo.
- Contêiner roda sem root e sem depender de UID fixo, como o OpenShift exige por padrão.
- Configuração por `ConfigMap` e segredo por `Secret` ou cofre, nunca no manifest em claro.
- Limites de CPU e memória declarados.
