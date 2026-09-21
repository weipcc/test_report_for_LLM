"""
inventory.py
負責管理館藏書籍：新增、移除、查詢可用性、補貨、預約排隊。
"""

from models import Book, Reservation


class InventoryManager:
    """管理整個圖書館的館藏書籍。"""

    def __init__(self) -> None:
        self._books: dict[str, Book] = {}
        self._reservations: dict[str, list[Reservation]] = {}

    def add_book(self, book: Book) -> None:
        """把一本新書加入館藏。如果 ISBN 已存在，會直接覆蓋。"""
        self._books[book.isbn] = book

    def remove_book(self, isbn: str) -> bool:
        """從館藏移除一本書，回傳是否成功移除。"""
        if isbn in self._books:
            del self._books[isbn]
            return True
        return False

    def get_book(self, isbn: str) -> Book | None:
        """依 ISBN 查詢書籍，找不到回傳 None。"""
        return self._books.get(isbn)

    def check_availability(self, isbn: str) -> bool:
        """檢查某本書目前是否還有可借閱的副本。"""
        book = self._books.get(isbn)
        if book is None:
            return False
        return book.is_available()

    def restock(self, isbn: str, quantity: int) -> None:
        """幫某本書補充副本數量（總數與可借數都增加），並依序處理等候中的預約。"""
        book = self._books.get(isbn)
        if book is None:
            raise ValueError(f"找不到 ISBN 為 {isbn} 的書籍")
        book.total_copies += quantity
        book.available_copies += quantity
        self._fulfill_pending_reservations(isbn)

    def reserve_book(self, isbn: str, member_id: str, priority: bool = False) -> Reservation:
        """
        幫會員預約目前無庫存的書籍，加入等候名單。
        依 priority 決定是否插到隊伍前面（例如 VIP 會員優先）。
        """
        from datetime import date

        reservation = Reservation(
            reservation_id=f"R-{isbn}-{member_id}",
            isbn=isbn,
            member_id=member_id,
            requested_date=date.today(),
            priority=priority,
        )
        queue = self._reservations.setdefault(isbn, [])
        if priority:
            queue.insert(0, reservation)
        else:
            queue.append(reservation)
        return reservation

    def _fulfill_pending_reservations(self, isbn: str) -> list[Reservation]:
        """補貨後，依隊伍順序把可借副本分配給等候中的預約。"""
        queue = self._reservations.get(isbn, [])
        book = self._books.get(isbn)
        fulfilled = []

        while queue and book and book.available_copies > 0:
            reservation = queue.pop(0)
            reservation.fulfilled = True
            book.available_copies -= 1
            fulfilled.append(reservation)

        return fulfilled

    def get_reservation_queue_length(self, isbn: str) -> int:
        """查詢某本書目前的預約等候人數。"""
        return len(self._reservations.get(isbn, []))

    def search_by_category(self, category: str) -> list[Book]:
        """依分類搜尋書籍。"""
        return [b for b in self._books.values() if b.category == category]

    def search_by_title(self, keyword: str) -> list[Book]:
        """依書名關鍵字搜尋書籍（不分大小寫）。"""
        keyword_lower = keyword.lower()
        return [b for b in self._books.values() if keyword_lower in b.title.lower()]

    def total_book_count(self) -> int:
        """回傳館藏總書籍種類數量。"""
        return len(self._books)

    def low_stock_books(self, threshold: int = 2) -> list[Book]:
        """找出可借副本數低於門檻的書籍，方便提醒補貨。"""
        return [b for b in self._books.values() if b.available_copies < threshold]
