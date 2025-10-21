# DemoClass.py

#1) 클래스를 정의
class Person:
    #초기화 메서드를 정의
    def  __init__(self):
        self.name = "default name"
    def print(self):
        print("My name is {0}".format(self.name))



#2) 인스턴스를 생성
#중단점
p1=Person()
p2=Person()
p1.name="전우치"
#3) 메서드를 호출
p1.print()
p2.print()