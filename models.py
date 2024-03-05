from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timezone
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User in the database"""

    __tablename__ = "users"

    id= db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(50),nullable=False)
    last_name = db.Column(db.String(50),nullable=False)
    username = db.Column(db.Text,nullable=False,unique=True)
    email = db.Column(db.Text,nullable=False,unique=True)
    password = db.Column(db.Text,nullable=False)
    profile_image_url = db.Column(db.Text,default="/static/images/default-pic.png")
    header_image_url = db.Column(db.Text,default="/static/images/default-pic.png")

    wishlists = db.relationship("WishList", backref="user",cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user",cascade="all, delete-orphan")

    @classmethod
    def sign_up(cls, first_name,last_name,username,email,password,profile_image_url,header_image_url):

        hash_password = bcrypt.generate_password_hash(password).decode("UTF-8'")

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hash_password,
            profile_image_url=profile_image_url,
            header_image_url=header_image_url
        )

        db.session.add(user)

        return user
    
    @classmethod 
    def authenticate(cls,username,password):

        user = cls.query.filter(username==username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password,password)
            if is_auth:
                return True
            else:False
        else:False

class WishList(db.Model):
    "Whislist in db"

    __tablename__ = "wishlists"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"),primary_key=True)
    game_id = db.Column(db.Integer,primary_key=True)
    game_title = db.Column(db.Text)
    game_thumb = db.Column(db.Text)
    store_id = db.Column(db.Integer,nullable=False)
    price= db.Column(db.Numeric(10,2))
    sales_price= db.Column(db.Numeric(10,2))
    savings= db.Column(db.Numeric(10,6))
    deal_id = db.Column(db.Text)
    meta_critic_score = db.Column(db.Text)
    meta_critic_link = db.Column(db.Text)
    steam_app_id = db.Column(db.Text)
    steam_rating_count = db.Column(db.Text)
    steam_rating_percent =db.Column(db.Text)
    steam_rating_text =db.Column(db.Text)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id= db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"),primary_key=True)
    game_id = db.Column(db.Integer,primary_key=True)
    store_id = db.Column(db.Integer,primary_key=True)
    price= db.Column(db.Numeric(10,2),primary_key=True)
    content = db.Column(db.Text)
    is_read = db.Column(db.Boolean,default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    read_at= db.Column(db.DateTime)