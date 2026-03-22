# D:\projects\watchlist\app.py（项目根目录）
# 只保留这几行！删除所有其他代码（尤其是 db = SQLAlchemy(...) 相关）
from watchlist import create_app

# 调用工厂函数创建app实例（核心：不再直接创建db/扩展）
app = create_app(config_name='development')

if __name__ == '__main__':
    app.run(debug=True)