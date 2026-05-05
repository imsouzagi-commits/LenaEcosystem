from __future__ import annotations

from openjarvis.lena.action_guard import LenaActionGuard
from openjarvis.lena.file_operator import LenaFileOperator


class LenaFileController:
    def __init__(self, kernel) -> None:
        self.kernel = kernel

    @staticmethod
    def _guard(action_name: str, payload: str) -> tuple[bool, str]:
        allowed, reason = LenaActionGuard.allow(action_name, payload)
        if not allowed:
            return False, reason
        return True, ""

    @staticmethod
    def _message(result: tuple[bool, str]) -> str:
        ok, message = result
        return message if ok else f"falha: {message}"

    @staticmethod
    def _payload(user_text: str, prefix: str) -> str:
        return user_text[len(prefix):].strip()

    def _create(self, file_name: str) -> str:
        allowed = self._guard("create_file", file_name)
        if not allowed[0]:
            return allowed[1]
        return self._message(LenaFileOperator.create_file(self.kernel, file_name))

    def _read(self, file_name: str) -> str:
        allowed = self._guard("read_file", file_name)
        if not allowed[0]:
            return allowed[1]
        return self._message(LenaFileOperator.read_file(file_name))

    def _delete(self, file_name: str) -> str:
        allowed = self._guard("delete_file", file_name)
        if not allowed[0]:
            return allowed[1]
        return self._message(LenaFileOperator.delete_file(self.kernel, file_name))

    def _move(self, file_name: str, zone: str) -> str:
        allowed_file = self._guard("move_file", file_name)
        if not allowed_file[0]:
            return allowed_file[1]

        allowed_zone = self._guard("move_file", zone)
        if not allowed_zone[0]:
            return allowed_zone[1]

        return self._message(LenaFileOperator.move_file(self.kernel, file_name, zone))

    def _list(self, zone: str) -> str:
        allowed = self._guard("list_files", zone)
        if not allowed[0]:
            return allowed[1]
        return self._message(LenaFileOperator.list_files(zone))

    def execute(self, user_text: str) -> str:
        lowered = user_text.lower().strip()

        prefix = "cria arquivo "
        if lowered.startswith(prefix):
            return self._create(self._payload(user_text, prefix))

        prefix = "criar arquivo "
        if lowered.startswith(prefix):
            return self._create(self._payload(user_text, prefix))

        prefix = "lê arquivo "
        if lowered.startswith(prefix):
            return self._read(self._payload(user_text, prefix))

        prefix = "le arquivo "
        if lowered.startswith(prefix):
            return self._read(self._payload(user_text, prefix))

        prefix = "lista arquivos "
        if lowered.startswith(prefix):
            return self._list(self._payload(user_text, prefix))

        prefix = "move arquivo "
        if lowered.startswith(prefix):
            payload = self._payload(user_text, prefix)
            if " para " not in payload:
                return "falha: faltou destino pra mover arquivo."

            file_name, zone = payload.split(" para ", 1)
            return self._move(file_name.strip(), zone.strip())

        prefix = "deleta arquivo "
        if lowered.startswith(prefix):
            return self._delete(self._payload(user_text, prefix))

        prefix = "deletar arquivo "
        if lowered.startswith(prefix):
            return self._delete(self._payload(user_text, prefix))

        return "falha: não entendi operação de arquivo."
