from datetime import datetime
from decimal import Decimal

from app.extensions import db
from sqlalchemy import func
from app.models.gift import GiftOrder
from app.models.intimacy import Intimacy
from app.services.log_service import log_operation


def update_intimacy(boss_id, player_id, amount):
    """
    增加/减少亲密度（仅礼物口径，1嗯呢币 = 1亲密度）
    """
    amount = Decimal(str(amount))
    record = Intimacy.query.filter_by(boss_id=boss_id, player_id=player_id).first()
    if record:
        record.value += amount
        if record.value < 0:
            record.value = Decimal('0')
    else:
        if amount > 0:
            record = Intimacy(boss_id=boss_id, player_id=player_id, value=amount)
            db.session.add(record)
    return record


def rebuild_intimacy_from_gifts(operator_id=None):
    """
    按礼物订单重建亲密度：
    - 仅统计 status='paid' 的礼物订单
    - 全量覆盖 intimacy 表（用于修复历史脏数据）
    """
    Intimacy.query.delete(synchronize_session=False)

    rows = db.session.query(
        GiftOrder.boss_id,
        GiftOrder.player_id,
        func.sum(GiftOrder.total_price).label('value'),
    ).filter(
        GiftOrder.status == 'paid'
    ).group_by(
        GiftOrder.boss_id,
        GiftOrder.player_id
    ).all()

    created = 0
    for boss_id, player_id, value in rows:
        amount = Decimal(str(value or 0))
        if amount <= 0:
            continue
        db.session.add(Intimacy(
            boss_id=boss_id,
            player_id=player_id,
            value=amount,
        ))
        created += 1

    if operator_id:
        log_operation(
            operator_id=operator_id,
            action_type='intimacy_rebuild',
            target_type='intimacy',
            target_id=0,
            detail=f'按礼物订单重建亲密度，共 {created} 条',
        )
    return created


def clear_intimacy(before_date, operator_id=None):
    """
    清空指定日期之前的亲密度数据 (管理员操作)
    """
    count = Intimacy.query.filter(Intimacy.updated_at < before_date).delete()
    if operator_id:
        log_operation(
            operator_id=operator_id,
            action_type='intimacy_clear',
            target_type='intimacy',
            target_id=0,
            detail=f'清空 {before_date.strftime("%Y-%m-%d")} 之前的亲密度, 共 {count} 条'
        )
    return count
