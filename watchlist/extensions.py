# 扩展对象定义（分离创建和初始化，支持工厂函数）
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# 定义SQLAlchemy基类
class Base(DeclarativeBase):
    pass

# 创建扩展对象（不传入app，后续在工厂函数中init_app）
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# 用户加载回调函数（避免循环导入，内部导入User）
@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User
    user = db.session.get(User, int(user_id))
    return user

# 未登录时重定向到登录页（蓝本端点需加前缀）
login_manager.login_view = 'auth.login'