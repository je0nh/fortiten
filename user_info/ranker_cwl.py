from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import requests

# API 설정
api_key = input('API key를 입력하세요: ')
user_ouids = []
pbar = tqdm(range(1000))
error_message = ['OPENAPI00003', 'OPENAPI00005','OPENAPI00006', 'OPENAPI00009']

# chrome driver option setting
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("headless")

# linux 환경에서 필요한 option
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Chrome 드라이버 생성
browser = webdriver.Chrome(options=chrome_options)

# 접속할 웹페이지 URL
url = 'https://fconline.nexon.com/datacenter/rank'

# 웹페이지 열기
browser.get(url)

# 랭커 유저 리스트
user_name_ls = []
rank_ls = []

# 반복 횟수 초기화
count = 0

# 5번 반복
while count < 50:
    for i in range(1, 11):
        try:
            # 다음 페이지로 이동
            link = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//*[@id="inner"]/div[2]/div/ul/li[{i}]/a'))
            )

            # 스크롤링
            browser.execute_script("arguments[0].scrollIntoView();", link)

            # 클릭 시도
            try:
                link.click()
            except Exception as e:
                print(f"클릭 오류 발생: {e}")
                # 클릭이 불가능한 경우 JavaScript로 클릭 시도
                browser.execute_script("arguments[0].click();", link)

            # 이전 링크가 stale될 때까지 대기
            WebDriverWait(browser, 10).until(EC.staleness_of(link))
        except Exception as e:
            print(f"오류 발생: {e}")
            # 필요에 따라 오류 처리
        
        for j in range(1, 21):
            try:
                # 유저 X.PATH 불러오기
                user = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="inner"]/div[1]/div/div[2]/div[{j}]/span[2]'))
                )

                # 유저 이름 가져오기
                user_name = user.find_element(By.CLASS_NAME, 'name.profile_pointer').text

                # 유저 랭크 가져오기
                rank_css = user.find_element(By.CSS_SELECTOR, 'span.ico_rank img')
                rank_url = rank_css.get_attribute("src")
                rank = rank_url.split('/')[-1][4:-4]

                user_name_ls.append(user_name)
                rank_ls.append(rank)

            except Exception as e:
                print(f"오류 발생: {e}")
                # 필요에 따라 오류 처리

    time.sleep(1)
    # 다음 페이지로 이동 후 대기
    next_page_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, f'//*[@id="inner"]/div[2]/div/a[3]'))
    )

    # 스크롤링
    browser.execute_script("arguments[0].scrollIntoView();", next_page_button)

    # 클릭 시도
    try:
        next_page_button.click()
    except Exception as e:
        print(f"클릭 오류 발생: {e}")
        # 클릭이 불가능한 경우 JavaScript로 클릭 시도
        browser.execute_script("arguments[0].click();", next_page_button)

    time.sleep(1)

    # 반복 횟수 증가
    count += 1

# rank mapping
rank_no = [i for i in range(1, len(user_name_ls) + 1)]
kor_rank = ['슈퍼챔피언스', '슈퍼챌린저', '챌린저1부', '챌린저2부', '챌린저3부', '월드클래스1부', '월드클래스2부', '월드클래스3부', '프로1부']
kor_rank_dict = dict(zip(sorted(list(set(rank_ls))), kor_rank))

# df csv로 저장
df = pd.DataFrame({"rank_no" : rank_no, "nickname" : user_name_ls, "rank_tier" : rank_ls})
df['kor_rank_tier'] = df['rank_tier'].map(kor_rank_dict)

# API로 ouid 받아오기
for i in pbar:
    headers = {
            "x-nxopen-api-key": api_key
        }
    
    urlString = "https://open.api.nexon.com/fconline/v1/id?nickname=" + user_name_ls[i]
    response = requests.get(urlString, headers = headers)
    try:
        error_code = response.json().get('error').get('name')
    except:
        pass
    
    if response.status_code == 400 and error_code in error_message:
        _now = datetime.now()
        _cur_time = _now.strftime('%m/%d/%Y %I:%M:%S %p')
        
        if error_code == 'OPENAPI00003':
            print(i, _cur_time, '유효하지 않은 식별자')
        elif error_code == 'OPENAPI00005':
            print(i, _cur_time, '유효하지 않은 API KEY')
        elif error_code == 'OPENAPI00006':
            print(i, _cur_time, '유효하지 않은 게임 또는 API PATH')
        elif error_code == 'OPENAPI00009':
            print(i, _cur_time, '데이터 준비 중')
        break
    
    while True:
        if response.status_code == 200:
            user_ouid = response.json().get("ouid")
            user_ouids.append(user_ouid)
            break
        elif response.status_code == 429:
            # API 호출이 1000건이 되면 종료
            if i == 999:
                break
            _now = datetime.now()
            _cur_time = _now.strftime('%m/%d/%Y %I:%M:%S %p')
            print(i, _cur_time, 'Too Many Requests')
            time.sleep(8)
            response = requests.get(urlString, headers = headers)  
        elif response.status_code == 400:
            _now = datetime.now()
            _cur_time = _now.strftime('%m/%d/%Y %I:%M:%S %p')
            error_code = response.json().get('error').get('name')
            if error_code == 'OPENAPI00004':
                # user_ouid = response.json().get("ouid")
                user_ouids.append('0')
                print(i, _cur_time, '파라미터 누락 또는 유효하지 않음')
                break

# data 저장
new_df = df[:1000]
new_df['ouid'] = user_ouids

new_df.to_parquet('./data/user_info.parquet', engine='pyarrow', index=False)