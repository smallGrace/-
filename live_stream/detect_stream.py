import time
import threading
import json
import os
from datetime import datetime
from draw_recangle import RegionSelector
from ocr_number import DigitRecognizer
from apm import APMCalculator
from micphone import realtime_volume_detector, get_current_volume

class MultiSensorMonitor:
    def __init__(self, config_file="sensor_config.json"):
        self.config_file = config_file
        self.region = None
        self.running = False
        self.threads = []
        
        # 加载配置
        self.load_config()
        
        # 初始化各个传感器
        self.region_selector = RegionSelector()
        self.digit_recognizer = DigitRecognizer()
        self.apm_calculator = None
        self.volume_thread = None
        
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'region' in config:
                        self.region = tuple(config['region'])
                    print("已加载保存的区域配置")
            except Exception as e:
                print(f"加载配置失败: {e}")
                self.region = None
        else:
            self.region = None
    
    def save_config(self):
        """保存配置文件"""
        try:
            config = {}
            if self.region:
                config['region'] = list(self.region)
                config['last_updated'] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("配置已保存")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def select_region_interactive(self):
        """交互式选择区域"""
        print("屏幕区域选择工具将在2秒后启动...")
        time.sleep(2)
        
        selector = RegionSelector()
        region = selector.select_region()
        
        if region:
            print(f"您选择的区域坐标: {region}")
            self.region = region
            self.save_config()
            return True
        else:
            print("未选择任何区域")
            return False
    
    def ask_region_selection(self):
        """询问用户是否需要重新选择区域"""
        if self.region:
            print(f"检测到已保存的区域: {self.region}")
            choice = input("是否需要重新选择区域？(y/n, 默认n): ").strip().lower()
            if choice == 'y' or choice == 'yes':
                return self.select_region_interactive()
            else:
                print("使用已保存的区域")
                return True
        else:
            print("未找到保存的区域配置")
            return self.select_region_interactive()
    
    def start_apm_monitor(self):
        """启动APM监控"""
        def apm_callback(apm):
            self.current_apm = apm
        
        self.apm_calculator = APMCalculator(window_size=60, callback=apm_callback)
        self.current_apm = 0.0
    
    def start_volume_monitor(self):
        """启动音量监控"""
        self.volume_thread = threading.Thread(
            target=realtime_volume_detector,
            kwargs={"threshold_db": -10}
        )
        self.volume_thread.daemon = True
        self.volume_thread.start()
    
    def monitor_sensors(self):
        """监控所有传感器并汇总数据"""
        print("开始监控传感器数据...")
        print("按Ctrl+C停止监控")
        
        try:
            while self.running:
                # 获取心跳值（OCR数字识别）
                heartbeat = ""
                if self.region:
                    try:
                        heartbeat = self.digit_recognizer.recognize_digits(self.region)
                    except Exception as e:
                        heartbeat = f"识别错误: {e}"
                
                # 获取APM值
                apm_value = self.current_apm if hasattr(self, 'current_apm') else 0.0
                
                # 获取麦克风音量
                volume_value = get_current_volume()
                
                # 汇总并打印数据
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}] 传感器数据汇总:")
                print(f"  心跳值: {heartbeat if heartbeat else '未检测到'}")
                print(f"  操作频率(APM): {apm_value:.1f}")
                print(f"  麦克风音量: {volume_value:.1f}dB")
                print("-" * 50)
                
                time.sleep(1)  # 每秒更新一次
                
        except KeyboardInterrupt:
            print("\n监控已停止")
        except Exception as e:
            print(f"监控过程中出现错误: {e}")
    
    def start_monitoring(self):
        """启动完整监控流程"""
        # 询问区域选择
        if not self.ask_region_selection():
            print("区域选择失败，程序退出")
            return
        
        # 启动各个监控器
        self.running = True
        
        # 启动APM监控
        self.start_apm_monitor()
        
        # 启动音量监控
        self.start_volume_monitor()
        
        # 启动主监控线程
        monitor_thread = threading.Thread(target=self.monitor_sensors)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # 保持主线程运行
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n正在停止所有监控...")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """停止所有监控"""
        self.running = False
        if self.apm_calculator:
            self.apm_calculator.stop()
        print("所有监控已停止")

def main():
    """主函数"""
    print("=" * 60)
    print("多传感器监控系统")
    print("功能: 心跳值识别 + 操作频率监控 + 麦克风音量检测")
    print("=" * 60)
    
    monitor = MultiSensorMonitor()
    
    try:
        monitor.start_monitoring()
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()