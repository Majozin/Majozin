#!/usr/bin/env python3
"""Atualiza somente o bloco público de projetos privados do README."""
import json
import os
import re
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

def progress_bar(percent):
    filled = round(percent / 10)
    return "█" * filled + "░" * (10 - filled)

def safe_name(value):
    return value.replace("|", " ").replace("\n", " ").replace("\r", " ")

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
    lines = ["| Projeto | Progresso | Indicador |", "|:--|:--|:--|"]
    for repo in repos:
        name = repo["name"]
        override = OVERRIDES.get(name, {})
        label = safe_name(override.get("public_name", name))
        if override.get("hidden", False):
            continue
        if "percent" in override:
            percent = int(override["percent"])
            if not 0 <= percent <= 100:
                raise ValueError("Percentual manual fora do intervalo: " + name)
            status = "Manual"
        elif repo.get("has_issues", True):
            try:
                issues = [x for x in pages("/repos/" + OWNER + "/" + urllib.parse.quote(name) + "/issues?state=all") if "pull_request" not in x]
            except (urllib.error.HTTPError, urllib.error.URLError) as exc:
                print("Falha ao obter issues de", name, "-", exc, file=sys.stderr)
                issues = []
            if issues:
                percent = round(100 * sum(x.get("state") == "closed" for x in issues) / len(issues))
                status = "Issues encerradas: " + str(sum(x.get("state") == "closed" for x in issues)) + "/" + str(len(issues))
            else:
                percent = None
                status = "Não aferido"
        else:
            percent = None
            status = "Não aferido"
        if percent is None:
            bar = "░" * 10
        else:
            bar = progress_bar(percent)
            status = str(percent) + "% · " + status
        lines.append("| " + label + " | `" + bar + "` | " + status + " |")
    path = Path("README.md")
    content = path.read_text(encoding="utf-8")
    if content.count(START) != 1 or content.count(END) != 1:
        raise RuntimeError("Marcadores ausentes ou duplicados; README não modificado.")
    first = content.index(START) + len(START)
    last = content.index(END)
    if first >= last:
        raise RuntimeError("Marcadores invertidos.")
    new_content = content[:first] + "\n" + "\n".join(lines) + "\n" + content[last:]
    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        print("Painel atualizado:", len(lines) - 2, "projetos.")
    else:
        print("Nenhuma alteração no painel.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
