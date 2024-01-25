import requests
import time
from datetime import datetime
from fake_useragent import UserAgent
import json

def nexon_api(urlString, headers):
    # 오류 메세지
    error_message = ['OPENAPI00003', 'OPENAPI00005', 'OPENAPI00006', 'OPENAPI00009']
    
    # 조건에 맞을 때 까지 반복
    while True:
        # API 요청
        response = requests.get(urlString, headers=headers)
        error_code = None

        try:
            # API 요청 시 error가 발생하면 error의 'name' 값 가져오기
            error_code = response.json().get('error').get('name')
        except (AttributeError, ValueError):
            pass
        
        # error 코드가 400이고 에러 이름이 error_message 있으면 API 호출 종료
        if response.status_code == 400 and error_code in error_message:
            now = datetime.now()
            cur_time = now.strftime('%m/%d/%Y %I:%M:%S %p')

            if error_code == 'OPENAPI00003':
                print(cur_time, '유효하지 않은 식별자')
            elif error_code == 'OPENAPI00005':
                print(cur_time, '유효하지 않은 API KEY')
            elif error_code == 'OPENAPI00006':
                print(cur_time, '유효하지 않은 게임 또는 API PATH')
            elif error_code == 'OPENAPI00009':
                print(cur_time, '데이터 준비 중')
            breakpoint
        # error 코드가 200이면 데이터 적재
        elif response.status_code == 200:
            data = response.json()
            return data
        # error 코드가 429이면 잠시 기다렸다가 API 다시 호출
        elif response.status_code == 429:
            now = datetime.now()
            cur_time = now.strftime('%m/%d/%Y %I:%M:%S %p')
            print(cur_time, 'Too Many Requests')
            time.sleep(10)
        # error 코드가 400이고 유저의 이름 변경으로 인해 파라미터가 누락되었다고 나오면 null값을 append
        elif response.status_code == 400:
            now = datetime.now()
            cur_time = now.strftime('%m/%d/%Y %I:%M:%S %p')
            error_code = response.json().get('error').get('name')
            if error_code == 'OPENAPI00004':
                data = response.json()
                print(cur_time, '파라미터 누락 또는 유효하지 않음')
                return data

def getMatchData(api_key, matchid, match_path, shoot_path, player_path):
    # nexon api로 ouid 가져오기
    ua = UserAgent()

    # header, url 정보 입력
    headers = {
        "User-Agent" : ua.random,
        "x-nxopen-api-key": api_key
        }
    match_detail_url = f'https://open.api.nexon.com/fconline/v1/match-detail?matchid={matchid}'
    
    # NEXON API로 match detail 가져오기
    match_detail = nexon_api(urlString=match_detail_url, headers=headers)

    # match detail 빈 리스트 만들기
    user_match_detail = []

    # match 고유 id 가져오기
    match_id = match_detail.get("matchId")

    # API에서 가져온 유저 정보들의 key 정보를 list로 추출해서 추출한 key로 values의 리스트 생성
    # zip() 함수 이용해서 dictionary 형태로 만들어서 json으로 저장
    # 한 매치에 2명의 유저가 플레이하기 때문에 밑의 과정을 2번 반복
    for i in range(2):
        # API로 가져온 match detail 정보에서 'matchInfo' key를 제외한 리스트 생성
        match_detail_keys = list(match_detail.keys())[:-1]
        
        # 'matchInfo' key를 제외한 나머지 key의 value를 조회해서 빈 list로 append
        match_detail_info_ls = []
        for match_detail_key in match_detail_keys:
            match_detail_info_ls.append(match_detail.get(match_detail_key))
        
        # match detail에서 'matchInfo'에 해당하는 value 가져오기
        match_info = match_detail.get('matchInfo')[i]
        
        # 가져온 value에서의 key값들 가져오고 user ouid값 가져와서 match_detail_info_ls에 append
        match_info_keys = list(match_info.keys())
        match_detail_info_ls.append(match_info.get('ouid'))
        
        # 'matchInfo'에서 'matchDetail', 'shoot', 'pass', 'defence'에 대한 key값 가져오기
        # 'shootDetail'과 'player'는 그 안에 여러 값들을 가지기 때문에 따로 json파일로 만들어서 저장함
        for match_info_key in match_info_keys:
            if match_info_key == 'matchDetail':
                matchDetail_keys = list(match_info.get('matchDetail').keys())
            elif match_info_key == 'shoot':
                shoot_keys = list(match_info.get('shoot').keys())
            elif match_info_key == 'pass':
                pass_keys = list(match_info.get('pass').keys())
            elif match_info_key == 'defence':
                defence_keys = list(match_info.get('defence').keys())
        
        # 'matchDetail', 'shoot', 'pass', 'defence'의 각 key를 조회해서 value를 가져오고 match_detail_info_ls에 append
        for matchDetail_key in matchDetail_keys:
            match_detail_info_ls.append(match_info.get('matchDetail').get(matchDetail_key))
        for shoot_key in shoot_keys:
            match_detail_info_ls.append(match_info.get('shoot').get(shoot_key))       
        for pass_key in pass_keys:
            match_detail_info_ls.append(match_info.get('pass').get(pass_key))       
        for defence_key in defence_keys:
            match_detail_info_ls.append(match_info.get('defence').get(defence_key))
        
        # key list 합치기
        sum_match_detail_keys = match_detail_keys + match_info_keys[:1] + matchDetail_keys + shoot_keys + pass_keys + defence_keys
        
        # key list와 value list를 dictionary 형태로 합쳐줌
        user_match_detail.append(dict(zip(sum_match_detail_keys, match_detail_info_ls)))

        # user ouid 가져오기
        user_ouid = match_info.get('ouid')
        
        # 'shootDetail' value 가져오기
        shoot_details = match_info.get('shootDetail')

        # 'shootDetail'에 'matchId', 'ouid'저장
        for shoot_detail in shoot_details:
            shoot_detail['matchId'] = match_id
            shoot_detail['ouid'] = user_ouid

        # 'shootDetail' 저장
        shoot_json_file_path = f'{shoot_path}/{match_id}_{user_ouid}_shootDetail.json'
        with open(shoot_json_file_path, 'w') as jsonfile:
            json.dump(shoot_details, jsonfile)
        
        # 'player' 값 가져오기
        player_get_infos = match_info.get('player')
        
        # player 정보를 담을 빈 list 만들기
        player_info_ls = []
        for player_get_info in player_get_infos:
            
            player_get_info_keys = list(player_get_info.keys())

            # matchId와 ouid 값을 미리 넣은 리스트 만들어서 primary key로 사용할수 있게함
            player_info  = [match_id, user_ouid]
            
            # 각 선수에서 'status' 제외한 값을 player_info에 append
            for player_get_info_key in player_get_info_keys[:-1]:
                player_info.append(player_get_info.get(player_get_info_key))

            # 각 선수에서 'status' 안의 key들 가져오기
            player_status = player_get_info.get(player_get_info_keys[-1])

            # 'status'안의 key값의 value 가져와서 player_info에 append
            player_status_keys = list(player_status.keys())
            for player_status_key in player_status_keys:
                player_info.append(player_status.get(player_status_key))

            # 추출한 key 값들 합쳐주기
            player_get_info_keys = ['matchId', 'ouid'] + player_get_info_keys[:-1] + player_status_keys

            # player_get_info_keys와 player_info를 dictionary로 합쳐주고 player_info_ls에 각 선수 정보를 append
            player_info_ls.append(dict(zip(player_get_info_keys, player_info)))

        # 선수 정보 저장
        player_json_file_path = f'{player_path}/{match_id}_{user_ouid}_playerDetail.json'
        with open(player_json_file_path, 'w') as jsonfile:
            json.dump(player_info_ls, jsonfile)

    # 'matchDetail' 저장
    match_json_file_path = f'{match_path}/{match_id}_matchDetail.json'
    with open(match_json_file_path, 'w') as jsonfile:
        json.dump(user_match_detail, jsonfile)