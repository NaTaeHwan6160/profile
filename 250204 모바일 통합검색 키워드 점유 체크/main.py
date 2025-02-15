import warnings
warnings.simplefilter("ignore", UserWarning)
import subprocess
import requests
import ctypes
import sys
import re
import os
from datetime import datetime, timedelta
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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scode.selenium import *
from update_input import *
import paramiko
import json
import th_moodule
def config_read():
    config = configparser.ConfigParser()
    try:config.read('config.ini', encoding='cp949')
    except:config.read('config.ini', encoding='utf-8')
    return config
# ===============================================================================
#                            데피니션
# ===============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir=os.path.join(current_dir,'output')
input_path=os.path.join(current_dir,'input.txt')
except_keyword_path=os.path.join(current_dir,'except_keyword.txt')
log_dir=os.path.join(current_dir,'log')
check_url_path=os.path.join(current_dir,'check_urls.txt')
db_error_log_path=os.path.join(current_dir,'db_error.txt')
open(db_error_log_path,'w').close()
check_urls=open(check_url_path,'r').read().splitlines()
tunnel=None



def send_monitoring_signal():
    url = ""
    try:
        response = requests.get(f'{url}', verify=False)
        if response.status_code == 200:
            a=1  # 서버의 응답 내용을 출력
        else:
            a=2
    except requests.RequestException as e:
        print(f"정상 동작 신호 전송 중 오류 발생: {e}")

def check_real_url(url):
    response=requests.head(url,allow_redirects=True)
    if response.status_code!=200:
        return 'Error'
    else:
        url=response.url.split('?')[0]#.replace('blog','m.blog')
        return url
        
def connect_to_server(hostname, username, password):
    """SSH로 서버에 연결합니다."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print(f"{hostname}에 성공적으로 연결되었습니다.")
        return ssh
    except Exception as e:
        print(f"{hostname}에 연결하는 중 오류가 발생했습니다: {e}")
        return None
    




def validate_blog_links(driver, url,wait_tag):
    exist='탈환필'
    print(f'\t\tㄴ{url}내 단축 주소를 확인합니다.')
    original_search_window = driver.current_window_handle
    driver.execute_script(f"window.open('{url}');")
    new_tab = driver.window_handles[-1]
    driver.switch_to.window(new_tab)
    time.sleep(3)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    original_window = driver.current_window_handle
    last_height = driver.execute_script('return document.body.scrollHeight')
    global suc_urls
    global faild_url_path
    
    # 스크롤을 끝까지 내리며 탐색
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(0.5)
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height
    
    try:
        try:
            # 1. se-oglink-info 클래스에서 링크 탐지
            se_oglink_elements = driver.find_elements(By.CLASS_NAME, 'se-oglink-info')
            for se_oglink_element in se_oglink_elements:
                se_oglink_href = se_oglink_element.get_attribute('href')
                if se_oglink_href:
                    response=requests.get(se_oglink_href,allow_redirects=True)
                    if response.status_code != 200 or "<html" not in response.text.lower():
                        print(f'\n\t\tㄴ게시글 내 {se_oglink_href} 접속 불가능 - {response.status_code}')
                        return exist
                    else:
                        cur_url=response.url
                        for check_url in check_urls:
                            domain = check_url
                            if check_url !="" and domain in cur_url:
                                #print(f'\t\tㄴ게시글 내 {se_oglink_href}의 최종 주소는 {cur_url}이며 {check_url} 도메인입니다.')
                                exist='점유'
                                return exist
                                
        except: pass                            
                    
        try:
            # 2. se-link 클래스의 a 태그에서 링크 탐지
            se_link_elements = driver.find_elements(By.CLASS_NAME, 'se-link')
            for se_link_element in se_link_elements:
                a_tag = se_link_element.find_element(By.TAG_NAME, 'a')
                se_link_href = a_tag.get_attribute('href')
                if se_link_href:
                    response=requests.get(se_link_href,allow_redirects=True)
                    if response.status_code != 200 or "<html" not in response.text.lower():
                        print(f'\n\t\tㄴ게시글 내 {se_link_href} 접속 불가능 - {response.status_code}')
                        return exist
                    else:
                        cur_url = response.url
                        for check_url in check_urls:
                            domain = check_url
                            if check_url !="" and domain in cur_url:
                                #print(f'\t\tㄴ게시글 내 {se_link_href}의 최종 주소는 {cur_url}이며 {check_url} 도메인입니다.')
                                exist='점유'
                                return exist

        except: pass                

        try:
            # 3. 이미지에 삽입된 URL 탐지
            image_link_elements = driver.find_elements(By.CLASS_NAME, 'se-module-image-link-use')
            for image_link in image_link_elements:
                data_linkdata = image_link.get_attribute('data-linkdata')
                if data_linkdata:
                    link_data = json.loads(data_linkdata)
                    embedded_link = link_data.get('link')  # 'link' 필드 추출
                    if embedded_link:
                        response=requests.get(embedded_link,allow_redirects=True)
                        if response.status_code != 200 or "<html" not in response.text.lower():
                            print(f'\n\t\tㄴ게시글 내 이미지에 삽입된 {embedded_link} 접속 불가능 - {response.status_code}')
                            return exist
                        else:
                            cur_url = response.url
                            #print(f'단축주소 : {embedded_link} 최종주소 : {cur_url}')
                            for check_url in check_urls:
                                domain = check_url
                                if check_url !="" and domain in cur_url:
                                    #print(f'\t\tㄴ게시글 내 {embedded_link}의 최종 주소는 {cur_url}이며 {check_url} 도메인입니다.')
                                    exist='점유'
                                    return exist

        except:pass
    finally:
        driver.close()
        # 기존 탭으로 전환
        driver.switch_to.window(original_search_window)
        # 로딩 기다리기
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, wait_tag))
        )
        return exist
        
# ===============================================================================
#                              카페 단축 주소 확인
# ===============================================================================


def validate_cafe_links(driver, url,wait_tag):
    exist='탈환필C'
    # 현재 창(통합검색 탭) 저장
    original_search_window = driver.current_window_handle
    # 카페 게시글 열기
    driver.execute_script(f"window.open('{url}');")
    new_tab = driver.window_handles[-1]
    driver.switch_to.window(new_tab)
    time.sleep(3)
    
    global error_flag
    global suc_urls
    global faild_url_path
    # 1. alert 창 탐지 (삭제된 게시글 처리)
    try:
        WebDriverWait(driver, 1).until(EC.alert_is_present())  # alert이 있으면 감지
        alert = driver.switch_to.alert
        print("삭제된 게시글입니다.")
        alert.accept()  # alert 창 닫기
        exist='탈환필C'
        return exist  # 삭제된 게시글이므로 광고 없음
    except TimeoutException:
        pass  # alert이 없으면 계속 진행

    # 페이지 로드 후 본문 준비
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    last_height = driver.execute_script('return document.body.scrollHeight')

    # 스크롤을 끝까지 내리며 탐색
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(0.5)
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height
    cafe_window = driver.current_window_handle            
    html = driver.page_source
    try:
        try:#이미지 링크 탐색
            image_link_elements = driver.find_elements(By.CLASS_NAME, 'se-module-image-link-use')
            for image_link in image_link_elements:
                data_linkdata = image_link.get_attribute('data-linkdata')
                if data_linkdata:
                    link_data = json.loads(data_linkdata)
                    embedded_link = link_data.get('link')
                    if embedded_link:
                        response=requests.get(embedded_link,allow_redirects=True)
                        if response.status_code!=200 or "<html" not in response.text.lower():
                            print(f'\n\t\tㄴ게시글 내 {embedded_link} 접속 불가능 - {response.status_code}')
                            return exist
                        else:
                            cur_url = response.url
                            for check_url in check_urls:
                                domain = check_url.split('https://')[-1]
                                if check_url !="" and domain in cur_url:
                                    #print(f'\t\tㄴ게시글 내 {embedded_link}의 최종 주소는 {cur_url}이며 {check_url} 도메인입니다.')
                                    exist='점유'
                                    return exist
        except:
            pass

        try:#본문 링크 탐색
            se_link_elements=driver.find_elements(By.CLASS_NAME,'se-link')
            for se_link in se_link_elements:
                se_href=se_link.get_attribute('href')
                if se_href:
                    response=requests.get(se_href,allow_redirects=True)
                    if response.status_code != 200 or "<html" not in response.text.lower():
                        print(f'\t\t\tㄴ게시글 내 {se_href} 접속 불가능 - {response.status_code}')
                        return exist
                    else:
                        cur_url=response.url
                        for check_url in check_urls:
                            domain = check_url.split('https://')[-1]
                            if check_url !='' and domain in cur_url:
                                exist='점유'
                                return exist

        except:
            pass

        try:#댓글 링크 탐색
            comment_links = driver.find_elements(By.CSS_SELECTOR, '.comment_text_view a')
            for comment_link in comment_links:
                comment_href = comment_link.get_attribute('href')
                if comment_href:
                    response=requests.get(comment_href,allow_redirects=True)
                    if response.status_code!=200 or "<html" not in response.text.lower():
                        print(f'\n\t\tㄴ게시글 내 {embedded_link} 접속 불가능 - {response.status_code}')
                        return exist
                    else:
                        cur_url = response.url
                        for check_url in check_urls:
                            domain = check_url.split('https://')[-1]
                            if check_url !="" and domain in cur_url:
                                #print(f'\t\tㄴ게시글 내 {embedded_link}의 최종 주소는 {cur_url}이며 {check_url} 도메인입니다.')
                                exist='점유'
                                return exist

        except:
            pass

    finally:
        driver.close()
        # 기존 탭으로 전환
        driver.switch_to.window(original_search_window)
        # 로딩 기다리기
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, wait_tag))
        )
        return exist
        


# ===============================================================================
#                            런
# ===============================================================================
def run():
    #print('프로그램 시작')
    keyword_lst=open('input.txt','r').read().splitlines()
    our_url_lst=open('our_url.txt','r').read().splitlines()
    current_time = datetime.now()
    output_filename = f'output_{current_time.strftime("%Y-%m-%d_%H%M")}.txt'
    
    output_path = os.path.join(output_dir, output_filename)
    id_lst=open('ids.txt','r').read().splitlines()
    log_path=os.path.join(log_dir,f'{datetime.now().strftime("%Y-%m-%d")}_log.txt')
    except_keywords=open(except_keyword_path,'r').read().splitlines()
    latest_log_path=os.path.join(log_dir,os.listdir(log_dir)[-1])
    latest_log_lst=open(latest_log_path,'r').read().splitlines()
    latest_tab={}
    global tunnel
    open(log_path,'w').close()

        # 서버에서 파일 목록 가져오기
    tunnel = th_moodule.create_ssh_tunnel(tunnel,'')
    connection=th_moodule.create_db_connection(tunnel,'')
    try:
    # 커서 생성
        with connection.cursor() as cursor:
            # 최신 regdate와 run_time 기준으로 정렬된 데이터를 가져오는 쿼리
            query = """SELECT regdate, keyword, headline, run_time FROM  ORDER BY regdate DESC, run_time DESC """
            print(f'쿼리 : {query} 실행0')
            cursor.execute(query)
            rows = cursor.fetchall()

            # 반복문으로 결과 처리
            first_regdate = None
            first_runtime = None

            for row in rows:
                regdate, keyword, headline, run_time = row['regdate'].strftime('%Y-%m-%d'), row['keyword'], row['headline'], row['run_time']

                # 첫 번째 행의 regdate와 run_time을 저장
                if first_regdate is None and first_runtime is None:
                    first_regdate = regdate
                    first_runtime = run_time

                # regdate 또는 run_time이 첫 번째와 다르면 종료
                if regdate != first_regdate or run_time != first_runtime:
                    break

                # 딕셔너리에 값 추가
                if keyword not in latest_tab:
                    latest_tab[keyword] = []
                if headline not in latest_tab[keyword]:
                    if '(신규)' in headline:
                        headline=headline.replace('(신규)','')
                    elif '(삭제)' in headline:
                        headline=headline.replace('(삭제)','')
                    latest_tab[keyword].append(headline)

    except Exception as e:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"현재 테이블 목록: {tables}")
        print(f"데이터베이스 쿼리 오류: {e}")
    tunnel.close()
    connection.close()
    indexing=1
    for key_idx,keyword in enumerate(keyword_lst, start=1):
        our_str=''
        output_dict={}
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument("--disable-popup-blocking")
        options.add_argument('--log-level=3')  # 로그 레벨 설정
        options.add_argument("--incognito")  # 시크릿 모드
        options.add_argument("--ignore-certificate-errors")  # 인증서 오류 무시
        driver = load_driver(options,mode='android')
        print(f'[{key_idx}/{len(keyword_lst)}]{keyword} 검색')
        url=f'https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={keyword}'
        driver.get(url)
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
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
        normal_block_roots=driver.find_elements(By.CLASS_NAME,'api_subject_bx')
        if smart_block_roots:
            for root in smart_block_roots:
                output_dict={}
                output_dict[keyword]=url
                try:
                    headline=root.find_element(By.CLASS_NAME,'fds-comps-header-headline').text
                    con_flag=False
                    if '관련 광고' in headline or '브랜드' in headline or '인기주제' in headline:
                        con_flag=True
                    
                    for exp_key in except_keywords:
                        if exp_key in headline:
                            con_flag=True
                    if con_flag:continue
                except: continue
                print(f' ㄴ {headline} 블록 탐색')
                try:
                    if headline in latest_tab[keyword] or f'{headline}(신규)' in latest_tab[keyword]:
                        output_dict[headline]=''
                        try:
                            latest_tab[keyword].remove(headline)
                        except:pass
                        try:
                            latest_tab[keyword].remove(f'{headline}(신규)')
                        except:pass
                    else:
                        output_dict[f"{headline}(신규)"]=''
                        headline=f'{headline}(신규)'
                except:
                    output_dict[headline]=''
                with open(log_path,'a') as flog:
                    flog.write(f'{keyword}\t{headline}\n')
                titles=None
                titles=root.find_elements(By.CLASS_NAME,'fds-comps-right-image-text-title')
                wait_tag='flick_bx'
                try:
                    wrap_root=root.find_elements(By.CLASS_NAME,'fds-comps-right-image-text-title-wrap')
                    if wrap_root:
                        title=wrap_root
                except:pass
                for title_rank, title in enumerate(titles,start=1):
                    our_str=f'{title_rank}위'
                    content_url=title.get_attribute('href')
                    if content_url == None:
                        content_url = root.find_elements(By.CLASS_NAME,'fds-comps-right-image-text-title-wrap')[title_rank-1].get_attribute('href')
                    if not content_url: continue
                    original_url=content_url
                    if 'm.cafe' in content_url:
                        content_url=content_url.split('?')[0].replace('m.cafe','cafe')
                        
                    elif 'in.naver.com' in content_url:
                        content_url=check_real_url(content_url)
                    print(f'   ㄴ {title_rank}위 글 주소 - {content_url}')
                    if content_url in our_url_lst:
                        if 'cafe' in original_url or 'cafe' in content_url:
                            res=validate_cafe_links(driver, original_url,wait_tag)
                        elif 'blog' in original_url or 'blog' in content_url:
                            res=validate_blog_links(driver, content_url,wait_tag)
                        if res=='점유':
                            our_str+='점유'
                        elif res=='탈환필C':
                            our_str+='KRV(카페)'
                        elif res=='탈환필':
                            partner_flag=True
                            for id in id_lst:
                                if id in content_url:
                                    partner_flag=False
                                    our_str+='KRV(임대)'
                                    break
                            if partner_flag:
                                our_str+='KRV(파트너)'

                    else:
                        if 'cafe' in original_url:
                            our_str+='탈환필C'
                        else:
                            our_str+='탈환필'
                    print(f'     ㄴ {our_str.split("위")[-1]}')
                    output_dict[our_str]=original_url
                with open(output_path,'a') as f:
                    f.write(f'{keyword}\t{headline}\t')
                    for key, item in output_dict.items():
                        if '1위' in key or '2위' in key or '3위' in key:
                            key=key.split('위')[-1]
                            f.write(f'{key}\t{item}\t')
                    f.write(f'\n')                
        elif normal_block_roots:
            for root in normal_block_roots:
                output_dict={}
                output_dict[keyword]=url
                try:
                    headline=root.find_element(By.CLASS_NAME,'mod_title_area').text
                    con_flag=True
                    if '인플루언서' in headline or '인기글' in headline:
                        con_flag=False
                    
                    for exp_key in except_keywords:
                        if exp_key in headline:
                            con_flag=True
                    if con_flag:continue
                except: continue
                if '인플루언서' in headline:
                    headline='인플루언서'
                print(f' ㄴ {headline} 블록 탐색')
                try:
                    if headline in latest_tab[keyword] or f'{headline}(신규)' in latest_tab[keyword]:
                        output_dict[headline]=''
                        try:
                            latest_tab[keyword].remove(headline)
                        except:pass
                        try:
                            latest_tab[keyword].remove(f'{headline}(신규)')
                        except:pass
                    else:
                        output_dict[f"{headline}(신규)"]=''
                        headline=f'{headline}(신규)'
                except:
                    output_dict[headline]=''
                titles=root.find_elements(By.CLASS_NAME,'title_link')
                with open(log_path,'a') as flog:
                    flog.write(f'{keyword}\t{headline}\n')
                wait_tag='flick_bx'
                adcr_cnt=0
                for title_rank, title in enumerate(titles,start=1):
                    our_str=f'{title_rank-adcr_cnt}위'
                    content_url=title.get_attribute('href')
                    if not content_url: continue
                    original_url=content_url
                    if 'adcr' in content_url:
                        adcr_cnt+=1
                        continue
                    if title_rank-adcr_cnt>3:
                        break
                    if 'm.cafe' in content_url:
                        
                        content_url=content_url.split('?')[0].replace('m.cafe','cafe')
                    elif 'in.naver.com' in content_url:
                        content_url=check_real_url(content_url)
                    print(f'   ㄴ {title_rank-adcr_cnt}위 글 주소 - {content_url}')
                    if content_url in our_url_lst:
                        if 'cafe' in original_url or 'cafe' in content_url:
                            res=validate_cafe_links(driver, original_url,wait_tag)
                        elif 'blog' in original_url or 'blog' in content_url:
                            res=validate_blog_links(driver, content_url,wait_tag)
                        if res=='점유':
                            our_str+='점유'
                        elif res=='탈환필C':
                            our_str+='KRV(카페)'
                        elif res=='탈환필':
                            partner_flag=True
                            for id in id_lst:
                                if id in content_url:
                                    partner_flag=False
                                    our_str+='KRV(임대)'
                                    break
                            if partner_flag:
                                our_str+='KRV(파트너)'
                    else:
                        if 'cafe' in original_url:
                            our_str+='탈환필C'
                        else:
                            our_str+='탈환필'
                    print(f'     ㄴ {our_str.split("위")[-1]}')
                    output_dict[our_str]=original_url
                with open(output_path,'a') as f:
                    f.write(f'{keyword}\t{headline}\t')
                    for key, item in output_dict.items():
                        if '1위' in key or '2위' in key or '3위' in key:
                            key=key.split('위')[-1]
                            f.write(f'{key}\t{item}\t')
                    f.write(f'\n') 
        else:
            print(' ㄴ 스마트블록 없음')
            headline='스마트블록 없음'
            output_dict={}
            output_dict[keyword]=url
            output_dict['탭 없음']=''
            output_dict['1위 ']=''
            output_dict['2위 ']=''
            output_dict['3위 ']=''
            with open(output_path,'a') as f:
                f.write(f'{keyword}\t{headline}\t')
                for key, item in output_dict.items():
                    if '1위' in key or '2위' in key or '3위' in key:
                        key=key.split('위')[-1]
                        f.write(f'{key}\t{item}\t')
                f.write(f'\n') 
        try:
            if latest_tab[keyword]:
                for tab_name in latest_tab[keyword]:
                    if '(신규)' in tab_name:
                        tab_name=tab_name.replace('(신규)','')
                    elif '(삭제)' in tab_name:
                        tab_name=tab_name.replace('(삭제)','')
                    with open(output_path,'a') as f:
                        f.write(f'{keyword}\t{tab_name}(삭제)\t\t\t\t\t\t\n')
        except: pass
        
        driver.quit()
        time.sleep(2)
    tunnel = th_moodule.create_ssh_tunnel(tunnel,'')
    connection=th_moodule.create_db_connection(tunnel,'')
    try:
    # 커서 생성
        with connection.cursor() as cursor:
            output_lst=open(output_path,'r').read().splitlines()
            for output_idx,output_str in enumerate(output_lst,start=1):
                print(f'[{output_idx}/{len(output_lst)}] DB입력')
                if len(output_str.split('\t'))==9:
                    try:
                        keyword,headline,first,first_url,second,second_url,third,third_url,_=output_str.split('\t')
                    except Exception as e:
                        print(f'아웃풋 파일 오류 - {e}')
                        with open(db_error_log_path,'a') as error:
                            error.write(f'{output_str}{e}\n')
                        continue
                elif len(output_str.split('\t'))==8:
                    try:
                        keyword,headline,first,first_url,second,second_url,third,third_url=output_str.split('\t')
                    except Exception as e:
                        print(f'아웃풋 파일 오류 - {e}')
                        with open(db_error_log_path,'a') as error:
                            error.write(f'{output_str}{e}\n')
                        continue
                elif len(output_str.split('\t'))==2 and ('삭제' not in output_str or '신규' not in output_str):
                        continue
                else:
                    try:
                        keyword,headline,_=output_str.split('\t')
                    except Exception as e:
                        print(f'아웃풋 파일 오류 - {e}')
                        with open(db_error_log_path,'a') as error:
                            error.write(f'{output_str}{e}\n')
                        continue
                run_time=datetime.now().strftime("%H")
                query=f"""INSERT INTO (keyword, headline, 1st, 1st_url, 2nd, 2nd_url, 3rd, 3rd_url, run_time) VALUES ("{keyword}","{headline}","{first}","{first_url}","{second}","{second_url}","{third}","{third_url}","{run_time}")"""
                try:
                    # 쿼리 실행
                    cursor.execute(query)
                    # 커밋하여 DB에 반영
                    connection.commit()
                except Exception as e:
                    print(f'쿼리 실행 실패 - {e}')
                    with open(db_error_log_path,'a') as error:
                        error.write(f'{output_str}{e}\n')
                    continue                
                time.sleep(0.05)
    except Exception as e:
        print(f'DB업로드 실패 - {e}')
    tunnel.close()
    connection.close()
    print('DB입력이 완료되었습니다.')
    

def task():
    """실행할 작업을 정의합니다."""
    start_time = datetime.now().strftime("%H:%M:%S")
    print(f'\n프로그램 시작 : {start_time}')
    
    try:
        if '1' in sys.argv[1]:
            print('우리글 주소 불러오기를 시작합니다.')
            read_url_list_from_google()
            run()
            send_monitoring_signal()
        elif '2' in sys.argv[1]:
            print('인슈랩스 공략 키워드에서 검색 키워드를 가져옵니다.')
            read_input()
            print('우리글 주소 불러오기를 시작합니다.')
            read_url_list_from_google()
            run()
            send_monitoring_signal()
        elif '3' in sys.argv[1]:
            print('인슈랩스 공략 키워드에서 검색 키워드를 가져옵니다.')
            read_input()
            run()
            send_monitoring_signal()
        else:
            run()
            send_monitoring_signal()
    except:
        print("작업 중 오류가 발생했습니다. 기본 작업을 실행합니다.")
        #read_input()
        #read_url_list_from_google()
        run()
        send_monitoring_signal()

    end_time = datetime.now().strftime("%H:%M:%S")
    print(f'프로그램 종료 : {end_time}')


def get_next_run_time():
    """다음 실행 시간을 계산합니다."""
    now = datetime.now()
    next_times = []
    for job in schedule.jobs:
        job_time = datetime.strptime(job.next_run.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        next_times.append(job_time)
    if next_times:
        return min(next_times)
    return None
schedule.every().day.at("12:00").do(task)  # 오전 08:00에 작업 실행
schedule.every().day.at("06:00").do(task)  # 오전 08:00에 작업 실행
schedule.every().day.at("09:00").do(task)  # 오전 08:00에 작업 실행
schedule.every().day.at("15:00").do(task)  # 오전 08:00에 작업 실행
schedule.every().day.at("18:00").do(task)  # 오전 08:00에 작업 실행
#schedule.every().day.at("17:00").do(task)  # 오후 17:00에 작업 실행
# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '241227'
__latest_update_date__ = '241231'
__version__ = 'v1.0.4'
__title__ = '모바일 통합검색 키워드 점유 체크 프로그램 - 나태환'
__desc__ = '모바일 통합검색 키워드 점유 체크 프로그램 - 나태환'
__changeLog__ = {
    'v1.00': ['Initial Release.'],
    'v1.01': ['1위 탈환필 필터링','프린트 CSS 추가','디자인 변경'],
    'v1.02': ['06시 실행 변경','카페 필터링 버튼 추가'],
    'v1.03': ['DB에 기록하는것으로 변경'],
    'v1.0.4': ['인플루언서탭 추가'],
    
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

    while True:
        try:
            if '1' in sys.argv[1]:
                print('우리글 주소 불러오기를 시작합니다.')
                read_url_list_from_google()
                run()
                send_monitoring_signal()
            elif '2' in sys.argv[1]:
                print('인슈랩스 공략 키워드에서 검색 키워드를 가져옵니다.')
                read_input()
                print('우리글 주소 불러오기를 시작합니다.')
                read_url_list_from_google()
                run()
                send_monitoring_signal()
            elif '3' in sys.argv[1]:
                print('인슈랩스 공략 키워드에서 검색 키워드를 가져옵니다.')
                read_input()
                run()
                send_monitoring_signal()
            else:
                run()
                send_monitoring_signal()
        except:
            print("작업 중 오류가 발생했습니다. 기본 작업을 실행합니다.")
            #read_input()
            #read_url_list_from_google()
            run()
            send_monitoring_signal()

            time.sleep(1)  # CPU 사용률 절약을 위해 1초 대기