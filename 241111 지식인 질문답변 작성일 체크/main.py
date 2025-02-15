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
try:
    from scode.util import *
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'scode'])
    from scode.util import *
try:
    import gspread as gs
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'gspread'])
    import gspread as gs
from bs4 import BeautifulSoup
try:
    from halo import Halo
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'halo'])
    from halo import Halo
import configparser

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
    import pandas as pd
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pandas'])
    import pandas as pd
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
input_path = os.path.join(current_dir,'input.txt')
output_path = os.path.join(current_dir,'output.txt')
open(output_path,'w').close()
input_str=open(input_path,'r').read().splitlines()
input_lst=[]
for idx, str in enumerate(input_str):
    url=str.split('\t')[0]
    ans=int(str.split('\t')[1])
    tmp_dict={}
    tmp_dict[url]=ans
    input_lst.append(tmp_dict)

# ===============================================================================
#                            런
# ===============================================================================
def run():

    for lst in input_lst:
        for link, ans in lst.items():
            try:
                docId = link.split('docId=')[-1]
                dirId = link.split('dirId=')[-1].split('&')[0]
            except AttributeError:
                continue
            kin_url = f'https://kin.naver.com/qna/detail.naver?d1id=6&dirId={dirId}&docId={docId}'
            ajax_link = f'https://kin.naver.com/ajax/detail/answerList.naver?dirId={dirId}&docId={docId}&answerSortType=DEFAULT&answerFilterType=ALL&answerViewType=DETAIL&page=1&count=30'

            respons_kin_url=requests.get(kin_url)

            if respons_kin_url.status_code != 200:
                print(f'{kin_url} 접속 불가 - {respons_kin_url.status_code}')
                break
            html = respons_kin_url.text
            soup = BeautifulSoup(html, 'html.parser')
            span_tags=soup.find_all('span','blind')
            date = None
            answer_date=None
            for tag in span_tags:
                if '작성일' in tag.get_text():
                    date = tag.find_parent('span').get_text().replace('작성일', '').strip()
                    print(f'질문 작성일 {date}')
                    break 
            if date==None:
                print(f'{kin_url} - 질문 삭제')
                date='질문 삭제'
            else:
                
                detail_response=requests.get(ajax_link)
                if detail_response.status_code != 200:
                    print(f'{ajax_link} 접속 불가 - {detail_response.status_code}')
                res_json = detail_response.json()
                detailAnswerList = res_json.get('detailAnswerList', [])
                if detailAnswerList:
                    for answer in detailAnswerList:
                        if answer['answerNo']==ans:
                            try:
                                if answer['deleted']==True:
                                    answer_date='답변 삭제'
                                    break
                            except:
                                pass
                            print(f"답변 작성일 {answer['formattedModifyTime']}")
                            answer_date=answer['formattedModifyTime']
                            break
                        
                else:
                    print(f'{kin_url} - 답변 삭제')
            output_str=''
            if date:
                output_str+=date
                if answer_date:
                    output_str+='\t'+answer_date
                with open(output_path,'a') as f:
                    f.write(f'{output_str}\n')

# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '241111'
__latest_update_date__ = '241111'
__version__ = 'v1.00'
__title__ = '지식인 질문 답변 작성일 체크 프로그램 - 나태환'
__desc__ = '지식인 질문 답변 작성일 체크 프로그램 - 나태환'
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