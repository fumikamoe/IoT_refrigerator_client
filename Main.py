# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for
import threading
import time
import img
import other

# 비동기 플래그 선언 부분
flag_motion_detected = True
flag_image_processed = False
flag_cloud_uploaded = False
once =  False
predict = []

# 플라스크 설정
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def Thread_Motion_Detect():
    print('Start Motion Detect Threading')
    def start_loop():
        global flag_image_processed
        global flag_motion_detected
        global once
        flag_motion_detected = True
        cnt = 0
        while(True):
            if flag_image_processed == False:
                cnt, diff = img.frame_diffrence(cnt)
                if diff >= 300000: # 모션감지에 대한 Threshold 설정 부분
                    print("{} : 움직임이 감지됬습니다!".format(other.now()))
                    cnt = 0
                    flag_motion_detected = True
                    once = False
                if flag_motion_detected == True and cnt >= 2: # 모션 감지 후 얼마나 더 기다릴건지 조정
                    if once == False:
                        print("{} : 움직임이 없습니다!".format(other.now()))
                    flag_motion_detected = False
            time.sleep(1)
    thread = threading.Thread(target=start_loop)
    thread.start()

def Thread_Image_Processing():
    print('Start Image Processing Threading')
    def start_loop():
        global flag_motion_detected
        global flag_image_processed
        global flag_cloud_uploaded
        global once
        once = True
        while(True):
            if flag_motion_detected == False and once == False:
                flag_image_processed = True
                name, parsed_data = img.Processing()
                once = True
                flag_image_processed = False
                flag_cloud_uploaded = True
                other.upload_blob(name, parsed_data)
                flag_cloud_uploaded = False
            time.sleep(1)
    thread = threading.Thread(target=start_loop)
    thread.start()

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', flag_motion_detected = flag_motion_detected, flag_image_processed=flag_image_processed, flag_cloud_uploaded=flag_cloud_uploaded)

if __name__ == '__main__':
    Thread_Motion_Detect()
    Thread_Image_Processing()
    app.run(host='0.0.0.0', threaded=True)
