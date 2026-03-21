import sys
import click
from typing import Optional
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.orm import DeclarativeBase
from pathlib import Path
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash

# 初始化Flask应用
app = Flask(__name__)

# 配置数据库（兼容Windows/Linux）
SQLITE_PREFIX = 'sqlite:///' if sys.platform.startswith('win') else 'sqlite:////'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_PREFIX + str(Path(app.root_path) / 'data.db')

# 配置flash消息/Flask-Login密钥（必须）
app.config['SECRET_KEY'] = 'dev'  # 开发环境临时密钥，部署时替换


# 初始化SQLAlchemy
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)

# 初始化Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # 未登录时重定向到登录页


# 用户加载回调函数（Flask-Login必需）
@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    return user


# 定义数据库模型（User新增用户名/密码散列字段，继承UserMixin）
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    username: Mapped[str] = mapped_column(String(20))  # 新增：登录用户名
    password_hash: Mapped[Optional[str]] = mapped_column(String(128))  # 新增：密码散列

    # 新增：设置密码（生成散列值）
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 新增：验证密码（对比散列值）
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    __tablename__ = 'movie'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(60))
    year: Mapped[str] = mapped_column(String(4))


# 自定义命令：初始化数据库
@app.cli.command('init-db')
@click.option('--drop', is_flag=True, help='Create after drop.')
def init_database(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


# 自定义命令：生成虚拟数据（更新User字段）
@app.cli.command()
def forge():
    """Generate fake data."""
    db.drop_all()
    db.create_all()
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
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    # 新增：设置用户名和密码
    user = User(name=name, username='admin')
    user.set_password('helloflask')  # 默认密码：helloflask
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done.')


# 自定义命令：创建/更新管理员账户（新增核心）
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create/Update admin user."""
    db.create_all()
    # 查询现有用户
    user = db.session.execute(select(User)).scalar()
    if user:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')


# 模板上下文处理器：统一注入user变量
@app.context_processor
def inject_user():
    user = db.session.execute(select(User)).scalar()
    return dict(user=user)


# 404错误处理
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# 登录视图（新增核心）
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        # 查询用户
        user = db.session.execute(select(User).filter_by(username=username)).scalar()
        # 验证密码
        if user and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')


# 登出视图（新增核心）
@app.route('/logout')
@login_required  # 登录保护：未登录无法访问
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))


# 设置页面视图（新增核心）
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name  # 更新当前登录用户的名字
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')


# 主页路由（新增：POST请求需登录验证）
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 未登录用户禁止创建条目
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        title = request.form.get('title', '').strip()
        year = request.form.get('year', '').strip()
        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input. Title is required, year must be 4 digits.')
            return redirect(url_for('index'))

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    movies = db.session.execute(select(Movie)).scalars().all()
    return render_template('index.html', movies=movies)


# 编辑电影条目（新增：登录保护）
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = db.get_or_404(Movie, movie_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        year = request.form.get('year', '').strip()
        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


# 删除电影条目（新增：登录保护）
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


# 运行程序
if __name__ == '__main__':
    app.run(debug=True)