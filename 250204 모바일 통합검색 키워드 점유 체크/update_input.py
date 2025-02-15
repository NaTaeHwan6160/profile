if True:
    import subprocess
    try:
        from tqdm import tqdm
    except ImportError:
        subprocess.run([sys.executable,'-m','pip','install','--upgrade','tqdm'])
        import tqdm
    import os
    import sys
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
    try:
        import shutil
    except ImportError:
        subprocess.run([sys.executable,'-m','pip','install','--upgrade','shutil'])
        import shutil

def read_input():
    dup_check_lst=[]
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
    client = gspread.authorize(creds)
    try:
        print('기존 input.txt를 백업합니다.')
        backup_input=open('input.txt','r').read()
    except:
        print('기존 input.txt가 없습니다. 새로 불러옵니다.')
    try:
        with open("input.txt",'w') as f:
            print('키워드 불러오기')
            sheet = client.open_by_url('').get_worksheet(0)
            
            data = sheet.get_all_values()
            for row in tqdm(data[2:],desc="input"):  # 3행부터 시작 (인덱스 2부터)
                
                keyword = row[5]
                check=row[6]
                if keyword and keyword not in dup_check_lst and check and '/' not in check:
                    f.write(f'{keyword}\n')
                    dup_check_lst.append(keyword)

            
    except Exception as e:
        print(f"시트 읽는 중 에러: {e}")
        print('백업된 파일을 사용합니다.')
        with open('input.txt','w') as f:
            f.write(backup_input)


def read_url_list_from_google():  # 구글 스프레드시트에서 광고 목록 읽기 함수
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    dup_check=[]
    creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
    client = gspread.authorize(creds)
    try:
        print('기존 our_url.txt를 백업합니다.')
        backup_input=open('our_url.txt','r').read()
    except:
        print('기존 our_url.txt가 없습니다. 새로 불러옵니다.')
    try:
        with open("our_url.txt",'w') as f:
            print('')
            sheet = client.open_by_url('').get_worksheet(0)
            
            data = sheet.get_all_values()
            for row in tqdm(data[1:],desc="blog_url"):  # 3행부터 시작 (인덱스 2부터)
                
                url = row[15]
                if url and url not in dup_check:
                    f.write(f'{url}\n')
                    dup_check.append(url)
            print('')
            sheet = client.open_by_url('').get_worksheet(0)
            
            data = sheet.get_all_values()
            for row in tqdm(data[1:],desc="blog_url"):  # 3행부터 시작 (인덱스 2부터)
                
                url = row[15]
                if url and url not in dup_check:
                    f.write(f'{url}\n')
                    dup_check.append(url)
            print('')
            sheet = client.open_by_url('').get_worksheet(0)
            
            data = sheet.get_all_values()
            for row in tqdm(data[1:],desc="blog_url"):  # 3행부터 시작 (인덱스 2부터)
                
                url = row[15]
                if url and url not in dup_check:
                    f.write(f'{url}\n')
                    dup_check.append(url)
            print('')
            sheet = client.open_by_url('').get_worksheet(0)
            
            data = sheet.get_all_values()
            for row in tqdm(data[1:],desc="blog_url"):  # 3행부터 시작 (인덱스 2부터)
                
                url = row[15]
                if url and url not in dup_check:
                    f.write(f'{url}\n')
                    dup_check.append(url)      
            print('')
            sheet = client.open_by_url('').get_worksheet(0)
            
            data = sheet.get_all_values()
            for row in tqdm(data[1:],desc="blog_url"):  # 3행부터 시작 (인덱스 2부터)
                
                url = row[15]
                if url and url not in dup_check:
                    f.write(f'{url}\n')
                    dup_check.append(url)
            print('')
            sheet = client.open_by_url('').get_worksheet(0)
            
            data = sheet.get_all_values()
            for row in tqdm(data[2:],desc="blog_url"):  # 3행부터 시작 (인덱스 2부터)
                
                url = row[14]
                if url and url not in dup_check and 'http' in url:
                    f.write(f'{url}\n')
                    dup_check.append(url)
                # else:
                #     url=row[41]
                #     if url:
                #         f.write(f'{url}\n')
            print('')
            sheet = client.open_by_url('').get_worksheet(0)
            
            data = sheet.get_all_values()
            for row in tqdm(data[3:],desc="blog_url"):  # 3행부터 시작 (인덱스 2부터)
                
                url = row[14]
                if url and url not in dup_check:
                    f.write(f'{url}\n')
                    dup_check.append(url)
            print('')
            sheet = client.open_by_url('').get_worksheet(1)
            
            data = sheet.get_all_values()
            for row in tqdm(data[2:],desc="cafe_url"):  # 3행부터 시작 (인덱스 2부터)
                url = row[15]
                if url and url not in dup_check:
                    f.write(f'{url}\n')
                    dup_check.append(url)
            
    except Exception as e:
        print(f"시트 읽는 중 에러: {e}")
        print('백업된 파일을 사용합니다.')
        with open('our_url.txt','w') as f:
            f.write(backup_input)
       