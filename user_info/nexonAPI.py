import requests
import time
from datetime import datetime

def nexon_api(urlString, headers):
    error_message = ['OPENAPI00003', 'OPENAPI00005', 'OPENAPI00006', 'OPENAPI00009']
    
    while True:
        response = requests.get(urlString, headers=headers)
        error_code = None

        try:
            error_code = response.json().get('error').get('name')
        except (AttributeError, ValueError):
            pass

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
            break
        
        elif response.status_code == 200:
            data = response.json()
            return data

        elif response.status_code == 429:
            now = datetime.now()
            cur_time = now.strftime('%m/%d/%Y %I:%M:%S %p')
            print(cur_time, 'Too Many Requests')
            time.sleep(10)

        elif response.status_code == 400:
            now = datetime.now()
            cur_time = now.strftime('%m/%d/%Y %I:%M:%S %p')
            error_code = response.json().get('error').get('name')
            if error_code == 'OPENAPI00004':
                data = response.json()
                print(cur_time, '파라미터 누락 또는 유효하지 않음')
                return data