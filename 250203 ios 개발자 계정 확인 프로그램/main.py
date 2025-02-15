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
import requests
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




# ===============================================================================
#                               Definitions
# ===============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
config_path=os.path.join(current_dir,'config.ini')
config = configparser.ConfigParser()
config.read(config_path)
wait_time=int(config['setting']['타임아웃'])
repeat_time=config['setting']['실행시간'].split(',')
NATE_API_URL = config['setting']['NATE_API_URL']
input_path=os.path.join(current_dir,'input.txt')
output_dir=os.path.join(current_dir,'output')
os.makedirs(output_dir,exist_ok=True)

def nateon_noti(msg):

    payload = {"text": msg}
    res = requests.post(NATE_API_URL, json=payload)

    #print(f"res.status_code: {res.status_code}")

    if res.status_code != 200:
        log_msg = f"네이트온 알림 전송 오류\t{msg}"

    else:
        log_msg = f"네이트온 알림 전송\t{msg}"

    return log_msg
        



def logging_err(error : Exception, msg=''):
    err_class = type(error).__name__
    err_msg = error

    logging.error(f'{err_class}	{err_msg}	{msg}',exc_info=True)



def run():
    print('프로그램 실행')
    run_time=datetime.now().strftime('%Y%m%d %H-%M')
    output_path=os.path.join(output_dir,f'{run_time}.txt')
    input_lst=open(input_path,'r').read().splitlines()
    for input_str in input_lst:
        try:
            driver.quit()
        except:
            pass
        mail,url=input_str.split('\t')
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--log-level=3')  # 로그 레벨 설정
        options.add_argument("--incognito")  # 시크릿 모드
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--ignore-certificate-errors")  # 인증서 오류 무시

        driver = load_driver(options)
        driver.get(url)
        wait_try=wait_time//5
        suc_flag=False
        for i in range(wait_try):
            try:
                driver.find_element(By.CLASS_NAME,'page-header__title')
                suc_flag=True
                break
            except:
                time.sleep(5)
        if not suc_flag:
            msg=f'{mail} : 페이지 접속 안됨'
            with open(output_path,'a') as f:
                f.write(f'{msg}\n')
            
            if '오류' in nateon_noti(msg):
                print('네이트온 알림 전송 실패')
                with open(output_path,'a') as f:
                    f.write(f'네이트온 알림 전송 실패\n')
        else:
            msg=f'{mail} : 페이지 로드 성공'
            with open(output_path,'a') as f:
                f.write(f'{msg}\n')

        driver.quit()
        
        


# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '250203'
__latest_update_date__ = '250203'
__version__ = '1.0.0'
__title__ = 'ios 개발자 계정 확인 프로그램'
__desc__ = '주소 접속 후 로딩 되는지 확인'
__changeLog__ = {
    'v1.00': ['Initial Release.'],

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

    # logging 정의
    error_file_path = 'error.txt'
    logging.basicConfig(
        filename=error_file_path,
        level=logging.ERROR,    # 기록하는 실행 단계 설정
        format='\n%(levelname)s:%(name)s:%(asctime)s:%(lineno)d:%(message)s\n', # 기록 하는 형식 설정
        datefmt='%Y-%m-%d %H:%M:%S' # 기록시 현재 날짜 설정
    )
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
        
    