# Integração canônica de status de projetos privados

## Fonte da verdade

Todo projeto novo deve ter `PROJECT_STATUS.json` na branch padrão, com `schema_version: "project-status/v1"`. O arquivo é mantido **no repositório do projeto**, acompanhado por `PROJECT_STATUS.md` com evidências. O perfil publica somente o nome, o percentual e a situação pública.

- `progress.percent` mede **entregas integradas/homologadas**, não issues fechadas ou commits.
- `progress.estimated=false` exige **`percent=0`**. Nunca gerar porcentagem a partir do total de issues de projetos que possuem contrato canônico.
- O perfil não divulga dados de servidores, logs, evidências internas, hashes, diretórios nem tokens.

## Mod Control Center — integração validada

O projeto foi renomeado para [`Majozin/mod-control-center`](https://github.com/Majozin/mod-control-center) e possui [`PROJECT_STATUS.json`](https://github.com/Majozin/mod-control-center/blob/main/PROJECT_STATUS.json) e o [contrato](https://github.com/Majozin/mod-control-center/blob/main/docs/PROJECT_STATUS_SCHEMA.md).

O token configurado para o workflow do perfil consegue listar repositórios e ler issues privadas, **mas não possui `Contents:read` nesses repositórios** (HTTP 403 confirmado na execução CI). Para manter o menor privilégio, em vez de ampliar acesso o fluxo é:

1. Alterar e revisar o `PROJECT_STATUS.json` **na `main` do projeto**.
2. [Workflow do projeto](https://github.com/Majozin/mod-control-center/blob/main/.github/workflows/publish-project-status.yml) valida o arquivo e publica **somente os campos públicos** na [issue gerenciada #8](https://github.com/Majozin/mod-control-center/issues/8), usando `GITHUB_TOKEN` com `contents:read` e `issues:write` **apenas no repositório de origem**.
3. [Workflow do perfil](../.github/workflows/update-private-projects.yml) consulta esse espelho por `Issues:read`, sincroniza o cartão e mantém a execução diária (ou manual). A alteração do espelho **não dispara atualização imediata entre repositórios**; o perfil reflete a próxima execução bem-sucedida.
4. `profile-projects.json` contém `status_projects: ["mod-control-center"]` e `status_issue_mirrors: {"mod-control-center": 8}`. Adicione novas entradas somente após criar e testar os respectivos arquivos e, se necessário, espelhos em issues gerenciadas.

Se o espelho estiver ilegível, com schema inválido ou com campos indevidos, o script **falha sem substituir o README anterior**. O fallback por issues fechadas permanece **somente para projetos legados ainda sem contrato**, e deve ser migrado gradualmente.

## Arquivo de exemplo

```json
{
  "schema_version": "project-status/v1",
  "repository": "OWNER/repository",
  "progress": {
    "percent": 0,
    "estimated": false,
    "basis": "homologated_deliverables"
  },
  "profile": {
    "visible": true,
    "public_name": "Project Name",
    "public_status": "Aguardando testes reais"
  }
}
```

`OWNER/repository` precisa corresponder ao repositório GitHub canônico. Modificar o nome do projeto ou repositório exige revisão do arquivo, URLs, espelho, configuração do perfil e regeneração dos cartões locais.

## Provas automatizadas

- [Teste local sem token](../tests/test_project_status.py) executado pelo [workflow de CI](../.github/workflows/test-profile-status.yml).
- Workflow de atualização do perfil preserva README em falhas; scripts e renderização SVG usam informações agregadas.
- Não há operações no Pelican, Wings, servidores de jogos ou containers realizadas por essa integração.

## Limites atuais

- O código e documentação dos MVPs do Mod Control Center estão em PRs draft; percentual **0%** representa **nenhuma entrega integrada/homologada**, apesar de haver testes de código aprovados.
- Para projetos legados ainda sem `PROJECT_STATUS.json`, o cálculo por issues continua existindo e **não deve ser confundido com conclusão de produto**. Migrá-los é trabalho separado.
- O status espelhado é atualizado por GitHub Actions; atrasos da fila ou falhas de permissão podem deixar o cartão anterior até execução posterior. Verificar logs de ambos os workflows antes de alegar sincronização.
