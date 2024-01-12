from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

def read_file(read_file_path):
    with open(read_file_path, "r") as f:
        data = f.read().split(',\n')
    return data

def save_file(save_file_path, data):
    with open(save_file_path, "w") as f:
        for item in data:
            f.write(item + ",\n")

# Chrome 드라이버 생성
browser = webdriver.Chrome()

# 접속할 웹페이지 URL
url = 'https://fconline.nexon.com/datacenter/rank'

# 웹페이지 열기
browser.get(url)

# 랭커 유저 리스트
ranker_user_ls = []

# 반복 횟수 초기화
count = 0

# 5번 반복
while count <= 5:
    for i in range(2, 10):
        for j in range(1, 20):
            try:
                # 유저 이름 가져오기
                user_name = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="inner"]/div[1]/div/div[2]/div[{j}]/span[2]/span[2]/span[2]'))
                ).text
                ranker_user_ls.append(user_name)
                time.sleep(0.04)
            except Exception as e:
                print(f"오류 발생: {e}")
                # 필요에 따라 오류 처리

        try:
            # 다음 페이지로 이동
            link = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//*[@id="inner"]/div[2]/div/ul/li[{i}]/a'))
            )
            link.click()

            # 클릭 후 300ms 대기
            time.sleep(0.3)
            
            # 이전 링크가 stale될 때까지 대기
            WebDriverWait(browser, 10).until(EC.staleness_of(link))
        except Exception as e:
            print(f"오류 발생: {e}")
            # 필요에 따라 오류 처리

    # 다음 페이지로 이동 후 대기
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, f'//*[@id="inner"]/div[2]/div/a[3]'))
    ).click()

    time.sleep(0.5)
    
    # 새로운 페이지 로드를 대기
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, f'//*[@id="inner"]/div[2]/div/ul/li[2]/a'))
    )

    # 반복 횟수 증가
    count += 1

# txt 파일로 저장
file_path = "./data/fc_ranker_name.txt"
save_file(file_path, ranker_user_ls)

# API 키 입력
headers = {
  "x-nxopen-api-key": "API-key"
}
    
# oudi 제한
# ranker_user_ls[:500]

# oudi 가져오기
user_ouids = []
for fc_ranker_name in ranker_user_ls:
    urlString = "https://open.api.nexon.com/fconline/v1/id?nickname=" + fc_ranker_name
    response = requests.get(urlString, headers = headers)
    user_ouid = response.json().get("ouid")
    user_ouids.append(user_ouid)

# oudi 저장
oudi_file_path = "./data/user_ouid.txt"
save_file(oudi_file_path, user_ouids)

# 유저 매치 id 조회, 유저당 100개까지 조회가능
matches = []
for user_ouid in user_ouids:
    match_urlString = f"https://open.api.nexon.com/fconline/v1/user/match?ouid={user_ouid}&matchtype=50"
    match_response = requests.get(match_urlString, headers = headers)
    match = match_response.json()
    matches.append(match)

# To many rquest로 dict가 list에 들어가는거 방지
matches = [item for item in matches if not isinstance(item, dict)]

# 저장
user_match_file_path = "./data/user_match.txt"
save_file(user_match_file_path, matches)

# 매치 정보 가져오기
_match_details = []
for match_id in matches:
    match_record_detail_urlString = f"https://open.api.nexon.com/fconline/v1/match-detail?matchid={match_id}"
    match_record_detail_response = requests.get(match_record_detail_urlString, headers = headers)
    match_detail = match_record_detail_response.json()
    _match_details.append(match_detail)

match_details = sum(_match_details, [])

# 저장
match_details_file_path = "./data/match_detail.txt"
save_file(match_details_file_path, match_details)