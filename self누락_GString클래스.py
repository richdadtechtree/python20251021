#전역 변수
strName = "Not Class Member"

class DemoString:
    def __init__(self):
        #인스턴스 멤버변수
        self.strName = "" 
    def set(self, msg):
        self.strName = msg
    def print(self):
        #버그변수
        print(self.strName)

d = DemoString()
d.set("First Message")
d.print()
