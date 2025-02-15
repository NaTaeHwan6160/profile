import requests
import subprocess
def send_popup(desktops=[],message='테스트'):
    for desktop in desktops:
        url=f'http://s.wkwk.kr/ahk/insert2.php?com_no={desktop}&text={message}'
        requests.post(url)

try:
    from sshtunnel import SSHTunnelForwarder
    import pymysql
except (ImportError, ModuleNotFoundError):
    subprocess.run(['python', '-m', 'pip', 'install', '--upgrade','pymysql','sshtunnel'])
    from sshtunnel import SSHTunnelForwarder
    import pymysql
def create_ssh_tunnel(tunnel,host):
    if tunnel is None or not tunnel.is_active:
        try:
            tunnel = SSHTunnelForwarder(
                (f'{host}', 22),
                ssh_username='',
                ssh_password='',
                remote_bind_address=('localhost', 3306),
                local_bind_address=('0.0.0.0', 10022),
                set_keepalive=30
            )
            tunnel.start()
            print("SSH 터널 생성 완료")
        except Exception as e:
            print(f"SSH 터널 생성 오류: {e}")
            tunnel = None
    else:
        print("기존 SSH 터널을 재사용합니다.")
    return tunnel

def create_db_connection(tunnel,db_name):
    if tunnel is None:
        print("SSH 터널이 없습니다.")
        return None
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user='',
            password='',
            db=f'{db_name}',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f'{db_name} 데이터베이스 연결 완료')
        return connection
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None
    
def do_query(tunnel,connection,query):
    if not tunnel:
        return None
    if connection is None:
        print("데이터베이스 연결이 없습니다.")
        return None
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            cursor.fetchall()
            return True
    except Exception as e:
        print(f"데이터베이스 쿼리 오류: {e}")
        return None
    finally:
        connection.commit()
        connection.close()
    
try:
    import selenium
    sel_version=selenium.__version__
    if sel_version != '3.141.0':
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'selenium==3.141.0'])
    from scode.selenium import *
    try:
        from scode.util import *
    except ImportError:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'scode'])
        from scode.util import *
except:
    from scode.selenium import *
    try:
        from scode.util import *
    except ImportError:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'scode'])
        from scode.util import *

def send_monitoring_signal(program_id):
    url = f"http://monitoring.inp.kr/work_pg_monitor/update.php?program_id={program_id}"
    try:
        response = requests.get(f'{url}', verify=False)
        if response.status_code == 200:
            a=1  # 서버의 응답 내용을 출력
        else:
            a=2
    except requests.RequestException as e:
        print(f"정상 동작 신호 전송 중 오류 발생: {e}")