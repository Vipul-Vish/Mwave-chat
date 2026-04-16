from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Message
from werkzeug.security import generate_password_hash, check_password_hash

routes = Blueprint('routes', __name__)

@routes.route("/")
def index():
    return redirect(url_for('routes.login'))

@routes.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_exists = db.session.execute(db.select(User).filter_by(username=username)).scalar()
        if user_exists:
            flash('Username already taken!')
            return redirect(url_for('routes.register'))
        
        new_user = User(username=username, 
                        password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('routes.login'))
    return render_template("register.html")

@routes.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('routes.dashboard'))
        flash('Invalid username or password')
    return render_template("login.html")

@routes.route("/dashboard")
@login_required
def dashboard():
    users = db.session.execute(db.select(User).filter(User.username != current_user.username)).scalars().all()
    return render_template("dashboard.html", users=users)

@routes.route("/chat/<partner_name>")
@login_required
def chat(partner_name):
    partner = db.session.execute(db.select(User).filter_by(username=partner_name)).scalar()
    if not partner:
        return "User not found", 404
    
    room = "_".join(sorted([current_user.username, partner_name]))
    
    
    messages = db.session.execute(
        db.select(Message).filter_by(room=room).order_by(Message.timestamp.asc())
    ).scalars().all()
    
    return render_template("chat.html", partner=partner_name, messages=messages)

@routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))