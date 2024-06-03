import socket
import signal
import sys

# 서버 IP 주소와 포트 설정
SERVER_IP = '172.20.10.3'  # 모든 IP 주소에서 수신
SERVER_PORT = 12000    # 아두이노와 동일한 포트 번호

# 서버 소켓 설정
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)

print(f"서버가 {SERVER_PORT} 포트에서 대기 중입니다...")

# 종료 신호 처리기
def signal_handler(sig, frame):
    print('서버가 종료됩니다.')
    server_socket.close()
    sys.exit(0)

# SIGINT 신호 처리기 설정
signal.signal(signal.SIGINT, signal_handler)

while True:
    try:
        client_socket, client_address = server_socket.accept()
        print(f"{client_address}에서 연결됨")

        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"받은 데이터: {data}")

                # 데이터를 파일에 저장 (또는 데이터베이스에 저장)
                with open('data.txt', 'a') as file:
                    file.write(data + '\n')
            except ConnectionResetError:
                break

        client_socket.close()
        print(f"{client_address} 연결이 종료되었습니다.")
    except socket.error as e:
        print(f"소켓 오류: {e}")
        break
