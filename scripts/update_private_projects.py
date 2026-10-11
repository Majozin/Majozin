#!/usr/bin/env python3
"""Atualiza somente o bloco público de projetos privados do README."""
from render_projects import render_projects
import base64
import binascii
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

OWNER = "Majozin"
START = "<!-- PRIVATE_PROJECTS_START -->"
END = "<!-- PRIVATE_PROJECTS_END -->"
TOKEN = os.getenv("PROFILE_PROJECTS_TOKEN", "").strip()
CONFIG = json.loads(Path("profile-projects.json").read_text(encoding="utf-8"))
OVERRIDES = CONFIG.get("overrides", {})
STATUS_PROJECTS = set(CONFIG.get("status_projects", []))
STATUS_ISSUE_MIRRORS = CONFIG.get("status_issue_mirrors", {})

def request(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Authorization": "Bearer " + TOKEN,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Majozin-profile-project-status",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)

def pages(path):
    page = 1
    while page <= 100:
        sep = "&" if "?" in path else "?"
        items = request(path + sep + "per_page=100&page=" + str(page))
        if not isinstance(items, list):
            raise RuntimeError("Resposta inesperada da API.")
        yield from items
        if len(items) < 100:
            break
        page += 1

STATUS_SCHEMA = "project-status/v1"
STATUS_FILE = "PROJECT_STATUS.json"


def project_status_mirror(repo_name):
    """Use a project-managed, public-fields-only issue when Contents:read is unavailable."""
    issue_number = STATUS_ISSUE_MIRRORS.get(repo_name)
    if type(issue_number) is not int or issue_number < 1:
        raise RuntimeError("Espelho de status nao configurado: " + repo_name)
    endpoint = ("/repos/" + OWNER + "/" + urllib.parse.quote(repo_name)
                + "/issues/" + str(issue_number))
    try:
        issue = request(endpoint)
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise RuntimeError("Falha ao ler espelho de status: " + repo_name) from exc
    if (not isinstance(issue, dict) or "pull_request" in issue
            or issue.get("state") != "open"):
        raise RuntimeError("Issue de status invalida: " + repo_name)
    body = issue.get("body")
    begin, end = "<!-- PROJECT_STATUS_PUBLIC_V1_BEGIN -->", "<!-- PROJECT_STATUS_PUBLIC_V1_END -->"
    if (not isinstance(body, str) or body.count(begin) != 1 or
            body.count(end) != 1 or len(body) > 20000):
        raise RuntimeError("Marcadores do espelho de status invalidos: " + repo_name)
    raw = body.split(begin, 1)[1].split(end, 1)[0].strip()
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise RuntimeError("JSON do espelho invalido: " + repo_name) from exc
    if (not isinstance(data, dict) or
            data.get("schema_version") != "project-status-public/v1" or
            data.get("repository") != OWNER + "/" + repo_name):
        raise RuntimeError("Identidade do espelho divergente: " + repo_name)
    percent = data.get("percent")
    estimated = data.get("estimated")
    if (type(percent) is not int or not 0 <= percent <= 100 or
            type(estimated) is not bool or
            (not estimated and percent != 0)):
        raise RuntimeError("Percentual do espelho invalido: " + repo_name)
    name = data.get("public_name")
    status = data.get("public_status")
    if (not isinstance(name, str) or not 1 <= len(name) <= 80
            or not isinstance(status, str) or not 1 <= len(status) <= 90
            or any(ord(c) < 32 or ord(c) == 127 for c in name + status)):
        raise RuntimeError("Campos publicos do espelho invalidos: " + repo_name)
    return {"name": name, "percent": percent, "status": status, "visible": True}


def project_status(repo_name):
    """Prefer the project-owned status contract over issue-close percentages.

    Only the explicit public fields are exported; source may be a private repo.
    404 is a legacy repository without a contract. Other API failures fail closed.
    """
    path = "/repos/" + OWNER + "/" + urllib.parse.quote(repo_name) + "/contents/" + STATUS_FILE
    try:
        payload = request(path)
    except urllib.error.HTTPError as exc:
        if exc.code == 403 and repo_name in STATUS_ISSUE_MIRRORS:
            return project_status_mirror(repo_name)
        if exc.code == 404 and repo_name not in STATUS_ISSUE_MIRRORS:
            return None
        if exc.code == 404:
            return project_status_mirror(repo_name)
        raise RuntimeError("Falha ao ler status do projeto " + repo_name) from exc
    if (not isinstance(payload, dict) or payload.get("type") != "file"
            or payload.get("encoding") != "base64"):
        raise RuntimeError("Status nao e um JSON regular: " + repo_name)
    try:
        raw = base64.b64decode(payload["content"], validate=False)
        if len(raw) > 65536:
            raise ValueError("Status excede limite de 64 KiB")
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, KeyError, UnicodeError, binascii.Error) as exc:
        raise RuntimeError("Status invalido para " + repo_name) from exc
    if (not isinstance(data, dict) or data.get("schema_version") != STATUS_SCHEMA
            or data.get("repository") != OWNER + "/" + repo_name):
        raise RuntimeError("Schema/identidade de status incorreto: " + repo_name)
    p = data.get("progress")
    pub = data.get("profile")
    if not isinstance(p, dict) or not isinstance(pub, dict):
        raise RuntimeError("Campos de status obrigatorios ausentes: " + repo_name)
    percent = p.get("percent")
    estimated = p.get("estimated")
    if (type(percent) is not int or not 0 <= percent <= 100
            or type(estimated) is not bool
            or (not estimated and percent != 0)):
        raise RuntimeError("Progresso nao auditavel: " + repo_name)
    if p.get("basis") != "homologated_deliverables":
        raise RuntimeError("Origem do percentual nao homologada: " + repo_name)
    visible = pub.get("visible", True)
    if type(visible) is not bool:
        raise RuntimeError("Visibilidade invalida: " + repo_name)
    def safe_public(value, limit):
        return (isinstance(value, str) and 1 <= len(value) <= limit
                and all(ord(c) >= 32 and ord(c) != 127 for c in value))
    name = pub.get("public_name")
    status = pub.get("public_status")
    if not safe_public(name, 80) or not safe_public(status, 90):
        raise RuntimeError("Metadados publicos invalidos: " + repo_name)
    return {"name": name, "percent": percent, "status": status, "visible": visible}


def main():
    if not TOKEN:
        print("PROFILE_PROJECTS_TOKEN não configurado; README preservado.")
        return 0
    user = request("/user")
    if user.get("login", "").lower() != OWNER.lower():
        raise RuntimeError("Token pertence a outra conta; nenhuma modificação realizada.")
    repos = sorted(
        (r for r in pages("/user/repos?affiliation=owner&sort=full_name&direction=asc")
         if r.get("private") and r.get("owner", {}).get("login", "").lower() == OWNER.lower()),
        key=lambda r: r["name"].lower(),
    )
    if not repos:
        raise RuntimeError("Nenhum repositório privado visível; abortando para evitar apagar o painel.")
    records = []
    for repo in repos:
        name = repo["name"]
        override = OVERRIDES.get(name, {})
        status_doc = project_status(name) if name in STATUS_PROJECTS else None
        if status_doc is not None:
            if not status_doc["visible"]:
                continue
            # A validated project-owned status is canonical. Never override it
            # with an issue count or a separate manual estimate.
            records.append({
                "name": status_doc["name"],
                "percent": status_doc["percent"],
                "status": status_doc["status"],
            })
            continue
        label = override.get("public_name", name)
        if override.get("hidden", False):
            continue
        if "percent" in override:
            percent = int(override["percent"])
            if not 0 <= percent <= 100:
                raise ValueError("Percentual manual fora do intervalo: " + name)
            status = "Progresso informado"
        elif repo.get("has_issues", True):
            try:
                issues = [x for x in pages("/repos/" + OWNER + "/" + urllib.parse.quote(name) + "/issues?state=all") if "pull_request" not in x]
            except (urllib.error.HTTPError, urllib.error.URLError) as exc:
                raise RuntimeError("Falha ao obter issues; painel preservado: " + name) from exc
            if issues:
                percent = round(100 * sum(x.get("state") == "closed" for x in issues) / len(issues))
                status = "Issues concluídas: " + str(sum(x.get("state") == "closed" for x in issues)) + "/" + str(len(issues))
            else:
                percent = None
                status = "Não aferido"
        else:
            percent = None
            status = "Não aferido"
        records.append({"name": label, "percent": percent, "status": status})
    records.sort(key=lambda item: (item["percent"] is None, -(item["percent"] or 0), item["name"].lower()))
    path = Path("README.md")
    content = path.read_text(encoding="utf-8")
    if content.count(START) != 1 or content.count(END) != 1:
        raise RuntimeError("Marcadores ausentes ou duplicados; README não modificado.")
    first = content.index(START) + len(START)
    last = content.index(END)
    if first >= last:
        raise RuntimeError("Marcadores invertidos.")
    new_content = content[:first] + "\n" + render_projects(records) + "\n" + content[last:]
    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        print("Painel atualizado:", len(records), "projetos.")
    else:
        print("Nenhuma alteração no painel.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
