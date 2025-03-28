from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import os
import time

class CommonUtils:
    # 获取当前身份信息
    @staticmethod
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
        
    @staticmethod
    def copy_field_not_none(source, target):
        """
        Copy fields from source object to target object if the value is not None.
        """
        for key, value in source.items():
            if value is not None:
                setattr(target, key, value)
        return target
    
    # 根据提供的路径生成对应的相对路径
    @staticmethod
    def generate_relative_path(apk_path, relative_dir="icon",file_suffix="png"):
        timestamp = int(time.time())
        # 分离文件名和扩展名
        file_name, _ = os.path.splitext(os.path.basename(apk_path))
        # 获取目录路径
        dir_path = os.path.dirname(apk_path)
        # 构建 相对 目录路径
        new_dir = os.path.join(dir_path, relative_dir)
        if os.path.exists(new_dir) is False:
            os.makedirs(new_dir)
        # 构建新的文件路径
        new_path = os.path.join(new_dir, f'{file_name}_{timestamp}.{file_suffix}')
        return new_path
