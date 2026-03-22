# 认证蓝本（登录、登出）
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import select
from watchlist.extensions import db
from watchlist.models import User

# 创建auth蓝本
auth_bp = Blueprint('auth', __name__)


# 登录
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('auth.login'))

        user = db.session.execute(select(User).filter_by(username=username)).scalar()
        if user and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('main.index'))

        flash('Invalid username or password.')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


# 登出
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('main.index'))