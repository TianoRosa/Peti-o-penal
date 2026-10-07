#!/usr/bin/env python3
"""Ecossistema de skills Rosa Advogados: hierarquia e relatórios JSON.

Uso:
  rosa.py arvore                       mostra a hierarquia de skills
  rosa.py novo <skill> <processo>      cria relatório-esqueleto da skill
  rosa.py validar <arquivo|processo>   valida relatório(s) contra esquema e regras
  rosa.py status <processo>            situação do pipeline e indice.json
  rosa.py consolidar <processo>        une todos os relatórios em consolidado.json
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HIERARQUIA = RAIZ / "ecossistema" / "hierarquia.json"
ESQUEMA = RAIZ / "schemas" / "relatorio.schema.json"
RELATORIOS = RAIZ / "relatorios"

DOMINIOS_OFICIAIS = ("stf.jus.br", "stj.jus.br", "tjrs.jus.br", "trf4.jus.br",
                     "cnj.jus.br", "planalto.gov.br", "jus.br", "gov.br")
VEDADOS = ("jusbrasil",)
ARQUIVOS_DERIVADOS = ("indice.json", "consolidado.json")


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def skills():
    """Mapa id -> skill (com o nível embutido)."""
    mapa = {}
    for nivel in carregar(HIERARQUIA)["niveis"]:
        for s in nivel["skills"]:
            mapa[s["id"]] = {**s, "nivel": nivel["nivel"], "nivel_nome": nivel["nome"]}
    return mapa


# --- Validação estrutural (subconjunto de JSON Schema) -----------------------

TIPOS = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}


def validar_esquema(valor, esquema, caminho="$"):
    erros = []
    tipo = esquema.get("type")
    if tipo:
        if not isinstance(valor, TIPOS[tipo]) or (tipo == "integer" and isinstance(valor, bool)):
            return [f"{caminho}: esperado {tipo}"]
    if "enum" in esquema and valor not in esquema["enum"]:
        erros.append(f"{caminho}: '{valor}' fora de {esquema['enum']}")
    if "pattern" in esquema and isinstance(valor, str) and not re.search(esquema["pattern"], valor):
        erros.append(f"{caminho}: '{valor}' não casa com {esquema['pattern']}")
    if "minimum" in esquema and valor < esquema["minimum"]:
        erros.append(f"{caminho}: menor que {esquema['minimum']}")
    if "maximum" in esquema and valor > esquema["maximum"]:
        erros.append(f"{caminho}: maior que {esquema['maximum']}")
    if tipo == "object":
        for campo in esquema.get("required", []):
            if campo not in valor:
                erros.append(f"{caminho}.{campo}: obrigatório")
        for campo, sub in esquema.get("properties", {}).items():
            if campo in valor:
                erros += validar_esquema(valor[campo], sub, f"{caminho}.{campo}")
    if tipo == "array" and "items" in esquema:
        for i, item in enumerate(valor):
            erros += validar_esquema(item, esquema["items"], f"{caminho}[{i}]")
    return erros


# --- Regras de negócio ------------------------------------------------------

def relatorios_do_processo(processo):
    pasta = RELATORIOS / processo
    if not pasta.is_dir():
        return []
    return sorted(p for p in pasta.glob("*.json") if p.name not in ARQUIVOS_DERIVADOS)


def ultimo_valido(processo, skill_id, status_aceitos=("concluido", "aprovado")):
    """Último relatório da skill no processo com status aceito, ou None."""
    for p in reversed(relatorios_do_processo(processo)):
        try:
            r = carregar(p)
        except json.JSONDecodeError:
            continue
        if r.get("meta", {}).get("skill") == skill_id and r.get("status") in status_aceitos:
            return p
    return None


def validar_regras(rel, arquivo, mapa):
    erros, avisos = [], []
    meta = rel["meta"]
    skill = mapa.get(meta["skill"])
    if not skill:
        return [f"skill '{meta['skill']}' não existe na hierarquia"], avisos
    if meta["nivel"] != skill["nivel"]:
        erros.append(f"nível {meta['nivel']} diverge do nível da skill ({skill['nivel']})")
    if arquivo and arquivo.parent.name != meta["processo"]:
        erros.append(f"arquivo está em '{arquivo.parent.name}' mas meta.processo é '{meta['processo']}'")

    bruto = json.dumps(rel, ensure_ascii=False).lower()
    for v in VEDADOS:
        if v in bruto:
            erros.append(f"fonte vedada mencionada: '{v}' — use apenas fontes oficiais")

    ids_prec = {p["id"] for p in rel["precedentes"]}
    for p in rel["precedentes"]:
        host = re.sub(r"^https://([^/]+).*$", r"\1", p["url_oficial"]).lower()
        if not any(host == d or host.endswith("." + d) for d in DOMINIOS_OFICIAIS):
            erros.append(f"precedente {p['id']}: domínio não oficial ({host})")
    # Teses podem apoiar-se em achados próprios ou dos relatórios consumidos.
    ids_achados = {a["id"] for a in rel["achados"]}
    for nome in rel["entrada"]["relatorios_consumidos"]:
        origem = RELATORIOS / meta["processo"] / nome
        if not origem.is_file():
            erros.append(f"relatório consumido não encontrado: {nome}")
            continue
        try:
            ids_achados |= {a.get("id") for a in carregar(origem).get("achados", [])}
        except json.JSONDecodeError:
            erros.append(f"relatório consumido ilegível: {nome}")
    for t in rel["teses"]:
        for pid in t.get("precedentes", []):
            if pid not in ids_prec:
                erros.append(f"tese {t['id']}: precedente '{pid}' não declarado em 'precedentes'")
        for aid in t.get("achados", []):
            if aid not in ids_achados:
                erros.append(f"tese {t['id']}: achado '{aid}' não declarado em 'achados'")
    for prox in rel["proximas_skills"]:
        if prox not in mapa:
            erros.append(f"proximas_skills: '{prox}' não existe na hierarquia")

    if rel["status"] in ("concluido", "aprovado"):
        for dep in skill["consome"]["obrigatorio"]:
            aceitos = ("aprovado",) if dep == "auditor-penal-antialucinacao" else ("concluido", "aprovado")
            if not ultimo_valido(meta["processo"], dep, aceitos):
                erros.append(f"dependência obrigatória sem relatório {'/'.join(aceitos)}: {dep}")
    if rel["status"] == "rascunho":
        avisos.append("relatório ainda em rascunho")
    return erros, avisos


def validar_arquivo(arquivo, mapa, esquema):
    try:
        rel = carregar(arquivo)
    except json.JSONDecodeError as e:
        return [f"JSON inválido: {e}"], []
    erros = validar_esquema(rel, esquema)
    if erros:
        return erros, []
    return validar_regras(rel, arquivo, mapa)


# --- Comandos ---------------------------------------------------------------

def cmd_arvore(_args):
    h = carregar(HIERARQUIA)
    print(f"{h['ecossistema']} (v{h['versao']})\n")
    for nivel in h["niveis"]:
        print(f"Nível {nivel['nivel']} — {nivel['nome']}")
        for s in nivel["skills"]:
            deps = ", ".join(s["consome"]["obrigatorio"]) or "—"
            print(f"  ├─ {s['id']}  [produz: {s['produz']}]  requer: {deps}")
        print()
    return 0


def cmd_novo(args):
    if len(args) != 2:
        print("uso: rosa.py novo <skill> <processo>")
        return 2
    skill_id, processo = args
    mapa = skills()
    if skill_id not in mapa:
        print(f"skill desconhecida: {skill_id}. Veja: rosa.py arvore")
        return 1
    if not re.fullmatch(r"[A-Za-z0-9._-]+", processo):
        print("processo deve conter apenas letras, números, '.', '_' ou '-'")
        return 1
    skill = mapa[skill_id]
    consumidos, faltando = [], []
    for dep in skill["consome"]["obrigatorio"] + skill["consome"]["opcional"]:
        p = ultimo_valido(processo, dep)
        if p:
            consumidos.append(p.name)
        elif dep in skill["consome"]["obrigatorio"]:
            faltando.append(dep)

    agora = datetime.now()
    rel = {
        "schema": "rosa/relatorio@1",
        "meta": {"skill": skill_id, "nivel": skill["nivel"], "processo": processo,
                 "cliente": "", "gerado_em": agora.isoformat(timespec="seconds"),
                 "autor": "Rosa Advogados", "comando": ""},
        "status": "rascunho",
        "resumo": "",
        "entrada": {"documentos": [], "relatorios_consumidos": consumidos},
        "achados": [], "teses": [], "precedentes": [], "riscos": [],
        "providencias": [], "pendencias": [], "proximas_skills": [],
        "dados_especificos": {},
    }
    pasta = RELATORIOS / processo
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"N{skill['nivel']}-{skill_id}-{agora:%Y%m%d-%H%M%S}.json"
    destino.write_text(json.dumps(rel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(destino.relative_to(RAIZ))
    if faltando:
        print(f"atenção: faltam relatórios obrigatórios: {', '.join(faltando)}")
    return 0


def cmd_validar(args):
    if len(args) != 1:
        print("uso: rosa.py validar <arquivo.json|processo>")
        return 2
    alvo = Path(args[0])
    arquivos = [alvo] if alvo.suffix == ".json" else relatorios_do_processo(args[0])
    if not arquivos:
        print("nenhum relatório encontrado")
        return 1
    mapa, esquema = skills(), carregar(ESQUEMA)
    falhas = 0
    for arq in arquivos:
        erros, avisos = validar_arquivo(arq.resolve(), mapa, esquema)
        print(f"{'✗' if erros else '✓'} {arq.name}")
        for e in erros:
            print(f"    erro: {e}")
        for a in avisos:
            print(f"    aviso: {a}")
        falhas += bool(erros)
    return 1 if falhas else 0


def cmd_status(args):
    if len(args) != 1:
        print("uso: rosa.py status <processo>")
        return 2
    processo = args[0]
    mapa, esquema = skills(), carregar(ESQUEMA)
    feitos = {}
    for arq in relatorios_do_processo(processo):
        erros, _ = validar_arquivo(arq, mapa, esquema)
        try:
            r = carregar(arq)
            sid = r["meta"]["skill"]
        except (json.JSONDecodeError, KeyError):
            continue
        feitos[sid] = {"arquivo": arq.name, "status": r.get("status"), "valido": not erros}

    sugeridas = set()
    for info in feitos.values():
        if info["valido"]:
            sugeridas.update(carregar(RELATORIOS / processo / info["arquivo"]).get("proximas_skills", []))

    indice = {"processo": processo, "gerado_em": datetime.now().isoformat(timespec="seconds"), "niveis": []}
    for nivel in carregar(HIERARQUIA)["niveis"]:
        bloco = {"nivel": nivel["nivel"], "nome": nivel["nome"], "skills": []}
        print(f"Nível {nivel['nivel']} — {nivel['nome']}")
        for s in nivel["skills"]:
            sid = s["id"]
            if sid in feitos:
                f = feitos[sid]
                situacao = f["status"] if f["valido"] else "inválido"
            else:
                pendentes = [d for d in s["consome"]["obrigatorio"]
                             if not (feitos.get(d, {}).get("valido")
                                     and feitos[d]["status"] in (("aprovado",) if d == "auditor-penal-antialucinacao" else ("concluido", "aprovado")))]
                situacao = f"bloqueada ({', '.join(pendentes)})" if pendentes else "disponível"
            marca = " ★ sugerida" if sid in sugeridas and sid not in feitos else ""
            print(f"  {sid:<40} {situacao}{marca}")
            bloco["skills"].append({"id": sid, "situacao": situacao, "sugerida": bool(marca),
                                    "arquivo": feitos.get(sid, {}).get("arquivo")})
        indice["niveis"].append(bloco)
    pasta = RELATORIOS / processo
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


def cmd_consolidar(args):
    if len(args) != 1:
        print("uso: rosa.py consolidar <processo>")
        return 2
    processo = args[0]
    mapa, esquema = skills(), carregar(ESQUEMA)
    cons = {"processo": processo, "gerado_em": datetime.now().isoformat(timespec="seconds"),
            "fontes": [], "achados": [], "teses": [], "precedentes": [], "riscos": [],
            "providencias": [], "pendencias": []}
    vistos_prec = set()
    for arq in relatorios_do_processo(processo):
        erros, _ = validar_arquivo(arq, mapa, esquema)
        if erros:
            print(f"ignorado (inválido): {arq.name}")
            continue
        r = carregar(arq)
        sid = r["meta"]["skill"]
        cons["fontes"].append({"arquivo": arq.name, "skill": sid, "status": r["status"]})
        for chave in ("achados", "teses", "riscos", "providencias"):
            for item in r[chave]:
                cons[chave].append({**item, "origem": sid})
        for p in r["precedentes"]:
            chave = (p["tribunal"], p["classe_numero"])
            if chave not in vistos_prec:
                vistos_prec.add(chave)
                cons["precedentes"].append({**p, "origem": sid})
        cons["pendencias"] += [f"[{sid}] {x}" for x in r.get("pendencias", [])]
    ordem = {"principal": 0, "subsidiaria": 1}
    cons["teses"].sort(key=lambda t: (ordem[t["tipo"]], t.get("ordem", 99)))
    destino = RELATORIOS / processo / "consolidado.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(cons, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(destino.relative_to(RAIZ))
    return 0


COMANDOS = {"arvore": cmd_arvore, "novo": cmd_novo, "validar": cmd_validar,
            "status": cmd_status, "consolidar": cmd_consolidar}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        print(__doc__)
        sys.exit(2)
    sys.exit(COMANDOS[sys.argv[1]](sys.argv[2:]))
