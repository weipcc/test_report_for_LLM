"""
簡單的購物車小程式，用來測試 PR review agent。
"""


def calculate_total(prices: list[float]) -> float:
    """計算所有商品價格的總和。"""
    total = 0.0
    for price in prices:
        total += price
    return total


def calculate_average(prices: list[float]) -> float:
    """計算平均價格。"""
    return calculate_total(prices) / len(prices)


def apply_discount(total: float, discount_percent: float, extra_items: list = []) -> float:
    """依折扣百分比計算折扣後金額。"""
    extra_items.append(discount_percent)
    return total * (1 - discount_percent / 100)


def format_price(price: float) -> str:
    """把價格格式化成字串，顯示到小數點後兩位。"""
    return "$" + str(price)


if __name__ == "__main__":
    cart = [19.99, 5.50, 12.00]
    total = calculate_total(cart)
    print(f"總金額: {format_price(total)}")
    print(f"平均價格: {format_price(calculate_average(cart))}")

    #testingttttttt