from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required
from models.auth_model import User
from extensions import db
from forms import LoginForm, RegisterForm
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login berhasil!", "success")
            
            # Redirect based on user role
            if user.role == 'admin':
                return redirect(url_for("route.dashboard"))
            elif user.role == 'user':
                return redirect(url_for("route.index"))
        else:
            flash("Login Gagal. Periksa email dan password.", "error")
    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    
    # Always return a response, even if form validation fails
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Check if username already exists
                if User.query.filter_by(username=form.username.data).first():
                    flash("Username sudah digunakan. Silakan pilih username lain.", "error")
                    return render_template("register.html", form=form)
                
                # Check if email already exists
                if User.query.filter_by(email=form.email.data).first():
                    flash("Email sudah terdaftar. Silakan gunakan email lain.", "error")
                    return render_template("register.html", form=form)
                
                # Create new user
                user = User(
                    username=form.username.data,
                    fullname=form.fullname.data,
                    email=form.email.data,
                    role='user'  # Set default role
                )
                user.set_password(form.password.data)
                
                db.session.add(user)
                db.session.commit()
                
                flash("Akun Anda telah dibuat! Anda sekarang dapat login.", "success")
                return redirect(url_for("auth.login"))
                
            except IntegrityError:
                db.session.rollback()
                flash("Terjadi kesalahan saat membuat akun. Silakan coba lagi.", "error")
                return render_template("register.html", form=form)
            
            except Exception as e:
                db.session.rollback()
                flash("Terjadi kesalahan sistem. Silakan coba lagi nanti.", "error")
                return render_template("register.html", form=form)
        
        # If form validation fails
        return render_template("register.html", form=form)
    
    # GET request
    return render_template("register.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah keluar dari sistem.", "info")
    return redirect(url_for("route.index"))