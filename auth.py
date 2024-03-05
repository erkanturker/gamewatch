from flask import Blueprint, render_template, redirect, flash, session, g
from models import db, User
from forms import UserAddForm, UserLoginForm
from sqlalchemy.exc import IntegrityError
from config import CURR_USER_KEY

auth_bp = Blueprint('auth', __name__)


def is_user_auth():
    if  g.user:
        return True
    else:return False

def add_user_to_global():
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:g.user=None

def do_login(user):
    session[CURR_USER_KEY] = user.id

def do_logout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@auth_bp.route("/register",methods=['GET','POST'])
def signup_user():

    if g.user:
        return redirect("/")

    form = UserAddForm()
    if form.validate_on_submit():
        try:
             user = User.sign_up(
                 first_name = form.first_name.data,
                 last_name = form.last_name.data,
                 username=form.username.data,
                 password=form.password.data,
                 email=form.email.data,
                 profile_image_url=form.profile_image_url.data or User.profile_image_url.default.arg,
                 header_image_url=form.header_image_url.data or User.header_image_url.default.arg,
                 )
             db.session.commit()
             do_login(user)
             return redirect("/")
        
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form, )

    return render_template("signup.html",form=form,current_page='/register')

@auth_bp.route("/login",methods=['GET','POST'])
def login():
    if g.user:
        return redirect("/")
    
    form = UserLoginForm()
    if form.validate_on_submit():
        is_auth = User.authenticate(username=form.username.data,password=form.password.data)
        if is_auth:
            user = User.query.filter(User.username==form.username.data).first()
            flash(f"Welcome {user.first_name} {user.last_name}","success")
            do_login(user)
            return redirect("/")
        else:
            flash("Invalid Username/Password","danger")
            redirect("/login")

    return render_template('login.html',form=form, current_page='/login')

@auth_bp.route("/logout")
def logout():
    if not g.user:
        return redirect("/")
    do_logout()
    flash("User logged out successfully.","success")
    return redirect("/")
