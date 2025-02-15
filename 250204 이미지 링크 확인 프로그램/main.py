import warnings
warnings.simplefilter("ignore", UserWarning)
import subprocess
import requests
import ctypes
import sys
import re
import os
from datetime import datetime
import time


from bs4 import BeautifulSoup
try:
    from halo import Halo
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'halo'])
    from halo import Halo
import configparser
import json
try:
    import urllib.parse
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'urllib'])
    import urllib.parse

def config_read():
    config = configparser.ConfigParser()
    try:config.read('config.ini', encoding='cp949')
    except:config.read('config.ini', encoding='utf-8')
    return config
# ===============================================================================
#                            데피니션
# ===============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
input_path=os.path.join(current_dir, 'input.txt')
input_lst=open(input_path,'r').read().splitlines()
output_path=os.path.join(current_dir, 'output.txt')
error_path=os.path.join(current_dir, 'error.txt')
open(error_path,'w').close()
pattern = r'<img[^>]+src=["\'](.*?)["\']'
# ===============================================================================
#                            런
# ===============================================================================
def run():
    print('프로그램 실행')
    with open(output_path, 'w') as f:
        for idx,input_str in enumerate(input_lst,start=1):
            try:
                if input_str == '': continue
                url=re.search(pattern, input_str).group(1)
                print(f'[{idx}/{len(input_lst)}] {url}')
                response = requests.get(url, allow_redirects=False)
                if response.status_code == 200:
                    print('  ㄴ 정상')
                    f.write(f'{url}\t정상\n')
                else:
                    print('  ㄴ 오류')
                    f.write(f'{url}\t오류\n')
            except Exception as e:
                print('  ㄴ 오류 발생')
                f.write(f'{url}\t오류\n')
                with open(error_path, 'a') as ef:
                    ef.write(f'{url}\t{e}\n')
                print(f'  ㄴ {e}')
            time.sleep(.5)
# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '250204'
__latest_update_date__ = '250204'
__version__ = 'v1.0.0'
__title__ = '이미지 태그 확인 프로그램'
__desc__ = '이미지 태그의 src 링크로 들어가 정상인지 확인하는 프로그램'
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

if __name__ == "__main__":
    ctypes.windll.kernel32.SetConsoleTitleW(f'{__title__} {__version__} ({__latest_update_date__})')
    sys.stdout.write(f'{__title__} {__version__} ({__latest_update_date__})\n')
    sys.stdout.write(f'제작자: {__author__}\n')
    sys.stdout.write(f'최종 수정자: {__latest_editor__}\n')
    sys.stdout.write(f'{short_version_log if short_version_log.strip() else full_version_log}\n')

    run()