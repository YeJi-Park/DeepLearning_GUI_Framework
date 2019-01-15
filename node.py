import numpy as np
class Node :
    def __init__(self, filename, coord, selected) :
        self.filename = filename #초기화할때 filename은 받아서.
        self.coord = coord #초기화할때 coordi는 받아서.
        self.selected = selected #초기화할때 부모의 몇 번 object로 부터 왔는지
        self.score = 0 #초기화할때 score는 0임.
        self.index = 0 #testscript 생성할때 쓸 index
        self.numchild = 0 #초기화할때 child수는 0임
        self.children = [] #새로 노드 추가할때 칠드런 없음..
        self.parent = None

    def add_child(self, newNode):
        self.children.append(newNode)#children 의 numchild 번째에 새로운 Node 추가.
        newNode.parent = self #자식노드의 부모는 나야나
        self.numchild = self.numchild + 1 #numchild + 1

    def get_numchild(self):
        return self.numchild

    def get_child(self, index):
        return self.children[index]

    def get_filename(self):
        return self.filename

    def get_parent(self):
        return self.parent

    def get_score(self):
        return self.score

    def get_index(self):
        return self.index

    def get_selected(self):
        return self.selected

    @property
    def get_amountobject(self):
        return len(self.coord)

    def set_score(self, score):
        self.score = score

    def set_index(self, index):
        self.index = index

    def is_leaf(self):
        if self.get_numchild() == 0 :
            return True
        else :
            return False

    def get_xy(self): #현재 노드에서 score를 통해서 해당 좌표를 받아와서 크롭할때와 클릭에 넘겨줄 때에 쓸 예정임. 결과값은 x1,x2,y1,y2
        X_center = self.coord[self.score][1] + self.coord[self.score][3]
        Y_center = self.coord[self.score][2] + self.coord[self.score][4]

        XY = [X_center, Y_center]

        return XY

