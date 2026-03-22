import os
import sys
from pathlib import Path

# 项目根目录（程序包的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent
# SQLite前缀（兼容Windows/Linux）
SQLITE_PREFIX = 'sqlite:///' if sys.platform.startswith('win') else 'sqlite:////'

# 配置基类
class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')  # 优先从环境变量读取
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭不必要的警告

# 开发环境配置
class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = SQLITE_PREFIX + str(BASE_DIR / 'data-dev.db')

# 测试环境配置（内存数据库）
class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 生产环境配置
class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', SQLITE_PREFIX + str(BASE_DIR / 'data.db'))

# 配置映射（方便工厂函数调用）
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}