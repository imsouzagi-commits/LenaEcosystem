from __future__ import annotations


class LenaTaskContext:
    last_file: str | None = None
    last_query: str | None = None

    app_stack: list[str] = []

    @classmethod
    def remember_file(cls, name: str) -> None:
        cls.last_file = name

    @classmethod
    def remember_query(cls, query: str) -> None:
        cls.last_query = query

    @classmethod
    def remember_app(cls, name: str) -> None:
        cls.app_stack.append(name)

    @classmethod
    def resolve_last_app(cls) -> str | None:
        if not cls.app_stack:
            return None
        return cls.app_stack[-1]

    @classmethod
    def consume_last_app(cls) -> str | None:
        if not cls.app_stack:
            return None
        return cls.app_stack.pop()

    @classmethod
    def forget_app(cls, name: str) -> None:
        if name in cls.app_stack:
            cls.app_stack = [x for x in cls.app_stack if x != name]
