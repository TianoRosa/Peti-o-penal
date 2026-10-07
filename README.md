# Peti-o-penal

Hierarquia das skills penais da Rosa Advogados, com relatórios JSON encadeados por processo.

## Estrutura

```
ecossistema/hierarquia.json     níveis 0–6, skills, comandos e dependências
schemas/relatorio.schema.json   esquema único dos relatórios (rosa/relatorio@1)
scripts/rosa.py                 ferramenta de linha de comando (Python 3, sem dependências)
relatorios/<processo>/          relatórios do caso (não versionados)
CLAUDE.md                       regras que o Claude segue neste repositório
```

## Níveis

| Nível | Fase | Exemplos |
|---|---|---|
| 0 | Entrada e triagem | diagnostico-processual |
| 1 | Análise probatória | cadeia-custodia-documental, auditoria-prova-memoria, analise-transcricao-audiencia |
| 2 | Construção de teses | teses-defensivas, dosimetria-penal, pesquisa-jurisprudencial |
| 3 | Portões de cabimento | admissibilidade-recursal, admissibilidade-recursal-agravos |
| 4 | Redação de peças | pedidos-de-liberdade, memoriais-defensivos, apelacao-criminal |
| 5 | Auditoria | auditor-penal-antialucinacao, design-thinking-penal |
| 6 | Saída e protocolo | peticoes-docx, eproc-peticionar, agendamento-outlook-ics |

## Comandos

```bash
python3 scripts/rosa.py arvore                        # mostra a hierarquia
python3 scripts/rosa.py novo diagnostico-processual 5001234-56.2026.8.21.0001
python3 scripts/rosa.py validar 5001234-56.2026.8.21.0001
python3 scripts/rosa.py status 5001234-56.2026.8.21.0001     # grava indice.json
python3 scripts/rosa.py consolidar 5001234-56.2026.8.21.0001 # grava consolidado.json
```

## O que o validador bloqueia

- campos obrigatórios ausentes ou fora do esquema;
- skill ou nível inexistente na hierarquia;
- qualquer menção a Jusbrasil;
- precedente com URL fora de domínio oficial ou sem data de verificação;
- tese que cite achado ou precedente não declarado;
- relatório concluído sem os relatórios obrigatórios anteriores;
- nível 6 sem auditoria antialucinação aprovada.
