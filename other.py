# -*- coding: utf-8 -*-
from datetime import datetime
from google.cloud import storage
import os
import requests
import json

# ML로 연결되는 주소 설정
addr = ''
URL = addr + ''

# Storage Setting
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ''
BUCKET_NAME = ''

client = storage.Client()
bucket = client.get_bucket(BUCKET_NAME)

def now():
    return datetime.now().strftime('%H:%M:%S')

def filetime():
    return datetime.now().strftime('%m%d_%H-%M-%S')

def delete_blob():
    for blob in bucket.list_blobs():
        bucket.delete_blob(blob_name=blob.name)
        print('{} : {} 삭제했습니다.'.format(now(), blob.name))

def upload_blob(name, parsed_data):
    # 업로드 전 클라우드 내 기존 내역 삭제
    delete_blob()
    print("{} : 클라우드 스토리지 초기화 완료".format(now()))

    # 원본 업로드
    print("{} : 업로드를 시작합니다.".format(now()))
    original_path = "data" + '/' + name + '/' + 'original' + '.png' #로컬 경로
    original_upload_name = name + '.png' #클라우드에 올라가는 이름
    original_img = bucket.blob(original_upload_name)
    original_img.upload_from_filename(filename=original_path)
    print("{} : {}를 {}로 클라우드에 업로드 하였습니다.".format(now(), original_path, original_upload_name))

    global predict
    # 각 파일 업로드
    #idx = 0
    for i in range(len(parsed_data)):  # 경계선 오브젝트마다
        croped_upload_name = name + '-' + str(i) + '_' + parsed_data[i][0] + '.jpg' #클라우드에 올라가는 이름
        try:
            croped_image = bucket.blob(croped_upload_name)
            croped_image_path = "data" + '/' + name + '/' + str(i) + '_' + parsed_data[i][0] + '.jpg' #로컬 경로
            croped_image.upload_from_filename(filename=croped_image_path)
            print("{} : {}를 {}로 클라우드에 업로드 하였습니다.".format(now(), croped_image_path, croped_upload_name))
        except:
            pass
    print("{} : 클라우드 업로드 완료!".format(now()))


def delete_file_dir(mydir):
    filelist = [f for f in os.listdir(mydir)]
    for f in filelist:
        os.remove(os.path.join(mydir, f))
        print(f + ' is deleted!')

def post_image(img_file, URL, headers):
    img = open(img_file, 'rb').read()
    #img = img_file
    response = requests.post(URL, data=img, headers=headers)
    return response

def request_vision(image):
    # prepare headers for http request
    content_type = 'image/jpeg'
    headers = {'content-type': content_type}

    res = post_image(image, URL, headers)
    print("{} : VISION - 인식 완료".format(now()))

    j = json.loads(res.json())
    result = j['predict']
    return result
