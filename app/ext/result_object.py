from flask import jsonify

class ResultObject:
    def __init__(self, success: bool, msg: str, data: dict = None):
        """
        初始化 ResultObject 实例
        :param success: 是否成功
        :param msg: 响应消息
        :param data: 返回的数据，默认为 None
        """
        self.success = success
        self.msg = msg
        self.data = data

    def build(self):
        """
        构建响应数据
        :return: 字典格式的响应数据
        """
        return {
            "success": self.success,
            "msg": self.msg,
            "data": self.data
        }

    def jsonify(self):
        """
        将响应数据转换为 JSON 格式
        :return: JSON 格式的响应
        """
        return jsonify(self.build())
