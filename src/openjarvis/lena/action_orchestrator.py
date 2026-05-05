from __future__ import annotations


class LenaActionOrchestrator:
    def normalize(self, user_text: str) -> str:
        return user_text.lower().strip()

    def is_desktop_action(self, user_text: str) -> bool:
        lowered = self.normalize(user_text)
        return lowered.startswith(("abre ", "abrir ", "fecha ", "fechar "))

    def is_file_action(self, user_text: str) -> bool:
        lowered = self.normalize(user_text)
        return lowered.startswith(
            ("cria arquivo", "criar arquivo", "move arquivo", "deleta arquivo", "apaga arquivo")
        )

    def is_web_action(self, user_text: str) -> bool:
        lowered = self.normalize(user_text)
        return lowered.startswith(
            ("pesquisa no google", "pesquise", "procura na internet", "busca na internet")
        )
