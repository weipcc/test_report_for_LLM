"""
notifications.py
負責產生跟寄送提醒訊息（實際寄送這裡先用印出來模擬，不接真正的郵件服務）。
"""

from datetime import date

from models import LendingRecord, Member


def format_due_reminder(member: Member, record: LendingRecord) -> str:
    """組出一則「即將到期提醒」的訊息文字。"""
    return (
        f"親愛的 {member.name} 您好，您借閱的書籍（ISBN: {record.isbn}）"
        f"將於 {record.due_date.isoformat()} 到期，請記得歸還。"
    )


def format_overdue_notice(member: Member, record: LendingRecord, today: date) -> str:
    """組出一則「已逾期通知」的訊息文字，包含目前累積的罰款金額。"""
    overdue_days = (today - record.due_date).days
    estimated_fee = overdue_days * 5.0
    return (
        f"親愛的 {member.name} 您好，您借閱的書籍（ISBN: {record.isbn}）"
        f"已逾期 {overdue_days} 天，目前累積罰款約 ${estimated_fee:.2f}，請盡快歸還。"
    )


def send_reminder(member: Member, message: str) -> bool:
    """模擬寄送提醒訊息給會員，實際上只是印出來。"""
    print(f"[通知] 寄送給 {member.email}: {message}")
    return True


def format_reservation_ready_notice(member: Member, isbn: str) -> str:
    """組出一則「預約書籍已到貨」的通知訊息文字。"""
    return (
        f"親愛的 {member.name} 您好，您預約的書籍（ISBN: {isbn}）已經到貨，"
        f"請於 3 天內前來借閱，逾期將自動釋出給下一位等候者。"
    )


def send_reservation_ready_notices(members: list[Member], fulfilled_isbns: list[str]) -> int:
    """批次通知「預約到貨」的會員，回傳成功寄送的數量。"""
    sent_count = 0
    for member in members:
        for isbn in list(member.waitlisted_books):
            if isbn in fulfilled_isbns:
                message = format_reservation_ready_notice(member, isbn)
                if send_reminder(member, message):
                    sent_count += 1
                    member.waitlisted_books.remove(isbn)
    return sent_count


def send_batch_reminders(members: list[Member], records: list[LendingRecord], today: date) -> int:
    """批次寄送提醒，回傳成功寄送的數量。"""
    sent_count = 0
    member_map = {m.member_id: m for m in members}

    for record in records:
        member = member_map.get(record.member_id)
        if member is None:
            continue

        if record.is_overdue(today):
            message = format_overdue_notice(member, record, today)
        else:
            message = format_due_reminder(member, record)

        if send_reminder(member, message):
            sent_count += 1

    return sent_count
