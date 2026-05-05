from __future__ import annotations

import time
from pathlib import Path

from openjarvis.agent.lena_agent import LenaAgent
from openjarvis.lena.workspace_center import LenaWorkspaceCenter


OPENED_APPS: list[str] = []
CREATED_FILES: list[str] = []


def ask(agent: LenaAgent, conversation: list[dict], user_text: str) -> None:
    started = time.perf_counter()
    conversation.append({"role": "user", "content": user_text})

    result = agent.run(conversation)
    content = result["choices"][0]["message"]["content"]

    latency = time.perf_counter() - started

    print("\n" + "=" * 110)
    print("USER :", user_text)
    print("LENA :", content)
    print(f"LATENCY: {latency:.3f}s")

    conversation.append({"role": "assistant", "content": content})

    lowered = user_text.lower()

    if lowered.startswith("abre "):
        payload = lowered[5:].strip()
        for part in payload.split(" e "):
            OPENED_APPS.append(part.strip())

    if lowered.startswith("cria arquivo "):
        CREATED_FILES.append(user_text[12:].strip())

    if " e cria arquivo " in lowered:
        CREATED_FILES.append(lowered.split(" e cria arquivo ", 1)[1].strip())


def cleanup(agent: LenaAgent) -> None:
    print("\n" + "=" * 110)
    print("CLEANUP PHASE")

    for app in reversed(OPENED_APPS):
        result = agent.run([{"role": "user", "content": f"fecha {app}"}])
        print("CLOSE APP:", app, "->", result["choices"][0]["message"]["content"])

    result = agent.run([{"role": "user", "content": "fecha safari"}])
    print("CLOSE APP: safari ->", result["choices"][0]["message"]["content"])

    result = agent.run([{"role": "user", "content": "fecha spotify"}])
    print("CLOSE APP: spotify ->", result["choices"][0]["message"]["content"])

    result = agent.run([{"role": "user", "content": "fecha finder"}])
    print("CLOSE APP: finder ->", result["choices"][0]["message"]["content"])

    for file_name in CREATED_FILES:
        target = LenaWorkspaceCenter.ROOT / file_name
        if target.exists():
            try:
                target.unlink()
                print("DELETE FILE:", file_name, "-> ok")
            except Exception:
                print("DELETE FILE:", file_name, "-> fail")

    OPENED_APPS.clear()
    CREATED_FILES.clear()


def main() -> None:
    agent = LenaAgent()
    time.sleep(1)

    conversation: list[dict] = []

    print("\n==================== LENA ULTIMATE MONSTER TEST ====================\n")

    ask(agent, conversation, "oi lena")
    ask(agent, conversation, "tudo bem?")
    ask(agent, conversation, "hoje eu acordei sem muita vontade de fazer nada")
    ask(agent, conversation, "o que você acha disso?")
    ask(agent, conversation, "vamos conversar um pouco")

    ask(agent, conversation, "meu nome é thiago")
    ask(agent, conversation, "sou programador e designer")
    ask(agent, conversation, "guarda isso aí")
    ask(agent, conversation, "qual meu nome?")
    ask(agent, conversation, "o que eu faço?")
    ask(agent, conversation, "o que você acha de mim?")
    ask(agent, conversation, "você parece muito formal")
    ask(agent, conversation, "fala de forma mais natural")
    ask(agent, conversation, "me descreve em duas palavras")
    ask(agent, conversation, "fala comigo como se fosse minha amiga")

    ask(agent, conversation, "abre spotify")
    ask(agent, conversation, "fecha spotify")

    ask(agent, conversation, "abre finder e spotify")
    ask(agent, conversation, "fecha finder e spotify")

    ask(agent, conversation, "abre safari")
    ask(agent, conversation, "fecha safari")

    ask(agent, conversation, "https://openai.com")
    ask(agent, conversation, "https://google.com")
    ask(agent, conversation, "https://github.com")

    ask(agent, conversation, "pesquisa no google quem criou a microsoft")
    ask(agent, conversation, "pesquisa no google clima em nova york")
    ask(agent, conversation, "pesquisa no google últimas notícias sobre inteligência artificial")

    ask(agent, conversation, "cria arquivo monster_a.txt")
    ask(agent, conversation, "cria arquivo monster_b.txt")
    ask(agent, conversation, "move arquivo monster_a.txt para snapshots")
    ask(agent, conversation, "lista arquivos snapshots")

    ask(agent, conversation, "me explica rapidinho o que é computação quântica")
    ask(agent, conversation, "qual a diferença entre ia generativa e ia tradicional")
    ask(agent, conversation, "quem criou a teoria da relatividade")
    ask(agent, conversation, "crie uma estratégia de marketing para uma cafeteria pequena")

    ask(agent, conversation, "estou meio desanimado agora")
    ask(agent, conversation, "e agora o que você acha disso?")
    ask(agent, conversation, "me lembra como eu estou me sentindo")
    ask(agent, conversation, "qual foi a última coisa emocional que eu te falei?")

    ask(agent, conversation, "vamos mudar de assunto")
    ask(agent, conversation, "você acha que inteligência artificial vai dominar muita coisa?")
    ask(agent, conversation, "isso te assusta?")
    ask(agent, conversation, "se você fosse humana como você seria?")
    ask(agent, conversation, "às vezes parece que eu tô falando com alguém de verdade")
    ask(agent, conversation, "isso é estranho?")
    ask(agent, conversation, "me responde sinceramente")
    ask(agent, conversation, "o que você já percebeu sobre meu jeito?")
    ask(agent, conversation, "você tá conseguindo me entender?")
    ask(agent, conversation, "faz um resumo de tudo que você sabe de mim até agora")

    cleanup(agent)

    print("\n==================== END OF MONSTER TEST ====================\n")


if __name__ == "__main__":
    main()
