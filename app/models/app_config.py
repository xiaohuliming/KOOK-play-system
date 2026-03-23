from datetime import datetime
from app.extensions import db


class AppConfig(db.Model):
    """通用键值配置表"""
    __tablename__ = 'app_configs'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True, index=True)
    value = db.Column(db.Text, default='')
    description = db.Column(db.String(200), default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get(key, default=''):
        """获取配置值"""
        cfg = AppConfig.query.filter_by(key=key).first()
        return cfg.value if cfg else default

    @staticmethod
    def set(key, value, description=''):
        """设置配置值"""
        cfg = AppConfig.query.filter_by(key=key).first()
        if cfg:
            cfg.value = value
            if description:
                cfg.description = description
        else:
            cfg = AppConfig(key=key, value=value, description=description)
            db.session.add(cfg)
        return cfg

    def __repr__(self):
        return f'<AppConfig {self.key}={self.value}>'
