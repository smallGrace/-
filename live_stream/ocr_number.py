import easyocr
import pyautogui
import cv2
import numpy as np
import time

class DigitRecognizer:
    def __init__(self):
        # 初始化EasyOCR阅读器，指定英语和数字识别
        self.reader = easyocr.Reader(['en'])
    
    def capture_screen(self, region=None):
        """捕获屏幕"""
        screenshot = pyautogui.screenshot(region=region)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def preprocess_image(self, img):
        """图像预处理"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 增强对比度
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        return enhanced
    
    def recognize_digits(self, region=None):
        """识别数字"""
        # 捕获屏幕
        img = self.capture_screen(region)
        
        # 预处理
        processed_img = self.preprocess_image(img)
        
        # 识别文本
        results = self.reader.readtext(processed_img, allowlist='0123456789')
        
        # 提取数字
        digits = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # 置信度阈值
                # 只保留数字字符
                digit_text = ''.join(filter(str.isdigit, text))
                if digit_text:
                    digits.append(digit_text)
        
        return ' '.join(digits) if digits else ""
    
    def continuous_recognition(self, region=None, interval=0.5):
        """
        持续实时识别数字
        :param region: 屏幕区域 (x, y, width, height)
        :param interval: 识别间隔时间（秒）
        """
        try:
            while True:
                result = self.recognize_digits(region)
                yield result  # 返回识别结果
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n实时识别已停止")

# 使用示例
if __name__ == "__main__":
    recognizer = DigitRecognizer()
    region = (438, 956, 154, 46)  # 你的目标区域
    
    print("开始实时数字识别（按Ctrl+C停止）...")
    for result in recognizer.continuous_recognition(region):
        if result:
            print(f"识别结果: {result}")
        else:
            print("未检测到数字")