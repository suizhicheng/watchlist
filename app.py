# import os
import sys
import click
from flask import Flask, render_template,request, url_for, redirect, flash
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
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(error):  # 接受异常对象作为参数
    return render_template('404.html'), 404
@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = db.session.execute(select(User)).scalar()
    return dict(user=user)  # 需要返回字典，等同于 return {'user': user}
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
@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        # 获取表单数据
        title = request.form.get('title', '').strip()
        year = request.form.get('year', '').strip()
        # 验证数据
        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input. Title is required, year must be 4 digits.')
            return redirect(url_for('index'))
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created.')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向回主页

    movies = db.session.execute(select(Movie)).scalars().all()  # 读取所有电影记录
    return render_template('index.html', movies=movies)  # 仅传movies即可


# 编辑电影条目路由
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = db.get_or_404(Movie, movie_id)  # 根据ID查电影，不存在则返回404

    if request.method == 'POST':  # 处理编辑表单提交
        title = request.form.get('title', '').strip()
        year = request.form.get('year', '').strip()
        # 验证数据
        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))
        # 更新数据
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    # GET请求：渲染编辑页面（传入当前电影数据）
    return render_template('edit.html', movie=movie)


# 删除电影条目路由（仅接受POST请求）
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
def delete(movie_id):
    movie = db.get_or_404(Movie, movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页


# 运行程序（仅在直接执行app.py时生效）
if __name__ == '__main__':
    app.run(debug=True)  # debug=True 开启调试模式，修改代码后自动重启