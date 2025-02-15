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

try:
    import urllib.parse
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'urllib'])
    import urllib.parse

try:
    import gspread
except ImportError:
    subprocess.run([sys.executable,'-m','pip','install','--upgrade','gspread'])
    import gspread
try:
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'aouth2client'])
    from oauth2client.service_account import ServiceAccountCredentials

import configparser
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
config_path=os.path.join(current_dir, 'config.ini')

config=config_read()
check_rank=int(config['setting']['check_rank'])


def check_real_url(url):
    response=requests.head(url,allow_redirects=True)
    if response.status_code!=200:
        return 'Error'
    else:
        url=response.url.split('?')[0]#.replace('blog','m.blog')
        return url

def write_to_sheet(data):
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url('').get_worksheet(0)

    # 열 이름 설정
    headers = ['시간', '키워드', '탭', '탭순위', '1위여부', '글순위', '주소']
    if sheet.row_count == 0:
        sheet.append_row(headers)

    # 데이터 추가
    for row in data:
        sheet.append_row(row)
# ===============================================================================
#                            런
# ===============================================================================
def run():
    print('프로그램 실행')
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    #options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--log-level=3')  # 로그 레벨 설정
    options.add_argument("--incognito")  # 시크릿 모드
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--ignore-certificate-errors")  # 인증서 오류 무시
    driver=None
    driver = load_driver(options)
    current_time = datetime.now().strftime('%y-%m-%d %H:%M')
    for idx,input_str in enumerate(open(input_path, 'r').read().splitlines(),start=1):
        if idx>30 and idx%30==0:
            print('30개 검색 후 60초 대기')
            for _ in range(60):
                time.sleep(1)
                print(f'{60-_}초 대기중',end='\r')
            print('    '*60)
        keyword,target_headline,target_url=input_str.split('\t')
        url=f'https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={keyword}'
        print(f'{idx}번째 검색어: {keyword} 검색중')
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        last_height = driver.execute_script('return document.body.scrollHeight')
        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(0.5)
            new_height = driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height

        smart_block_roots=driver.find_elements(By.CLASS_NAME,'fds-collection-root')
        try:
            if '함께 많이 찾는' in smart_block_roots[0].text:
                smart_block_roots=None
        except:pass
        normal_block_roots=driver.find_elements(By.CLASS_NAME,'_fe_view_root')
        find_flag=False
        if smart_block_roots:
            headline_find_flag=False
            except_cnt=0
            for block_rank,root in enumerate(smart_block_roots,start=1):
                try:
                    headline=root.find_element(By.CLASS_NAME,'fds-comps-header-headline').text
                    if '관련 광고' in headline or '인기주제' in headline or '개정출시' in headline or '이미지' in headline or '함께 많이 찾는' in headline:
                        except_cnt+=1
                    if headline!=target_headline:
                        continue
                except:
                    if '함께 많이 찾는' in root.text or '관련 광고' in root.text or '인기주제' in root.text or '개정출시' in root.text or '이미지' in root.text:
                        except_cnt+=1
                    continue
                print(f' ㄴ {keyword} {headline} 발견')
                headline_find_flag=True
                
                titles=root.find_elements(By.CLASS_NAME,'fds-comps-right-image-text-title')
                for title_rank, title in enumerate(titles,start=1):
                    content_url=title.get_attribute('href')
                    if content_url==None:
                        wrap_title=root.find_elements(By.CLASS_NAME,'fds-comps-right-image-text-title-wrap')[title_rank-1]
                        content_url=wrap_title.get_attribute('href')
                    if 'm.cafe' in content_url:
                        content_url=content_url.split('?')[0].replace('m.cafe','cafe')
                    elif 'in.naver.com' in content_url:
                        content_url=check_real_url(content_url)
                    if content_url==target_url:
                        find_flag=True
                        print(f'  ㄴ {keyword} {headline} {block_rank-except_cnt}  {title_rank} {content_url}')
                        data = [[current_time, keyword, headline, block_rank-except_cnt, title_rank, content_url]]
                        write_to_sheet(data)

                if headline_find_flag==True and find_flag==False:
                    print(f'  ㄴ {keyword} {headline} {block_rank-except_cnt} X {target_url}')
                    data = [[current_time, keyword, headline, block_rank-except_cnt, 'X', target_url]]
                    write_to_sheet(data)
                   
            if not find_flag and headline_find_flag==False:
                print(f'  ㄴ {keyword} {target_headline} 탭없음 X {target_url}')
                data = [[current_time, keyword, target_headline, '탭없음', 'X', target_url]]
                write_to_sheet(data)
                
        elif normal_block_roots:
            headline_find_flag=False
            for block_rank,root in enumerate(normal_block_roots,start=1):
                try:
                    headline=root.find_element(By.CLASS_NAME,'mod_title_area').text
                    if headline!=target_headline:
                        continue
                except:
                    continue
                print(f' ㄴ {keyword} {headline} 발견')
                headline_find_flag=True
                adcr_cnt=0
                titles=root.find_elements(By.CLASS_NAME,'title_link')
                for title_rank, title in enumerate(titles,start=1):
                    content_url=title.get_attribute('href')
                    original_url=content_url
                    if 'adcr' in content_url:
                        adcr_cnt+=1
                        continue
                    now_rank=title_rank-adcr_cnt
                    if now_rank>check_rank:
                        break
                    if 'm.cafe' in content_url:
                        content_url=content_url.split('?')[0].replace('m.cafe','cafe')
                    elif 'in.naver.com' in content_url:
                        content_url=check_real_url(content_url)
                    if content_url==target_url:
                        find_flag=True
                        print(f'  ㄴ {keyword} {headline} {block_rank} {title_rank-adcr_cnt} {content_url}')
                        data = [[current_time, keyword, headline, block_rank, title_rank-adcr_cnt, content_url]]
                        write_to_sheet(data)
                        
                if headline_find_flag==True and find_flag==False:
                    print(f'  ㄴ {keyword} {headline} {block_rank} X {target_url}')
                    data = [[current_time, keyword, headline, block_rank, 'X', target_url]]
                    write_to_sheet(data)
                   
            if not find_flag and headline_find_flag==False:
                print(f'  ㄴ {keyword} {target_headline} 탭없음 X {target_url}')
                data = [[current_time, keyword, target_headline, '탭없음', 'X', target_url]]
                write_to_sheet(data)
                
        
# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '250117'
__latest_update_date__ = '250204'
__version__ = 'v1.1.0'
__title__ = '블로그 글 주소 모니터링 프로그램'
__desc__ = '블로그 글 주소 모니터링 프로그램'
__changeLog__ = {
    'v1.00': ['Initial Release.'],
    'v1.0.1': ['순위 적는거 추가'],
    'v1.1.0': ['스프레드 시트에 기록하도록 변경','output 양식 변경','30분마다 재실행 추가'],
    
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
    while True:
        for i in range(1800):
            dots='.'*(i%5)
            print(f'{1800-i}초 대기중{dots}',end='\r')
            time.sleep(1)
            print('    '*15,end='\r')
        run()