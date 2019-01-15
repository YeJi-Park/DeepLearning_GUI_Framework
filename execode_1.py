import uiautomator2 as u2
import cv2
from time import sleep
import revisedCompare as com
import pytesseract as TA
import os
import crop_ob
import testingdef as obj_detect
import shutil
from difflib import SequenceMatcher

def backtoMain(n):
    k = int(n)
    for k in range(k):
        d.press("back")
        sleep(1)

def button_to_text(image) :
    return TA.image_to_string(image,lang='kor')

def compare_text(imgpath1, imgpath2) :
    image1 = cv2.imread(imgpath1,cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread(imgpath2,cv2.IMREAD_GRAYSCALE)

    text1 = button_to_text(image1)
    text2 = button_to_text(image2)
    #print(text1)
    #print('-----------------------------------')
    #print(text2)

    if text1 == text2 :
        return True
    elif text1 in text2 :
        return True
    elif text2 in text1 :
        return True #해상도에 따른 정보량 차이 때문에 포함관계 == 같은화면으로 인식
    else :
        return False
def similar(text1, text2) : #text간의 유사도 비교
    return SequenceMatcher(None, text1, text2).ratio()

def compare_text_button(img_path1, img_path2) :
    image1 = cv2.imread(img_path1, cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread(img_path2, cv2.IMREAD_GRAYSCALE)

    text1 = button_to_text(image1)
    text2 = button_to_text(image2)

    if text1 == text2 :
        return True
    else :
        return False

def compare_text_button_img(img1, img_path) :
    image1 = img1
    image2 = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    text1 = button_to_text(image1)
    text2 = button_to_text(image2)

    #print(text1)
    #print('-----------------------------------')
    #print(text2)

    if similar(text1, text2) > 0.4 :
        return True
    else :
        return False
    '''
    print(text1, text2)
    if text1 == text2:
        return True
    else:
        return False
    '''


def sliceFile(path):
    caseList = [] # Case Script를 슬라이스해서 넣을 리스트
    filepath = os.path.join(path, 'script.txt')
    with open(filepath, 'r') as f: # 파일 오픈
        while True:
            line = f.readline() # 한 줄 읽기
            if not line: # 라인 끝났으면 종료
                break
            caseList.append(line.split()) # 슬라이스해서 리스트에 추가
    return caseList

def click(XY):
    x = XY[0]/2
    y = XY[1]/2
    d.click(x, y)

def capture():
    sleep(1) #화면전환 기다림
    image = d.screenshot(format='opencv')

    return image

def write_result(line, flag, model_name):
    if flag == True:
        line = ' '.join(line)
        line = line + '\t+PASS+\n'
        result_path = os.path.join('result', model_name + '.txt')
        f_output = open(result_path, 'a', encoding='utf-8')
        f_output.write(str(line))
        f_output.close()
    else:
        line = ' '.join(line)
        line = line + '\t+FAIL+\n'
        result_path = os.path.join('result', model_name + '.txt')
        f_output = open(result_path, 'a', encoding='utf-8')
        f_output.write(str(line))
        f_output.close()
def execute():
    model_name = str(d.device_info['model'])
    result = 0
    caseList = sliceFile('Tree')
    sample_image = capture()
    x_temp = sample_image.shape[0]
    y_temp = sample_image.shape[1]
    target_image = cv2.imread(os.path.join('Tree', caseList[0][0] +'.jpg'))
    x_target = target_image.shape[0]
    y_target = target_image.shape[1] #화면 비율을 확인하기 위해서 샘플 데이터로 해상도 추출
    x_ratio = x_temp/x_target
    y_ratio = y_temp/y_target #템플랫 매칭 실패시 비율 조정하여 다시 매칭할 때에 사용할 변수

    flag = True # 테스팅 결과를 저장하는 flag, 성공이면 true 다르면 false
    for i in range(len(caseList)):
        for j in range(len(caseList[i])):
            if j%2 == 0:  #노드 번호인 경우
                image = capture()
                #image = cv2.resize(image, (int(image.shape[1] / 4), int(image.shape[0] / 4))) # 현재 화면 캡쳐
                cv2.imwrite('temp.jpg', image)  # temp.jpg로 저장(jpg 양자화 때문에)
                sshot = os.path.join('Tree', str(caseList[i][j]))
                coord = obj_detect.findButton('temp.jpg')
                shutil.rmtree('temp',ignore_errors=True)
                crop_ob.cropSave('temp.jpg', coord)

                if not com.folder_compare(sshot, 'temp', len(coord)) : #다른 화면이면
                    flag = False
                    backtoMain(j/2)
                    break
                else:
                    print("같은 화면: "+str(j))
            else:  #obj 번호인 경우
                # caseList[i][j-1] 폴더에 들어가서
                print('dir '+caseList[i][j-1])
                print('ob'+caseList[i][j])
                ob_path = os.path.join('Tree', caseList[i][j-1], 'ob'+caseList[i][j]+'.jpg')
                ob_temp = cv2.imread(ob_path)
                ob_temp = cv2.resize(ob_temp, (int(ob_temp.shape[1] * y_ratio), int(ob_temp.shape[0] * x_ratio)))#오브젝트 리사이즈 해주고
                cv2.imwrite('re_temp.jpg', ob_temp)
                match = com.find_obj(image,ob_temp) #템플릿 매칭해서

                if not match : #리사이즈 매칭 실패시, 크롭해서 텍스트 비교해봅시다.
                    X_center = None
                    Y_center = None
                    k = 0
                    while k < len(coord):
                        ob_target = os.path.join('temp', 'ob' + str(k) + '.jpg')
                        if compare_text_button_img(ob_temp, ob_target) : #텍스트 매칭 성공하면 클릭하기위해 해당 좌표 저장
                            X_center = coord[k][1]/2 + coord[k][3]/2
                            Y_center = coord[k][2]/2 + coord[k][4]/2 #저장저장~
                            #print('ob' + str(k) + ' 텍스트는 찾아야지 새끼야')
                            break
                        k = k+1
                    if k == len(coord) : #이것까지 실패하다니...형편없는놈
                        backtoMain((j-1) / 2)
                        flag = False
                        #print('이것까지 실패하다니...형편없는놈')
                        break
                    else : #조건 2에서 성공
                        print('텍스트 매칭 성공')
                        d.click(X_center, Y_center)
                else : #조건1에서 성공
                    print('매칭 성공')
                    print(match[0])
                    X_center = ((match[0][0] + match[0][2]) / 2)   # resize 때문에
                    Y_center = ((match[0][1] + match[0][3]) / 2)
                    d.click(X_center, Y_center)

        #flag 체크해서 패스 여부 출력
        if flag:
           print(caseList[i])
           #print('pass')
           backtoMain(j/2)
           write_result(caseList[i], flag, model_name)
           result = result + 1
              
        else:
           print(caseList[i])
           #print('fail')
           write_result(caseList[i], flag, model_name)
        
        
        #print("---------------------")
        flag = True
    result_p = result/len(caseList)*100
    result_path = os.path.join('result', model_name + '.txt')
    file = open(result_path, mode='a', encoding='utf-8')
    file.write('Result : ' + str(result) + '/' + str(len(caseList)) + '=' + str(result_p)+ '%')

# 결과 출력
d = u2.connect()
execute()