from skimage.measure import compare_ssim as ssim
import numpy as np
import cv2
import os
import pytesseract as TA
from difflib import SequenceMatcher

def button_to_text(image) :
    return TA.image_to_string(image,lang='kor')

def similar(text1, text2) :
    return SequenceMatcher(None, text1, text2).ratio()

def compare_text_button(img_path1, img_path2) :
    image1 = cv2.imread(img_path1, cv2.IMREAD_COLOR)
    image2 = cv2.imread(img_path2, cv2.IMREAD_COLOR)

    text1 = button_to_text(image1)
    text2 = button_to_text(image2)

    print(text1)
    print('-----------------------------------')
    print(text2)

    if similar(text1, text2) > 0.4 :
        return True
    else :
        return False

#x, y는 파일명 (상대경로 사용)
def compare(filename1, filename2):
    img1 = cv2.imread(filename1, cv2.IMREAD_COLOR)
    img2 = cv2.imread(filename2, cv2.IMREAD_COLOR)

    s = ssim(img1, img2, multichannel=True)
    
    if s<0:
        s=0
    sub = np.subtract(img1, img2)
    dif = np.nonzero(sub)
    result = np.size(dif)/np.size(sub)

    if result * 100 == 0 and (1 - s) * 100 == 0:
        #print("완전히 같은 화면")
        return 1
    elif result*100 < 10 and (1-s)*100 < 3.8:
        return 1
    elif result*100 > 10 and (1-s)*100 < 3.8:
        #print("같은화면+애니메이션")
        return 1
    elif result*100 > 40 and (1-s)*100 > 3.8:
        #print("다른화면+애니메이션")
        return 2
    else:
        #print("다른화면")
        return 2

def resize_compare(filename1, filename2):
    img1 = cv2.imread(filename1, cv2.IMREAD_COLOR)
    img2 = cv2.imread(filename2, cv2.IMREAD_COLOR)

    y1 = img1.shape[0]
    x1 = img1.shape[1]
    y2 = img2.shape[0]
    x2 = img2.shape[1]

    if x1 > x2 and y1 > y2 :
        img1 = cv2.resize(img1,(x2, y2))
    elif x1 < x2 and y1 < y2 :
        img2 = cv2.resize(img2,(x1, y1))
    elif x1 == x2 and y1 != y2 :
        print('4')
        return 4 #한쪽 비율은 맞는데 다른쪽 아닌 경우임...잘라서 해줘야해
    elif x1 != x2 and y1 == y2:
        print('4')
        return 4 #한쪽 비율은 맞는데 다른쪽은 아닌 경우임...잘라서
    elif x1 > x2 and y1 < y2 :
        print('3')
        return 3 #세로모드와 가로모드를 비교한 경우
    elif x1 < x2 and y1 > y2 :
        print('3')
        return 3 ##가로모드와 세로모드를 비교한 경우임..
    else : # 해상도 같음
        img1 = img1
        img2 = img2 #그대로비교할끄임

    s = ssim(img1, img2, multichannel=True)
    s = s*100

    if s > 55 :
        print(s)
        return  1 ##같은화면으로 판단됨
    else :
        print(s)
        return 2 ##다른화면으로 판단됨

'''
Template Match Method
['cv2.TM_CCOEFF','cv2.TM_CCOEFF_NORMED','cv2.TM_CCORR','cv2.TM_CCORR_NORMED','cv2.TM_SQDIFF','cv2.TM_SQDIFF_NORMED']
6개 중 신뢰도가 떨어지는 TM_CCORR을 제하고 Threshold 선정이 쉬운 TM_CCOEFF_NORMED로 정했습니다
'''


def find_obj(img, obj):
    h, w = obj.shape[:2] # 찾을 obj의 너비, 높이! 만약 obj의 해상도 달라질 경우에는 좀 수정 필요할 듯~_~
    THR = 0.95 # THR 이상의 유사도를 갖는 obj 탐색

    res = cv2.matchTemplate(img, obj, cv2.TM_CCOEFF_NORMED) # 템플릿매칭

    loc = np.where(res >= THR) # THR 이상의 유사도를 갖는 픽셀[row,column] 반환

    objList = [] # 찾은 obj의 좌표 저장할 리스트

    # pt: 매칭된 obj의 좌상우하 좌표, thr 이상의 유사도를 가진 픽셀 있을 경우 objList에 추가
    for pt in zip(*loc[::-1]):
        #좌:pt[0] 상:pt[1]+h 우:pt[0]+w 하:pt[1]
        objList.append([pt[0],pt[1]+h, pt[0]+w, pt[1]])

    return objList

def folder_compare(target_folder, folder2, temp_len) :
    target_len = len(next(os.walk(target_folder))[2])
    index = 0
    flag = 0
    if target_len > temp_len :
        index = temp_len
    else :
        index = target_len
    for i in range(0, index) :
        target_path = os.path.join(target_folder, 'ob' + str(i) + '.jpg')
        temp_path = os.path.join(folder2, 'ob' + str(i) + '.jpg')

        if resize_compare(target_path, temp_path) == 1 :
            print("same")
            flag = flag + 1
        else :
            if compare_text_button(target_path, temp_path) :
                print("same text")
                flag = flag + 1
    if flag > temp_len * 0.7 :
        print('Good')
        return True
    else :
        return False
