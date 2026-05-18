from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlparse, urljoin

auth_bp = Blueprint("auth", __name__)


# ===== 用户认证 =====
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember", False)

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            if next_page:
                host = request.host_url.rstrip("/")
                next_url = urljoin(host, next_page)
                if (
                    not urlparse(next_url).netloc
                    or urlparse(next_url).netloc == urlparse(host).netloc
                ):
                    next_page = next_url
                else:
                    next_page = None
            flash("登录成功！", "success")
            return redirect(next_page or url_for("main.index"))
        else:
            flash("用户名或密码错误", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not User.validate_username(username):
            flash("用户名格式不正确（3-20 位，允许字母、数字、下划线、中文）", "danger")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("用户名已存在", "danger")
            return render_template("register.html")

        try:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("注册成功，请登录", "success")
            return redirect(url_for("auth.login"))
        except ValueError as e:
            # 密码验证失败
            db.session.rollback()
            flash(f"密码格式错误：{str(e)}", "danger")
            return render_template("register.html")
        except Exception as e:
            db.session.rollback()
            flash(f"注册失败：{str(e)}", "danger")

    return render_template("register.html")
