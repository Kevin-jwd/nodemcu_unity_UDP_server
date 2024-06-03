import socket
import threading
import signal
import sys

# 클라이언트 소켓
arduino_client = None
unity_client = None

# 서버 소켓
server_socket = None

# 아두이노에서 데이터 수신 및 유니티로 전송
def handle_arduino():
    global arduino_client, unity_client
    while True:
        try:
            data = arduino_client.recv(1024)
            if not data:
                break
            print("Received from Arduino:", data.decode())
            if unity_client:
                unity_client.send(data)
        except (ConnectionResetError, OSError) as e:
            print(f"Arduino connection error: {e}")
            break
    if arduino_client:
        arduino_client.close()
        arduino_client = None

# 유니티 클라이언트 관리
def handle_unity():
    global unity_client
    while True:
        try:
            data = unity_client.recv(1024)
            if not data:
                break
            print("Received from Unity:", data.decode())
        except (ConnectionResetError, OSError) as e:
            print(f"Unity connection error: {e}")
            break
    if unity_client:
        unity_client.close()
        unity_client = None

# 신호 핸들러
def signal_handler(sig, frame):
    global arduino_client, unity_client, server_socket
    print('Interrupt received, shutting down...')
    if arduino_client:
        arduino_client.close()
    if unity_client:
        unity_client.close()
    if server_socket:
        server_socket.close()
    sys.exit(0)

def main():
    global arduino_client, unity_client, server_socket
    host = "172.20.10.10"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("Server listening on port", port)

    # SIGINT 신호를 처리하도록 설정
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")

            if not arduino_client:
                arduino_client = conn
                arduino_thread = threading.Thread(target=handle_arduino)
                arduino_thread.start()
            elif not unity_client:
                unity_client = conn
                unity_thread = threading.Thread(target=handle_unity)
                unity_thread.start()
        except (OSError, KeyboardInterrupt) as e:
            print(f"Server error: {e}")
            break

    # 서버 소켓 종료
    if server_socket:
        server_socket.close()

if __name__ == "__main__":
    main()
