import cv2
import numpy as np
import pyautogui
import time
from PIL import Image, ImageDraw, ImageFont

class RegionSelector:
    def __init__(self):
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.fx, self.fy = -1, -1
        self.screen = None
        self.window_name = "select region"
        self.scale_factor = 0.5  # 图像缩放因子，降低处理负荷
        self.font = None
        
        # 尝试加载中文字体
        try:
            # Windows系统常见中文字体路径
            self.font = ImageFont.truetype("simsun.ttc", 20)
        except:
            try:
                # macOS系统常见中文字体路径
                self.font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 20)
            except:
                print("警告: 无法加载中文字体，将使用默认字体")
    
    def _add_chinese_text(self, image, text, position, color=(255, 255, 255)):
        """在图像上添加中文文本"""
        if self.font is None:
            # 如果没有中文字体，使用OpenCV添加英文文本
            cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            return image
        
        # 将OpenCV图像转换为PIL图像
        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        
        # 绘制中文文本
        draw.text(position, text, font=self.font, fill=color)
        
        # 转换回OpenCV格式
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    def _mouse_callback(self, event, x, y, flags, param):
        # 调整坐标到原始尺寸
        x_orig = int(x / self.scale_factor)
        y_orig = int(y / self.scale_factor)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x_orig, y_orig
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.fx, self.fy = x_orig, y_orig
                # 只更新显示区域，避免全屏重绘
                self._update_display()
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.fx, self.fy = x_orig, y_orig
            self._update_display()
    
    def _update_display(self):
        """只更新显示区域，避免全屏重绘"""
        if not self.drawing:
            return
            
        # 创建显示图像的副本
        display_img = self.display_screen.copy()
        
        # 计算缩放后的坐标
        ix_scaled = int(self.ix * self.scale_factor)
        iy_scaled = int(self.iy * self.scale_factor)
        fx_scaled = int(self.fx * self.scale_factor)
        fy_scaled = int(self.fy * self.scale_factor)
        
        # 绘制矩形
        cv2.rectangle(display_img, (ix_scaled, iy_scaled), 
                      (fx_scaled, fy_scaled), (0, 255, 0), 2)
        
        # 添加提示文本
        display_img = self._add_chinese_text(
            display_img, 
            "拖动鼠标选择区域 - ESC确认 | R重置", 
            (10, 30), 
            (0, 255, 0)
        )
        
        # 显示图像
        cv2.imshow(self.window_name, display_img)
    
    def select_region(self):
        """允许用户通过鼠标在屏幕上选择区域"""
        # 获取屏幕截图（使用更高效的捕获方法）
        self.screen = np.array(pyautogui.screenshot())
        
        # 创建缩放后的显示图像
        self.display_screen = cv2.resize(
            self.screen, 
            (0, 0), 
            fx=self.scale_factor, 
            fy=self.scale_factor
        )
        
        # 添加初始提示文本
        self.display_screen = self._add_chinese_text(
            self.display_screen, 
            "拖动鼠标选择区域 - ESC确认 | R重置", 
            (10, 30), 
            (0, 255, 0)
        )
        
        # 创建窗口并设置鼠标回调
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
        
        # 显示初始图像
        cv2.imshow(self.window_name, self.display_screen)
        
        # 等待用户完成选择
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC键退出
                break
            elif key == ord('r') or key == ord('R'):  # 重置选择
                self.ix, self.iy = -1, -1
                self.fx, self.fy = -1, -1
                cv2.imshow(self.window_name, self.display_screen)
        
        cv2.destroyAllWindows()
        
        # 确保坐标正确（左上角到右下角）
        if self.ix == -1 or self.iy == -1:
            return None
        
        x1, y1 = min(self.ix, self.fx), min(self.iy, self.fy)
        x2, y2 = max(self.ix, self.fx), max(self.iy, self.fy)
        
        return (x1, y1, x2 - x1, y2 - y1)  # (x, y, width, height)

# 使用示例
if __name__ == "__main__":
    print("屏幕区域选择工具将在2秒后启动...")
    time.sleep(2)  # 给用户时间准备
    
    selector = RegionSelector()
    region = selector.select_region()
    
    if region:
        print(f"您选择的区域坐标: {region}")
        print(f"格式: (左上角x坐标, 左上角y坐标, 宽度, 高度)")
    else:
        print("未选择任何区域")
        