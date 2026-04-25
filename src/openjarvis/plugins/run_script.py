# src/openjarvis/plugins/run_script.py

import subprocess


def run_script(query: str) -> str:
    """
    Executa um script simples baseado no query.
    """
    if not query or "script" not in query.lower():
        return ""

    try:
        subprocess.run(["echo", "Hello from script"], check=True)
        return "Script executado com sucesso"
    except Exception as e:
        return f"Erro ao executar script: {e}"