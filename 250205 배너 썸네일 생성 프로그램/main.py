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

try:
    import imageio
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'imageio'])
    import imageio
import numpy as np
try:
    import cv2
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'opencv-python'])
    import cv2

from PIL import ImageEnhance
def config_read():
    config = configparser.ConfigParser()
    try:config.read('config.ini', encoding='cp949')
    except:config.read('config.ini', encoding='utf-8')
    return config
# ===============================================================================
#                            데피니션
# ===============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
background_dir = os.path.join(current_dir, '배경')
temp_dir=r"C:\temp\banner_thumbnails"
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
output_dir=os.path.join(temp_dir,'output')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
config_path=os.path.join(current_dir,'config.ini')
def select_banner_1_moongu(category):
    print(' >> 배너문구 1 선택')
    moongu_path= os.path.join(current_dir, '배너문구1.txt')
    try:
        input_lst=open(moongu_path,'r',encoding='cp949').read().split('-')
    except:
        input_lst=open(moongu_path,'r',encoding='utf-8').read().split('-')
    for big_group in input_lst:
        if big_group=='':continue
        split_group= big_group.splitlines()
        if split_group[0].replace(' ','')==category:
            return random.choice(split_group[1:])
    
def select_thumb_sub_moongu(category):
    print(' >> 썸네일 서브 문구 선택')
    moongu_path= os.path.join(current_dir, '썸네일 서브문구.txt')
    try:
        input_lst=open(moongu_path,'r',encoding='cp949').read().split('-')
    except:
        input_lst=open(moongu_path,'r',encoding='utf-8').read().split('-')
    for big_group in input_lst:
        if big_group == '':
            continue
        split_group = [line for line in big_group.splitlines() if line.strip()]
        if split_group[0].replace(' ', '') == category:
            # 1번 인덱스부터 두 개씩 묶기
            pairs = [split_group[i:i+2] for i in range(1, len(split_group), 2)]
            # 묶인 것 중 하나 랜덤으로 선택
            
            random_pair = random.choice(pairs)
            result='\n'.join(random_pair)
            if len(result.splitlines())<2:
                return select_thumb_sub_moongu(category)
            return result

def select_gif_moongu(category):
    print(' >> GIF 문구 선택')
    moongu_path= os.path.join(current_dir, '배너문구3.txt')
    try:
        input_lst=open(moongu_path,'r',encoding='cp949').read().split('-')
    except:
        input_lst=open(moongu_path,'r',encoding='utf-8').read().split('-')
    common_group = input_lst[0]
    common_group = [line for line in common_group.splitlines() if line.strip()]
    for big_group in input_lst:
        if big_group == '':
            continue
        split_group = [line for line in big_group.splitlines() if line.strip()]
        
        split_group = split_group +common_group
        if split_group[0].replace(' ', '') == category:
            # 1번 인덱스부터 두 개씩 묶기
            pairs = [split_group[i:i+2] for i in range(1, len(split_group), 2)]
            # 묶인 것 중 하나 랜덤으로 선택
            
            random_pair = random.choice(pairs)
            result='\n'.join(random_pair)
            if len(result.splitlines())<2:
                return select_thumb_sub_moongu(category)
            return result

def select_one_line(path,category):
    print(f' >> {path}에서 한 줄 선택')
    moongu_path= os.path.join(current_dir, f'{path}.txt')
    try:
        input_lst=open(moongu_path,'r',encoding='cp949').read().splitlines()
    except:
        input_lst=open(moongu_path,'r',encoding='utf-8').read().splitlines()
    selected_line=random.choice(input_lst)
    if '#'in selected_line:
        return selected_line
    else:
        return selected_line.replace('oo',category.replace('보험',''))

def select_background(category):
    print(' >> 배경 선택')
    try:
        background_path = os.path.join(background_dir, category)
        background_lst = os.listdir(background_path)
    except:
        background_path = os.path.join(background_dir, category.replace('보험',''))
        background_lst = os.listdir(background_path)
    selected_backgrounds = random.sample(background_lst, min(7, len(background_lst)))

    return [os.path.join(background_path, bg) for bg in selected_backgrounds]


def select_one_file(dir):
    print(f' >> {dir}에서 파일 선택')
    dir=os.path.join(current_dir,dir)
    file_lst=os.listdir(dir)
    selected_file=random.choice(file_lst)
    return os.path.join(dir,selected_file)


def paste_image_top_left(base_img, overlay_img):
    """
    기존 이미지 위에 새로운 캔버스를 생성하고,
    상단 왼쪽에 다른 이미지를 붙인 후 기존 이미지를 아래에 배치하는 함수.
    overlay_img의 폭을 base_img의 폭에 맞춰 조정.
    :param base_img: 기존 이미지
    :param overlay_img: 상단 왼쪽에 붙일 이미지
    :return: 결합된 이미지
    """
    # 기존 이미지 크기 가져오기
    base_width, base_height = base_img.size

    # overlay_img의 폭을 base_img의 폭에 맞춰 조정
    overlay_width, overlay_height = overlay_img.size
    scale_factor = base_width / overlay_width
    new_overlay_height = int(overlay_height * scale_factor)
    resized_overlay_img = overlay_img.resize((base_width, new_overlay_height), Image.ANTIALIAS)

    # 새로운 캔버스 크기 계산 (폭은 동일, 높이는 조정된 overlay와 base 합산)
    new_height = base_height + new_overlay_height
    new_img = Image.new("RGBA", (base_width, new_height), (0, 0, 0, 0))  # 흰 배경

    # 상단 왼쪽에 resized_overlay_img 추가
    new_img.paste(resized_overlay_img, (0, 0), resized_overlay_img)

    # 아래쪽에 base_img 추가
    new_img.paste(base_img, (0, new_overlay_height), base_img)

    return new_img



def combine_img(img_file_1, img_file_2):
    source1_img_RGBA = img_file_1.convert('RGBA')
    source2_img_RGBA = img_file_2.convert('RGBA')

    result_image = Image.alpha_composite(source1_img_RGBA, source2_img_RGBA)

    return result_image


def load_config(file_path, section):
    """
    Config 파일에서 설정값 로드
    :param file_path: config 파일 경로
    :param section: 읽을 섹션 이름
    :return: 섹션의 설정값 딕셔너리
    """
    config = configparser.ConfigParser()
    config.read(file_path)
    if section not in config:
        raise ValueError(f"'{section}' 섹션이 config 파일에 없습니다.")
    return {key: int(value) for key, value in config[section].items()}



def add_text_to_field(image, text, font_path, fill='black', field_box=None, line_spacing=10, char_spacing=0, split_mode=" "):
    """
    입력 칸(field_box)에 텍스트를 자동으로 배치하고, 필요하면 줄바꿈 처리하며 자간과 중앙 정렬 지원
    :param image: PIL.Image 객체
    :param text: 삽입할 텍스트
    :param font_path: 폰트 파일 경로 (예: 'arial.ttf')
    :param fill: 텍스트 색상
    :param field_box: (left, top, right, bottom) 튜플, 입력 칸의 좌표
    :param line_spacing: 줄 간격 (기본값: 10)
    :param char_spacing: 글자 간격 (기본값: 0)
    :param split_mode: 텍스트 줄바꿈 기준 (" " 또는 "\n", 기본값: " ")
    """
    draw = ImageDraw.Draw(image)

    if field_box is None:
        raise ValueError("field_box 좌표를 설정해야 합니다!")

    left, top, right, bottom = field_box
    field_width = right - left
    field_height = bottom - top

    # 폰트 크기 초기화
    font_size = 10
    font = ImageFont.truetype(font_path, font_size)

    # 텍스트 줄바꿈 기준에 따라 나누기
    lines = text.split(split_mode)

    # 폰트 크기 자동 조정
    while True:
        max_line_width = max(
            [sum([font.getbbox(char)[2] - font.getbbox(char)[0] + char_spacing for char in line]) - char_spacing for line in lines]
        )
        total_text_height = sum(
            [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
        ) + line_spacing * (len(lines) - 1)
        if max_line_width <0:
            font_size=5
            break
        if max_line_width > field_width or total_text_height > field_height:
            break
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)

    # 최종 폰트 크기 설정 (넘치기 전 단계로)
    font_size -= 1
    font = ImageFont.truetype(font_path, font_size)

    # 텍스트 삽입 위치 계산
    total_text_height = sum(
        [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
    ) + line_spacing * (len(lines) - 1)
    y = top + (field_height - total_text_height) / 2  

    for line in lines:
        total_line_width = sum(
            [font.getbbox(char)[2] - font.getbbox(char)[0] + char_spacing for char in line]
        ) - char_spacing
        x = left + (field_width - total_line_width) / 2  
        
        for char in line:
            bbox = font.getbbox(char)
            char_width = bbox[2] - bbox[0]
            draw.text((x, y), char, fill=fill, font=font)
            x += char_width + char_spacing  # 글자 간격 적용
        y += font.getbbox(line)[3] - font.getbbox(line)[1] + line_spacing

    return image


def add_click_text_to_field(image, text, font_path, default_fill, click_fill, field_box=None, line_spacing=10, char_spacing=0, split_mode=" "):
    """
    배너문구3 전용 함수 - "CLICK!" 부분만 색상 변경하여 렌더링
    :param image: PIL.Image 객체
    :param text: 삽입할 텍스트
    :param font_path: 폰트 파일 경로
    :param default_fill: 기본 텍스트 색상
    :param click_fill: "CLICK!" 색상
    :param field_box: (left, top, right, bottom) 튜플, 입력 칸의 좌표
    :param line_spacing: 줄 간격
    :param char_spacing: 글자 간격
    :param split_mode: 텍스트 줄바꿈 기준
    """
    draw = ImageDraw.Draw(image)

    if field_box is None:
        raise ValueError("field_box 좌표를 설정해야 합니다!")

    left, top, right, bottom = field_box
    field_width = right - left
    field_height = bottom - top

    # 폰트 크기 초기화
    font_size = 10
    font = ImageFont.truetype(font_path, font_size)

    # 텍스트 줄바꿈 기준에 따라 나누기
    lines = text.split(split_mode)

    # 폰트 크기 자동 조정
    while True:
        max_line_width = max(
            [sum([font.getbbox(char)[2] - font.getbbox(char)[0] + char_spacing for char in line]) - char_spacing for line in lines]
        )
        total_text_height = sum(
            [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
        ) + line_spacing * (len(lines) - 1)

        if max_line_width > field_width or total_text_height > field_height:
            break
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)

    # 최종 폰트 크기 설정 (넘치기 전 단계로)
    font_size -= 1
    font = ImageFont.truetype(font_path, font_size)

    # 텍스트 삽입 위치 계산
    total_text_height = sum(
        [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
    ) + line_spacing * (len(lines) - 1)
    y = top + (field_height - total_text_height) / 2  # 세로 중앙 정렬

    # 텍스트 렌더링
    for line in lines:
        x = left + (field_width - sum([font.getbbox(char)[2] - font.getbbox(char)[0] + char_spacing for char in line]) + char_spacing) / 2  # 가로 중앙 정렬
        
        words = line.split("CLICK!")
        for i, word in enumerate(words):
            # 일반 텍스트
            for char in word:
                bbox = font.getbbox(char)
                char_width = bbox[2] - bbox[0]
                draw.text((x, y), char, fill=default_fill, font=font)
                x += char_width + char_spacing

            # "CLICK!" 부분 색상 변경
            if i < len(words) - 1:
                for char in "CLICK!":
                    bbox = font.getbbox(char)
                    char_width = bbox[2] - bbox[0]
                    draw.text((x, y), char, fill=click_fill, font=font)
                    x += char_width + char_spacing

        y += font.getbbox(line)[3] - font.getbbox(line)[1] + line_spacing  # 줄 간격 적용

    return image


def add_click_text_to_image(image, text, font_path, default_fill, click_fill, field_box=None, line_spacing=10, char_spacing=0, split_mode=" "):
    """
    일반 이미지에 CLICK 문구를 특정 색으로 칠하는 함수
    :param image: PIL.Image 객체
    :param text: 삽입할 텍스트
    :param font_path: 폰트 파일 경로
    :param default_fill: 일반 텍스트 색상
    :param click_fill: "CLICK!" 부분 색상
    :param field_box: (left, top, right, bottom) 입력 칸 좌표
    :param line_spacing: 줄 간격
    :param char_spacing: 글자 간격
    :param split_mode: 텍스트 줄바꿈 기준
    """
    draw = ImageDraw.Draw(image)

    if field_box is None:
        raise ValueError("field_box 좌표를 설정해야 합니다!")

    left, top, right, bottom = field_box
    field_width = right - left
    field_height = bottom - top

    # 폰트 초기화
    font_size = 10
    font = ImageFont.truetype(font_path, font_size)

    # 텍스트 줄바꿈 기준에 따라 나누기
    lines = text.split(split_mode)

    # 폰트 크기 자동 조정
    while True:
        max_line_width = max(
            [sum([font.getbbox(char)[2] - font.getbbox(char)[0] + char_spacing for char in line]) - char_spacing for line in lines]
        )
        total_text_height = sum(
            [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
        ) + line_spacing * (len(lines) - 1)

        if max_line_width > field_width or total_text_height > field_height:
            break
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)

    # 최종 폰트 크기 설정 (넘치기 전 단계로)
    font_size -= 1
    font = ImageFont.truetype(font_path, font_size)

    # 텍스트 삽입 위치 계산
    total_text_height = sum(
        [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
    ) + line_spacing * (len(lines) - 1)
    y = top + (field_height - total_text_height) / 2  # 세로 중앙 정렬

    # 텍스트 삽입
    for line in lines:
        x = left + (field_width - sum([font.getbbox(char)[2] - font.getbbox(char)[0] + char_spacing for char in line]) + char_spacing) / 2  # 가로 중앙 정렬

        # "CLICK!" 또는 "Click" 처리
        if "CLICK!" in line:
            words = line.split("CLICK!")
            click_word = "CLICK!"
        elif "Click" in line:
            words = line.split("Click")
            click_word = "Click"
        else:
            words = [line]
            click_word = None

        for i, word in enumerate(words):
            # 일반 텍스트
            for char in word:
                bbox = font.getbbox(char)
                char_width = bbox[2] - bbox[0]
                draw.text((x, y), char, fill=default_fill, font=font)
                x += char_width + char_spacing

            # "CLICK!" 또는 "Click" 색상 변경
            if click_word and i < len(words) - 1:
                for char in click_word:
                    bbox = font.getbbox(char)
                    char_width = bbox[2] - bbox[0]
                    draw.text((x, y), char, fill=click_fill, font=font)
                    x += char_width + char_spacing

        y += font.getbbox(line)[3] - font.getbbox(line)[1] + line_spacing  # 줄 간격 적용

    return image


 # 1.png 처리 함수
def process_1_png(image_path, filter_path, thumb_main_moongu, thumb_sub_moongu, color, output_file_name, config_path, main_font_path, sub_font_path):
    """
    Config 파일과 add_text_to_field를 사용해 1.png에 텍스트를 배치
    """
    from PIL import Image

    # Config 파일 로드
    config = configparser.ConfigParser()
    config.read(config_path)

    sub_box = (
        config.getint("1.png", "sub_left"),
        config.getint("1.png", "sub_top"),
        config.getint("1.png", "sub_right"),
        config.getint("1.png", "sub_bottom")
    )

    main_box = (
        config.getint("1.png", "main_left"),
        config.getint("1.png", "main_top"),
        config.getint("1.png", "main_right"),
        config.getint("1.png", "main_bottom")
    )
    sub_line_spacing = config.getint("1.png", "sub_line_spacing")
    main_line_spacing = config.getint("1.png", "main_line_spacing")
    sub_char_spacing = config.getint("1.png", "sub_char_spacing")
    main_char_spacing = config.getint("1.png", "main_char_spacing")
    # 이미지 로드 및 크기 조정
    image = Image.open(image_path).convert("RGBA")
    if image.size != (1080, 1080):
        image = image.resize((1080, 1080), Image.Resampling.LANCZOS)

    # 필터 적용
    if filter_path:
        filter_image = Image.open(filter_path).convert("RGBA")
        if filter_image.size != (1080, 1080):
            filter_image = filter_image.resize((1080, 1080), Image.Resampling.LANCZOS)
        image = Image.alpha_composite(image, filter_image)

    # 서브 문구 삽입
    image = add_text_to_field(
        image=image,
        text=thumb_sub_moongu,
        font_path=sub_font_path,
        fill=color,
        field_box=sub_box,
        line_spacing=sub_line_spacing,  # 서브 문구 줄 간격
        char_spacing=sub_char_spacing,
        split_mode="\n"
    )

    # 메인 문구 삽입
    image = add_text_to_field(
        image=image,
        text=thumb_main_moongu,
        font_path=main_font_path,
        fill="white",
        field_box=main_box,
        line_spacing=main_line_spacing,  # 메인 문구 줄 간격 (늘림)
        char_spacing=main_char_spacing,
        split_mode=" "  # 띄어쓰기 기준 줄바꿈
    )

    # 이미지 저장
    image.save(output_file_name)
    print(f' >> {output_file_name} 저장 완료')


def process_gif(image_path, filter_path, banner_1, banner_2, banner_3, color, line_path, output_file_name, config_path, main_font_path, sub_font_path, click_font_path):
    """
    Config 파일과 add_text_to_field를 사용해 GIF를 생성하는 함수
    """
    print(f' >> GIF 생성 중: {output_file_name}')
    
    # Config 파일 로드
    config = configparser.ConfigParser()
    config.read(config_path)

    # 텍스트 배치 영역 가져오기
    banner_1_box = (
        config.getint("GIF", "banner_1_left"),
        config.getint("GIF", "banner_1_top"),
        config.getint("GIF", "banner_1_right"),
        config.getint("GIF", "banner_1_bottom")
    )
    banner_2_box = (
        config.getint("GIF", "banner_2_left"),
        config.getint("GIF", "banner_2_top"),
        config.getint("GIF", "banner_2_right"),
        config.getint("GIF", "banner_2_bottom")
    )
    banner_3_box = (
        config.getint("GIF", "banner_3_left"),
        config.getint("GIF", "banner_3_top"),
        config.getint("GIF", "banner_3_right"),
        config.getint("GIF", "banner_3_bottom")
    )

    # 줄 간격 및 글자 간격 설정
    banner_1_line_spacing = config.getint("GIF", "banner_1_line_spacing")
    banner_2_line_spacing = config.getint("GIF", "banner_2_line_spacing")
    banner_3_line_spacing = config.getint("GIF", "banner_3_line_spacing")

    banner_1_char_spacing = config.getint("GIF", "banner_1_char_spacing")
    banner_2_char_spacing = config.getint("GIF", "banner_2_char_spacing")
    banner_3_char_spacing = config.getint("GIF", "banner_3_char_spacing")

    # 이미지 로드 및 크기 조정
    base_image = Image.open(image_path).convert("RGBA")
    if base_image.size != (1080, 1080):
        base_image = base_image.resize((1080, 1080), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Brightness(base_image)
    base_image = enhancer.enhance(0.5)
    # dark_overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 200))  # 반투명 검정색 (alpha=128)
    # base_image = Image.alpha_composite(base_image, dark_overlay)
    # 필터 적용
    # if filter_path:
    #     filter_image = Image.open(filter_path).convert("RGBA")
    #     if filter_image.size != (1080, 1080):
    #         filter_image = filter_image.resize((1080, 1080), Image.Resampling.LANCZOS)
    #     base_image = Image.alpha_composite(base_image, filter_image)
    # 선 이미지 로드
    line_image = Image.open(line_path).convert("RGBA")
    if line_image.size != (1080, 1080):
        line_image = line_image.resize((1080, 1080), Image.Resampling.LANCZOS)
    # 선 파일 로드 및 크기 조정

    # GIF 프레임 리스트
    frames = []
    insulabs_moongu_path=os.path.join(current_dir,'insulabs_moongu.png')
    insulabs_moongu_image=Image.open(insulabs_moongu_path).convert("RGBA")
    if insulabs_moongu_image.width < 1080:
        new_height = int(insulabs_moongu_image.height * (1080 / insulabs_moongu_image.width))  # 비율 유지
        insulabs_moongu_image = insulabs_moongu_image.resize((1080, new_height), Image.Resampling.LANCZOS)
    for i in range(2):  # GIF 애니메이션 2프레임 생성
        # 배경 복사
        frame = base_image.copy()
        # frame=frame.convert("RGB")
        frame = Image.alpha_composite(frame, line_image)
        # 배너문구1 (색상)
        frame = add_text_to_field(
            image=frame,
            text=banner_1,
            font_path=sub_font_path,
            fill=color,
            field_box=banner_1_box,
            line_spacing=banner_1_line_spacing,
            char_spacing=banner_1_char_spacing,
            split_mode="\n"
        )

        # 배너문구2 (흰색)
        frame = add_text_to_field(
            image=frame,
            text=banner_2,
            font_path=main_font_path,
            fill="white",
            field_box=banner_2_box,
            line_spacing=banner_2_line_spacing,
            char_spacing=banner_2_char_spacing,
            split_mode=" "
        )



        # 배너문구3 (CLICK! 색상 변경)
        click_color = "white" if i == 0 else color
        frame = add_click_text_to_field(
            image=frame,
            text=banner_3,
            font_path=click_font_path,
            default_fill='white',
            click_fill=click_color,
            field_box=banner_3_box,
            line_spacing=banner_3_line_spacing,
            char_spacing=banner_3_char_spacing,
            split_mode="\n"
        )
        # frame_np = np.array(frame)  # PIL 이미지를 numpy 배열로 변환
        # frame_rgb = cv2.cvtColor(frame_np, cv2.COLOR_RGBA2RGB)  # RGBA -> RGB 변환
        if i==1:
        # frames.append(frame_rgb)
            if '2' in output_file_name:
                combine_heihgt=insulabs_moongu_image.height+frame.height
                combined_image=Image.new('RGBA',(frame.width,combine_heihgt),(255,255,255,0))
                combined_image.paste(insulabs_moongu_image, (0, 0))
                combined_image.paste(frame, (0, insulabs_moongu_image.height))
                frame=combined_image
            jpg_path = f'{output_file_name.replace(".gif","")}.png'
            
            frame.save(jpg_path, "png", quality=100)  # 높은 품질로 저장
        # frame = frame.resize((1080, 1080), Image.Resampling.LANCZOS)
        # frame = frame.quantize(method=Image.ADAPTIVE, dither=Image.RASTERIZE)
        # frames.append(frame.quantize(method=Image.ADAPTIVE))

    # GIF 저장
    # frames[0].save(
    #     output_file_name,
    #     save_all=True,
    #     append_images=frames[1:],
    #     duration=500,  # 프레임 전환 속도 (500ms = 0.5초)
    #     loop=0,  # 무한 반복
    #     optimize=True,  # GIF 팔레트 최적화
    #     dither=Image.FLOYDSTEINBERG
    # )
    # for idx, frame in enumerate(frames):
    #     cv2.imwrite(f"{idx}_{output_file_name.replace('gif','jpg')}", frame)
    # imageio.mimsave(output_file_name, frames, fps=2)


    print(f' >> GIF 저장 완료: {output_file_name}')

def process_normal(image_path, filter_path,line_path ,main_moongu,sub_moongu ,click_moongu, color, output_file_name, config_path, main_font_path, sub_font_path ,click_font_path):
    print(f' >> 중간이미지 생성 중: {output_file_name}')
    config = configparser.ConfigParser()
    config.read(config_path)
    
    normal_main_box = (
        config.getint("normal", "main_left"),
        config.getint("normal", "main_top"),
        config.getint("normal", "main_right"),
        config.getint("normal", "main_bottom")
    )
    normal_sub_box = (
        config.getint("normal", "sub_left"),
        config.getint("normal", "sub_top"),
        config.getint("normal", "sub_right"),
        config.getint("normal", "sub_bottom")
    )
    normal_click_box = (
        config.getint("normal", "click_left"),
        config.getint("normal", "click_top"),
        config.getint("normal", "click_right"),
        config.getint("normal", "click_bottom")
    )
    normal_main_line_spacing = config.getint("normal", "main_line_spacing")
    normal_main_char_spacing = config.getint("normal", "main_char_spacing")
    normal_sub_line_spacing = config.getint("normal", "sub_line_spacing")
    normal_sub_char_spacing = config.getint("normal", "sub_char_spacing")
    normal_click_line_spacing = config.getint("normal", "click_line_spacing")
    normal_click_char_spacing = config.getint("normal", "click_char_spacing")
    base_image = Image.open(image_path).convert("RGBA")
    if base_image.size != (1080, 1080):
        base_image = base_image.resize((1080, 1080), Image.Resampling.LANCZOS)
    if filter_path:
        filter_image = Image.open(filter_path).convert("RGBA")
        if filter_image.size != (1080, 1080):
            filter_image = filter_image.resize((1080, 1080), Image.Resampling.LANCZOS)
        base_image = Image.alpha_composite(base_image, filter_image)
    # 선 이미지 로드
    line_image = Image.open(line_path).convert("RGBA")
    if line_image.size != (1080, 1080):
        line_image = line_image.resize((1080, 1080), Image.Resampling.LANCZOS)

    base_image = Image.alpha_composite(base_image, line_image)
    base_image = add_text_to_field(
        image=base_image,
        text=sub_moongu,
        font_path=sub_font_path,
        fill=color,
        field_box=normal_sub_box,
        line_spacing=normal_sub_line_spacing,  # 서브 문구 줄 간격
        char_spacing=normal_sub_char_spacing,
        split_mode=" "
    )
    base_image = add_text_to_field(
        image=base_image,
        text=main_moongu,
        font_path=main_font_path,
        fill="white",
        field_box=normal_main_box,
        line_spacing=normal_main_line_spacing,  # 메인 문구 줄 간격 (늘림)
        char_spacing=normal_main_char_spacing,
        split_mode=" "  # 띄어쓰기 기준 줄바꿈
    )
    base_image = add_click_text_to_image(
        image=base_image,
        text=click_moongu,
        font_path=click_font_path,
        default_fill='white',
        click_fill=color,
        field_box=normal_click_box,
        line_spacing=normal_click_line_spacing,
        char_spacing=normal_click_char_spacing,
        split_mode="\n"
    )
    # 이미지 저장
    base_image.save(output_file_name)
    print(f' >> {output_file_name} 저장 완료')


def process_mileage(color, mileage_image_path, mileage_moongu, config_path, font_path, output_file_name):
    """
    마일리지 이미지를 생성하는 함수.
    """
    print(f' >> 마일리지 이미지 생성 중: {output_file_name}')

    # Config 파일 로드
    config = configparser.ConfigParser()
    config.read(config_path)

    # 텍스트 배치 영역 가져오기
    main_box = (
        config.getint("마일리지", "main_left"),
        config.getint("마일리지", "main_top"),
        config.getint("마일리지", "main_right"),
        config.getint("마일리지", "main_bottom")
    )

    # 줄 간격 및 글자 간격 설정
    main_line_spacing = config.getint("마일리지", "main_line_spacing")
    main_char_spacing = config.getint("마일리지", "main_char_spacing")

    # 배경 이미지 로드 및 크기 조정
    mileage_bg_image = Image.open(mileage_image_path).convert("RGBA")
    if mileage_bg_image.size != (500, 270):  # 2배율 해상도 기준
        mileage_bg_image = mileage_bg_image.resize((500, 270), Image.Resampling.LANCZOS)

    # 색상 바탕 생성
    color_background = Image.new("RGBA", mileage_bg_image.size, color)

    # 마일리지 배경 이미지 덮기
    combined_image = Image.alpha_composite(color_background, mileage_bg_image)

    # 문구 작성
    combined_image = add_text_to_field(
        image=combined_image,
        text=mileage_moongu,
        font_path=font_path,
        fill="Black",  # 텍스트 색상
        field_box=main_box,
        line_spacing=main_line_spacing,
        char_spacing=main_char_spacing,
        split_mode="\n"
    )

    # 이미지 저장
    combined_image.save(output_file_name, "PNG")
    print(f' >> 마일리지 이미지 저장 완료: {output_file_name}')

# ===============================================================================
#                            런
# ===============================================================================
def run():
    print(' >> 프로그램 실행')
    try:
        category=sys.argv[1]
        if category=='input':
            category=input(' >> 보종을 입력하세요 : ')
    except:
        category=input(' >> 보종을 입력하세요 : ')
    if '보험' not in category:
        category=category+'보험'
    background_lst=os.listdir(background_dir)
    if category.replace('보험','') not in background_lst:
        print(' >> 해당 보종의 배경이미지가 없습니다.')
        return
    moongu_1s=[]
    moongu_1s.append(select_banner_1_moongu(category))
    while len(moongu_1s)<2:
        cur_moongu_1=select_banner_1_moongu(category)
        if cur_moongu_1 not in moongu_1s:
            moongu_1s.append(cur_moongu_1)
    print(f' >> 선택된 배너문구1: {moongu_1s}')
    moongu_2s=[]
    moongu_2s.append(select_one_line('배너문구2',category))
    while len(moongu_2s)<2:
        cur_moongu_2=select_one_line('배너문구2',category)
        if cur_moongu_2 not in moongu_2s:
            moongu_2s.append(cur_moongu_2)
    print(f' >> 선택된 배너문구2: {moongu_2s}')
    moongu_3s=[]
    moongu_3s.append(select_gif_moongu(category))
    while len(moongu_3s)<2:
        cur_moongu_3=select_gif_moongu(category)
        if cur_moongu_3 not in moongu_3s:
            moongu_3s.append(cur_moongu_3)
    print(f' >> 선택된 배너문구3: {moongu_3s}')

    thumb_main_moongu=select_one_line('썸네일 메인문구',category)
    print(f' >> 선택된 썸네일 메인 문구: {thumb_main_moongu}')

    thumb_sub_moongu=select_thumb_sub_moongu(category)
    print(f' >> 선택된 썸네일 서브 문구: {thumb_sub_moongu}')

    normal_main_moongus=[]
    normal_main_moongus.append(select_one_line('중간 메인문구',category))

    while len(normal_main_moongus)<4:
        cur_main_moongu=select_one_line('중간 메인문구',category)
        if cur_main_moongu not in normal_main_moongus:
            normal_main_moongus.append(cur_main_moongu)
    print(f' >> 선택된 중간 메인 문구: {normal_main_moongus}')

    normal_click_moongu=select_one_line('중간 클릭문구',category)
    print(f' >> 선택된 중간 클릭 문구: {normal_click_moongu}')

    color=select_one_line('색상표',category)
    print(f' >> 선택된 색상: {color}')
    banner_line=select_one_file('배너선')
    print(f' >> 선택된 배너 선: {banner_line}')

    line=select_one_file('선')
    print(f' >> 선택된 선: {line}')

    selected_filter=select_one_file('필터')
    print(f' >> 선택된 필터: {selected_filter}')

    main_font=select_one_file(r'폰트\타이틀')
    print(f' >> 선택된 메인 폰트: {main_font}')

    sub_font=select_one_file(r'폰트\서브')
    while sub_font==main_font:
        sub_font=select_one_file(r'폰트\서브')
    
    print(f' >> 선택된 서브 폰트: {sub_font}')
    click_font=select_one_file(r'폰트\클릭')
    print(f' >> 선택된 클릭 폰트: {click_font}')

    backgrounds=select_background(category)
    print(f' >> 선택된 배경: {backgrounds}')

    for idx, background in enumerate(backgrounds):
        print(f' >> {idx+1}번째 배경 이미지: {background} 처리')
        if idx==1 or idx==6:
            output_file_name=f'{idx+1}(링크삽입).gif'
        else:
            output_file_name=f'{idx+1}.png'
        output_path=os.path.join(output_dir,output_file_name)
        if idx==0:
            process_1_png(
                image_path=background,
                filter_path=selected_filter,
                thumb_main_moongu=thumb_main_moongu,
                thumb_sub_moongu=thumb_sub_moongu,
                color=color,
                output_file_name=output_path,
                config_path = config_path,
                main_font_path = main_font,
                sub_font_path = sub_font
            )
        elif idx == 1 or idx == 6:  # GIF 생성 조건
            if idx==1:
                m_idx=0
            else:
                m_idx=1
            process_gif(
                image_path=background,  # 배경 이미지 경로
                filter_path=selected_filter,  # 필터 이미지 경로
                banner_1=moongu_1s[m_idx],  # 배너문구1
                banner_2=moongu_2s[m_idx],  # 배너문구2
                banner_3=moongu_3s[m_idx],  # 배너문구3
                color=color,  # 선택된 색상 (예제: 주황색)
                line_path=banner_line,  # 선 이미지 경로
                output_file_name=output_path,  # 최종 GIF 파일명
                config_path=config_path,  # 설정 파일
                main_font_path=main_font,  # 메인 문구 폰트
                sub_font_path=sub_font,  # 서브 문구 폰트
                click_font_path=click_font  # 클릭 문구 폰트
            )
        else:
            m_idx=idx-2
            sub_text=f'0{m_idx+1}'
            normal_main_moongu=normal_main_moongus[m_idx]
            process_normal(
                image_path=background,  
                filter_path=selected_filter, 
                line_path=line,  
                main_moongu=normal_main_moongu, 
                sub_moongu=f'{sub_text}',  
                click_moongu=normal_click_moongu, 
                color=color, 
                output_file_name=output_path,  
                config_path=config_path, 
                main_font_path=main_font, 
                sub_font_path=sub_font,
                click_font_path=click_font 
            )

    mileage_dir=os.path.join(current_dir,'마일리지')
    mileage_images=os.listdir(mileage_dir)
    selected_mileage=random.choice(mileage_images)
    print(f' >> 선택된 마일리지 이미지: {selected_mileage}')
    mileage_image_path=os.path.join(mileage_dir,selected_mileage)
    mileage_moongu_path=os.path.join(current_dir,'마일리지.txt')
    mileage_moongu=open(mileage_moongu_path,'r').read()
    mileage_font=select_one_file(r'폰트\마일리지')
    output_file_name=os.path.join(output_dir,'8.png')
    process_mileage(color, mileage_image_path, mileage_moongu, config_path, mileage_font, output_file_name)
# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '241206'
__latest_update_date__ = '241206'
__version__ = 'v1.00'
__title__ = '배너 자동 생성 프로그램'
__desc__ = '배너 자동 생성 프로그램'
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