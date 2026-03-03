from datetime import datetime, timedelta, timezone


BJ_TZ = timezone(timedelta(hours=8), name='Asia/Shanghai')


def to_beijing(dt: datetime | None) -> datetime | None:
    """将时间统一转换为北京时间（默认将无时区时间按 UTC 解释）。"""
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(BJ_TZ)


def fmt_dt(dt: datetime | None, fmt: str = '%Y-%m-%d %H:%M') -> str:
    """格式化为北京时间字符串。"""
    bj = to_beijing(dt)
    return bj.strftime(fmt) if bj else ''
