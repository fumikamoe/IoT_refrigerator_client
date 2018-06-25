# -*- coding: utf-8 -*-
import cv2
import numpy as np
from sys import platform
import os
import time
import random

import other

margin = 30

# 라즈베리 파이 환경에서 실행시 picamera 실행
if platform == 'linux2':
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    camera = PiCamera()
    def capture_picam():
        rawCapture = PiRGBArray(camera)
        time.sleep(0.1)
        camera.capture(rawCapture, format="bgr")
        frame = rawCapture.array
        return frame
else:
    cap = cv2.VideoCapture(1)
    def capture_cv2():
        _, frame = cap.read()
        return frame

def capture_resize():
    frame = capture_picam()
    resized_image = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
    return resized_image

def frame_diffrence(cnt):
    cnt += 1

    # Capture frame-by-frame
    if platform == 'linux2':
        before_frame = capture_picam()
    else:
        before_frame = capture_cv2()
    before_frame = cv2.cvtColor(before_frame, cv2.COLOR_BGR2GRAY)

    if platform == 'linux2':
        after_frame = capture_picam()
    else:
        after_frame = capture_cv2()

    after_frame = cv2.cvtColor(after_frame, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(after_frame, before_frame)
    _, diff = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)

    return cnt, np.sum(diff)

def saveimg(folder, process, frame):
    resized_frame = cv2.resize(frame, (0, 0), fx=0.4, fy=0.4)
    cv2.imwrite("static" + '/' + process + '.png', resized_frame)
    cv2.imwrite("data" + '/' + folder + '/' + process + '.png', frame)

def saveimg_orig(folder, process, frame):
    cv2.imwrite("static" + '/' + process + '.jpg', frame)
    cv2.imwrite("data" + '/' + folder + '/' + process + '.jpg', frame)

def saveimg_jpg(folder, process, frame):
    resized_frame = cv2.resize(frame, (0, 0), fx=0.4, fy=0.4)
    cv2.imwrite("static" + '/' + process + '.jpeg', resized_frame)
    cv2.imwrite("data" + '/' + folder + '/' + process + '.jpeg', frame)

def Processing():
    name = other.filetime()
    os.mkdir("data/" + name)
    other.delete_file_dir('static')
    if platform == 'linux2':
        image = capture_picam()
    else:
        image = capture_cv2()
    saveimg(name, 'original', image)
    print(image.shape)
    border_img = Add_border(image, 100)
    print(border_img.shape)
    saveimg_jpg(name, 'border', border_img)
    original = border_img
    boxed = border_img

    # Visioning
    print("{} : 이미지를 ML로 분석합니다".format(other.now()))
    parsed_data = other.request_vision("data" + '/' + name + '/' + 'border' + '.jpeg')
    predicted_size = len(parsed_data)

    for i in range(predicted_size):
        #Data Parsing
        print(parsed_data[i])
        label = parsed_data[i][0]
        prob = str(float(parsed_data[i][1]) * 100)
        xmin = int(parsed_data[i][2])
        xmax = int(parsed_data[i][3])
        ymin = int(parsed_data[i][4])
        ymax = int(parsed_data[i][5])

        #Image Croping Part
        if xmax - xmin > 50 and ymax - ymin > 50:
            new_img = original[ymin - margin:ymax + margin, xmin - margin: xmax + margin]
            saveimg_orig(name, "{}_{}".format(str(i),label), new_img)
            print("분할한 이미지를 {}로 저장했습니다.".format(str(i) + '.png'))

    for i in range(predicted_size):
        # Data Parsing
        print(parsed_data[i])
        label = parsed_data[i][0]
        prob = str(float(parsed_data[i][1]) * 100)
        xmin = int(parsed_data[i][2])
        xmax = int(parsed_data[i][3])
        ymin = int(parsed_data[i][4])
        ymax = int(parsed_data[i][5])

        #Image Boxing
        color1 = random.randint(0, 255)
        color2 = random.randint(0, 255)
        color3 = random.randint(0, 255)
        cv2.putText(boxed, label + ' : ' + prob + '%' , (xmin, ymin - 10), cv2.FONT_HERSHEY_DUPLEX, 1.5,
                    (0, 255, 255), 2, cv2.LINE_AA)
        cv2.rectangle(boxed, (xmin, ymin), (xmax, ymax), (color1, color2, color3), 3)
    boxed = delete_border(boxed, 100)
    saveimg(name, 'boxed', boxed)
    return name, parsed_data

def Add_border(frame, size):
    row, col = frame.shape[:2]
    bottom= frame[row-2:row, 0:col]
    bordersize=size
    border=cv2.copyMakeBorder(frame, top=bordersize, bottom=bordersize, left=bordersize, right=bordersize, borderType= cv2.BORDER_CONSTANT, value=[255,255,255] )
    return border

def delete_border(frame, size):
    new_img = frame[0+size:frame.shape[0]-size, 0+size:frame.shape[1]-size]
    return new_img
