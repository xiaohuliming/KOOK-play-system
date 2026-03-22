"""
VIP 等级管理 — 管理员页面
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required

from app.extensions import db
from app.models.vip import VipLevel
from app.utils.permissions import staff_required

vip_admin_bp = Blueprint('vip_admin', __name__, template_folder='../templates')


def _get_kook_roles():
    """安全获取 KOOK 标签列表"""
    try:
        from app.services.kook_service import fetch_kook_role_catalog
        result, err = fetch_kook_role_catalog()
        if err or not result:
            return []
        return result.get('roles', [])
    except Exception:
        return []


@vip_admin_bp.route('/')
@login_required
@staff_required
def index():
    levels = VipLevel.query.order_by(VipLevel.sort_order).all()
    return render_template('admin/vip_levels.html', levels=levels)


@vip_admin_bp.route('/<int:level_id>/edit', methods=['GET', 'POST'])
@login_required
@staff_required
def edit(level_id):
    level = VipLevel.query.get_or_404(level_id)

    if request.method == 'POST':
        level.name = request.form.get('name', '').strip() or level.name
        level.min_experience = request.form.get('min_experience', type=int) or 0
        level.discount = request.form.get('discount', type=float) or 100.0
        level.sort_order = request.form.get('sort_order', type=int) or 0
        level.benefits = request.form.get('benefits', '').strip() or None
        level.kook_role_id = request.form.get('kook_role_id', '').strip() or None

        try:
            db.session.commit()
            flash(f'VIP等级 {level.name} 已更新', 'success')
        except Exception:
            db.session.rollback()
            flash('更新失败', 'error')
        return redirect(url_for('vip_admin.index'))

    kook_roles = _get_kook_roles()
    return render_template('admin/vip_form.html', level=level, kook_roles=kook_roles)


@vip_admin_bp.route('/add', methods=['GET', 'POST'])
@login_required
@staff_required
def add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('等级名称不能为空', 'error')
            return redirect(url_for('vip_admin.add'))

        level = VipLevel(
            name=name,
            min_experience=request.form.get('min_experience', type=int) or 0,
            discount=request.form.get('discount', type=float) or 100.0,
            sort_order=request.form.get('sort_order', type=int) or 0,
            benefits=request.form.get('benefits', '').strip() or None,
            kook_role_id=request.form.get('kook_role_id', '').strip() or None,
        )
        db.session.add(level)
        try:
            db.session.commit()
            flash(f'VIP等级 {name} 已创建', 'success')
        except Exception:
            db.session.rollback()
            flash('创建失败（名称可能重复）', 'error')
        return redirect(url_for('vip_admin.index'))

    kook_roles = _get_kook_roles()
    return render_template('admin/vip_form.html', level=None, kook_roles=kook_roles)


@vip_admin_bp.route('/<int:level_id>/delete', methods=['POST'])
@login_required
@staff_required
def delete(level_id):
    level = VipLevel.query.get_or_404(level_id)
    name = level.name
    db.session.delete(level)
    try:
        db.session.commit()
        flash(f'VIP等级 {name} 已删除', 'success')
    except Exception:
        db.session.rollback()
        flash('删除失败', 'error')
    return redirect(url_for('vip_admin.index'))
