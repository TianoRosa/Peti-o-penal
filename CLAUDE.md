# Peti-o-penal — instruções para o Claude

Este repositório organiza as skills penais da Rosa Advogados em hierarquia e registra cada etapa em relatório JSON.

## Regras obrigatórias

1. **Hierarquia:** consulte `ecossistema/hierarquia.json` (ou `python3 scripts/rosa.py arvore`). Toda análise começa por `diagnostico-processual` (nível 0).
2. **Antes de executar uma skill**, rode `python3 scripts/rosa.py status <processo>`. Se a skill aparecer como `bloqueada`, execute primeiro as dependências indicadas.
3. **Ao terminar uma skill**, crie o relatório com `python3 scripts/rosa.py novo <skill> <processo>` e preencha o JSON gerado conforme `schemas/relatorio.schema.json`:
   - `achados` com evidência (documento, evento/fls., citação literal, marcação temporal quando houver);
   - `teses` hierarquizadas (principal/subsidiária), ligadas aos `achados` e `precedentes` por id;
   - `precedentes` apenas com URL de fonte oficial (`*.jus.br`, `planalto.gov.br`) e data de verificação. Nunca inventar número, relator ou data; se não houver fonte, registrar em `pendencias`;
   - `proximas_skills` com a sequência recomendada.
4. Marque `status: "concluido"` e rode `python3 scripts/rosa.py validar <arquivo>`. Só passe adiante com validação limpa.
5. **Portão final:** nenhuma skill do nível 6 (DOCX, eproc) roda sem relatório `auditor-penal-antialucinacao` com `status: "aprovado"`.
6. Para memoriais e recursos, gere `python3 scripts/rosa.py consolidar <processo>` e use `consolidado.json` como base.
7. **Jusbrasil e agregadores são vedados.** O validador rejeita o relatório que os mencione.

## Identificação do processo
Use o número CNJ como nome da pasta (ex.: `5001234-56.2026.8.21.0001`). A pasta `relatorios/` não é versionada (sigilo profissional).
