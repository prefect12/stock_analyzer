from app import create_app
import socket
import subprocess
import os
import sys
import time

app = create_app()

def kill_process_on_port(port):
    """关闭占用指定端口的进程"""
    try:
        # 对于不同的操作系统使用不同的命令
        if sys.platform.startswith('win'):
            # Windows
            cmd = f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :{port}') do taskkill /F /PID %a"
            subprocess.run(cmd, shell=True)
        elif sys.platform.startswith('darwin'):
            # macOS
            cmd = f"lsof -i :{port} | grep LISTEN | awk '{{print $2}}' | xargs kill -9"
            subprocess.run(cmd, shell=True)
        else:
            # Linux
            cmd = f"lsof -i :{port} | grep LISTEN | awk '{{print $2}}' | xargs kill -9"
            subprocess.run(cmd, shell=True)
            
        print(f"已尝试关闭占用端口 {port} 的进程")
        # 等待进程终止
        time.sleep(1)
        return True
    except Exception as e:
        print(f"关闭占用端口 {port} 的进程时出错: {e}")
        return False

if __name__ == '__main__':
    # 指定使用的端口
    port = 8080
    reloader_env = os.environ.get('WERKZEUG_RUN_MAIN')
    
    # 只在非reloader进程中执行端口清理
    if reloader_env != 'true':
        # 检查端口是否被占用
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) == 0:
                print(f"端口 {port} 已被占用，尝试关闭占用的进程...")
                
                # 尝试关闭占用端口的进程
                if kill_process_on_port(port):
                    # 再次检查端口是否可用
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                        if s2.connect_ex(('localhost', port)) != 0:
                            print(f"成功释放端口 {port}，继续启动应用...")
                        else:
                            print(f"无法释放端口 {port}，请手动关闭占用该端口的程序")
                            sys.exit(1)
                else:
                    print(f"无法自动关闭占用端口 {port} 的进程，请手动关闭")
                    sys.exit(1)
    
    # 启动应用
    print(f"在端口 {port} 上启动应用...")
    app.run(debug=True, port=port, host='0.0.0.0') 