from watchlist import create_app
app = create_app('development')
with app.app_context():
    from watchlist.extensions import db
    db.create_all()
    print('Database tables created successfully')