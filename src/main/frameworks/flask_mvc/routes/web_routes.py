from flask import Blueprint, redirect, render_template, session, url_for


web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def landing():
    return render_template("landing.html")


@web_bp.get("/ingresar")
def login_view():
    if session.get("usuario_id") is not None:
        return redirect(url_for("web.app_view"))
    return render_template("auth.html", mode="login")


@web_bp.get("/registro")
def register_view():
    if session.get("usuario_id") is not None:
        return redirect(url_for("web.app_view"))
    return render_template("auth.html", mode="register")


@web_bp.get("/activar")
def activate_view():
    return render_template("auth.html", mode="activate")


@web_bp.get("/recuperar")
def recover_view():
    return render_template("auth.html", mode="recover")


@web_bp.get("/restablecer")
def reset_view():
    return render_template("auth.html", mode="reset")


@web_bp.get("/verificar-certificado")
def verify_certificate_view():
    return render_template("verify_certificate.html")


@web_bp.get("/app")
def app_view():
    if session.get("usuario_id") is None:
        return redirect(url_for("web.login_view"))
    return render_template("app.html")
