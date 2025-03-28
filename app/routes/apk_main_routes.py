# app/routes/apk_routes.py
from flask import session,Blueprint, request, jsonify
from app import db
from app.models.apk_main import ApkMain
from app.utils.unzipApkUtil import UnzipApkUtil
from app.utils.screenshotApkUtil import ScreenshotApkUtil

apk_main_bp = Blueprint('apkMain', __name__)

@apk_main_bp.route('/apkMain', methods=['GET'])
def get_apks():
    # 获取查询参数
    loginUser = session.get('loginUser')
    app_name = request.args.get('app_name', '')
    package_name = request.args.get('package_name', '')
    md5 = request.args.get('file_md5', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    # 构建查询条件
    query = ApkMain.query
    if app_name:
        query = query.filter(ApkMain.app_name.like(f'%{app_name}%'))
    if package_name:
        query = query.filter(ApkMain.package_name.like(f'%{package_name}%'))
    if md5:
        query = query.filter(ApkMain.file_md5 == md5)

    # 分页查询
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    apks = pagination.items

    # 构建返回数据
    result = {
        'items': [apk.to_dict() for apk in apks],
        'total': pagination.total,
        'page': page,
        'page_size': page_size,
        'pages': pagination.pages,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next,
    }

    return jsonify(result)
# 获取apk列表
# @apk_bp.route('/apkMain', methods=['GET'])
# def get_apk_list():
#     apks = ApkMain.query.all()
#     return jsonify([apk.to_dict() for apk in apks])

# 获取单个apk的详情
@apk_main_bp.route('/apkMain/<int:id>', methods=['GET'])
def get_apk(id):
    apk = ApkMain.query.get_or_404(id)
    return jsonify(apk.to_dict())

# 创建apk
@apk_main_bp.route('/apkMain', methods=['POST'])
def create_apk():
    data = request.get_json()
    new_apk = ApkMain(**data)
    db.session.add(new_apk)
    db.session.commit()
    return jsonify(new_apk.to_dict()), 201

# 更新apk
@apk_main_bp.route('/apkMain/<int:id>', methods=['PUT'])
def update_apk(id):
    data = request.get_json()
    apk = ApkMain.query.get_or_404(id)
    apk.app_name = data.get('app_name', apk.app_name)
    apk.package_name = data.get('package_name', apk.package_name)
    apk.main_activity = data.get('main_activity', apk.main_activity)
    apk.android_version = data.get('android_version', apk.android_version)
    apk.parse_time = data.get('parse_time', apk.parse_time)
    apk.apk_size = data.get('apk_size', apk.apk_size)
    apk.file_md5 = data.get('file_md5', apk.file_md5)
    apk.file_sha1 = data.get('file_sha1', apk.file_sha1)
    apk.file_sha256 = data.get('file_sha256', apk.file_sha256)
    apk.apk_location = data.get('apk_location', apk.apk_location)
    apk.icon_location = data.get('icon_location', apk.icon_location)
    apk.screenshot_location = data.get('screenshot_location', apk.screenshot_location)
    apk.apk_download_url = data.get('apk_download_url', apk.apk_download_url)
    apk.download_page_url = data.get('download_page_url', apk.download_page_url)

    db.session.commit()
    return jsonify(apk.to_dict())

# 删除apk
@apk_main_bp.route('/apkMain/<int:id>', methods=['DELETE'])
def delete_apk(id):
    apk = ApkMain.query.get_or_404(id)
    db.session.delete(apk)
    db.session.commit()
    return '', 204


# 静态解析apk
@apk_main_bp.route('/apkMain/analysis/<int:id>', methods=['POST'])
def analysis_apk(id):
    apk = ApkMain.query.get_or_404(id)
    UnzipApkUtil.getApkStatic(apk.apk_location,apk)
    db.session.commit()
    return jsonify(apk.to_dict())


# 模拟器打开apk并截图
@apk_main_bp.route('/apkMain/screenshot/<int:id>', methods=['POST'])
def screenshot_apk(id):
    apk = ApkMain.query.get_or_404(id)
    apk.screenshot_location = ScreenshotApkUtil.screenshot(apk.apk_location)
    db.session.commit()
    return jsonify(apk.to_dict())
