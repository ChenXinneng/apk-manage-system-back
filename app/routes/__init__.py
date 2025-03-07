from app.routes.auth import auth_bp
from app.routes.apk_main_routes import apk_main_bp
from app.routes.upload_routes import upload_bp


def init_app(app):
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(apk_main_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')

# 你可以在这里添加其他的路由注册操作
