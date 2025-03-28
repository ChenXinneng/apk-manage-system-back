import os
import time
import subprocess
import requests
from apkutils import APK
from PIL import Image
import shutil
from app import app
from app.utils.commonUtils import CommonUtils

# 配置参数
ADB_PATH = app.config["ADB_PATH"] # ADB命令路径（已配置环境变量）
EMULATOR_DEVICE = app.config['ADB_IP_PORT']
EMULATOR_PATH = app.config['EMULATOR_PATH']

class ScreenshotApkUtil:
    @staticmethod
    def parse_apk_info(apk_path):
        """解析APK包名和主Activity"""
        apk = APK.from_file(apk_path)
        # manifest = apk.get_manifest()
        package_name = apk.get_package_name()
        main_activity = apk.get_main_activities()[0]
        apk.close()
        return package_name, main_activity

    @staticmethod
    def install_and_launch(apk_path, package_name, main_activity):
        """安装APK并启动主Activity"""
        # 安装APK
        subprocess.run(
            [ADB_PATH, "-s", EMULATOR_DEVICE, "install", apk_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # 启动主Activity
        subprocess.run(
            [ADB_PATH, "-s", EMULATOR_DEVICE, "shell", "am", "start", "-n", f"{package_name}/{main_activity}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(5)  # 等待应用启动

    @staticmethod
    def take_screenshot(apk_path):
        """截图并保存"""
        timestamp = int(time.time())
        # screenshot_path = os.path.join(SCREENSHOT_DIR, f"{package_name}_{timestamp}.png")
        screenshot_path = CommonUtils.generate_relative_path(apk_path,'screenshot','png')
        # 设置截图分辨率为 iPhone 12 Pro 的视网膜分辨率 1170x2532
        # target_width = 1170
        # target_height = 2532
        # 截图命令
        subprocess.run(
            [ADB_PATH, "-s", EMULATOR_DEVICE, "exec-out", "screencap", "-p"],
            stdout=open(screenshot_path, "wb"),
            check=True
        )
        # 优化截图（可选）
        img = Image.open(screenshot_path)
        # 设置目标分辨率为 iPhone 12 Pro 的视网膜分辨率 1170x2532,现在mumu模拟器已经是这个尺寸
        # img = img.resize((target_width, target_height), Image.LANCZOS)
        img.save(screenshot_path, optimize=True)
        return screenshot_path

    @staticmethod
    def move_file(apk_path, target_dir):
        try:
            # 确保目标目录存在
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, os.path.basename(apk_path))
            shutil.move(apk_path, target_path)
            print(f"File moved successfully: {apk_path} -> {target_path}")
        except Exception as e:
            print(f"Failed to move {apk_path}: {e}")

    @staticmethod
    def cleanup(apk_path, package_name):
        """卸载APK并删除临时文件"""
        subprocess.run(
            [ADB_PATH, "-s", EMULATOR_DEVICE, "uninstall", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    @staticmethod
    def process_apk(apk_path):
        """处理单个APK链接"""
        try:
            print(f"Processing APK: {apk_path}")
            # 解析包名和主Activity
            package_name, main_activity = ScreenshotApkUtil.parse_apk_info(apk_path)
            if not main_activity:
                raise ValueError("Main activity not found in APK!")
            # 安装并启动
            ScreenshotApkUtil.install_and_launch(apk_path, package_name, main_activity)
            # 截图
            screenshot_path = ScreenshotApkUtil.take_screenshot(apk_path)
            print(f"Screenshot saved: {screenshot_path}")
            
            # 清理
            ScreenshotApkUtil.cleanup(apk_path, package_name)
            return screenshot_path
        except Exception as e:
            print(f"Failed to process {apk_path}: {str(e)}")
            return None

    @staticmethod
    def get_adb_devices():
        """ 获取当前连接的 ADB 设备列表 """
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True,encoding='utf-8')
        lines = result.stdout.strip().split("\n")
        devices = [line for line in lines[1:] if line.strip()]  # 过滤掉标题行和空行
        return devices
        
    @staticmethod
    def start_mumu_emulator():
        """ 启动 MuMu 模拟器 """
        emulator_path = EMULATOR_PATH
        if os.path.exists(emulator_path):
            subprocess.Popen(emulator_path, shell=True)
            print("已启动 MuMu 模拟器，等待 5 秒以确保其完全启动...")
            time.sleep(5)
        else:
            print("错误：模拟器文件不存在！")

    @staticmethod
    def connect_mumu():
        try:
            result = subprocess.run(["adb", "connect", EMULATOR_DEVICE], capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            pass
        

    @staticmethod
    def screenshot(apk_url=r"C:\Users\ot763\Desktop\uni.wnsefn.lgwkbzcx.apk"):
        # 判断模拟器是否打开，未打开则打开
        devices = ScreenshotApkUtil.get_adb_devices()
        if not devices or "offline" in devices[0]:
            print("未检测到 ADB 设备，尝试启动模拟器...")
            ScreenshotApkUtil.start_mumu_emulator()
            try_count = 1
            while try_count <= 5:
                ScreenshotApkUtil.connect_mumu()
                start_devices = ScreenshotApkUtil.get_adb_devices()
                if start_devices and "device" in start_devices[0]:
                    print("ADB 设备已连接:", start_devices[0])
                    break
                else:
                    print("等待 5 秒后重试...")
                    time.sleep(5)
                    try_count += 1
        else:
            print("ADB 设备已连接:", devices[0])
        screenshot_path = ScreenshotApkUtil.process_apk(apk_url)
        print("All APKs processed!")
        return screenshot_path
            
        
    