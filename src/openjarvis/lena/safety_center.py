from __future__ import annotations


class LenaSafetyCenter:
    HIGH_RISK_ACTIONS = {
        "kill_process",
        "send_email",
        "external_upload",
    }

    MEDIUM_RISK_ACTIONS = {
        "create_file",
        "delete_file",
        "move_file",
        "close_app",
        "open_url",
    }

    @classmethod
    def classify(cls, action_name: str) -> str:
        if action_name in cls.HIGH_RISK_ACTIONS:
            return "high"
        if action_name in cls.MEDIUM_RISK_ACTIONS:
            return "medium"
        return "low"

    @classmethod
    def requires_confirmation(cls, action_name: str) -> bool:
        return action_name in cls.HIGH_RISK_ACTIONS
