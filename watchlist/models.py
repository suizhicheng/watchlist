# 模型类（User、Movie）
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from watchlist.extensions import db


# 用户模型（继承UserMixin）
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    username: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[Optional[str]] = mapped_column(String(128))

    # 设置密码（生成散列值）
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


# 电影模型
class Movie(db.Model):
    __tablename__ = 'movie'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(60))
    year: Mapped[str] = mapped_column(String(4))