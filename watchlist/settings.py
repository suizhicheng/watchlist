import os
import sys
from pathlib import Path

# 项目根目录（程序包的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent
# SQLite前缀（兼容Windows/Linux）
SQLITE_PREFIX = 'sqlite:///' if sys.platform.startswith('win') else 'sqlite:////'

# 配置基类
# watchlist/settings.py
import os
from pathlib import Path

# 基础配置（生产环境覆盖 SECRET_KEY）
class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')  # 生产环境从环境变量读取
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{Path(__file__).parent.parent / "data.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# 生产环境配置
class ProductionConfig(BaseConfig):
    pass  # 复用基础配置，仅通过环境变量覆盖 SECRET_KEY
# 开发环境配置
class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = SQLITE_PREFIX + str(BASE_DIR / 'data-dev.db')





# 测试环境配置（内存数据库）
class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置映射（方便工厂函数调用）
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}