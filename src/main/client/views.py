from flask import Blueprint, render_template

# Session-based redirects live in the JS now: the client has no access to the API session.
web_bp = Blueprint("web", __name__)
AUTH_TEMPLATE = "auth.html"


@web_bp.get("/")
def landing():
    return render_template("landing.html")


@web_bp.get("/ingresar")
def login_view():
    return render_template(AUTH_TEMPLATE, mode="login")


@web_bp.get("/registro")
def register_view():
    return render_template(AUTH_TEMPLATE, mode="register")


@web_bp.get("/activar")
def activate_view():
    return render_template(AUTH_TEMPLATE, mode="activate")


@web_bp.get("/recuperar")
def recover_view():
    return render_template(AUTH_TEMPLATE, mode="recover")


@web_bp.get("/restablecer")
def reset_view():
    return render_template(AUTH_TEMPLATE, mode="reset")


@web_bp.get("/verificar-certificado")
def verify_certificate_view():
    return render_template("verify_certificate.html")


@web_bp.get("/app")
def app_view():
    return render_template("app.html")
