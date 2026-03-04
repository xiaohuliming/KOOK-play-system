from datetime import datetime, timedelta
from decimal import Decimal

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func, desc, case
from sqlalchemy.orm import aliased

from app.extensions import db
from app.models.order import Order
from app.models.gift import GiftOrder
from app.models.user import User
from app.models.finance import CommissionLog

rankings_bp = Blueprint('rankings', __name__, template_folder='../templates')


def _parse_date_range(period):
    """根据时间筛选返回 (start_date, end_date)"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if period == 'today':
        return today, today + timedelta(days=1)
    elif period == 'yesterday':
        return today - timedelta(days=1), today
    elif period == 'this_week':
        start = today - timedelta(days=today.weekday())
        return start, today + timedelta(days=1)
    elif period == 'last_week':
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=7)
        return start, end
    elif period == 'this_month':
        start = today.replace(day=1)
        return start, today + timedelta(days=1)
    elif period == 'last_month':
        first_of_month = today.replace(day=1)
        end = first_of_month
        start = (first_of_month - timedelta(days=1)).replace(day=1)
        return start, end
    elif period == 'this_quarter':
        q = (today.month - 1) // 3
        start = today.replace(month=q * 3 + 1, day=1)
        return start, today + timedelta(days=1)
    elif period == 'this_year':
        start = today.replace(month=1, day=1)
        return start, today + timedelta(days=1)
    elif period == 'last_7':
        return today - timedelta(days=7), today + timedelta(days=1)
    elif period == 'last_30':
        return today - timedelta(days=30), today + timedelta(days=1)
    else:
        # 默认本月
        start = today.replace(day=1)
        return start, today + timedelta(days=1)


@rankings_bp.route('/')
@login_required
def index():
    period = request.args.get('period', 'this_month')
    tab = request.args.get('tab', 'player')
    start_date, end_date = _parse_date_range(period)

    player_ranking = []
    boss_ranking = []
    intimacy_ranking = []

    if tab == 'player':
        # 陪玩收益排行：按佣金日志累计统计（提现不计入排行，不会把排行清零）
        income_sub = db.session.query(
            CommissionLog.user_id.label('player_id'),
            func.sum(
                case(
                    (CommissionLog.change_type == 'order_income', CommissionLog.amount),
                    else_=0
                )
            ).label('order_earning'),
            func.sum(
                case(
                    (CommissionLog.change_type == 'gift_income', CommissionLog.amount),
                    else_=0
                )
            ).label('gift_earning'),
            func.sum(CommissionLog.amount).label('total_income')
        ).filter(
            CommissionLog.change_type.in_(['order_income', 'gift_income', 'refund_deduct']),
            CommissionLog.created_at >= start_date,
            CommissionLog.created_at < end_date
        ).group_by(CommissionLog.user_id).subquery()

        results = db.session.query(
            User,
            func.coalesce(income_sub.c.order_earning, 0).label('order_earning'),
            func.coalesce(income_sub.c.gift_earning, 0).label('gift_earning'),
            func.coalesce(income_sub.c.total_income, 0).label('total_income'),
        ).join(
            income_sub, User.id == income_sub.c.player_id
        ).filter(
            User.role_filter_expr('player')
        ).all()

        for user, oe, ge, total_income in results:
            total = Decimal(str(total_income or 0))
            player_ranking.append({
                'user': user,
                'order_earning': Decimal(str(oe or 0)),
                'gift_earning': Decimal(str(ge or 0)),
                'total': total,
            })
        player_ranking.sort(key=lambda x: x['total'], reverse=True)

    elif tab == 'boss':
        # 老板消费排行: 按消费嗯呢币排序 (订单+礼物)
        order_spend = db.session.query(
            Order.boss_id,
            func.sum(Order.total_price).label('order_spend')
        ).filter(
            Order.status.in_(['paid', 'pending_pay']),
            Order.created_at >= start_date,
            Order.created_at < end_date
        ).group_by(Order.boss_id).subquery()

        gift_spend = db.session.query(
            GiftOrder.boss_id,
            func.sum(GiftOrder.total_price).label('gift_spend')
        ).filter(
            GiftOrder.status == 'paid',
            GiftOrder.created_at >= start_date,
            GiftOrder.created_at < end_date
        ).group_by(GiftOrder.boss_id).subquery()

        results = db.session.query(
            User,
            func.coalesce(order_spend.c.order_spend, 0).label('order_spend'),
            func.coalesce(gift_spend.c.gift_spend, 0).label('gift_spend'),
        ).outerjoin(
            order_spend, User.id == order_spend.c.boss_id
        ).outerjoin(
            gift_spend, User.id == gift_spend.c.boss_id
        ).filter(
            User.role == 'god',
            db.or_(order_spend.c.order_spend != None, gift_spend.c.gift_spend != None)
        ).all()

        for user, os_val, gs_val in results:
            total = Decimal(str(os_val or 0)) + Decimal(str(gs_val or 0))
            boss_ranking.append({
                'user': user,
                'order_spend': Decimal(str(os_val or 0)),
                'gift_spend': Decimal(str(gs_val or 0)),
                'total': total,
            })
        boss_ranking.sort(key=lambda x: x['total'], reverse=True)

    elif tab == 'intimacy':
        # 亲密度排行：仅按礼物统计（不计订单）
        gift_intimacy = db.session.query(
            GiftOrder.boss_id.label('boss_id'),
            GiftOrder.player_id.label('player_id'),
            func.sum(GiftOrder.total_price).label('value'),
        ).filter(
            GiftOrder.status == 'paid'
        ).group_by(
            GiftOrder.boss_id,
            GiftOrder.player_id
        ).subquery()

        BossUser = aliased(User)
        PlayerUser = aliased(User)

        rows = db.session.query(
            BossUser,
            PlayerUser,
            gift_intimacy.c.value,
        ).select_from(
            gift_intimacy
        ).join(
            BossUser, gift_intimacy.c.boss_id == BossUser.id
        ).join(
            PlayerUser, gift_intimacy.c.player_id == PlayerUser.id
        ).filter(
            gift_intimacy.c.value > 0
        ).order_by(
            desc(gift_intimacy.c.value)
        ).limit(100).all()

        intimacy_ranking = [
            {
                'boss': boss,
                'player': player,
                'value': Decimal(str(value or 0)),
            }
            for boss, player, value in rows
        ]

    return render_template('rankings/index.html',
                           tab=tab,
                           period=period,
                           player_ranking=player_ranking,
                           boss_ranking=boss_ranking,
                           intimacy_ranking=intimacy_ranking)
