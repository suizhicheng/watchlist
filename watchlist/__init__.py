# 程序包构造文件（核心：工厂函数）
from flask import Flask, current_app
from sqlalchemy import select
from watchlist.settings import config
from watchlist.extensions import db, login_manager
from watchlist.blueprints.main import main_bp
from watchlist.blueprints.auth import auth_bp
from watchlist.models import User
from watchlist.errors import register_errors
from watchlist.commands import register_commands


# 工厂函数（动态创建程序实例）
def create_app(config_name='development'):
    # 1. 创建Flask实例
    app = Flask(__name__)
    # 2. 加载配置
    app.config.from_object(config[config_name])

    # 3. 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)

    # 4. 注册蓝本
    app.register_blueprint(main_bp)  # main蓝本无URL前缀
    app.register_blueprint(auth_bp)  # auth蓝本无URL前缀

    # 5. 注册上下文处理器（全局注入user）
    @app.context_processor
    def inject_user():
        with app.app_context():  # 手动创建上下文（工厂函数中需显式声明）
            user = db.session.execute(select(User)).scalar()
        return dict(user=user)

    # 6. 注册错误处理函数
    register_errors(app)

    # 7. 注册自定义命令
    register_commands(app)

    return app