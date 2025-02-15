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
import random
import shutil
import string
from PIL import Image,ImageDraw, ImageFont

def config_read(path):
    config = configparser.ConfigParser()
    try:config.read(f'{path}', encoding='cp949')
    except:config.read(f'{path}', encoding='utf-8')
    return config
# ===============================================================================
#                            데피니션
# ===============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
folders = [item for item in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, item))]
font_dir=os.path.join(current_dir,'font')
output_dir=os.path.join(current_dir,'output')
os.makedirs(output_dir,exist_ok=True)
def add_text_to_field(image, text, font_path, fill, field_box=None, font_size=None, line_spacing=10):
    """
    텍스트를 왼쪽 정렬로 지정된 위치에 출력, 박스 크기를 넘어가도 출력하며, 자동 줄바꿈 없음
    :param image: PIL.Image 객체
    :param text: 삽입할 텍스트
    :param font_path: 폰트 경로
    :param fill: 텍스트 색상 (기본값: 검정색)
    :param field_box: (left, top, right, bottom) 튜플, 입력 칸의 좌표
    :param font_size: 폰트 크기
    :param line_spacing: 줄 간격 (기본값: 10)
    """
    draw = ImageDraw.Draw(image)

    if field_box is None:
        raise ValueError("field_box 좌표를 설정해야 합니다!")

    left, top, _, _ = field_box

    # 폰트 크기 설정
    if font_size is None:
        raise ValueError("font_size를 지정해야 합니다.")
    font = ImageFont.truetype(font_path, font_size)

    # 텍스트 렌더링 (자동 줄바꿈 없음)
    y_offset = top
    for line in text.split("\n"):  # 기존 줄바꿈 (\n)만 처리
        draw.text((left, y_offset), line, fill=fill, font=font)
        text_height = draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]
        y_offset += text_height + line_spacing

    return image




# ===============================================================================
#                            런
# ===============================================================================
def run():
    print('프로그램 실행')
    for folder in folders:
        print('  '*50,end='\r')
        print(f'{folder} 내용 처리중....',end='\r')
        if 'font' in folder or 'output' in folder: continue
        folder_path=os.path.join(current_dir,folder)
        input_files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)) and file.endswith('.txt')]
        png_files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)) and file.endswith('.png')]
        image_path=os.path.join(folder_path,png_files[0])
        output_path=os.path.join(output_dir,png_files[0])
        setting_path=os.path.join(folder_path,'setting.ini')
        setting=config_read(setting_path)
        image_img = Image.open(image_path)
        
        for input_file in input_files:
            input_path=os.path.join(folder,input_file)
            font_path=os.path.join(font_dir,setting[input_file]['font'])
            font_size=int(setting[input_file]['size'])
            color=setting[input_file]['color']
            input_field_box = (int(setting[input_file]['left']), int(setting[input_file]['top']), int(setting[input_file]['right']), int(setting[input_file]['bottom']))
            text=open(input_path,'r').read()
            image_img=add_text_to_field(image_img,text,font_path,color,input_field_box,font_size)
        image_img.save(output_path)
        time.sleep(1)
        print('  '*50,end='\r')
        print(f'{folder} 내용 처리완료....',end='\r')
    print('  '*50,end='\r')
    print('프로그램 종료')
# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '250106'
__latest_update_date__ = '250106'
__version__ = 'v1.00'
__title__ = '텔레몬 카드뉴스 수정 프로그램'
__desc__ = '텔레몬 카드뉴스 수정 프로그램'
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