from flask import Flask, render_template

# 初始化Flask应用
app = Flask(__name__)

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
    {'title': 'The Pork of Music', 'year': '2012'},
]

# 定义主页路由，渲染模板
@app.route('/')
def index():
    # 传入模板变量：name和movies，渲染index.html
    return render_template('index.html', name=name, movies=movies)

# 运行程序（仅在直接执行app.py时生效）
if __name__ == '__main__':
    app.run(debug=True)  # debug=True 开启调试模式，修改代码后自动重启