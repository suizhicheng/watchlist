from watchlist import create_app
app = create_app('development')
with app.app_context():
    from watchlist.extensions import db
    from watchlist.models import User
    user = User(username='admin', name='Admin')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    print('Admin user created successfully')