# src/openjarvis/cli/main.py

from openjarvis.agent.lena_agent import LenaAgent


def main():
    agent = LenaAgent()

    print("Lena CLI iniciada (digite 'exit' para sair)\n")

    while True:
        user = input(">>> ")

        if user.lower() in ["exit", "quit"]:
            break

        response = agent.run([
            {"role": "user", "content": user}
        ])

        print(response["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()