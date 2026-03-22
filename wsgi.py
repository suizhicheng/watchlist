# wsgi.py
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 导入工厂函数，创建生产环境的 app 实例
from watchlist import create_app
app = create_app(config_name='production')