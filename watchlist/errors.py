# 错误处理函数（封装成注册函数，供工厂函数调用）
from flask import render_template


def register_errors(app):
    # 400错误
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    # 404错误
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    # 500错误
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

