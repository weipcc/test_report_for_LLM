"""
共用的工具函式。
"""


def calculate_discount(price: float, discount_percent: float, member_tier: str) -> float:
    """依折扣百分比計算折扣後金額，並依會員等級再疊加額外折扣。"""
    base_discounted = price * (1 - discount_percent / 100)
    tier_extra = {"gold": 0.05, "silver": 0.02, "regular": 0.0}
    extra = tier_extra.get(member_tier, 0.0)
    return base_discounted * (1 - extra)


def format_currency(amount: float) -> str:
    """把金額格式化成字串，顯示到小數點後兩位。"""
    return f"${amount:.2f}"
