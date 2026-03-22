import unittest
from watchlist import create_app
from watchlist.extensions import db
from watchlist.models import Movie, User

class WatchlistTestCase(unittest.TestCase):
    # 测试固件：每个测试方法执行前初始化
    def setUp(self):
        # 1. 创建测试环境的程序实例（使用内存数据库，不影响开发库）
        self.app = create_app(config_name='testing')
        # 2. 激活程序上下文（Flask 操作必须有上下文）
        self.context = self.app.app_context()
        self.context.push()
        # 3. 创建数据库表 + 测试数据
        db.create_all()
        # 测试用户（用户名：test，密码：123）
        user = User(name='Test', username='test')
        user.set_password('123')
        # 测试电影
        movie = Movie(title='Test Movie Title', year='2019')
        db.session.add_all([user, movie])
        db.session.commit()
        # 4. 创建测试客户端（模拟浏览器）和命令运行器（模拟终端命令）
        self.client = self.app.test_client()
        self.runner = self.app.test_cli_runner()

    # 测试固件：每个测试方法执行后清理
    def tearDown(self):
        db.session.remove()  # 清除数据库会话
        db.drop_all()        # 删除所有表
        self.context.pop()   # 清除上下文

    # -------------------------- 基础测试 --------------------------
    def test_app_exist(self):
        """测试程序实例是否存在"""
        self.assertIsNotNone(self.app)  # 修复：用self.app而非全局app

    def test_app_is_testing(self):
        """测试程序是否处于测试模式"""
        self.assertTrue(self.app.config['TESTING'])

    # -------------------------- 页面测试 --------------------------
    def test_404_page(self):
        """测试404页面"""
        response = self.client.get('/nothing')  # 访问不存在的URL
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    def test_index_page(self):
        """测试主页"""
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)

    # -------------------------- 辅助方法：登录 --------------------------
    def login(self):
        """辅助方法：模拟登录"""
        return self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

    # -------------------------- 电影操作测试 --------------------------
    def test_create_item(self):
        """测试创建电影条目"""
        self.login()
        # 正常创建
        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)
        self.assertIn('New Movie', data)
        # 标题为空
        response = self.client.post('/', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)
        # 年份为空
        response = self.client.post('/', data=dict(
            title='New Movie',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

    def test_update_item(self):
        """测试更新电影条目"""
        self.login()
        # 访问编辑页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit Item', data)
        self.assertIn('Test Movie Title', data)
        # 正常更新
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.', data)
        self.assertIn('New Movie Edited', data)
        # 标题为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertIn('Invalid input.', data)

    def test_delete_item(self):
        """测试删除电影条目"""
        self.login()
        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie Title', data)

    # -------------------------- 认证功能测试 --------------------------
    def test_login_protect(self):
        """测试登录保护（未登录看不到编辑/删除）"""
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Delete', data)

    def test_login(self):
        """测试登录功能"""
        # 正确账号密码
        response = self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertIn('Logout', data)
        # 错误密码
        response = self.client.post('/login', data=dict(
            username='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid username or password.', data)
        # 空用户名
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input.', data)

    def test_logout(self):
        """测试登出功能"""
        self.login()
        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye.', data)
        self.assertNotIn('Logout', data)

    def test_settings(self):
        """测试设置功能"""
        self.login()
        # 访问设置页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        # 正常更新名称
        response = self.client.post('/settings', data=dict(
            name='Grey Li',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated.', data)
        self.assertIn('Grey Li', data)
        # 名称为空
        response = self.client.post('/settings', data=dict(
            name='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input.', data)

    # -------------------------- 自定义命令测试 --------------------------
    def test_forge_command(self):
        """测试forge命令（生成测试数据）"""
        result = self.runner.invoke(args=['forge'])
        self.assertIn('Done.', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    def test_initdb_command(self):
        """测试init-db命令（初始化数据库）"""
        result = self.runner.invoke(args=['init-db'])
        self.assertIn('Initialized database.', result.output)

    def test_admin_command(self):
        """测试admin命令（创建管理员）"""
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username', 'grey', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'grey')

    def test_admin_command_update(self):
        """测试admin命令（更新管理员）"""
        result = self.runner.invoke(args=['admin', '--username', 'peter', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertEqual(User.query.first().username, 'peter')

# 执行所有测试
if __name__ == '__main__':
    unittest.main()