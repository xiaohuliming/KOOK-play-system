"""
退款未到账修复脚本

扫描所有退款日志，找出「退款记录显示有金额但实际退回 0」的情况，
自动补回漏退的余额。

用法:
    # 仅审计（不修改数据）
    python fix_refund.py

    # 确认后执行修复
    python fix_refund.py --fix
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.finance import BalanceLog

app = create_app()


def audit_and_fix(do_fix=False):
    with app.app_context():
        # 查找所有退款日志：change_type='refund', reason 包含 '(币:0.00, 赠:0.00)' 但 amount > 0
        bad_refunds = BalanceLog.query.filter(
            BalanceLog.change_type == 'refund',
            BalanceLog.amount > 0,
            BalanceLog.reason.like('%币:0.00, 赠:0.00%'),
        ).order_by(BalanceLog.created_at.asc()).all()

        if not bad_refunds:
            print('✅ 没有找到漏退的退款记录，一切正常！')
            return

        print(f'⚠️  找到 {len(bad_refunds)} 笔退款未实际到账的记录:\n')
        print(f'{"ID":<8} {"用户ID":<8} {"金额":>10} {"原因":<50} {"时间"}')
        print('-' * 110)

        total_missing = Decimal('0')
        user_missing = {}  # user_id -> total_missing

        for log in bad_refunds:
            amt = Decimal(str(log.amount))
            total_missing += amt
            user_missing[log.user_id] = user_missing.get(log.user_id, Decimal('0')) + amt
            print(f'{log.id:<8} {log.user_id:<8} {str(amt):>10} {log.reason:<50} {log.created_at}')

        print(f'\n{"="*110}')
        print(f'共计 {len(bad_refunds)} 笔，总漏退金额: {total_missing} 嗯呢币')
        print(f'涉及 {len(user_missing)} 个用户:\n')

        for uid, missing in sorted(user_missing.items()):
            user = User.query.get(uid)
            name = (user.nickname or user.username) if user else f'用户#{uid}'
            current_balance = (user.m_coin + user.m_coin_gift) if user else '?'
            print(f'  用户 {uid} ({name}): 漏退 {missing} 嗯呢币, 当前余额: {current_balance}')

        if not do_fix:
            print(f'\n👆 以上为审计结果，如需修复请运行:  python fix_refund.py --fix')
            return

        # 执行修复
        print(f'\n🔧 开始修复...\n')
        fixed_count = 0

        for uid, missing in sorted(user_missing.items()):
            user = User.query.get(uid)
            if not user:
                print(f'  ❌ 用户 {uid} 不存在，跳过')
                continue

            old_balance = user.m_coin + user.m_coin_gift
            user.m_coin += missing

            # 写一条补偿日志
            fix_log = BalanceLog(
                user_id=uid,
                change_type='refund',
                amount=missing,
                balance_after=user.m_coin + user.m_coin_gift,
                reason=f'系统修复: 补回历史退款未到账金额 {missing} 嗯呢币',
            )
            db.session.add(fix_log)
            fixed_count += 1
            print(f'  ✅ 用户 {uid} ({user.nickname or user.username}): '
                  f'+{missing} 嗯呢币, 余额 {old_balance} → {user.m_coin + user.m_coin_gift}')

        db.session.commit()
        print(f'\n🎉 修复完成！共修复 {fixed_count} 个用户，补回 {total_missing} 嗯呢币')


if __name__ == '__main__':
    do_fix = '--fix' in sys.argv
    if do_fix:
        print('⚡ 修复模式：将实际修改数据库\n')
    else:
        print('📊 审计模式：仅扫描不修改数据\n')
    audit_and_fix(do_fix=do_fix)
