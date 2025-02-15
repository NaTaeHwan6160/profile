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




# ===============================================================================
#                            데피니션
# ===============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
input_path=os.path.join(current_dir,'input.txt')
output_path=os.path.join(current_dir,'output.txt')
id_list=os.path.join(current_dir,'id_list.txt')
open(output_path,'w').close()
# ===============================================================================
#                            런
# ===============================================================================
def run():
    print('프로그램 실행')

    for id_str in open(id_list,'r').read().splitlines():
        n_id,n_pw=id_str.split('\t')
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        #options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--log-level=3')  # 로그 레벨 설정
        options.add_argument("--incognito")  # 시크릿 모드
        options.add_argument("--ignore-certificate-errors")  # 인증서 오류 무시
    
        driver = load_driver(options)
        if(n_login(driver,n_id,n_pw)==True):
            with open(output_path,'a') as f:
                for url in open(input_path,'r').read().splitlines():
                    print(f'{url} 접속')
                    driver.get(url)
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME,'civ__header__btn--share')))
                    try:
                        share_btn=driver.find_element(By.CLASS_NAME,'civ__header__btn--share')
                        share_btn.click()
                        print(f'  ㄴ 공유버튼 클릭')
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME,'link_blog')))
                    except:
                        f.write(f'{url}\t공유버튼 클릭 오류\n')
                    try:
                        blog_btn=driver.find_element(By.CLASS_NAME,'link_blog')
                        blog_btn.click()
                        print(f'  ㄴ 블로그 버튼 클릭')
                        time.sleep(1)
                        try:
                            unexepted_alert = driver.switch_to.alert.text
                            if '이미 다수' in unexepted_alert:
                                print(f'  ㄴ 이미 다수의 스크랩이 발생한 이미지 문구 확인')
                                f.write(f'{url}\t실패\n')
                            unexepted_alert.accept()
                        except:
                            pass
                    except:
                        f.write(f'{url}\t블로그버튼 클릭 오류\n')

                    try:
                        secret_btn=driver.find_element(By.CLASS_NAME,'set_close')
                        secret_btn.click()
                        print(f'  ㄴ 비공개 버튼 클릭')
                        time.sleep(1)
                    except:
                        f.write(f'{url}\t비공개 설정 오류\n')
                    try:
                        ok_btn=driver.find_element(By.CLASS_NAME,'btn_ok')
                        ok_btn.click()
                        print(f'  ㄴ 등록 버튼 클릭')
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'lyr_cont')))
                    except:
                        f.write(f'{url}\t등록 클릭 오류\n')
                    try:
                        alert_txt=driver.find_element(By.CLASS_NAME,'lyr_cont').text
                        if '내 블로그에 담았습니다.' in alert_txt:
                            print(f'  ㄴ 성공')
                            f.write(f'{url}\t성공\n')
                        else:
                            print('  ㄴ 실패')
                            f.write(f'{url}\t실패\n')
                    except:
                        f.write(f'{url}\t등록 확인 오류\n')
        driver.quit()
        break

    
# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '250106'
__latest_update_date__ = '250106'
__version__ = 'v1.00'
__title__ = '블로그 이미지 스크랩 프로그램'
__desc__ = '블로그 이미지 스크랩 프로그램'
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