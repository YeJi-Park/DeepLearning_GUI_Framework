from tree import Tree
from node import Node
from time import sleep
import uiautomator2 as u2
import testingdef as obj_detect
import crop_ob
import revisedCompare as com
import cv2
import os
import csv

def capture():
    sleep(1) #화면전환 기다림
    image = d.screenshot(format='opencv')

    return image

def click(XY):
    x = XY[0]/2
    y = XY[1]/2
    d.click(x, y)

def mkTree(tempNode):
    if tempNode == None : #이번 캡쳐가 처음인 경우
        image = capture() #이미지 캡쳐해주고
        os.makedirs(os.path.join('Tree'))#ratio 가 같은 경로에 저장할 것
        #image = cv2.resize(image,(int(image.shape[1]/4), int(image.shape[0]/4)))#1/16으로 리사이즈 for 속도
        imagepath = os.path.join('Tree', '0.jpg')
        cv2.imwrite(imagepath, image)  # 이미지 저장하고
        coord = obj_detect.findButton(imagepath) #오브젝트 디텍션 해줌
        crop_ob.cropSave(imagepath,coord)
        newNode = Node(0, coord, None)  # 루트 노드 생성해주고
        tree.set_root(newNode) # 트리에 루트 노드 추가.

        return mkTree(newNode) #새로설정된 루트노드로부터 탐색. 루트가 없는경우가 아니라면 tempNode로부터 클릭하고 시작하니 괜찮다.

    else: #루트노드가 있는 경우
        while tempNode.get_score() < tempNode.get_amountobject :#누를 것이 있는 경우
            if(tempNode.get_parent() != None):
                print('tempNode:', tempNode.get_filename(), 'score:', tempNode.get_score(), 'Parent:', tempNode.get_parent().get_filename())
            else:
                print('tempNode:', tempNode.get_filename(), 'score:', tempNode.get_score())
            curApp = d.current_app()['package']
            click(tempNode.get_xy()) #클릭 하고
            tempNode.set_score(tempNode.get_score()+1) #탐색할 인덱스 바꿔주고
            if curApp != d.current_app()['package']: # 외부앱 연결 검사
                sleep(1)
                d.press("back")
                sleep(0.5)
                d.press("back")

                continue

            image = capture() #캡쳐 하고
            #image = cv2.resize(image, (int(image.shape[1]/4), int(image.shape[0]/4)))#리사이즈 for 속도
            imagepath = os.path.join('Tree', 'temp.jpg')
            cv2.imwrite(imagepath, image)
            target_imagepath = os.path.join('Tree', str(tempNode.get_filename()) + '.jpg')
            flag = com.compare(target_imagepath, imagepath) # 화면전환이 일어났는지 비교..

            if flag == 2 :#화면전환이 일어난경우
                if tempNode.get_parent() == None : #부모랑 비교할 필요 없으면
                    newfilename = str(tempNode.filename) + '.' + str(tempNode.get_numchild()) #저장할 파일명 정해주고
                    imagepath = os.path.join('Tree', newfilename +'.jpg')
                    cv2.imwrite(imagepath, image) #이미지 저장해주고
                    coord = obj_detect.findButton(imagepath) #이미지 모델로 보내서 리스트 받아오고
                    crop_ob.cropSave(imagepath, coord) # 리스트 통해서 이미지 크롭해주고 저장하고
                    newNode = Node(newfilename, coord, tempNode.get_score()-1) #새로운 노드 생성해주고
                    tempNode.add_child(newNode) # 트리에 노드 추가해주고

                    return mkTree(newNode) #newNode로가서 다시시작

                elif isLoop('Tree', tempNode, imagepath) != -1: # compare 했는데, 부모세대에 같은 화면이 존재한다(잠재적인 무한루프)
                    count = isLoop('Tree', tempNode, imagepath)
                    xy_list = [] # 현재 화면까지 돌아올려면 눌러야 할 xy 좌표들을 저장할 리스트 생성
                    targetNode = tempNode
                    for i in range (0, count) :
                        targetNode = targetNode.get_parent() # 같은 화면이 있던 해당 노드로 돌아오기 위해 부모노드를 따라간다
                        targetNode.set_score(targetNode.get_score()-1)#지시자 뒤로 백해주고
                        xy_list.append(targetNode.get_xy()) #눌러야 할 좌표들을 저장하고
                        targetNode.set_score(targetNode.get_score()+1)#지시자 돌려놓음

                    xy_list.reverse()
                    for i in range(0, count) :
                        click(xy_list[i]) # 순서대로 클릭하여 현재 화면까지 돌아온다.

                    continue#현재노드에서 다음 object 눌러봄

                else : #새로운 화면이다
                    newfilename = str(tempNode.filename) + '.' + str(tempNode.get_numchild())  # 저장할 파일명 정해주고
                    imagepath = os.path.join('Tree', newfilename + '.jpg')
                    cv2.imwrite(imagepath, image)  # 이미지 저장해주고
                    coord = obj_detect.findButton(imagepath)  # 이미지 모델로 보내서 리스트 받아오고
                    crop_ob.cropSave(imagepath, coord)  # 리스트 통해서 이미지 크롭해주고 저장하고
                    newNode = Node(newfilename, coord, tempNode.get_score()-1)  # 새로운 노드 생성해주고
                    tempNode.add_child(newNode)  # 트리에 노드 추가해주고

                    return mkTree(newNode)  # newNode로가서 다시시작

            else: #눌렀는데 화면이 변하지 않았따(잘못된 오브젝트를 찾았다)

                continue #담거누르자
        # 누를 것이 없는 경우 while문 끝난거 tempNode.score == amountobject인 경우
        if tempNode.get_parent() == None : #루트노드인 경우
            print("Menu Tree Generate Complete!")
            return 0 #끝조건임.
        else :
            sleep(1)
            d.press("back") #뒤로가고
            sleep(1)

            return mkTree(tempNode.get_parent())#부모노드로부터 시작

def isLoop(ratio, Node, img):
    count = 1
    while Node.get_parent() != None :
        target_imagepath = os.path.join(ratio, str(Node.get_parent().filename) + '.jpg')
        if com.compare(target_imagepath, img) == 1 : #같으면
            return count
        elif Node.get_parent() == None :
            return -1
        else :
            Node = Node.get_parent()
            count = count+1
    return -1

def genscript(path, tempNode, data) :
    if tempNode.is_leaf():
        filepath = os.path.join(path, 'script.txt')
        file = open(filepath, 'a', encoding='utf-8')
        data = data + ' ' + str(tempNode.get_selected()) + ' ' + str(tempNode.get_filename()) + '\n'
        file.write(data)
    elif tempNode == tree.root :
        for i in range (0, tempNode.get_numchild()) :
            genscript(path, tempNode.get_child(i), data)
    else :
        data = data + ' ' + str(tempNode.get_selected()) + ' ' + str(tempNode.get_filename())
        for i in range(0, tempNode.get_numchild()):
            genscript(path, tempNode.get_child(i), data)

d = u2.connect()
tree = Tree()
mkTree(None)
genscript('tree', tree.root, '0')