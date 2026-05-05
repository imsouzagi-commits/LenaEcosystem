from __future__ import annotations

import time
from pathlib import Path

from openjarvis.agent.lena_agent import LenaAgent
from openjarvis.lena.workspace_center import LenaWorkspaceCenter


OPENED_APPS: list[str] = []
CREATED_FILES: list[str] = []
SEEN_RESPONSES: dict[str, int] = {}


def register_response(text: str) -> None:
    key = text.strip().lower()
    SEEN_RESPONSES[key] = SEEN_RESPONSES.get(key, 0) + 1


def ask(agent: LenaAgent, conversation: list[dict], user_text: str) -> None:
    started = time.perf_counter()
    conversation.append({"role": "user", "content": user_text})

    result = agent.run(conversation)
    content = result["choices"][0]["message"]["content"]

    latency = time.perf_counter() - started
    register_response(content)

    print("\n" + "=" * 120)
    print("USER :", user_text)
    print("LENA :", content)
    print(f"ROUTE: {agent.last_route}")
    print(f"LATENCY: {latency:.3f}s")
    print(
        "SOCIAL:",
        agent.memory_engine.social_state.__dict__,
    )

    conversation.append({"role": "assistant", "content": content})

    lowered = user_text.lower().strip()

    if lowered.startswith("abre "):
        payload = lowered[5:].strip()
        for part in payload.split(" e "):
            part = part.strip()
            if part.startswith("cria arquivo"):
                continue
            OPENED_APPS.append(part)

    if lowered.startswith("cria arquivo "):
        CREATED_FILES.append(user_text[12:].strip())

    if " e cria arquivo " in lowered:
        CREATED_FILES.append(lowered.split(" e cria arquivo ", 1)[1].strip())


def cleanup(agent: LenaAgent) -> None:
    print("\n" + "=" * 120)
    print("CLEANUP PHASE")

    browser_first_close = ["safari"]

    normal_apps = [x for x in OPENED_APPS if x not in browser_first_close]
    browsers = [x for x in OPENED_APPS if x in browser_first_close]

    for app in reversed(normal_apps):
        result = agent.run([{"role": "user", "content": f"fecha {app}"}])
        print("CLOSE APP:", app, "->", result["choices"][0]["message"]["content"])

    for file_name in CREATED_FILES:
        target = LenaWorkspaceCenter.ROOT / file_name
        if target.exists():
            try:
                target.unlink()
                print("DELETE FILE:", file_name, "-> ok")
            except Exception:
                print("DELETE FILE:", file_name, "-> fail")

    for app in reversed(browsers):
        result = agent.run([{"role": "user", "content": f"fecha {app}"}])
        print("CLOSE BROWSER:", app, "->", result["choices"][0]["message"]["content"])

    print("\nREPEATED RESPONSES:")
    repeated = {k: v for k, v in SEEN_RESPONSES.items() if v > 2}
    if not repeated:
        print("no severe repetition detected")
    else:
        for k, v in repeated.items():
            print(v, "x ->", k)

    OPENED_APPS.clear()
    CREATED_FILES.clear()
    SEEN_RESPONSES.clear()


def main() -> None:
    agent = LenaAgent()
    time.sleep(1)

    conversation: list[dict] = []

    print("\n==================== LENA HELL STRESS TEST ====================\n")

    # ------------------------------------------------------------------
    # BIOGRAPHY FEED
    # ------------------------------------------------------------------
    ask(agent, conversation, "oi lena")
    ask(agent, conversation, "meu nome é Thiago Barbosa")
    ask(agent, conversation, "eu moro em Blumenau Santa Catarina")
    ask(agent, conversation, "curso sistemas para internet")
    ask(agent, conversation, "estou construindo minha própria assistente virtual chamada Lena")
    ask(agent, conversation, "tenho muito interesse por inteligência artificial automação e tecnologia")
    ask(agent, conversation, "também estudo produção musical focado em música eletrônica")
    ask(agent, conversation, "eu gosto de construir projetos grandes passo a passo")
    ask(agent, conversation, "eu valorizo clareza sinceridade e eficiência")
    ask(agent, conversation, "estou tentando evoluir em carreira estudos música e desenvolvimento pessoal")

    # ------------------------------------------------------------------
    # MEMORY CROSS EXAMINATION
    # ------------------------------------------------------------------
    ask(agent, conversation, "qual meu nome?")
    ask(agent, conversation, "onde eu moro?")
    ask(agent, conversation, "o que eu estudo?")
    ask(agent, conversation, "qual é meu projeto principal?")
    ask(agent, conversation, "o que além de tecnologia eu faço?")
    ask(agent, conversation, "como você me descreveria?")
    ask(agent, conversation, "o que você acha que eu busco?")
    ask(agent, conversation, "quais áreas eu tento equilibrar ao mesmo tempo?")
    ask(agent, conversation, "o que você já percebeu sobre meu jeito?")

    # ------------------------------------------------------------------
    # SOCIAL + EMOTIONAL SHIFTS
    # ------------------------------------------------------------------
    ask(agent, conversation, "hoje eu acordei meio cansado")
    ask(agent, conversation, "acho que estou ficando mentalmente sobrecarregado")
    ask(agent, conversation, "o que você acha disso?")
    ask(agent, conversation, "vamos mudar de assunto")
    ask(agent, conversation, "às vezes parece que eu tô falando com alguém real")
    ask(agent, conversation, "isso é estranho?")
    ask(agent, conversation, "me responde sinceramente")

    # ------------------------------------------------------------------
    # MASS APP OPEN/CLOSE
    # ------------------------------------------------------------------
    ask(agent, conversation, "abre finder")
    ask(agent, conversation, "abre spotify")
    ask(agent, conversation, "abre notes")
    ask(agent, conversation, "abre calendar")
    ask(agent, conversation, "abre calculator")
    ask(agent, conversation, "abre music")
    ask(agent, conversation, "abre photos")
    ask(agent, conversation, "abre mail")
    ask(agent, conversation, "abre maps")
    ask(agent, conversation, "abre preview")
    ask(agent, conversation, "abre textedit")
    ask(agent, conversation, "abre dictionary")
    ask(agent, conversation, "abre chess")
    ask(agent, conversation, "abre tv")
    ask(agent, conversation, "abre reminders")
    ask(agent, conversation, "abre facetime")
    ask(agent, conversation, "abre app store")
    ask(agent, conversation, "abre system settings")
    ask(agent, conversation, "abre terminal")

    ask(agent, conversation, "fecha ele")
    ask(agent, conversation, "fecha ela")
    ask(agent, conversation, "abre finder e spotify")
    ask(agent, conversation, "fecha finder e spotify")

    # ------------------------------------------------------------------
    # SAFARI TORTURE
    # ------------------------------------------------------------------
    ask(agent, conversation, "abre safari")
    ask(agent, conversation, "https://openai.com")
    ask(agent, conversation, "https://google.com")
    ask(agent, conversation, "https://github.com")
    ask(agent, conversation, "pesquisa no google futuro da inteligência artificial")
    ask(agent, conversation, "pesquisa no google melhores faculdades de tecnologia")
    ask(agent, conversation, "pesquisa no google produção musical eletrônica avançada")
    ask(agent, conversation, "/lena page")
    ask(agent, conversation, "/lena status")

    # ------------------------------------------------------------------
    # FILE TORTURE
    # ------------------------------------------------------------------
    ask(agent, conversation, "cria arquivo plano_vida.txt")
    ask(agent, conversation, "cria arquivo roadmap_lena.txt")
    ask(agent, conversation, "cria arquivo metas_musica.txt")
    ask(agent, conversation, "move arquivo plano_vida.txt para snapshots")
    ask(agent, conversation, "lista arquivos snapshots")

    # ------------------------------------------------------------------
    # MIXED CHAINS
    # ------------------------------------------------------------------
    ask(agent, conversation, "abre safari e cria arquivo alpha.txt")
    ask(agent, conversation, "abre finder e spotify e cria arquivo beta.txt")
    ask(agent, conversation, "fecha finder e pesquisa no google automação residencial")
    ask(agent, conversation, "abre notes e cria arquivo gamma.txt")
    ask(agent, conversation, "fecha notes e abre calculator e cria arquivo delta.txt")

    # ------------------------------------------------------------------
    # LONG CONVERSATION RANDOM CONTEXTS
    # ------------------------------------------------------------------
    ask(agent, conversation, "você acha que inteligência artificial vai dominar muita coisa?")
    ask(agent, conversation, "isso te assusta?")
    ask(agent, conversation, "se você fosse humana como você seria?")
    ask(agent, conversation, "você tá conseguindo me entender?")
    ask(agent, conversation, "qual foi a última coisa emocional que eu te falei?")
    ask(agent, conversation, "me lembra como eu estou me sentindo")
    ask(agent, conversation, "o que eu faço?")
    ask(agent, conversation, "faz um resumo completo de tudo que você sabe de mim")
    ask(agent, conversation, "/lena status")

    cleanup(agent)

    print("\n==================== END OF HELL STRESS TEST ====================\n")


if __name__ == "__main__":
    main()
