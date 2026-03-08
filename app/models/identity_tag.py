from datetime import datetime

from app.extensions import db


class IdentityTag(db.Model):
    __tablename__ = 'identity_tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    description = db.Column(db.String(255))

    # 经验规则：达到阈值前按倍率加经验，达到后恢复正常(1x)
    exp_multiplier = db.Column(db.Numeric(5, 2), nullable=False, default=1.00)
    exp_bonus_until = db.Column(db.Integer)  # None/0 表示无阈值加成

    status = db.Column(db.Boolean, nullable=False, default=True, index=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<IdentityTag {self.name}>'
