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




# ===============================================================================
#                            데피니션
# ===============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
input_path=os.path.join(current_dir, 'input.txt')
id_list_path=os.path.join(current_dir, 'id_list.txt')
output_path=os.path.join(current_dir, 'output.txt')
open(output_path, 'w').close()

input_lst=open(input_path, 'r').read().splitlines()
id_lst=open(id_list_path, 'r').read().splitlines()
# ===============================================================================
#                            런
# ===============================================================================
def run():
    print('프로그램 실행')
    driver = None
    for id_idx, id_str in enumerate(id_lst,start=1):
        try:
            driver.quit()
        except:
            pass
        try:
            n_id, n_pw = id_str.split('\t')
        except:
            print(f'[{id_idx}/{len(id_lst)}] 아이디 리스트의 {id_idx}번째 줄 내용이 잘못되었습니다.')
        print(f'[{id_idx}/{len(id_lst)}] {n_id} 로그인 시도')
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        #options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--log-level=3')  # 로그 레벨 설정
        options.add_argument("--incognito")  # 시크릿 모드
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--ignore-certificate-errors")  # 인증서 오류 무시

        driver = load_driver(options)
        driver.get('https://www.naver.com')
        time.sleep(1)
        login_flag=n_login(driver, n_id, n_pw)
        if login_flag!=True:
            driver.quit()
            continue
        for url_idx, url in enumerate(input_lst,start=1):
            result_str=f'{n_id}\t{url}\t'
            print(f'[{id_idx}/{len(id_lst)}] [{url_idx}/{len(input_lst)}] 접속 시도', end='\r')
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'profileEdit_button')))
            except Exception as e:
                print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 접속 실패')
                result_str+='실패\n'
                with open(output_path, 'a') as f:
                    f.write(result_str)
                continue
            try:
                driver.find_element(By.CLASS_NAME,'profileEdit_button').click()
                time.sleep(1)
                try:
                    more_menus=driver.find_elements(By.CLASS_NAME,'menu_item')
                    for menu in more_menus:
                        if menu.text=='프로필 신고':
                            menu.click()
                            time.sleep(1)
                            break
                except Exception as e:
                    print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 프로필 신고 버튼 클릭 실패')
                    result_str+='실패\n'
                    with open(output_path, 'a') as f:
                        f.write(result_str)
                    continue
                print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 프로필 신고 클릭 완료',end='\r')
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'popup')))
                    popup_items=driver.find_elements(By.CLASS_NAME,'popup__item')
                except Exception as e:
                    print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 신고 창 찾기 실패')
                    result_str+='실패\n'
                    with open(output_path, 'a') as f:
                        f.write(result_str)
                    continue
                click_cnt=0
                print('  '*40,end='\r')
                print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 신고 항목 클릭 시도',end='\r')
                try:
                    for item in popup_items:
                        if click_cnt>=2:
                            break
                        if item.text=='URL':
                            item.click()
                            click_cnt+=1
                            continue
                        elif item.text=='자기소개':
                            item.click()
                            click_cnt+=1
                            continue
                except Exception as e:
                    print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 신고 항목 클릭 실패')
                    result_str+='실패\n'
                    with open(output_path, 'a') as f:
                        f.write(result_str)
                    continue
                time.sleep(1)
                print('  '*40,end='\r')
                print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 신고 버튼 클릭 시도',end='\r')
                try:
                    c_buttons=driver.find_elements(By.CLASS_NAME,'c-button-default')
                    for c_button in c_buttons:
                        if c_button.text=='신고':
                            c_button.click()
                            break
                except Exception as e:
                    print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 신고 버튼 클릭 실패')
                    result_str+='실패\n'
                    with open(output_path, 'a') as f:
                        f.write(result_str)
                    continue
                time.sleep(1)
                print('  '*40,end='\r')
                print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 신고 버튼 클릭 완료',end='\r')
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'popup__text')))
                    suc_flag=False
                    popup_texts=driver.find_elements(By.CLASS_NAME,'popup__text')
                    for popup_text in popup_texts:
                        if popup_text.text=='신고되었습니다.':
                            suc_flag=True
                            break
                    if suc_flag==True:
                        result_str+='성공\n'
                    else:
                        result_str+='실패\n'
                except Exception as e:
                    print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 신고 결과 확인 실패')
                    result_str+='실패\n'
                print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 신고 결과 저장, 동작 완료')
                with open(output_path, 'a') as f:
                    f.write(result_str)
            except:
                print(f'[{id_idx}/{len(id_lst)}][{url_idx}/{len(input_lst)}] 신고 실패')
                result_str+='실패\n'
                with open(output_path, 'a') as f:
                    f.write(result_str)
            
# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '250204'
__latest_update_date__ = '250204'
__version__ = 'v1.0.0'
__title__ = '지식인 프로필 신고 프로그램'
__desc__ = '지식인 프로필을 신고하는 프로그램'
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