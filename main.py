"""
main.py
圖書館管理系統的示範入口，串接館藏、借還書、通知、報表四個模組。
"""

from datetime import date

from inventory import InventoryManager
from lending import LendingService
from models import Book, Member
from notifications import send_batch_reminders
from reports import generate_monthly_report


def setup_demo_data() -> tuple[InventoryManager, LendingService, list[Member]]:
    """建立一組示範資料，方便展示整個系統怎麼運作。"""
    inventory = InventoryManager()
    inventory.add_book(
        Book(isbn="978-1", title="深度學習入門", author="齋藤康毅", total_copies=3, available_copies=3)
    )
    inventory.add_book(
        Book(isbn="978-2", title="演算法圖鑑", author="石田保輝", total_copies=2, available_copies=2)
    )

    lending = LendingService(inventory)

    members = [
        Member(member_id="M001", name="小明", email="ming@example.com", join_date=date(2024, 1, 1)),
        Member(member_id="M002", name="小華", email="hua@example.com", join_date=date(2024, 3, 1)),
    ]

    return inventory, lending, members


def run_demo() -> None:
    """跑一遍完整流程：借書、預約、產生報表、寄送提醒。"""
    inventory, lending, members = setup_demo_data()
    today = date(2026, 9, 21)

    record = lending.borrow_book(members[0], "978-1", today)
    print(f"借閱成功，紀錄編號: {record.record_id}")

    # 示範預約流程：小華想借一本目前已被借光的書
    inventory.restock("978-1", 0)  # 確保狀態一致，不影響庫存
    if not inventory.check_availability("978-2"):
        lending.request_reservation(members[1], "978-2", is_vip=False)
        print(f"{members[1].name} 已加入《演算法圖鑑》預約等候名單")

    report = generate_monthly_report(inventory, lending, members, today)
    print(report)

    overdue_records = lending.get_overdue_records(today)
    sent = send_batch_reminders(members, overdue_records, today)
    print(f"共寄送 {sent} 則提醒")


if __name__ == "__main__":
    run_demo()
