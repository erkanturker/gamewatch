import os
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql:///game_watch_db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'XXXYYYZZZ')
CURR_USER_KEY = "curr_user"