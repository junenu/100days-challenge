from dataclasses import dataclass
from typing import Optional
import datetime


@dataclass(frozen=True)
class Book:
    id: int
    title: str
    author: str
    genre: Optional[str]
    pages: Optional[int]
    status: str
    rating: Optional[int]
    notes: Optional[str]
    started_at: Optional[datetime.date]
    finished_at: Optional[datetime.date]
    created_at: datetime.datetime

    @classmethod
    def from_row(cls, row: dict) -> "Book":
        return cls(**row)

    def status_label(self) -> str:
        return {"want": "積読", "reading": "読書中", "read": "読了"}.get(self.status, self.status)

    def rating_stars(self) -> str:
        if self.rating is None:
            return "—"
        return "★" * self.rating + "☆" * (5 - self.rating)
