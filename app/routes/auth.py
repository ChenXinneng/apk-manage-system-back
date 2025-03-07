from flask import g,session,Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.ext.result_object import ResultObject

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 验证用户名和密码
    if username == "1" and password == "1":
        access_token = create_access_token(identity=username)
        response = ResultObject(True, "Login successful!", {"userName":username,"authToken": access_token})
        return response.jsonify(), 200
    else:
        response = ResultObject(False, "Invalid credentials", None)
        return response.jsonify(), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """登出接口"""
    session.pop("loginUser", None)  # 清除 session
    return jsonify({"message": "Logged out"})