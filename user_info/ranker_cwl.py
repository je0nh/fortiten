from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Chrome 드라이버 생성
browser = webdriver.Chrome()

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
                EC.presence_of_element_located((By.XPATH, f'//*[@id="inner"]/div[2]/div/ul/li[{i}]/a'))
            )
            link.click()
            
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
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, f'//*[@id="inner"]/div[2]/div/a[3]'))
    ).click()

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

df.to_csv("./user_info.csv", encoding='utf-8', index=False)