def format_distance_persian(meters: float) -> str:
    """
    تبدیل متر به رشته فارسی مناسب
    """
    if meters < 1000:
        return f"فاصله حدود {int(meters)} متر است."
    else:
        km = meters / 1000
        return f"فاصله حدود {km:.1f} کیلومتر است."


def format_area_persian(m2: float) -> str:
    """
    تبدیل متر مربع به رشته فارسی
    """
    if m2 < 10000:
        return f"مساحت حدود {int(m2)} متر مربع است."
    else:
        km2 = m2 / 1_000_000
        return f"مساحت حدود {km2:.2f} کیلومتر مربع است."
