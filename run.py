from app import create_app
import socket

app = create_app()

def find_free_port(start_port=5000, max_port=5050):
    """查找可用端口"""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return None

if __name__ == '__main__':
    # 尝试使用默认端口，如果被占用则查找可用端口
    try:
        port = 5000
        # 检查端口是否被占用
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) == 0:
                # 端口被占用，查找可用端口
                port = find_free_port()
                if port:
                    print(f"端口5000已被占用，使用新端口: {port}")
                else:
                    print("无法找到可用端口，请手动关闭占用端口5000的程序")
                    port = 5000
    except Exception as e:
        print(f"检查端口时出错: {e}")
        port = 5000
    
    app.run(debug=True, port=port) 