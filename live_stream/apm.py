import time
import threading
from collections import deque
from pynput import keyboard, mouse

class APMCalculator:
    def __init__(self, window_size=60, callback=None):
        """
        初始化APM计算器
        
        参数:
            window_size: 统计时间窗口（秒），默认为10秒
            callback: 当APM更新时的回调函数
        """
        self.window_size = window_size
        self.events = deque()  # 存储事件时间戳的队列
        self.lock = threading.Lock()  # 线程锁
        self.running = True  # 运行状态标志
        self.current_apm = 0.0  # 当前APM值
        self.callback = callback  # APM更新时的回调函数
        
        # 启动键盘和鼠标监听器
        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        
        self.keyboard_listener.start()
        self.mouse_listener.start()
        
        # 启动APM计算线程
        self.apm_thread = threading.Thread(target=self._calculate_apm)
        self.apm_thread.daemon = True
        self.apm_thread.start()
    
    def _on_key_press(self, key):
        """键盘按键事件处理"""
        with self.lock:
            self.events.append(time.time())
    
    def _on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        if pressed:  # 只统计按下事件，忽略释放事件
            with self.lock:
                self.events.append(time.time())
    
    def _calculate_apm(self):
        """计算APM"""
        try:
            while self.running:
                current_time = time.time()
                cutoff_time = current_time - self.window_size
                
                with self.lock:
                    # 移除过时的事件
                    while self.events and self.events[0] < cutoff_time:
                        self.events.popleft()
                    
                    # 计算当前窗口内的操作次数
                    actions = len(self.events)
                    apm = actions * (60 / self.window_size)
                    self.current_apm = apm
                
                # 如果有回调函数，调用它
                if self.callback:
                    self.callback(apm)
                
                # 每秒更新10次
                time.sleep(0.1)
        except Exception as e:
            print(f"APM计算错误: {e}")
    
    def get_current_apm(self):
        """获取当前APM值"""
        return self.current_apm
    
    def set_window_size(self, window_size):
        """设置时间窗口大小"""
        self.window_size = window_size
    
    def stop(self):
        """停止监听器和计算线程"""
        self.running = False
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.apm_thread.join()


# 使用示例
if __name__ == "__main__":
    # 定义APM更新时的回调函数
    def apm_callback(apm):
        print(f"当前APM: {apm:.1f}")
    
    # 创建APM计算器
    apm_calculator = APMCalculator(window_size=60, callback=apm_callback)
    
    try:
        # 主程序可以在这里执行其他任务
        # APM计算器会在后台持续运行并调用回调函数
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("程序停止")
    finally:
        apm_calculator.stop()