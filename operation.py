import serial
import time
import schedule
import json
import csv
import ssl
import logging
import requests
import boto3
import pandas as pd
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
from inotify_simple import INotify, flags
from datetime import datetime


GPIO.setwarnings(False)
logging.basicConfig(level=logging.DEBUG)

# Motor pins
motor_pwm_pin = 12
motor_brk_pin = 16
motor_dir_pin = 18

# PWM settings
pwm_frequency = 100  # PWM frequency (Hz)
pwm_duty_cycle = 0   # Initial speed (0 ~ 100)
pwm_range = 100      # PWM range (0 ~ 100)

# GPIO pin setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor_pwm_pin, GPIO.OUT)
GPIO.setup(motor_brk_pin, GPIO.OUT)
GPIO.setup(motor_dir_pin, GPIO.OUT)

# PWM
pwm = GPIO.PWM(motor_pwm_pin, pwm_frequency)
pwm.start(pwm_duty_cycle)

# Raspberry Pi - Arduino serial port
ser = serial.Serial('/dev/ttyACM0', 9600)

# Raspberry Pi - XBee serial port
xbee_ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# AWS credentials and region
aws_access_key_id = ''
aws_secret_access_key = ''
aws_region = 'ap-northeast-2'

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name=aws_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# DynamoDB table names
dynamodb_table_outside = 'Outside'
dynamodb_table_order = 'Order'
dynamodb_table_state = 'State'

# Get DynamoDB tables
outside_table = dynamodb.Table(dynamodb_table_outside)
order_table = dynamodb.Table(dynamodb_table_order)
state_table = dynamodb.Table(dynamodb_table_state)

# AWS IoT Core
iot_endpoint = 'a2mgnb1vux7nei-ats.iot.ap-northeast-2.amazonaws.com'
thing_name = 'air_purifier'
cert_path = '/home/joljak/certs/air_purifier.cert.pem'
key_path = '/home/joljak/certs/air_purifier.private.key'
root_ca_path = '/home/joljak/certs/root-CA.crt'

topic_a = 'data/air'    # Air data sent from IoT Core to air data
topic_o = 'data/order'  # Order data sent from Raspberry Pi to motor order, window order
topic_s = 'data/state'   # Data sent from IoT Core to motor state, window state
topic_os = 'data/outside'

# last row get function
def get_last_row(file_path):
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        if rows:
            return rows[-1]
        else:
            return None

# MQTT
def initialize_mqtt():
    mqtt_client = mqtt.Client(client_id=thing_name)
    mqtt_client.tls_set(root_ca_path, certfile=cert_path, keyfile=key_path,
                        tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    return mqtt_client

mqtt_client = initialize_mqtt()

def on_connect(mqttc, obj, flags, rc):
    if rc == 0:
        print('Connected to MQTT broker')
    else:
        print(f'Connection to MQTT broker failed with code {rc}')

def on_subscribe(mqttc, obj, mid, granted_qos):
    if mid == 1:
        print("Subscribed: " + topic_a)
    elif mid == 2:
        print("Subscribed: " + topic_s)
    elif mid == 3:
        print("Subscribed: " + topic_o)
    elif mid == 4:
        print("Subscribed: " + topic_os)
        
auto = "na"
        
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode('utf-8'))
    global auto
    
    if msg.topic == topic_o:
        motor_order = payload.get("motor_order", "na")
        window_order = payload.get("window_order", "na")
        auto = payload.get("auto", "na")
        
        if motor_order == "motor_stop":
            print("motor_stop")
            GPIO.output(motor_brk_pin, GPIO.HIGH)
        elif motor_order == "motor_1":
            print("motor_1")
            GPIO.output(motor_brk_pin, GPIO.LOW)
            pwm.ChangeDutyCycle(5)
        elif motor_order == "motor_2":
            print("motor_2")
            GPIO.output(motor_brk_pin, GPIO.LOW)
            pwm.ChangeDutyCycle(20)
        elif motor_order == "motor_3":
            print("motor_3")
            GPIO.output(motor_brk_pin, GPIO.LOW)
            pwm.ChangeDutyCycle(40)
        '''    
        elif auto == "on":
            print("auto_on")
            making_decision()
            
        elif auto == "off":
            print("auto_off")
            GPIO.output(motor_brk_pin, GPIO.HIGH)
            xbee_ser.write(str.encode('L'))
            if xbee_ser.in_waiting > 0:
                update_device_state(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "motor_stop", "window_close", "N/A")
            
        elif window_order == "window_open":
            xbee_ser.write(str.encode('O'))
            print("window_open")
            if xbee_ser.in_waiting > 0:
                xbee_received = xbee_ser.readline().decode('utf-8').strip()
                print(f"Received data from arduino: {xbee_received}")
                
        elif window_order == "window_close":
            xbee_ser.write(str.encode('L'))
            print("window_close")
            if xbee_ser.in_waiting > 0:
                xbee_received = xbee_ser.readline().decode('utf-8').strip()
                print(f"Received data from arduino: {xbee_received}")
        '''
                
# outside recieve
def get_outside_data():
    try:
        # Scan DynamoDB table to get all items
        response = outside_table.scan(
            Select="ALL_ATTRIBUTES",
        )
        # Check if there are items in the response
        if 'Items' in response and len(response['Items']) > 0:
            sorted_items = sorted(response['Items'], key=lambda x: x['Date_time'], reverse=True)
            latest_data = sorted_items[0]
            latest_data_json = json.loads(json.dumps(latest_data, default=str))
            return latest_data_json
        else:
            print("No data found in the DynamoDB table.")
            return None
        
    except Exception as e:
        print(f"Error querying DynamoDB: {str(e)}")

        return None

# print outside recieve
def print_outside_data():
    latest_outside_data = get_outside_data()
    
    if latest_outside_data:
        pty_value = latest_outside_data.get("PTY", "N/A")
        khai_grade_value = latest_outside_data.get("khaiGrade", "N/A")
        temp_value = latest_outside_data.get("TMP", "N/A")
        print(latest_outside_data)
        return pty_value, khai_grade_value, temp_value
    else:
        print("No data found.")


def update_device_state(date_time, motor_state, window_state, window_warning):
    try:
        response = state_table.put_item(
            Item={
                'Date_time': date_time,
                'motor_state': motor_state,
                'window_state': window_state,
                'window_warning': window_warning,
            }
        )
        print("DynamoDB state updated successfully.")
    except Exception as e:
        print(f"Error updating DynamoDB state: {str(e)}")
    
    
def get_last_row(file_path):
	with open(file_path, 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		rows = list(reader)
		if rows:
			return rows[-1]
		else:
			return None


csv_file_path = '/home/joljak/sensor_data_pred.csv'
pred_df = pd.read_csv(csv_file_path, names=['Date_time', 'pred_CO2', 'pred_PM'])

current_time = datetime.now()
hour_value = current_time.hour
minute_value = current_time.minute

pred_df['Date_time'] = pd.to_datetime(pred_df['Date_time'])
data_p = pred_df[(pred_df['Date_time'].dt.hour == hour_value) & (pred_df['Date_time'].dt.minute == minute_value)]

# schedule.every(1).minutes.do(new_pred)
# load making_decision dataset1
window_isopen = 0

def making_decision():
    global sensor
    global window_isopen
    
    data = get_last_row('/home/joljak/sensor_data_v4.csv')
    sensor = [data['CO'], data['CO2'], data['PM'], data['Temp'],
             data['Voc'], data_p['pred_CO2'], data_p['pred_PM']] # Voc, CO, CO2, PM
    pty_value, khai_grade_value, temp_value = print_outside_data()
    temp_value = float(temp_value)
    sensor = list(map(float, sensor))
    summer_case = temp_value - sensor[3]
    winter_case = sensor[3] - temp_value
    
    # Case: YES
    if sensor[1] > 500 or sensor[5] > 1000 or sensor[0]  > 5 or sensor[4] > 500 : # CO2 > 1000 or pred_CO2 > 1000 or CO > 10 or VOC > 400 -> 정지, 열기
        #if pty_value == "rain" : # 비올때 검사용
        if pty_value == "no_rain" : # 현재 비 와서 수정
            if khai_grade_value == "good" or khai_grade_value == "normal" :
                if summer_case > 10 or winter_case > 15: 
                    if window_isopen == 0:
                        print("case1")
                        GPIO.output(motor_brk_pin, GPIO.HIGH)   # 5min
                        xbee_ser.write(str.encode('O'))
                        if xbee_ser.in_waiting > 0:
                            update_device_state(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "motor_stop", "window_open", "N/A")
                        window_isopen = 1
                    else:
                        print("case1-1")
                        time.sleep(10) # 5분, 10초로 임시 수정
                else:
                    if window_isopen == 0:
                        print("case2")
                        GPIO.output(motor_brk_pin, GPIO.HIGH) # 10min
                        xbee_ser.write(str.encode('O'))
                        if xbee_ser.in_waiting > 0:
                            update_device_state(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "motor_stop", "window_open", "N/A") 
                        window_isopen = 1
                    else:
                        print("case2-1")
                        time.sleep(10) # 10분, 10초로 임시 수정
                    
            else: # 밖의 공기질 안 좋을 때 약풍, 열기
                if window_isopen == 0:
                    print("case3")
                    GPIO.output(motor_brk_pin, GPIO.LOW) # 5min
                    pwm.ChangeDutyCycle(1)
                    xbee_ser.write(str.encode('O'))
                    if xbee_ser.in_waiting > 0:
                        update_device_state(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "motor_1", "window_open", "N/A") 
                    window_isopen = 1
                else:
                    print("case3-1")
                    time.sleep(10) # 10분, 10초로 임시 수정
        else: # 비가 올 때
            print("case3-2")
            GPIO.output(motor_brk_pin, GPIO.LOW)
            pwm.ChangeDutyCycle(20)
            xbee_ser.write(str.encode('L'))
            if xbee_ser.in_waiting > 0:
                update_device_state(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "motor_2", "window_close", "N/A")
            window_isopen = 0
            
    elif sensor[2] > 35 or sensor[6] > 35: # PM > 35 or pred_PM > 35 강풍, 닫기
        # | sensor[] > 10 | pred[] > 35
            print("case4")
            GPIO.output(motor_brk_pin, GPIO.LOW)
            pwm.ChangeDutyCycle(40)
            xbee_ser.write(str.encode('L'))
            if xbee_ser.in_waiting > 0:
                update_device_state(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "motor_3", "window_close", "N/A")
            window_isopen = 0
            
    else: 
        print("case5")
        print(pty_value)
        GPIO.output(motor_brk_pin, GPIO.LOW)
        pwm.ChangeDutyCycle(1)
        xbee_ser.write(str.encode('L'))
        if xbee_ser.in_waiting > 0:
            update_device_state(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "motor_1", "window_close", "N/A") 
        window_isopen = 0

try:
    # MQTT connection setup
    mqtt_client = initialize_mqtt()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.connect(iot_endpoint, port=8883)
    time.sleep(1)
    mqtt_client.subscribe(topic_a)  # Air data
    mqtt_client.subscribe(topic_s)  # Motor/window state data
    mqtt_client.subscribe(topic_o)  # Client order data
    mqtt_client.subscribe(topic_os)  # Client outside data
    mqtt_client.loop_start()
    
    # CSV file setup
    sensor_csv_filename = '/home/joljak/sensor_data_v4.csv'
    with open(sensor_csv_filename, 'a', newline='') as csvfile:
        sensor_fieldnames = ['Device_type', 'Date_time', 'D_Week', 'Voc', 'CO', 'Temp', 'Humi', 'CO2', 'CO2_s', 'PM', 'pred_CO2', 'pred_PM']
        sensor_writer = csv.DictWriter(csvfile, fieldnames=sensor_fieldnames)
        sensor_writer.writeheader()

        data_count = 0
        max_data_count = 20  # Send data to MQTT and reconnect after 20 data points
        
        while True:
            try:
                data = ser.readline().decode('utf-8').strip()
                sensor_data = data.split(',')


                # Initialize variables before using them
                if len(sensor_data) >= 7:
                    voc = float(sensor_data[0] or 0)
                    co = float(sensor_data[1] or 0)
                    temp = float(sensor_data[2] or 0)
                    humi = float(sensor_data[3] or 0)
                    co2 = float(sensor_data[4] or 0)
                    co2_s = str(sensor_data[5] or 0)
                    pm= float(sensor_data[6] or 0)
                    
                    csv_file_path = '/home/joljak/sensor_data_pred.csv'
                    pred_df = pd.read_csv(csv_file_path, names=['Date_time', 'pred_CO2', 'pred_PM'])

                    current_time = datetime.now()
                    hour_value = current_time.hour
                    minute_value = current_time.minute
                    pred_df['Date_time'] = pd.to_datetime(pred_df['Date_time'])

                    data_p = pred_df[(pred_df['Date_time'].dt.hour == hour_value) & (pred_df['Date_time'].dt.minute == minute_value)].iloc[-1]
                    
                    sensor_dict = {
                        'Device_type': 'air_purifier',
                        'Date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'D_Week': datetime.now().strftime('%A'),
                        'Voc': voc,
                        'CO': co,
                        'Temp': temp,
                        'Humi': humi,
                        'CO2': co2,
                        'CO2_s': co2_s,
                        'PM': pm,
                        'pred_CO2': data_p['pred_CO2'],
                        'pred_PM' : data_p['pred_PM']
                    }

                    # CSV 파일에 데이터 추가
                    sensor_writer.writerow(sensor_dict)
                    csvfile.flush()

                    # JSON 형식으로 데이터 변환
                    json_data = json.dumps(sensor_dict)

                    # MQTT 데이터 전송
                    if mqtt_client:
                        mqtt_client.publish(topic_a, json_data, qos=1)
                    else:
                        print('MQTT client not available')
                        
                    sensor = [voc, co, temp, humi, co2, co2_s, pm] 
                    
                    if auto == "on":
                        print("auto_on")
                        making_decision()
                    elif auto == "off":
                        print("auto_off")
                        GPIO.output(motor_brk_pin, GPIO.HIGH)
                        xbee_ser.write(str.encode('L'))
                        if xbee_ser.in_waiting > 0:
                            update_device_state(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "motor_stop", "window_close", "N/A")
                    
                    time.sleep(5)

            except KeyboardInterrupt:
                raise  # Reraise KeyboardInterrupt to trigger cleanup

            except serial.SerialException as se:
                logging.error(f'Serial communication error: {str(se)}')

            except Exception as e:
                logging.error(f'An error occurred: {str(e)}')
                raise

finally:
    # Clean up GPIO, serial, and MQTT client on exit
    ser.close()
    pwm.stop()
    GPIO.cleanup()

    if mqtt_client:
        mqtt_client.disconnect()
        
        
