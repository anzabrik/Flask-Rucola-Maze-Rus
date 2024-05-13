from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from .extensions import db, login_manager
from .models import User
from .forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required


bp = Blueprint("auth", __name__, url_prefix="/auth")


@login_manager.unauthorized_handler
def unauthorized():
    return render_template("auth/unauthorized.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        user = User(username=username, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            flash(f"Вы зарегистрированы как {username}")
            login_user(user, remember=form.remember.data)
            return redirect(url_for("inventory.home"))
        except:
            flash(f"Имя пользователя '{username}' занято. Попробуйте другое!")
            db.session.rollback()

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            flash(f"Вы вошли как {user.username}")
            login_user(user, remember=form.remember.data)
            return redirect(url_for("inventory.home"))
        flash("Ошибка в пароле или имени пользователя.")

    return render_template("auth/login.html", form=form)


@bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы")
    return redirect(url_for("auth.login"))
