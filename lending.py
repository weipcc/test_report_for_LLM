"""
lending.py
負責處理借書、還書、逾期罰款計算的核心業務邏輯。
"""

from datetime import date, timedelta

from inventory import InventoryManager
from models import LendingRecord, Member

DEFAULT_LOAN_PERIOD_DAYS = 14
LATE_FEE_PER_DAY = 5.0


class LendingService:
    """處理借還書流程，依賴 InventoryManager 來查詢與更新館藏狀態。"""

    def __init__(self, inventory: InventoryManager) -> None:
        self.inventory = inventory
        self._records: dict[str, LendingRecord] = {}

    def borrow_book(self, member: Member, isbn: str, today: date) -> LendingRecord:
        """處理借書流程：檢查會員資格、檢查庫存、建立借閱紀錄。"""
        if not member.can_borrow(member.get_borrow_limit()):
            raise PermissionError(f"會員 {member.name} 已達借閱上限或有過多逾期紀錄")

        if not self.inventory.check_availability(isbn):
            raise ValueError(f"書籍 {isbn} 目前無可借閱副本")

        book = self.inventory.get_book(isbn)
        book.available_copies -= 1
        member.borrowed_books.append(isbn)

        record = LendingRecord(
            record_id=f"{member.member_id}-{isbn}-{today.isoformat()}",
            member_id=member.member_id,
            isbn=isbn,
            borrow_date=today,
            due_date=today + timedelta(days=DEFAULT_LOAN_PERIOD_DAYS),
        )
        self._records[record.record_id] = record
        return record

    def return_book(self, member: Member, isbn: str, today: date) -> float:
        """處理還書流程：更新館藏、計算逾期罰款、更新會員紀錄。"""
        matching_records = [
            r
            for r in self._records.values()
            if r.member_id == member.member_id and r.isbn == isbn and r.return_date is None
        ]
        if not matching_records:
            raise ValueError("找不到對應的借閱紀錄")

        record = matching_records[0]
        record.return_date = today

        late_fee = 0.0
        if today > record.due_date:
            overdue_days = (today - record.due_date).days
            late_fee = overdue_days * LATE_FEE_PER_DAY
            member.overdue_count += 1

        record.late_fee = late_fee

        book = self.inventory.get_book(isbn)
        if book is not None:
            book.available_copies += 1

        if isbn in member.borrowed_books:
            member.borrowed_books.remove(isbn)

        return late_fee

    def get_overdue_records(self, today: date) -> list[LendingRecord]:
        """列出所有目前逾期未還的借閱紀錄。"""
        return [r for r in self._records.values() if r.is_overdue(today)]

    def request_reservation(self, member: Member, isbn: str, is_vip: bool = False) -> None:
        """
        當書籍目前無庫存時，幫會員登記預約，加入等候名單。
        VIP 會員（is_vip=True）會被排在隊伍前面優先處理。
        """
        if self.inventory.check_availability(isbn):
            raise ValueError("這本書目前仍有庫存，不需要預約，請直接借閱")

        reservation = self.inventory.reserve_book(
            isbn=isbn, requester_id=member.member_id, priority=is_vip
        )
        member.waitlisted_books.append(isbn)
        return reservation

    def get_waitlist_position(self, isbn: str) -> int:
        """查詢某本書目前的預約等候人數，方便告知會員大概要等多久。"""
        return self.inventory.get_reservation_queue_length(isbn)
