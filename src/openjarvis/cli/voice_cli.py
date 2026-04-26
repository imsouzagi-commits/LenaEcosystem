# src/openjarvis/cli/voice_cli.py

from openjarvis.agent.lena_agent import LenaAgent
from openjarvis.voice.voice_input import record_audio, transcribe


class DummyEngine:
    def generate(self, messages, model=None):
        return {
            "content": f"Echo: {messages[-1].content}"
        }


agent = LenaAgent(engine=DummyEngine())


def main():
    print("🎤 Lena Voice CLI (CTRL+C para sair)\n")

    while True:
        try:
            input("Pressione ENTER para falar...")

            audio = record_audio()
            text = transcribe(audio)

            print(f"\n🗣 Você disse: {text}")

            if not text.strip():
                print("⚠️ Nada detectado\n")
                continue

            response = agent.run([
                {"role": "user", "content": text}
            ])

            print(f"🤖 Lena: {response['choices'][0]['message']['content']}\n")

        except KeyboardInterrupt:
            print("\nSaindo...")
            break


if __name__ == "__main__":
    main()