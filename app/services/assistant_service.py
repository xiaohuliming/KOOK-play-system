"""
AI 助理小呢 — SiliconFlow MiniMax-M2.5 对接服务
"""
import json
import requests
from decimal import Decimal
from datetime import datetime, timedelta
from flask import current_app
from flask_login import current_user

from app.extensions import db
from app.models.user import User
from app.models.order import Order
from app.models.gift import GiftOrder
from app.models.finance import WithdrawRequest

SILICONFLOW_API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
SILICONFLOW_API_KEY = 'sk-obelmguwyjrhsifohvmryzgsknvmkaodwcclznhyqnyecqwi'
SILICONFLOW_MODEL = 'Pro/MiniMaxAI/MiniMax-M2.5'


def _build_system_prompt(user):
    """构建包含平台上下文的系统提示词"""
    role_label = '老板' if user.is_god else ('陪玩' if user.is_player else ('客服' if user.has_role('staff') else ('管理员' if user.is_admin else '用户')))
    return f"""你是"助理小呢"，嗯呢呗电竞陪玩店的智能助理。你性格温柔可爱、专业靠谱。
当前用户: {user.nickname or user.username} (角色: {role_label}, ID: {user.id})

平台介绍:
- 嗯呢呗电竞是一个基于KOOK的游戏陪玩店中控管理系统
- 支持常规陪玩、护航、代练三种订单类型
- 货币体系: 嗯呢币(m_coin, 充值余额) + 赠金(m_coin_gift, 赠送余额) + 小猪粮(m_bean, 陪玩收益) + 冻结小猪粮(m_bean_frozen)
- 老板通过充值嗯呢币下单，陪玩通过接单赚取小猪粮

你可以帮助用户:
1. 查询平台数据（用户信息、订单统计、财务概况等）
2. 解答平台使用问题
3. 提供运营建议

回答规则:
- 用中文简洁回复，善用emoji让回复更生动
- 数据查询时给出准确数字
- 如果问到你无法确定的数据，诚实说明
- 不要编造数据"""


def _get_platform_context(user):
    """获取平台实时数据作为上下文"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    context_parts = []

    try:
        # 基本统计
        total_users = User.query.count()
        total_orders = Order.query.filter(Order.status == 'paid').count()
        today_orders = Order.query.filter(
            Order.status == 'paid',
            Order.created_at >= today_start
        ).count()

        # 待处理事项
        pending_orders = Order.query.filter(Order.status.in_(['pending_report', 'pending_confirm'])).count()
        frozen_orders = Order.query.filter(Order.freeze_status == 'frozen', Order.status == 'paid').count()
        pending_withdraws = WithdrawRequest.query.filter_by(status='pending').count()

        context_parts.append(f"""📊 平台实时数据:
- 总用户数: {total_users}
- 已完成订单: {total_orders}
- 今日订单: {today_orders}
- 待处理订单: {pending_orders}
- 冻结中订单: {frozen_orders}
- 待审提现: {pending_withdraws}""")

        # 若是当前用户的个人数据
        if user.is_god:
            context_parts.append(f"""
💰 当前用户余额:
- 嗯呢币: {user.m_coin}
- 赠金: {user.m_coin_gift}""")
        elif user.is_player:
            context_parts.append(f"""
💰 当前用户余额:
- 小猪粮: {user.m_bean}
- 冻结小猪粮: {user.m_bean_frozen}""")

    except Exception as e:
        current_app.logger.warning(f'[Assistant] 获取平台数据失败: {e}')
        context_parts.append('(平台数据暂时无法获取)')

    return '\n'.join(context_parts)


def chat(user_message, conversation_history=None):
    """
    调用 SiliconFlow API 进行对话
    conversation_history: [{"role": "user/assistant", "content": "..."}]
    返回: (success, reply_text, error_msg)
    """
    user = current_user._get_current_object()

    system_prompt = _build_system_prompt(user)
    platform_context = _get_platform_context(user)

    messages = [
        {'role': 'system', 'content': system_prompt + '\n\n' + platform_context}
    ]

    # 加入对话历史（最多保留最近 10 轮）
    if conversation_history:
        messages.extend(conversation_history[-20:])

    messages.append({'role': 'user', 'content': user_message})

    try:
        resp = requests.post(
            SILICONFLOW_API_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {SILICONFLOW_API_KEY}',
            },
            json={
                'model': SILICONFLOW_MODEL,
                'messages': messages,
                'max_tokens': 2048,
                'temperature': 0.7,
                'top_p': 0.9,
            },
            timeout=60,
        )

        if resp.status_code != 200:
            current_app.logger.error(f'[Assistant] API error {resp.status_code}: {resp.text[:500]}')
            return False, None, f'AI 服务暂时不可用 (HTTP {resp.status_code})'

        data = resp.json()
        reply = data['choices'][0]['message']['content']
        return True, reply.strip(), None

    except requests.Timeout:
        return False, None, '请求超时，请稍后重试 ⏳'
    except Exception as e:
        current_app.logger.error(f'[Assistant] Unexpected error: {e}')
        return False, None, '助理出了点小问题，请稍后再试 😢'
