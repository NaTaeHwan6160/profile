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
import paramiko

def config_read():
    config = configparser.ConfigParser()
    try:config.read('config.ini', encoding='cp949')
    except:config.read('config.ini', encoding='utf-8')
    return config

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
        except Exception as e:
            print(f"SSH 터널 생성 오류: {e}")
            tunnel = None

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

def upload_files(sftp, local_dir, remote_dir):
    """로컬 폴더의 파일 및 폴더를 원격 서버에 업로드합니다."""
    try:
        for root, dirs, files in os.walk(local_dir):
            # 원격 경로 설정
            relative_path = os.path.relpath(root, local_dir)
            target_path = os.path.join(remote_dir, relative_path).replace('\\', '/')
            
            try:
                sftp.mkdir(target_path)
            except IOError:  # 이미 존재하면 무시
                pass

            # 파일 업로드
            for file in files:
                local_file = os.path.join(root, file)
                remote_file = os.path.join(target_path, file).replace('\\', '/')
                sftp.put(local_file, remote_file)
                print(f"업로드 성공: {remote_file}")
        return True
    except Exception as e:
        print(f"파일 업로드 중 오류 발생: {e}")
        return False
# ===============================================================================
#                            데피니션
# ===============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
folders = [item for item in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, item))]
error_path=os.path.join(current_dir, 'error.txt')
open(error_path, 'w').close()
output_path=os.path.join(current_dir, 'output.txt')
open(output_path, 'w').close()
default_dir=os.path.join(current_dir, 'default')

xml_code=f"""
<url>
    <loc>@@domain@@/</loc>
    <lastmod>@@lastmod@@</lastmod>
    <priority>@@priority</priority>
</url>
"""

# ===============================================================================
#                            런
# ===============================================================================
def run():
    print('프로그램 실행')

    try:
        for folder_idx, folder in enumerate(folders,start=1):
            tunnel=None
            
            if folder =='default':continue
            print('  '*50,end='\r')
            print(f'[{folder_idx}/{len(folders)-1}] {folder} 작업 시작')
            folder_path = os.path.join(current_dir, folder)
            input_files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)) and file.endswith('.csv')]
            config_path=os.path.join(folder_path, 'config.ini')
            config = configparser.ConfigParser()
            try:
                config.read(config_path, encoding='cp949')
            except:
                config.read(config_path, encoding='utf-8')
            main_title=config['DEFAULT']['title']
            domain=config['DEFAULT']['domain']
            aws_path=config['DEFAULT']['aws_path']
            bg_color=config['DEFAULT']['bg_color']
            ca_pub_code=config['DEFAULT']['ca_pub_code']
            search_console_code=config['DEFAULT']['search_console_code']
            db_path=aws_path.split('/')[3]
            try:
                tunnel=create_ssh_tunnel(tunnel,domain)
                conn = pymysql.connect(
                    host='127.0.0.1',
                    port=tunnel.local_bind_port,
                    user='',
                    password='',
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                )
                with conn.cursor() as cursor:
                    sql = f"CREATE DATABASE IF NOT EXISTS `{db_path}`"
                    cursor.execute(sql)
                    sql=f"USE `{db_path}`"
                    cursor.execute(sql)
                    sql = """CREATE TABLE IF NOT EXISTS `` (
                        `seq` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        `code` varchar(255),
                        `title` varchar(255),
                        `subtitle` varchar(255),
                        `content` varchar(1000),
                        `image` varchar(255),
                        `link` varchar(255),
                        `reg_date` timestamp NOT NULL DEFAULT current_timestamp(),
                        `update_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
                    cursor.execute(sql)
                    conn.commit()
                conn.close()
            except Exception as e:
                print(f'  ㄴ 에러 발생: {e}')
                with open(error_path, 'a') as f:
                    f.write(f'{datetime.now()} - {folder} -{e}\n')
                with open(output_path, 'a') as f:
                    f.write(f'{datetime.now()}\t{folder}\t실패\n')
                continue


            index_php_path=os.path.join(default_dir, 'index.php')
            sub_php_path=os.path.join(default_dir, 'sub.php')
            header_php_path=os.path.join(default_dir, 'header.php')
            front_header_php_path=os.path.join(default_dir, 'front_header.php')
            temp_path=r"C:/temp/site"
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)

            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            css_dir=os.path.join(default_dir, 'css')
            img_dir=os.path.join(default_dir, 'img')
            adminer_php_path=os.path.join(default_dir, 'adminer.php')
            
            db_php_path=os.path.join(default_dir, 'db.php')
            print('  ㄴ 각종 파일 title 작성 시도',end='\r')
            try:
                index_php=open(index_php_path, 'r', encoding='utf-8').read()
                sub_php=open(sub_php_path, 'r', encoding='utf-8').read()
                header_php=open(header_php_path, 'r', encoding='utf-8').read()
                front_header_php=open(front_header_php_path, 'r', encoding='utf-8').read()
                db_php=open(db_php_path, 'r', encoding='utf-8').read()
                index_php=index_php.replace('@@TITLE@@',main_title)
                sub_php=sub_php.replace('@@TITLE@@',main_title)
                header_php=header_php.replace('@@TITLE@@',main_title)
                front_header_php=front_header_php.replace('@@TITLE@@',main_title)
                front_header_php=front_header_php.replace('@@ca-pub-코드@@',ca_pub_code)
                front_header_php=front_header_php.replace('@SEARCH_CONSOLE@',search_console_code)
                css_dir=os.path.join(default_dir, 'css')
                shutil.copytree(css_dir, os.path.join(temp_path, 'css'))
                common_css_path=os.path.join(css_dir, 'common.css')
                common_css=open(common_css_path, 'r', encoding='utf-8').read()
                common_css=common_css.replace('@@bg_color@@',bg_color)
                db_php=db_php.replace('@@dbname@@',db_path)
                db_php=db_php.replace('@@user@@','root')
                with open(os.path.join(temp_path, 'index.php'), 'w', encoding='utf-8') as f:
                    f.write(index_php)
                with open(os.path.join(temp_path, 'sub.php'), 'w', encoding='utf-8') as f:
                    f.write(sub_php)
                with open(os.path.join(temp_path, 'header.php'), 'w', encoding='utf-8') as f:
                    f.write(header_php)
                with open(os.path.join(temp_path, 'front_header.php'), 'w', encoding='utf-8') as f:
                    f.write(front_header_php)
                with open(os.path.join(temp_path, 'db.php'), 'w', encoding='utf-8') as f:
                    f.write(db_php)
                temp_css_dir=os.path.join(temp_path, 'css')
                with open(os.path.join(temp_css_dir, 'common.css'), 'w', encoding='utf-8') as f:
                    f.write(common_css)
                shutil.copytree(img_dir, os.path.join(temp_path, 'img'))
                shutil.copy2(adminer_php_path, os.path.join(temp_path, 'adminer.php'))
                last_mode=datetime.now().strftime('%Y-%m-%d')+'T'+datetime.now().strftime('%H:%M:%S')+'+00:00'
                xml_code=f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                            xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
                            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">

                            
                <url>
                    <loc>https://{domain}/</loc>
                    <lastmod>{last_mode}</lastmod>
                    <priority>1.00</priority>
                </url>
                <url>
                    <loc>https://{domain}/index.php/</loc>
                    <lastmod>{last_mode}</lastmod>
                    <priority>1.00</priority>
                </url>
                """
                with open(os.path.join(temp_path, 'sitemap.xml'), 'w', encoding='utf-8') as f:
                    f.write(f'{xml_code}\n')
            
            except Exception as e:
                print(f'  ㄴ 에러 발생: {e}')
                with open(error_path, 'a') as f:
                    f.write(f'{datetime.now()} - {folder} -{e}\n')
                with open(output_path, 'a') as f:
                    f.write(f'{datetime.now()}\t{folder}\t실패\n')
                continue
            print('  ㄴ 각종 파일 title 작성 완료')
            detail_lst=[]
            code_lst=[]
            for input_idx, input_file in enumerate(input_files,start=1):
                print('  '*50,end='\r')
                print(f'  ㄴ [{input_idx}/{len(input_files)}] {input_file} 파일 처리 시작')
                input_path = os.path.join(folder_path, input_file)
                df = pd.read_csv(input_path, encoding='utf-8')
                for i in range(len(df)):
                    detail_lst.append([df['seq'][i],df['페이지 구분코드'][i],df['타이틀'][i],df['서브타이틀'][i],df['내용'][i]])#,df['이미지삽입'][i],df['링크삽입'][i],df['reg_date'][i],df['update_time'][i]])
                    seq=df['seq'][i]
                    page_code=df['페이지 구분코드'][i]
                    if page_code not in code_lst:
                        code_lst.append(page_code)
                    csv_title=df['타이틀'][i] if pd.notna(df['타이틀'][i]) else ''
                    sub_title=df['서브타이틀'][i]
                    content=df['내용'][i]
                    tunnel=create_ssh_tunnel(tunnel,domain)
                    connection=create_db_connection(tunnel,db_path)
                    if connection is None:
                        print('  ㄴ 데이터베이스 연결 실패')
                        with open(output_path, 'a') as f:
                            f.write(f'{datetime.now()}\t{folder}\t실패\n')
                        continue
                    cursor = connection.cursor()
                    try:
                        sql=f"INSERT IGNORE INTO `` (`seq`, `code`, `title`, `subtitle`, `content`, `reg_date`, `update_time`) VALUES ('{seq}', '{page_code}', '{csv_title}', '{sub_title}', '{content}', now(), now())"
                        cursor.execute(sql)
                        connection.commit()
                    except Exception as e:
                        print(f'  ㄴ 에러 발생: {e}')
                        with open(error_path, 'a') as f:
                            f.write(f'{datetime.now()} - {folder} -{e}\n')
                        with open(output_path, 'a') as f:
                            f.write(f'{datetime.now()}\t{folder}\t실패\n')
                        continue
                    finally:
                        connection.close()
                print(f'  ㄴ [{input_idx}/{len(input_files)}] {input_file} 파일 처리 완료',end='\r')
            for code in code_lst:
                xml_code=f"""
                <url>
                    <loc>https://{domain}/sub.php?code={code}</loc>
                    <lastmod>{last_mode}</lastmod>
                    <priority>0.80</priority>
                </url>
                """
                with open(os.path.join(temp_path, 'sitemap.xml'), 'a', encoding='utf-8') as f:
                    f.write(f'{xml_code}\n')
            xml_code=f"""
            </urlset>
            """
            print('  '*50,end='\r')
            print(f'  ㄴ [{folder_idx}/{len(folders)-1}] {folder} input 파일 처리 완료')
            print('  ㄴ 웹사이트 파일 업로드 시도',end='\r')
            try:
                ssh = connect_to_server(domain, '', '')
                sftp = ssh.open_sftp()
                success=upload_files(sftp, temp_path, aws_path)
                if success:
                    print('  ㄴ 웹사이트 파일 업로드 성공')
                else:
                    print('  ㄴ 웹사이트 파일 업로드 실패')
                    with open(output_path, 'a') as f:
                        f.write(f'{datetime.now()}\t{folder}\t실패\n')
            except Exception as e:
                print(f'  ㄴ 에러 발생: {e}')
                with open(error_path, 'a') as f:
                    f.write(f'{datetime.now()} - {folder} -{e}\n')
                with open(output_path, 'a') as f:
                    f.write(f'{datetime.now()}\t{folder}\t실패\n')
                
    except Exception as e:
        print(f'  ㄴ 에러 발생: {e}')
        with open(error_path, 'a') as f:
            f.write(f'{datetime.now()} - {folder} -{e}\n')
        with open(output_path, 'a') as f:
            f.write(f'{datetime.now()}\t{folder}\t실패\n')

# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '나태환'
__requester__ = ''
__latest_editor__ = '나태환'
__registration_date__ = '250203'
__latest_update_date__ = '250203'
__version__ = 'v1.00'
__title__ = '애드센스 승인용 사이트 자동화 프로그램'
__desc__ = '애드센스 승인용 사이트 자동 제작 프로그램'
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