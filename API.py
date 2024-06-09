# 통합 API

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta

import boto3
from boto3.dynamodb.conditions import Key


aws_access_key_id = ''
aws_secret_access_key = ''

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2',
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)

dynamodb_client = boto3.client('dynamodb', region_name='ap-northeast-2',
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)

# 특정 테이블 선택
outside_table_name = 'Outside'
client_table_name = 'Customer'
client_table = dynamodb.Table(client_table_name)

# 특정 항목 가져오기
key_value = 'phoenix' # client_id
response = client_table.get_item(
    Key={
        'email': key_value
    }
)

# Read data from Excel file
df = pd.read_excel('/home/joljak/Area.xlsx')

ad_item = response.get('Item', {})
city = ad_item.get('city')
district = ad_item.get('district')
town = ad_item.get('town')

if len(city) > 0:
    if len(district) > 0:
        if len(town) > 0:
            filtered_df = df[(df['1단계'] == city) & (df['2단계'] == district) & (df['3단계'] == town)]
            if not filtered_df.empty:
                x_coordinate = filtered_df['격자 X'].values[0]
                y_coordinate = filtered_df['격자 Y'].values[0]
                #print(f"searched location: {city} {district} {town}")
            else:
                print("no locations found")
        else:
            filtered_df = df[(df['1단계'] == city) & (df['2단계'] == district)]
            if not filtered_df.empty:
                y_coordinate = filtered_df['격자 Y'].values[0]
                print(f"searched location: {city} {district} {town}")
                print(f"X coordinates: -")
                print(f"Y coordinates: {y_coordinate}")
            else:
                print("no locations found")
    else:
        filtered_df = df[(df['1단계'] == city)]
        if not filtered_df.empty:
            x_coordinate = filtered_df['격자 X'].values[0]
            y_coordinate = filtered_df['격자 Y'].values[0]
            print(f"searched location: {city} {district} {town}")
        else:
            print("no locations found")
else:
    print("please enter a location")

we_url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
tm_url = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getTMStdrCrdnt'
ne_url = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList'
pm_url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'

key = 'vmsJG48NnTphuvVephYEKCU6jv96X/cgJYqY5lwwnvDwPlJ9LnhfSFrssbOfKrNeE3ggWdH4o1bG9v5RBg9iRQ=='

now = datetime.today()
current_time = int(now.strftime('%H%M'))
fcst_time = int(now.strftime('%H00'))

now_date_time = now.strftime("%Y-%m-%d %H:20")

# 현재 시간에 따라 base_time 조정
if current_time < 300:  # 00:00 ~ 02:59
    now -= timedelta(days=1)
    base_time = '2300'
elif current_time < 600:  # 03:00 ~ 05:59
    base_time = '0200'
elif current_time < 900:  # 06:00 ~ 08:59
    base_time = '0500'
elif current_time < 1200:  # 09:00 ~ 11:59
    base_time = '0800'
elif current_time < 1500:  # 12:00 ~ 14:59
    base_time = '1100'
elif current_time < 1800:  # 15:00 ~ 17:59
    base_time = '1400'
elif current_time < 2100:  # 18:00 ~ 20:59
    base_time = '1700'
elif current_time < 2400:  # 21:00 ~ 23:59
    base_time = '2000'

# base_date 설정
base_date = now.strftime('%Y%m%d')

# 현재 정보
params_NOW = {
    'serviceKey': key,
    'numOfRows': '36',
    'pageNo': '1',
    'dataType': 'JSON',
    'base_date': base_date,
    'base_time': base_time,
    'nx': x_coordinate,
    'ny': y_coordinate
}

def convert_code(value, category):
    if category == 'PTY':
        if value == '0':
            return 'no_rain'
        elif value == '1':
            return 'rain'
        elif value == '2':
            return 'rain/snow'
        elif value == '3':
            return 'snow'
        elif value == '4':
            return 'shower'
        else:
            return 'unknown'
    elif category == 'SKY':
        if value == '1':
            return 'sunny'
        elif value == '3':
            return 'cloudy'
        elif value == '4':
            return 'fog'
        else:
            return 'unknown'
    elif category == 'SNO':
        if value == '적설없음':
            return 'no_snow'
        else:
            return value.split('cm')[0]
    elif category == 'PCP':
        if value == '강수없음':
            return 'no_rain'
        else:
            return value.split('mm')[0]
        
we_response = requests.get(we_url, params=params_NOW, timeout=30)

if we_response.status_code == 200:
    res = json.loads(we_response.text)

    current_hour_data = [item for item in res['response']['body']['items']['item'] if item['fcstTime'] == str(fcst_time).zfill(4)]
    
    desired_categories = ['POP', 'PTY', 'PCP', 'REH', 'SNO', 'SKY', 'TMP', 'WSD']

    result_dict = {item['category']: item['fcstValue'] for item in current_hour_data}

    we_data = {
        'Date': now_date_time,
        'address': city + " " + district + " " + town,
        'SKY': convert_code(result_dict.get('SKY', None), 'SKY') if 'SKY' in result_dict else None, # 하늘상태
        'PTY': convert_code(result_dict.get('PTY', None), 'PTY') if 'PTY' in result_dict else None, # 강수형태        
        'POP': result_dict.get('POP', None), # 강수확률
        'PCP': convert_code(result_dict.get('PCP', None), 'PCP')if 'PCP' in result_dict else None, # 1시간 강수량
        'SNO': convert_code(result_dict.get('SNO', None), 'SNO')if 'SNO' in result_dict else None, # 1시간 적설량
        'TMP': result_dict.get('TMP', None), # 1시간 기온
        'REH': result_dict.get('REH', None), # 습도
        'WSD': result_dict.get('WSD', None) # 풍속
    }


# 미세먼지
# TM 좌표 조회
tm_params = {
    'serviceKey': key,
    'returnType': 'JSON',
    'numOfRows': '10',
    'pageNo': '1',
    'umdName': town
}

tm_response = requests.get(tm_url, params=tm_params)

if tm_response.status_code == 200:
    data = tm_response.json()
    if 'items' in data['response']['body']:
        items = data['response']['body']['items'][0]
        tmX = items['tmX']
        tmY = items['tmY']
    else:
        print("TM 좌표 API에서 데이터를 찾을 수 없습니다.")
else:
    print(f"TM 좌표 API 요청이 실패하였습니다. 상태 코드: {tm_response.status_code}")

# 근접 측정소 조회
ne_params = {
    'serviceKey': key,
    'returnType': 'JSON',
    'tmX': tmX,
    'tmY': tmY
}

ne_response = requests.get(ne_url, params=ne_params)

if ne_response.status_code == 200:
    data = ne_response.json()
    if 'items' in data['response']['body']:
        items = data['response']['body']['items'][0]
        addr = items['addr']
        stationName = items['stationName']
    else:
        print("근접 측정소 API에서 데이터를 찾을 수 없습니다.")
else:
    print(f"근접 측정소 API 요청이 실패하였습니다. 상태 코드: {ne_response.status_code}")

# 실시간 측정 데이터 조회
pm_params = {
    'serviceKey': key,
    'returnType': 'JSON',
    'stationName': stationName,
    'dataTerm': 'DAILY',
    'ver': '1.3'
}

pm_response = requests.get(pm_url, params=pm_params)

def convert_grade(grade):
    if grade == '1':
        return 'good'
    elif grade == '2':
        return 'normal'
    elif grade == '3':
        return 'bad'
    elif grade == '4':
        return 'very_bad'
    else:
        return 'unknown'

# 데이터 출력
if pm_response.status_code == 200:
    data = pm_response.json()['response']['body']['items']

    # 현재 시간과 가장 가까운 시간대 찾기
    nearest_data = min(data, key=lambda x: abs(datetime.strptime(x['dataTime'].replace('24:00', '00:00'), '%Y-%m-%d %H:%M') - now))
    # value
    khaiValue = nearest_data['khaiValue']
    pm25Value = nearest_data['pm25Value']
    pm10Value = nearest_data['pm10Value']
    o3Value = nearest_data['o3Value']
    no2Value = nearest_data['no2Value']
    so2Value = nearest_data['so2Value']
    coValue = nearest_data['coValue']
    # grade
    khaiGrade = convert_grade(nearest_data['khaiGrade'])

    pm_data = {
        'Date': nearest_data['dataTime'],  # 예제로 timestamp 사용, 실제로는 적절한 키 사용
        'station': stationName,
        'khaiValue': khaiValue,
        'pm25Value': pm25Value,
        'pm10Value': pm10Value,
        'o3Value': o3Value,
        'no2Value': no2Value,
        'so2Value': so2Value,
        'coValue': coValue,
        'khaiGrade': khaiGrade
    }

else:
    print(f"실시간 측정 API 요청이 실패하였습니다. 상태 코드: {pm_response.status_code}")

combined_data = we_data.copy()
combined_data.update(pm_data)

item = {
    'Date_time': {'S': now_date_time},
    'address': {'S': combined_data['address']},
    'SKY': {'S': combined_data['SKY']},
    'PTY': {'S': combined_data['PTY']},
    'POP': {'S': str(combined_data['POP'])},
    'PCP': {'S': combined_data['PCP']},
    'SNO': {'S': combined_data['SNO']},
    'TMP': {'S': str(combined_data['TMP'])},
    'REH': {'S': str(combined_data['REH'])},
    'WSD': {'S': str(combined_data['WSD'])},
    'station': {'S': combined_data['station']},
    'khaiValue': {'S': combined_data['khaiValue']},
    'pm25Value': {'S': combined_data['pm25Value']},
    'pm10Value': {'S': combined_data['pm10Value']},
    'o3Value': {'S': combined_data['o3Value']},
    'no2Value': {'S': combined_data['no2Value']},
    'so2Value': {'S': combined_data['so2Value']},
    'coValue': {'S': combined_data['coValue']},
    'khaiGrade': {'S': combined_data['khaiGrade']}
}

db_response = dynamodb_client.put_item(
    TableName=outside_table_name,
    Item=item
)

