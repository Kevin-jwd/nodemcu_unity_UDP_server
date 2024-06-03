import socket
import threading
import signal
import sys
import mysql.connector
import json

# 클라이언트 소켓
arduino_client = None
unity_client = None

# 서버 소켓
server_socket = None

# MySQL conn
dbConn = None

# MySQL 서버 연결 정보
host = '127.0.0.1'  # 호스트 주소
database = 'mpu6050_test_2_schema'  # 데이터베이스명
user = 'python_TCP_server'  # 사용자이름
password = '111122223333'  # 비밀번호

# 각 mpu의 값을 콤마로 분리하고, 올바른 경우에만 딕셔너리에 추가
def parse_mpu_data(mpu_string):
    mpu_data = {}
    for item in mpu_string.split(','):
        if ':' in item:
            key, value = item.split(':', 1)
            mpu_data[key.strip()] = value.strip()
    return mpu_data

# 아두이노에서 데이터 수신 및 유니티로 전송
def handle_arduino():
    global arduino_client, unity_client, dbConn
    while True:
        try:
            data = arduino_client.recv(1024)
            if not data:
                break
        
            print("Received from Arduino:", data.decode())
            # 바이트 문자열을 디코딩하여 문자열로 변환
            data_str = data.decode('utf-8').strip()

            # 줄 단위로 JSON 객체 파싱
            for line in data_str.split('\n'):
                try:
                    parsed_data = json.loads(line)
                    print(parsed_data)

                    if 'mpu1' in parsed_data and 'mpu2' in parsed_data:
                        mpu1_device = parse_mpu_data(parsed_data['mpu1'])
                        mpu2_device = parse_mpu_data(parsed_data['mpu2'])

                        # 센서값 MySQL로 전송
                        mysql_insert_data(dbConn, 'mpu1_table', mpu1_device)
                        mysql_insert_data(dbConn, 'mpu2_table', mpu2_device)

                        if unity_client:
                            unity_client.send(data)
                except json.JSONDecodeError as e:
                    print(f"JSON 디코딩 오류: {e}")
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
            parsed_data = json.loads(data.decode())
            print("Received from Unity:", parsed_data)
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

# MySQL 서버연결
def mysql_connector(host, database, user, password):
    try:
        conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
        print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
        return conn
    except mysql.connector.Error as err:
        print(f"오류 : {err}")
        return None

# MySQL에 센서값 전송
def mysql_insert_data(connection, table_name, device_data):
    try:
        cursor = connection.cursor()

        # SQL 쿼리 정의 (테이블 이름은 동적으로 설정)
        query = f"INSERT INTO `{table_name}` (q_w, q_x, q_y, q_z) VALUES (%s, %s, %s, %s)"

        # 데이터 준비
        data = (device_data.get('w'), device_data.get('x'), device_data.get('y'), device_data.get('z'))

        # 쿼리 실행
        cursor.execute(query, data)

        # 변경사항 커밋
        connection.commit()

        print("데이터가 성공적으로 삽입되었습니다.")
    except mysql.connector.Error as err:
        print(f"오류: {err}")
    finally:
        cursor.close()

def main():
    global arduino_client, unity_client, server_socket, dbConn
    host = "172.20.10.3"
    port = 12000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("Server listening on port", port)

    # SIGINT 신호를 처리하도록 설정
    signal.signal(signal.SIGINT, signal_handler)

    # MySQL 연결
    dbConn = mysql_connector(host, database, user, password)

    if dbConn is not None:
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
    else:
        print("데이터베이스 연결 실패")
        server_socket.close()

    # 서버 소켓 종료
    if server_socket:
        server_socket.close()

if __name__ == "__main__":
    main()
