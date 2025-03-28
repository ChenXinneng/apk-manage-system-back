import concurrent.futures
import hashlib
import zipfile
import io
import datetime
import zipfile
from PIL import Image
from ApkParse.main import ApkFile
from app.models.apk_main import ApkMain
import os
from app.utils.commonUtils import CommonUtils
from androguard.misc import AnalyzeAPK
import re
import logging



"""
    静态解析apk
    输出内容：MD5、SHA-1、SHA-256、Package Name、The main activity、Version Name、icon
"""
class UnzipApkUtil:
    @staticmethod
    def calculate_hash(file_path, algorithm):
        """
        计算APK文件的哈希值。
        通过并行化哈希计算过程提升性能
        """
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):  # 使用Python 3.8+的海象运算符
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    def search_icon(apk_path,zip_ref):
        # 排除的关键字
        except_keywords = ['dcloud', 'bg', 'background']
        for file_info in zip_ref.infolist():
            #先找到res文件夹下的icon或launcher图标
            if file_info.filename.startswith('res/') and (r'/icon' in file_info.filename or r'/launcher' in file_info.filename):
                print(f"Found icon: {file_info.filename}")
                with zip_ref.open(file_info) as icon_file:
                    try:
                        icon_bytes = io.BytesIO(icon_file.read())
                        img = Image.open(icon_bytes)
                        new_path = CommonUtils.generate_relative_path(apk_path,'icon','png')
                        img.save(new_path)
                        img.close()
                        return new_path
                    except Exception as e:
                        pass
            #如果没有找到，再找其他命名的icon
            if file_info.filename.startswith('res/') and ('icon' in file_info.filename or 'launcher' in file_info.filename) \
                and (file_info.filename.endswith('.png') or file_info.filename.endswith('.jpg'))\
                and (all(keyword not in file_info.filename for keyword in except_keywords)):
                    print(f"Found icon: {file_info.filename}")
                    with zip_ref.open(file_info) as icon_file:
                        try:
                            icon_bytes = io.BytesIO(icon_file.read())
                            img = Image.open(icon_bytes)
                            new_path = CommonUtils.generate_relative_path(apk_path,'icon','png')
                            img.save(new_path)
                            img.close()
                            return new_path
                        except Exception as e:
                            continue
        return None
                    
    # 获得图标
    @staticmethod
    def extract_icon_from_apk(apk_path):
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            search_icon_result = UnzipApkUtil.search_icon(apk_path,zip_ref)
            return search_icon_result   
        return None
    
    @staticmethod
    def scan_libs(apk_path):
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            libs = [file for file in zip_ref.namelist() if file.startswith('lib/')]
            print(f"Found libraries: {libs}")
            return libs
        return None


    # 静态解析apk
    @staticmethod
    def analyze_apk(file_path,apkMain):
        start_time= datetime.datetime.now()
        # 并行计算MD5、SHA1和SHA256哈希
        with concurrent.futures.ThreadPoolExecutor() as executor:
            hash_futures = {
                'MD5': executor.submit(UnzipApkUtil.calculate_hash, file_path, 'md5'),
                'SHA-1': executor.submit(UnzipApkUtil.calculate_hash, file_path, 'sha1'),
                'SHA-256': executor.submit(UnzipApkUtil.calculate_hash, file_path, 'sha256'),
                'icon_path':executor.submit(UnzipApkUtil.extract_icon_from_apk, file_path),
                # 'libs':executor.submit(UnzipApkUtil.scan_libs, file_path)
            }
            
            # 获取哈希值
            md5_hash = hash_futures['MD5'].result()
            sha1_hash = hash_futures['SHA-1'].result()
            sha256_hash = hash_futures['SHA-256'].result()
            icon_path = hash_futures['icon_path'].result()

        print(f"MD5: {md5_hash}")
        apkMain.file_md5 = md5_hash
        print(f"SHA-1: {sha1_hash}")
        apkMain.file_sha1 = sha1_hash
        print(f"SHA-256: {sha256_hash}")
        apkMain.file_sha256 = sha256_hash
        print(f"icon_path: {icon_path}")
        apkMain.icon_location = icon_path
        # print(f"libs: {hash_futures['libs'].result()}")

    @staticmethod
    def apkParse(apk_path,apkMain):
        start_time= datetime.datetime.now()
        # 创建 ApkFile 对象
        apk = ApkFile(apk_path)

        # 获取解析出来的信息
        app_name = apk.app_name
        package_name = apk.package
        main_activity = apk.main_activity
        # permissions = apk.permissions  # permissions 通常为列表
        version_name = apk.version
        file_size = apk.zip.file_size

        # 打印信息
        print(f"App Name: {app_name}")
        apkMain.app_name = app_name
        print(f"Package Name: {package_name}")
        apkMain.package_name = package_name
        print(f"The main activity is: {main_activity}")
        apkMain.main_activity = main_activity
        #print(f"Permissions: {permissions[:5]}")  # 仅打印前5个权限
        print(f"Version Name: {version_name}")
        apkMain.android_version = version_name
        print(f"File Size: {file_size}")
        apkMain.apk_size = file_size

    @staticmethod
    def analyze_apk_for_meiqia(apk_path):
        # 设置 Androguard 相关日志级别为 ERROR
        logging.getLogger("androguard").setLevel(logging.ERROR)
        # 或者仅对分析模块进行设置
        logging.getLogger("androguard.core.analysis.analysis").setLevel(logging.ERROR)
        a, dex_list, dx = AnalyzeAPK(apk_path)
        
        all_strings = []
        for d in dex_list:
            for current_class in d.get_classes():
                for method in current_class.get_methods():
                    code = method.get_code()
                    if code:
                        for instruction in code.get_instructions():
                            if instruction.get_name() == "const-string":
                                all_strings.append(instruction.get_output())
        
        combined_text = " ".join(all_strings).lower()
        
        if "meiqia" in combined_text or "美洽" in combined_text:
            print("检测到美洽客服相关关键词，可能使用了美洽客服 SDK。")
            pattern = re.compile(r'setclientid\(["\']([^"\']+)["\']\)', re.IGNORECASE)
            match = pattern.search(combined_text)
            if match:
                meiqia_id = match.group(1)
                print("提取到美洽客服 ID:", meiqia_id)
                return meiqia_id
            else:
                print("未能提取到美洽客服 ID。")
        else:
            print("未检测到美洽客服相关信息。")
        return None

    @staticmethod
    def getApkStatic(file_path=r'C:\Users\ot763\Desktop\uni.wnsefn.lgwkbzcx.apk',apkMain=ApkMain()):
        UnzipApkUtil.apkParse(file_path,apkMain)
        UnzipApkUtil.analyze_apk(file_path,apkMain)
        apkMain.parse_time = datetime.datetime.now()
        # UnzipApkUtil.analyze_apk_for_meiqia(file_path)
