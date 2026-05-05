from __future__ import annotations

import shutil
from pathlib import Path

from openjarvis.lena.action_guard import LenaActionGuard
from openjarvis.lena.workspace_center import LenaWorkspaceCenter


class LenaFileOperator:
    MAX_READ_CHARS = 4000
    MAX_LIST_ITEMS = 40
    ALLOWED_ZONES = {
        "delivery": LenaWorkspaceCenter.DELIVERY,
        "temp": LenaWorkspaceCenter.TEMP,
        "exports": LenaWorkspaceCenter.EXPORTS,
        "reports": LenaWorkspaceCenter.REPORTS,
    }



    @classmethod
    def _assert_allowed_target(cls, target: Path) -> None:
        allowed_roots = [zone.resolve() for zone in cls.ALLOWED_ZONES.values()]
        resolved = target.resolve()

        if not any(resolved == root or root in resolved.parents for root in allowed_roots):
            raise ValueError("zona não permitida para operação de arquivo")

    @classmethod
    def _safe_path(cls, file_name: str) -> Path:
        raw = str(file_name or "").strip()
        if not raw:
            raise ValueError("zona não permitida para operação de arquivo")

        candidate = Path(raw).expanduser()

        if candidate.is_absolute():
            target = candidate.resolve()
        else:
            parts = candidate.parts
            if not parts:
                raise ValueError("zona não permitida para operação de arquivo")

            zone_name = parts[0].lower()
            zone_root = cls.ALLOWED_ZONES.get(zone_name)
            if zone_root is None:
                raise ValueError("zona não permitida para operação de arquivo")

            relative_inside_zone = Path(*parts[1:]) if len(parts) > 1 else Path()
            target = (zone_root / relative_inside_zone).resolve()

        cls._assert_allowed_target(target)

        return target

    @staticmethod
    def _short_error(exc: Exception) -> str:
        return str(exc) or exc.__class__.__name__

    @staticmethod
    def _valid_list_file(path: Path) -> bool:
        if not path.is_file():
            return False
        if path.name.startswith("."):
            return False
        if LenaActionGuard.is_sensitive_file_payload(path.name):
            return False
        return True

    @classmethod
    def create_file(cls, kernel, file_name: str) -> tuple[bool, str]:
        try:
            path = cls._safe_path(file_name)

            if path.exists() and path.is_dir():
                return False, f"{file_name} é um diretório."

            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)

            if not path.exists() or not path.is_file():
                return False, f"não confirmei a criação de {file_name}."

            return True, f"arquivo {file_name} criado."
        except Exception as exc:
            return False, f"não consegui criar {file_name}: {cls._short_error(exc)}."

    @classmethod
    def read_file(cls, file_name: str) -> tuple[bool, str]:
        try:
            path = cls._safe_path(file_name)

            if not path.exists():
                return False, f"{file_name} não existe."

            if not path.is_file():
                return False, f"{file_name} não é um arquivo."

            content = path.read_text(encoding="utf-8", errors="replace")
            truncated = len(content) > cls.MAX_READ_CHARS
            content = content[: cls.MAX_READ_CHARS].strip()

            if not content:
                return True, f"{file_name} está vazio."

            suffix = " [conteúdo truncado em 4000 caracteres]" if truncated else ""
            return True, f"conteúdo de {file_name}: {content}{suffix}"
        except Exception as exc:
            return False, f"não consegui ler {file_name}: {cls._short_error(exc)}."

    @classmethod
    def delete_file(cls, kernel, file_name: str) -> tuple[bool, str]:
        try:
            path = cls._safe_path(file_name)

            if not path.exists():
                return False, f"{file_name} não existe."

            if not path.is_file():
                return False, f"{file_name} não é um arquivo."

            path.unlink()

            if path.exists():
                return False, f"não confirmei a remoção de {file_name}."

            return True, f"arquivo {file_name} deletado."
        except Exception as exc:
            return False, f"não consegui deletar {file_name}: {cls._short_error(exc)}."

    @classmethod
    def move_file(cls, kernel, file_name: str, zone: str) -> tuple[bool, str]:
        try:
            source = cls._safe_path(file_name)

            if not source.exists():
                return False, f"{file_name} não existe."

            if not source.is_file():
                return False, f"{file_name} não é um arquivo."

            target_zone = cls._safe_path(zone)
            target = (target_zone / source.name).resolve()
            cls._assert_allowed_target(target)

            if target.exists():
                return False, f"{target.name} já existe em {zone}."

            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))

            if source.exists() or not target.exists() or not target.is_file():
                return False, f"não confirmei a movimentação de {file_name}."

            return True, f"arquivo {file_name} movido para {zone}."
        except Exception as exc:
            return False, f"não consegui mover {file_name}: {cls._short_error(exc)}."

    @classmethod
    def list_files(cls, zone: str) -> tuple[bool, str]:
        try:
            target = cls._safe_path(zone)

            if not target.exists():
                return False, f"{zone} não existe."

            if not target.is_dir():
                return False, f"{zone} não é um diretório."

            files = sorted(
                path.name
                for path in target.iterdir()
                if cls._valid_list_file(path)
            )[: cls.MAX_LIST_ITEMS]

            if not files:
                return True, f"{zone} tá vazio."

            return True, f"arquivos em {zone}: {', '.join(files)}"
        except Exception as exc:
            return False, f"não consegui listar {zone}: {cls._short_error(exc)}."

    @classmethod
    def list_zone(cls, zone: str) -> tuple[bool, str]:
        return cls.list_files(zone)
