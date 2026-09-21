"""
主程式，計算購物車總金額並套用折扣。
"""

from utils import calculate_discount, format_currency


def checkout(cart_total: float, discount_percent: float) -> None:
    """結帳流程：套用折扣並印出最終金額。"""
    print(f"開始結帳，購物車金額: {format_currency(cart_total)}")
    final_amount = calculate_discount(cart_total, discount_percent)
    print(f"結帳金額: {format_currency(final_amount)}")


if __name__ == "__main__":
    checkout(cart_total=150.0, discount_percent=10)
