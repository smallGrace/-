import pyaudio
import numpy as np
import time
import sys

# 全局变量存储当前音量值
current_volume_db = -np.inf

def realtime_volume_detector(threshold_db=-20, sample_rate=44100, chunk_size=1024):
    global current_volume_db
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk_size)
    
    # print(f"🎤 实时麦克风音量检测器已启动 | 阈值: {threshold_db}dB")
    print("按下Ctrl+C停止程序...")
    
    above_threshold = False
    
    try:
        while True:
            data = stream.read(chunk_size, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            rms = np.sqrt(np.mean(np.square(audio_data)))
            current_volume_db = 20 * np.log10(rms / 32768) if rms > 0 else -np.inf
            
            # # 显示实时音量
            # bar_length = 30
            # bar = '█' * int(np.interp(current_volume_db, [-60, 0], [0, bar_length]))
            # sys.stdout.write(f"\r音量: {current_volume_db:6.1f}dB [{bar:<{bar_length}}]")
            # sys.stdout.flush()
            
            # 阈值检测
            if current_volume_db > threshold_db:
                if not above_threshold:
                    print("\n🔊 音量超过阈值! (当前音量: {:.1f}dB)".format(current_volume_db))
                    above_threshold = True
            else:
                above_threshold = False
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n程序已停止")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# 外部获取音量的函数
def get_current_volume():
    return current_volume_db

# 使用示例
if __name__ == "__main__":
    import threading
    
    # 启动检测器线程
    detector_thread = threading.Thread(
        target=realtime_volume_detector,
        kwargs={"threshold_db": -10}
    )
    detector_thread.daemon = True
    detector_thread.start()
    
    # 在主线程中访问音量值
    try:
        while True:
            volume = get_current_volume()
            # 在这里添加你的音量处理逻辑
            print(f"外部获取的音量值: {volume:.1f}dB")
            # 例如：print(f"外部获取的音量值: {volume:.1f}dB")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n主程序退出")