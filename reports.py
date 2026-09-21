"""
reports.py
負責彙整統計資料，產生管理報表（例如月報、逾期摘要）。
"""

from datetime import date

from inventory import InventoryManager
from lending import LendingService
from models import Member


def generate_inventory_summary(inventory: InventoryManager) -> dict:
    """產生館藏整體摘要：總書籍種類數、低庫存清單。"""
    low_stock = inventory.low_stock_books(threshold=2)
    return {
        "total_titles": inventory.total_book_count(),
        "low_stock_count": len(low_stock),
        "low_stock_titles": [b.title for b in low_stock],
    }


def generate_overdue_summary(lending: LendingService, today: date) -> dict:
    """產生逾期摘要：逾期筆數、預估總罰款。"""
    overdue_records = lending.get_overdue_records(today)
    total_estimated_fee = 0.0
    for record in overdue_records:
        overdue_days = (today - record.due_date).days
        total_estimated_fee += overdue_days * 5.0

    return {
        "overdue_count": len(overdue_records),
        "estimated_total_fee": total_estimated_fee,
    }


def generate_member_activity_report(members: list[Member]) -> dict:
    """產生會員活動報表：各等級的會員數、平均借閱本數。"""
    tier_counts: dict[str, int] = {}
    total_borrowed = 0

    for member in members:
        tier_counts[member.membership_tier] = tier_counts.get(member.membership_tier, 0) + 1
        total_borrowed += len(member.borrowed_books)

    average_borrowed = total_borrowed / len(members) if members else 0.0

    return {
        "tier_counts": tier_counts,
        "average_borrowed_books": average_borrowed,
        "total_members": len(members),
    }


def generate_reservation_summary(inventory: InventoryManager, isbns: list[str]) -> dict:
    """產生預約隊伍摘要：列出每本書目前的等候人數。"""
    queue_lengths = {isbn: inventory.get_reservation_queue_length(isbn) for isbn in isbns}
    total_waiting = sum(queue_lengths.values())
    return {
        "queue_lengths": queue_lengths,
        "total_waiting": total_waiting,
    }


def generate_monthly_report(
    inventory: InventoryManager, lending: LendingService, members: list[Member], today: date
) -> str:
    """把三份摘要組合成一份人類可讀的月報文字。"""
    inventory_summary = generate_inventory_summary(inventory)
    overdue_summary = generate_overdue_summary(lending, today)
    member_report = generate_member_activity_report(members)

    lines = [
        f"=== 圖書館月報（{today.isoformat()}）===",
        f"館藏總種類數: {inventory_summary['total_titles']}",
        f"低庫存書籍數: {inventory_summary['low_stock_count']}",
        f"目前逾期筆數: {overdue_summary['overdue_count']}",
        f"預估逾期罰款總額: ${overdue_summary['estimated_total_fee']:.2f}",
        f"總會員數: {member_report['total_members']}",
        f"平均每人借閱本數: {member_report['average_borrowed_books']:.2f}",
    ]
    return "\n".join(lines)
