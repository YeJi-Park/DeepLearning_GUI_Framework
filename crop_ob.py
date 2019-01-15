import cv2
import math
from PIL import Image
import tensorflow as tf
import os
import numpy as np
import revisedCompare as rC

#원시 화면- 스크롤 안 내린 화면
#스크롤된 화면 - 스크롤 내린 화면

#for 원시 화면 crop
def crop(image, list):
    
    img = cv2.imread(image)  #이미지 읽어옴
    (img_h, img_w) = img.shape[:2]  #height, width 읽어옴 
    
    #상대 좌표값을 절대 좌표로 변환
    left =math.floor(list[1]*img_w)  #가로 시작 좌표 (좌)
    up = math.floor(list[2]*img_h)  #세로 끝 좌표 (상)
    right = math.floor(list[3]*img_w)  #가로 끝 좌표 (우)
    down = math.floor(list[4]*img_h)  #세로 시작 좌표 (하)
  
    #이미지 크롭 후 반환
    crop = img[down:up, left:right]
    return crop



#for 원시 화면 cropSave
def cropSave(image_path, coord):
    
    #크롭된 오브젝트들이 들어갈 path
    obj_path = os.path.splitext(image_path)[0]
    if not os.path.isdir(obj_path) :
        os.mkdir(obj_path)  #폴더 존재 안하면 이미지 이름과 동일한 이름 가진 폴더 만들고
        
    #오브젝트 갯수만큼 반복
    for i in range(len(coord)):
        cropImg = crop(image_path, coord[i])  #이미지 크롭 후
        cv2.imwrite(os.path.join(obj_path, "ob"+str(i)+".jpg"), cropImg) #저장
        
  
    
#스크롤된 화면일 경우에만 호출
def scrollSave(img_path, scr_img, scr_coord):
    #스크롤된 화면의 기원을 알아야 동일 디렉토리가 있는지 확인 및 크롭저장 가능하므로
    #원시 화면 이미지 path 인 img_path 를 인자로 받음
    
    
    obj_path = os.path.splitext(img_path)[0] #크롭된 오브젝트들이 들어갈 path
    num = len(next(os.walk(obj_path))[2]) #폴더 안에 이미 존재하는 오브젝트 갯수
    
    #동일 폴더가 있을 경우
    #if(os.path.exists(obj_path)): 
    
    img = cv2.imread(scr_img) 
    (img_h, img_w) = img.shape[:2]  #이미지 높이 너비 읽어온 후
    scr_list = transToNatural(img_w,img_h,scr_coord)  #상대 좌표 리스트->절대 좌표 리스트
    
    
    for j in range(num):
        old_ob = cv2.imread(os.path.join(obj_path, "ob"+str(j)+".jpg"))
        
        #스크롤된 화면에 중복 object 있는지 후보 좌표 리스트 받아옴
        candi = rC.find_obj(img, old_ob)  
    
    
        for c in range(len(candi)):
            for i in range(len(scr_list)):
                if scr_list[i] == candi[c]:  #중복 obj 로 판별될 시 (좌상우하 좌표 동일할 시)
                    scr_list.remove(scr_list[i])  #스크롤 화면 obj 리스트에서 제거
                    break;
    
    #중복 아닌 오브젝트 좌표 리스트 이용하여 크롭
    for r in range(len(scr_list)):
        cropImg = cropAbs(scr_img, scr_list[r])   #이미지와 절대 좌표 받아서 크롭 후
        cv2.imwrite(os.path.join(obj_path, "ob"+str(num+r)+".jpg"), cropImg) #저장
        
    



#only for scrollSave
#스크롤된 화면의 상대 좌표 리스트를 절대 좌표 리스트로 변환       
def transToNatural(img_w, img_h, coord):
    
    Trans_list =[]  
    for i in range(len(coord)):
        #상대 좌표값을 절대 좌표로 변환
        left = math.floor(coord[i][1]*img_w)  #가로 시작 좌표 (좌)
        up = math.floor(coord[i][2]*img_h)  #세로 끝 좌표 (상)
        right = math.floor(coord[i][3]*img_w)  #가로 끝 좌표 (우)
        down = math.floor(coord[i][4]*img_h)  #세로 시작 좌표 (하)
        
        Trans_list.append([left,up,right,down])
        
        
    return Trans_list;        


#only for scrollSave : 이미지와 절대 좌표 받아서 크롭 
def cropAbs(image, list):
    img = cv2.imread(image)  #이미지 읽어옴
    
    left = list[0]
    up = list[1]
    right = list[2]
    down = list[3]
    
    crop = img[down:up, left:right]
    return crop
 


    