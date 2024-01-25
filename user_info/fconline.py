from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import requests
from nexonAPI import nexon_api
from fake_useragent import UserAgent

def rankerCwl(save_path, api_key):
    # 데이터 저장을 위한 현재시간
    now = datetime.now()
    cur_time = now.strftime('%y%m%d%H')

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
    user_rank_num, user_lvs, user_names, user_prices, user_rank_scores, user_ranks = [], [], [], [], [], []

    # 반복 횟수 설정
    current_iter = 0
    total_iter = 50

    while current_iter < total_iter:
        time.sleep(1)
        for i in range(2, 12):
            time.sleep(1)
            # 요소를 찾을때 까지 대키
            user_info_wait = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="inner"]/div[1]/div/div[2]')))
            WebDriverWait(user_info_wait, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'tr')))
            WebDriverWait(user_info_wait, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.td.rank_coach span.ico_rank img')))
            
            # 요소 찾기
            user_info = user_info_wait.find_elements(By.CLASS_NAME, 'tr')
            user_ranks_url = user_info_wait.find_elements(By.CSS_SELECTOR, 'span.td.rank_coach span.ico_rank img')

            for user in user_info:
                info = user.text.split('\n')
                user_rank_num.append(info[0])
                user_lvs.append(info[1])
                user_names.append(info[2])
                user_prices.append(info[3].split(' ')[0])
                user_rank_scores.append(info[4])
                
            for user_rank in user_ranks_url:
                src = user_rank.get_attribute('src').split('/')[-1][4:-4]
                user_ranks.append(src)
                
            if i == 11:
                next_list_wait = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="inner"]/div[2]/div/a[3]')))
                next_list = next_list_wait.click()
                break
            
            # 요소를 찾을 때까지 대기
            next_page_xpath = f'//*[@id="inner"]/div[2]/div/ul/li[{i}]/a'
            next_page_wait = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, next_page_xpath)))

            # JavaScript를 사용하여 스크롤합니다.
            browser.execute_script("arguments[0].click();", next_page_wait)
            
            time.sleep(1)
            
        # 반복 횟수 증가
        tqdm.write(f"Processing iteration {current_iter + 1}/{total_iter}")
        current_iter += 1

    # nexon api로 ouid 가져오기
    ua = UserAgent()
    # api key 입력하기
    headers = {
        "User-Agent" : ua.random,
        "x-nxopen-api-key": api_key
        }

    pbar = tqdm(range(len(user_names)))

    # rank mapping
    kor_rank = ['슈퍼챔피언스', '슈퍼챌린저', '챌린저1부', '챌린저2부', '챌린저3부', '월드클래스1부', '월드클래스2부', '월드클래스3부', '프로1부']
    kor_rank_dict = dict(zip(sorted(list(set(user_ranks))), kor_rank))

    ouid_ls = []
    for i in pbar:
        urlString = "https://open.api.nexon.com/fconline/v1/id?nickname=" + user_names[i]
        ouid = nexon_api(urlString, headers)
        ouid_ls.append(ouid.get('ouid'))

    # df으로 저장
    df = pd.DataFrame({
        'rankNo' : user_rank_num,
        'LV' : user_lvs,
        'nickName' : user_names,
        'rankScore' : user_rank_scores,
        'tier' : user_ranks,
        'price' : user_prices,
        'ouid' : ouid_ls
    })

    df['korRankTier'] = df['tier'].map(kor_rank_dict)
    df = df.dropna()
    df.to_parquet(f'{save_path}/{cur_time}_user_info.parquet', engine='pyarrow', index=False)