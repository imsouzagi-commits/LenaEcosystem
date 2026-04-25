# src/openjarvis/plugins/open_url.py

from typing import Dict
import webbrowser
import re


def open_url(query: str) -> str:
    match = re.search(r"(https?://\S+)", query)

    if not match:
        return "URL não encontrada"

    url = match.group(1)

    try:
        webbrowser.open(url)
        return f"Abrindo {url}"
    except Exception as e:
        return f"Erro ao abrir URL: {str(e)}"