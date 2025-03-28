from flask import Flask,session, request,jsonify,send_file
from .extensions import db
from flask_jwt_extended import JWTManager
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from app.config import Config
from flask_cors import CORS
import os
# 初始化Flask应用和配置
app = Flask(__name__)

app.config.from_object(Config)


# 允许跨域，并允许携带 Cookie
CORS(app, supports_credentials=True)

# 初始化数据库和JWT
db.init_app(app)
jwt = JWTManager(app)

# 初始化路由和模型
from app.routes import init_app as init_routes
from app.models import *

# 注册路由
init_routes(app)

# 你可以在这里进行其他的初始化操作
# 全局拦截器，除 /login 和 /logout 之外的请求都必须登录


from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

def check_jwt():
    """拦截请求，校验 JWT 身份"""
    if request.method == 'OPTIONS':  
        return  # 放行 OPTIONS 预检请求

    # 允许跳过身份校验的接口
    if request.path in ['/api/login', '/api/logout']:
        return  

    try:
        verify_jwt_in_request()  # 先校验请求中的 JWT 令牌
        identity = get_jwt_identity()  # 获取用户身份
        if not identity:
            return jsonify({"error": "Unauthorized"}), 401
    except Exception as e:
        return jsonify({"error": "Invalid token", "message": str(e)}), 401

# 在 Flask 应用的 before_request 里调用
@app.before_request
def before_request():
    return check_jwt()

# 允许访问多个路径
@app.route("/get_image")
def get_image():
    image_path = request.args.get("path")  # 获取前端传来的完整路径
    if not image_path or not os.path.exists(image_path):
        return "File not found", 404
    return send_file(image_path, mimetype="image/png")

