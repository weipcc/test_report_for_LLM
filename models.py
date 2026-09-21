"""
models.py
定義圖書館管理系統裡的核心資料結構：書籍與會員。
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Book:
    """代表館藏中的一本書。"""

    isbn: str
    title: str
    author: str
    total_copies: int
    available_copies: int
    category: str = "一般"
    location: str = "主館"
    tags: list[str] = field(default_factory=list)

    def is_available(self) -> bool:
        """檢查是否還有可借閱的副本。"""
        return self.available_copies > 0

    def add_tag(self, tag: str) -> None:
        """為這本書新增一個標籤，方便分類與搜尋。"""
        if tag not in self.tags:
            self.tags.append(tag)


@dataclass
class Member:
    """代表圖書館的會員。"""

    member_id: str
    name: str
    email: str
    join_date: date
    membership_tier: str = "regular"
    borrowed_books: list[str] = field(default_factory=list)
    overdue_count: int = 0
    waitlisted_books: list[str] = field(default_factory=list)

    def can_borrow(self, max_books: int = 5) -> bool:
        """檢查會員是否還能繼續借書（未超過借閱上限，且沒有過多逾期紀錄）。"""
        if len(self.borrowed_books) >= max_books:
            return False
        if self.overdue_count >= 3:
            return False
        return True

    def get_borrow_limit(self) -> int:
        """依會員等級決定最大可借閱本數。"""
        tier_limits = {"regular": 5, "gold": 10, "platinum": 15}
        return tier_limits.get(self.membership_tier, 5)


@dataclass
class LendingRecord:
    """代表一筆借還書紀錄。"""

    record_id: str
    member_id: str
    isbn: str
    borrow_date: date
    due_date: date
    return_date: date | None = None
    late_fee: float = 0.0

    def is_overdue(self, today: date) -> bool:
        """判斷這筆紀錄目前是否已逾期未還。"""
        if self.return_date is not None:
            return False
        return today > self.due_date


@dataclass
class Reservation:
    """代表一筆預約紀錄：會員預約目前無庫存的書籍，補貨後依序通知。"""

    reservation_id: str
    isbn: str
    member_id: str
    requested_date: date
    priority: bool = False
    fulfilled: bool = False
