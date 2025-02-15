import warnings
warnings.simplefilter('ignore', UserWarning)
import os
import sys
import re
import time
import ctypes
import subprocess
import configparser
import logging
from datetime import datetime

try:
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'beautifulsoup4'])
    from bs4 import BeautifulSoup
try:
    from sshtunnel import SSHTunnelForwarder
    import pymysql
except (ImportError, ModuleNotFoundError):
    subprocess.run(['python', '-m', 'pip', 'install', '--upgrade','pymysql','sshtunnel'])
    from sshtunnel import SSHTunnelForwarder
    import pymysql
try:
    import schedule
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'schedule'])
    import schedule
try:
    import urllib.parse
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'urllib'])
    import urllib.parse
try:
    from halo import Halo
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'halo'])
    from halo import Halo
try:
    import gspread as gs
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'gspread'])
    import gspread as gs

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


import configparser
# ===============================================================================
#                               Definitions
# ===============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
input_path=os.path.join(current_dir,'input.txt')
input_lst=open(input_path,'r').read().splitlines()
error_file_path = 'error.txt'
config_path=os.path.join(current_dir,'config.ini')
config = configparser.ConfigParser()
config.read(config_path)
wait_time=int(config['setting']['타임아웃'])
repeat_time=config['setting']['실행시간'].split(',')
NATE_API_URL = config['setting']['NATE_API_URL']
open(error_file_path, 'w').close()
outpur_dir=os.path.join(current_dir,'output')
if not os.path.exists(outpur_dir):
    os.makedirs(outpur_dir)
tunnel=None
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
        return connection
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None

def nateon_noti(msg):

    payload = {"text": msg}
    res = requests.post(NATE_API_URL, json=payload)

    #print(f"res.status_code: {res.status_code}")

    if res.status_code != 200:
        log_msg = f"네이트온 알림 전송 오류\t{msg}"

    else:
        log_msg = f"네이트온 알림 전송\t{msg}"

    return log_msg
        

def run():
    global tunnel
    for input_str in input_lst:
        run_time = datetime.now().strftime(DEFAULT_DATETIME_FORMAT)
        start_time = datetime.now().strftime(DEFAULT_DATETIME_FORMAT)
        try:
            nick_name,id,pw=input_str.split('\t')
        except:
            print('입력값이 잘못되었습니다.')
            continue
        id_output_path=os.path.join(outpur_dir,f'{datetime.now().strftime(DEFAULT_DATE_FORMAT)}_{id}.txt')
        try:
            driver.quit()
        except:
            pass

        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--log-level=3')  # 로그 레벨 설정
        options.add_argument('--incognito')  # 시크릿 모드
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시

        driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
        url='https://account.proton.me/mail'
        driver.get(url)
        wait_try=wait_time//5
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[id="username"]')))
        driver.find_element(By.CSS_SELECTOR,'input[id="username"]').send_keys(id)
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR,'input[id="password"]').send_keys(pw)
        time.sleep(1)
        suc_flag=False
        for i in range(wait_try):
            try:
                driver.find_element(By.CSS_SELECTOR,'button[type="submit"]').click()
                suc_flag=True
                break
            except:
                time.sleep(5)
                continue
        if not suc_flag:
            print('로그인 창 타임아웃')
            msg_str=f'{run_time}\t{id}\t로그인 창 타임아웃\n'
            with open(error_file_path, 'a') as f:
                f.write(f'{msg_str}')
            continue

        try:
            wait_try=wait_time//5
            close_btn=None
            for i in range(wait_try):
                close_btns=driver.find_elements(By.CLASS_NAME,'button-for-icon')
                if len(close_btns)>=2:
                    close_btn=close_btns[-1]
                    break
                time.sleep(5)
            try:
                if close_btn != None and close_btn.text != '사이드 패널 열기':
                    print('로그인 실패')
                    msg_str=f'{run_time}\t{id}\t계정정보 확인\n'
                    with open(error_file_path, 'a') as f:
                        f.write(f'{run_time}\t{id}\t계정정보 확인\n')
                    with open(error_file_path, 'a') as f:
                        f.write(f'{nateon_noti(f"{msg_str}")}\n')
                    continue
            except:
                pass
            time.sleep(1)
        except:
            pass
        #print(driver.current_url)
        wait_try=wait_time//5
        for i in range(wait_try):
            if 'inbox' in driver.current_url:
                break
            time.sleep(5)

        if 'inbox' not in driver.current_url:
            print('로그인 실패')
            msg_str=f'{run_time}\t{id}\t로그인이후 메일 접속 타임아웃\n'
            with open(error_file_path, 'a') as f:
                f.write(f'{run_time}\t{id}\t로그인이후 메일 접속 타임아웃\n')
            with open(error_file_path, 'a') as f:
                f.write(f'{nateon_noti(f"{msg_str}")}\n')
            continue

        print(f'{id} 로그인 성공')
        time.sleep(1)
        small_buttons=driver.find_elements(By.CLASS_NAME,'button-ghost-weak')
        for small_button in small_buttons:
            sorting=None
            try:
                sorting=small_button.get_attribute('data-testid')
            except:
                continue
            if sorting:
                if 'unread' in sorting:
                    try:
                        small_button.click()
                    except:
                        try:
                            find_flag=False
                            underline_buttons=None
                            underline_buttons=driver.find_elements(By.CLASS_NAME,'button-underline')
                            if underline_buttons:
                                for underline_button in underline_buttons:
                                    if '나중에' in underline_button.text:
                                        underline_button.click()
                                        time.sleep(1)
                                        small_button.click()
                                        find_flag=True
                                        break
                            if not find_flag:
                                with open(error_file_path, 'a') as f:
                                    f.write(f'{run_time}\t{id}\t읽지 않은 메일 클릭 실패\n')
                                continue
                        except:
                            with open(error_file_path, 'a') as f:
                                f.write(f'{run_time}\t{id}\t읽지 않은 메일 클릭 실패\n')
                            continue
                    try:
                        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'item-container')))
                    except:
                        print('읽지 않은 메일 없습니다.')
                        with open(error_file_path, 'a') as f:
                            f.write(f'{run_time}\t{id}\t읽지 않은 메일 없습니다.\n')
                        break
                    time.sleep(5)
                    break
        inline_blocks=None
        inline_blocks=driver.find_elements(By.CLASS_NAME,'item-container')
        if inline_blocks==[]:
            print('읽지 않은 메일이 없습니다.')
            with open(error_file_path, 'a') as f:
                f.write(f'{run_time}\t{id}\t읽지 않은 메일이 없습니다.\n')
            with open(id_output_path, 'a') as f:
                f.write(f'읽지 않은 메일이 없습니다.\n')
            continue
        for inline_block in inline_blocks:
            try:
                inline_block.click()
            except:
                with open(error_file_path, 'a') as f:
                    f.write(f'{run_time}\t{id}\t메일 클릭 실패\n')
                continue
            time.sleep(5)
            try:
                email=driver.find_element(By.CLASS_NAME,'message-recipient-item-address').text.replace('<','').replace('>','')
                sr_only=driver.find_element(By.CLASS_NAME,'message-header-metas-container').text.split('\n')[-1]
                title=driver.find_element(By.CLASS_NAME,'message-conversation-summary-header').text.replace('\n','')
                message_iframe=driver.find_element(By.TAG_NAME,'iframe')
                driver.switch_to.frame(message_iframe)
                message_content=driver.find_element(By.TAG_NAME,'body').text
            except:
                with open(error_file_path, 'a') as f:
                    f.write(f'{run_time}\t{id}\t메일 세부 내용 수집 실패\n')
                driver.back()
                time.sleep(5)
                continue

            print(f'보낸 이메일: {email}\n받은 이메일: {id}\n전송 시간: {sr_only}\n제목: {title}\n내용: {message_content}')
            write_str=f'보낸 이메일: {email}\n받은 이메일: {id}\n전송 시간: {sr_only}\n제목: {title}\n내용: {message_content}\n'
            write_str=write_str.encode('cp949','ignore').decode('cp949')
            with open(id_output_path, 'a') as f:
                f.write('==='*20+'\n')
                f.write(write_str)
                f.write('==='*20+'\n')
            driver.back()
            time.sleep(5)
            tunnel=create_ssh_tunnel(tunnel,'')
            connection=create_db_connection(tunnel,'')
            if not tunnel:
                print("SSH 터널 생성 실패")
                with open(error_file_path, 'a') as f:
                    f.write(f'{run_time}\t{id}\tSSH 터널 생성 실패\n')
                continue
            if connection is None:
                print("데이터베이스 연결이 없습니다.")
                with open(error_file_path, 'a') as f:
                    f.write(f'{run_time}\t{id}\t데이터베이스 연결 실패\n')
                continue
            try:
                with connection.cursor() as cursor:
                    year=sr_only.split('년')[0]
                    month=sr_only.split('년')[1].split('월')[0].replace(' ','')
                    day=sr_only.split('년')[1].split('월')[1].split('일')[0].replace(' ','')
                    time_=sr_only.split('년')[1].split('월')[1].split('일')[-1].split(' ')[-1].replace(' ','')
                    sr_only=f'{year}-{month}-{day} {time_}'
                    select_query = """SELECT * FROM `` WHERE `mail_id`=%s AND `mail_from`=%s AND `mail_to`=%s AND `subject`=%s AND `mail_date`=%s AND `content_text`=%s;"""
                    cursor.execute(select_query, (id, nick_name, email, title, sr_only, message_content))
                    result=cursor.fetchall()
                    if result:
                        print('중복된 데이터 임으로 저장하지 않습니다.')
                    else:
                        query = "INSERT INTO `` (`mail_id`, `mail_from`, `mail_to`, `subject`, `mail_date`, `content_text`) VALUES (%s, %s, %s, %s, %s, %s);"
                        cursor.execute(query, (id, nick_name, email, title, sr_only, message_content))
                        connection.commit()
                connection.close()
                print('데이터베이스 동작 성공')
            except Exception as e:
                print(f"데이터베이스 동작 오류: {e}")
                with open(error_file_path, 'a') as f:
                    f.write(f'{run_time}\t{id}\t데이터베이스 동작 실패\n')

        end_time = datetime.now().strftime(DEFAULT_DATETIME_FORMAT)
        print(f'{id}시작시간: {start_time}\n종료시간: {end_time}')


    
# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '250124'
__latest_update_date__ = '250131'
__version__ = '1.1.0'
__title__ = '이메일 크롤링 프로그램'
__desc__ = '이메일 크롤링 프로그램'
__changeLog__ = {
    'v1.0.0': ['Initial Release.'],
    'v1.0.1': ['쿼리 입력 오류 수정.'],
    'v1.1.0': ['로그인 오류 시 네이트온 메시지 발송 추가'],
    'v1.1.1': ['크롬 버전 고정'],

}
version_lst = list(__changeLog__.keys())

full_version_log = '\n'
short_version_log = '\n'

for ver in __changeLog__:
    full_version_log += f'{ver}\n' + '\n'.join(['    - ' + x for x in __changeLog__[ver]]) + '\n'

if len(version_lst) > 5:
    short_version_log += '.\n.\n.\n'
    short_version_log += f'{version_lst[-2]}\n' + '\n'.join(['    - ' + x for x in __changeLog__[version_lst[-2]]]) + '\n'
    short_version_log += f'{version_lst[-1]}\n' + '\n'.join(['    - ' + x for x in __changeLog__[version_lst[-1]]]) + '\n'

# ===============================================================================
#                                 Main Code
# ===============================================================================

if __name__ == '__main__':
    ctypes.windll.kernel32.SetConsoleTitleW(f'{__title__} {__version__} ({__latest_update_date__})')
    sys.stdout.write(f'{__title__} {__version__} ({__latest_update_date__})\n')
    sys.stdout.write(f'제작자: {__author__}\n')
    sys.stdout.write(f'최종 수정자: {__latest_editor__}\n')
    sys.stdout.write(f'{short_version_log if short_version_log.strip() else full_version_log}\n')

    run()

    while True:
        now_time=datetime.now().strftime('%H:%M')
        if now_time in repeat_time:
            os.system('cls')
            print(f'지정된 실행시간입니다. 실행중...')
            run()
        else:
            for i in range(60):
                print(f'{now_time} 대기중... {60-i}초',end='\r')
                time.sleep(1)
                print(' '*100,end='\r')
        
    