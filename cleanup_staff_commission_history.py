from decimal import Decimal, ROUND_HALF_UP
import argparse

from sqlalchemy import func

from app import create_app, db
from app.models.finance import CommissionLog
from app.models.user import User

STAFF_TYPES = ('staff_commission', 'staff_refund_deduct')
ADJUST_REASON = '系统清理历史客服分红入账（仅保留绩效统计，不计入可提现余额）'


def _q(value):
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def run_cleanup(apply=False, delete_logs=True, allow_negative=False, user_id=None):
    app = create_app(start_background_tasks=False)

    with app.app_context():
        query = db.session.query(
            CommissionLog.user_id.label('user_id'),
            func.coalesce(func.sum(CommissionLog.amount), 0).label('net_amount'),
            func.count(CommissionLog.id).label('log_count'),
        ).filter(
            CommissionLog.change_type.in_(STAFF_TYPES)
        )

        if user_id:
            query = query.filter(CommissionLog.user_id == user_id)

        rows = query.group_by(CommissionLog.user_id).all()

        if not rows:
            print('未发现历史客服分红流水，无需处理。')
            return

        print(f'命中用户数: {len(rows)}')
        print(f'执行模式: {"APPLY(写入)" if apply else "PREVIEW(预览)"}')
        print(f'删除历史客服分红流水: {"是" if delete_logs else "否"}')
        print(f'允许余额为负以完全抵消: {"是" if allow_negative else "否"}')
        print('-' * 80)

        total_net = Decimal('0.00')
        total_delta = Decimal('0.00')
        unresolved_total = Decimal('0.00')
        deleted_total = 0
        adjusted_users = 0

        for row in rows:
            user = db.session.get(User, row.user_id)
            if not user:
                continue

            net = _q(row.net_amount)
            bean_before = _q(user.m_bean)
            bean_after = bean_before - net
            unresolved = Decimal('0.00')

            if not allow_negative and bean_after < 0:
                unresolved = -bean_after
                bean_after = Decimal('0.00')

            delta = bean_after - bean_before
            total_net += net
            total_delta += delta
            unresolved_total += unresolved

            print(
                f'user_id={user.id:<6} 用户={user.username:<16} '
                f'历史净分红={net:>8} 当前小猪粮={bean_before:>8} '
                f'调整后={bean_after:>8} 调整额={delta:>8} 未抵消={_q(unresolved):>8} '
                f'日志数={int(row.log_count)}'
            )

            if not apply:
                continue

            if delta != 0:
                user.m_bean = bean_after
                db.session.add(CommissionLog(
                    user_id=user.id,
                    change_type='admin_adjust',
                    amount=delta,
                    balance_after=bean_after,
                    reason=ADJUST_REASON,
                ))
                adjusted_users += 1

            if delete_logs:
                deleted = CommissionLog.query.filter(
                    CommissionLog.user_id == user.id,
                    CommissionLog.change_type.in_(STAFF_TYPES),
                ).delete(synchronize_session=False)
                deleted_total += int(deleted or 0)

        print('-' * 80)
        print(f'历史净分红合计: {_q(total_net)}')
        print(f'余额调整合计: {_q(total_delta)}')
        print(f'未抵消合计: {_q(unresolved_total)}')

        if not apply:
            print('预览完成，未写入数据库。')
            return

        try:
            db.session.commit()
            print(f'写入完成：已调整用户 {adjusted_users} 个，已删除历史分红流水 {deleted_total} 条。')
            if unresolved_total > 0:
                print('注意：存在余额不足导致未完全抵消的金额，请手动核对。')
        except Exception as exc:
            db.session.rollback()
            print(f'写入失败，已回滚: {exc}')
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='清理历史客服分红：仅保留绩效统计，不计入余额。')
    parser.add_argument('--apply', action='store_true', help='执行写入（默认仅预览）')
    parser.add_argument('--keep-logs', action='store_true', help='保留 staff_commission/staff_refund_deduct 历史流水')
    parser.add_argument('--allow-negative', action='store_true', help='允许 m_bean 为负以完全抵消历史分红')
    parser.add_argument('--user-id', type=int, default=0, help='只处理指定 user_id')
    args = parser.parse_args()

    run_cleanup(
        apply=args.apply,
        delete_logs=not args.keep_logs,
        allow_negative=args.allow_negative,
        user_id=(args.user_id or None),
    )
