from __future__ import annotations

from datetime import datetime, timedelta


class TemporalCenter:
    def __init__(self):
        pass

    def now(self) -> datetime:
        return datetime.now()

    def current_hour(self) -> int:
        return self.now().hour

    def period_of_day(self) -> str:
        hour = self.current_hour()

        if 5 <= hour < 12:
            return "manhã"

        if 12 <= hour < 18:
            return "tarde"

        return "noite"

    def human_now(self) -> str:
        return self.now().strftime("%d/%m/%Y %H:%M")

    def today_name(self) -> str:
        return self.now().strftime("%d/%m/%Y")

    def tomorrow_name(self) -> str:
        return (self.now() + timedelta(days=1)).strftime("%d/%m/%Y")

    def yesterday_name(self) -> str:
        return (self.now() - timedelta(days=1)).strftime("%d/%m/%Y")

    def day_has_turned(self) -> bool:
        return self.current_hour() < 5

    def is_morning(self) -> bool:
        return self.period_of_day() == "manhã"

    def is_afternoon(self) -> bool:
        return self.period_of_day() == "tarde"

    def is_night(self) -> bool:
        return self.period_of_day() == "noite"