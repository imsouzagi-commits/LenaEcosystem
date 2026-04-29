from __future__ import annotations

from collections import Counter


class LenaScoreReport:
    def __init__(self) -> None:
        self.total_tests = 0
        self.route_counter: Counter[str] = Counter()

        self.total_latency = 0.0
        self.max_latency = 0.0

        self.bad_outputs = 0
        self.desktop_failures = 0
        self.agent_failures = 0

    def register(self, route: str, latency: float, answer: str) -> None:
        self.total_tests += 1
        self.route_counter[route] += 1

        self.total_latency += latency
        self.max_latency = max(self.max_latency, latency)

        lowered = answer.lower()

        robotic_flags = [
            "como inteligência artificial",
            "como ia",
            "sou apenas uma ia",
            "não tenho sentimentos",
            "não posso sentir",
            "não possuo emoções",
            "sou um modelo de linguagem",
        ]

        if any(flag in lowered for flag in robotic_flags):
            self.bad_outputs += 1

    def register_desktop_failure(self) -> None:
        self.desktop_failures += 1

    def register_agent_failure(self) -> None:
        self.agent_failures += 1

    def _average_latency(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.total_latency / self.total_tests

    def _human_score(self) -> float:
        if self.total_tests == 0:
            return 100.0

        score = 100.0
        score -= (self.bad_outputs * 8.0)
        score -= (self.desktop_failures * 3.0)
        score -= (self.agent_failures * 5.0)

        return max(score, 0.0)

    def _azure_usage_percent(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.route_counter.get("AZURE_OPENAI", 0) / self.total_tests) * 100

    def _unknown_usage_percent(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.route_counter.get("UNKNOWN", 0) / self.total_tests) * 100

    def _final_grade(self) -> str:
        human = self._human_score()
        avg_latency = self._average_latency()

        if (
            human >= 90
            and avg_latency <= 1.5
            and self.desktop_failures == 0
            and self.agent_failures == 0
        ):
            return "A+"

        if human >= 80 and avg_latency <= 2.5:
            return "A"

        if human >= 70:
            return "B"

        if human >= 55:
            return "C"

        return "D"

    def render(self) -> None:
        avg_latency = self._average_latency()
        human_score = self._human_score()
        azure_percent = self._azure_usage_percent()
        unknown_percent = self._unknown_usage_percent()
        final_grade = self._final_grade()

        print("\n" + "=" * 118)
        print("LENA PERFORMANCE SCORE REPORT")
        print("=" * 118)

        print("TOTAL TESTS:", self.total_tests)
        print()

        for route, count in self.route_counter.items():
            print(f"{route}: {count}")

        print()
        print(f"AVG LATENCY: {avg_latency:.3f}s")
        print(f"MAX LATENCY: {self.max_latency:.3f}s")
        print()

        print("BAD HUMANNESS OUTPUTS:", self.bad_outputs)
        print("DESKTOP FAILURES:", self.desktop_failures)
        print("AGENT FAILURES:", self.agent_failures)
        print()

        print(f"HUMAN SCORE: {human_score:.1f}%")
        print(f"AZURE ROUTE USAGE: {azure_percent:.1f}%")
        print(f"UNKNOWN ROUTE USAGE: {unknown_percent:.1f}%")
        print()

        print("FINAL QA GRADE:", final_grade)
        print("=" * 118)