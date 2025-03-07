from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def get_current_user():
    """
    获取当前登录用户信息
    :return: 用户身份 或 None
    """
    try:
        verify_jwt_in_request(optional=True)  # 如果请求未携带 JWT，不会抛异常
        return get_jwt_identity()  # 返回用户身份
    except Exception:
        return None  # 未登录或 JWT 失效
