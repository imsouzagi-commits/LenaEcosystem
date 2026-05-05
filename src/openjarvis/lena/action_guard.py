from __future__ import annotations

from openjarvis.lena.audit_log_center import LenaAuditLogCenter
from openjarvis.lena.safety_center import LenaSafetyCenter


class LenaActionGuard:
    BLOCKED_TOKENS = (
        "..",
        "~",
        "/etc",
        "/usr",
        "/private",
        ".ssh",
        ".env",
        ".git",
        "keychains",
    )

    SENSITIVE_FILE_EXTENSIONS = {
        ".env",
        ".pem",
        ".key",
        ".sqlite",
        ".db",
    }

    PROTECTED_APPS = {
        "Terminal",
        "Console",
        "Activity Monitor",
        "System Settings",
        "ChatGPT",
        "Code",
        "Visual Studio Code",
    }

    BLOCKED_WEB_PAYLOADS = (
        "javascript:",
        "file://",
        "about:",
        "data:",
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
    )

    @classmethod
    def _invalid_payload(cls, payload: str) -> bool:
        if not payload or not payload.strip():
            return True

        lowered = payload.lower()
        return (
            any(token in lowered for token in cls.BLOCKED_TOKENS)
            or cls.is_sensitive_file_payload(payload)
        )

    @classmethod
    def is_sensitive_file_payload(cls, payload: str) -> bool:
        value = str(payload or "").strip()
        if not value:
            return True

        normalized = value.replace("\\", "/")
        lowered = normalized.lower()
        parts = [part for part in normalized.split("/") if part]

        if "\\" in value:
            return True

        if ".." in parts:
            return True

        if any(part.startswith(".") for part in parts):
            return True

        if any(lowered.endswith(ext) for ext in cls.SENSITIVE_FILE_EXTENSIONS):
            return True

        return False

    @classmethod
    def _app_blocked(cls, action_name: str, payload: str) -> bool:
        if action_name != "close_app":
            return False

        return payload.strip().title() in cls.PROTECTED_APPS

    @classmethod
    def _web_payload_blocked(cls, action_name: str, payload: str) -> bool:
        if action_name != "open_url":
            return False

        lowered = payload.lower().strip()
        return any(token in lowered for token in cls.BLOCKED_WEB_PAYLOADS)

    @classmethod
    def allow(cls, action_name: str, payload: str) -> tuple[bool, str]:
        risk = LenaSafetyCenter.classify(action_name)

        if cls._invalid_payload(payload):
            LenaAuditLogCenter.write(action_name, payload, "blocked_invalid_payload")
            return False, "payload bloqueado por segurança."

        if cls._app_blocked(action_name, payload):
            LenaAuditLogCenter.write(action_name, payload, "blocked_protected_app")
            return False, "esse app é protegido da sessão."

        if cls._web_payload_blocked(action_name, payload):
            LenaAuditLogCenter.write(action_name, payload, "blocked_web_payload")
            return False, "url bloqueada por segurança."

        if LenaSafetyCenter.requires_confirmation(action_name):
            LenaAuditLogCenter.write(action_name, payload, "blocked_confirmation_required")
            return False, "essa ação exige confirmação explícita."

        LenaAuditLogCenter.write(action_name, payload, f"allowed_{risk}")
        return True, risk
