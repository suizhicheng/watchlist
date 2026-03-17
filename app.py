# import os
import sys
import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
from sqlalchemy.orm import DeclarativeBase
from pathlib import Path
from sqlalchemy import String,select
from sqlalchemy.orm import Mapped, mapped_column
app = Flask(__name__)# 初始化Flask应用
SQLITE_PREFIX = 'sqlite:///' if sys.platform.startswith('win') else 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_PREFIX + str(Path(app.root_path) / 'data.db')
class Base(DeclarativeBase):
  pass



db = SQLAlchemy(app, model_class=Base)  # 初始化扩展，传入程序实例 app

class User(db.Model):
    __tablename__ = 'user' # 定义表名称
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键
    name: Mapped[str] = mapped_column(String(20))  # 名字


class Movie(db.Model):  # 表名将会是 movie
    __tablename__ = 'movie'
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键
    title: Mapped[str] = mapped_column(String(60))  # 电影标题
    year: Mapped[str] = mapped_column(String(4))  # 电影年份

@app.cli.command('init-db')  # 注册为命令，传入自定义命令名
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def init_database(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息
@app.cli.command()
def forge():
    """Generate fake data."""
    db.drop_all()
    db.create_all()

# 虚拟数据：模拟用户名称和电影列表
    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'}
]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')

# 定义主页路由，渲染模板
@app.route('/')
def index():
    user = db.session.execute(select(User)).scalar()  # 读取用户记录
    movies = db.session.execute(select(Movie)).scalars().all()  # 读取所有电影记录
    return render_template('index.html', user=user, movies=movies)
    # 传入模板变量：name和movies，渲染index.html


# 运行程序（仅在直接执行app.py时生效）
if __name__ == '__main__':
    app.run(debug=True)  # debug=True 开启调试模式，修改代码后自动重启