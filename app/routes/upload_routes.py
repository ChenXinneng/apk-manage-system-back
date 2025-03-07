import os
import pandas as pd
from flask import current_app,Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, ApkMain  # 确保 ApkMain 是你的数据库模型

upload_bp = Blueprint("upload", __name__)

# 允许的 Excel 格式
ALLOWED_EXTENSIONS = {"xls", "xlsx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route("/upload-excel", methods=["POST"])
def upload_excel():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "未上传文件"}), 400
    
    file = request.files["file"]

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"success": False, "message": "文件格式不正确"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['EXCEL_UPLOAD_FOLDER'], filename)  # 临时存储文件
    file.save(file_path)
    try:
        # 解析 Excel
        df = pd.read_excel(file_path)

        # 检查是否包含所需列
        required_columns = {"app名称", "包名", "主程序", "安卓版本号", "apk大小(MB)","md5","sha1","sha256","apk文件路径","apk下载url"}
        if not required_columns.issubset(set(df.columns)):
            return jsonify({"success": False, "message": "Excel 文件缺少必要的列"}), 400

        # 将数据存入数据库
        new_entries = []
        for _, row in df.iterrows():
            apk = ApkMain(
                app_name=row["app名称"],
                package_name=row["包名"],
                main_activity=row["主程序"],
                android_version=row["安卓版本号"],
                apk_size=row["apk大小(MB)"],
                file_md5=row["md5"],
                file_sha1=row["sha1"],
                file_sha256=row["sha256"],
                apk_location=row["apk文件路径"],
                apk_download_url=row["apk下载url"],

            )
            new_entries.append(apk)

        # db.session.bulk_save_objects(new_entries)
        for entry in new_entries:
            db.session.add(entry)
        db.session.commit()

        return jsonify({"success": True, "message": f"{len(new_entries)} 条记录已成功存入数据库"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"数据库错误: {str(e)}")
        return jsonify({"success": False, "message": f"数据库错误: {str(e)}"}), 500

    except Exception as e:
        print(f"解析 Excel 失败: {str(e)}")
        return jsonify({"success": False, "message": f"解析 Excel 失败: {str(e)}"}), 500

    finally:
        os.remove(file_path)  # 删除临时文件
