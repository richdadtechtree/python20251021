# DeomForm.py
# DeomoForm.ui(화면단) + DeomoForm.py(로직단) 구성된 예제


import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic


#디자인 파일을 로딩
form_class = uic.loadUiType("DemoForm.ui")[0]

#폼 클래스를 정의
class DemoForm(QDialog, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label.setText("문자열을 출력")

#진입점을 체크
if __name__ == "__main__":
    app = QApplication(sys.argv)
    #위에서 정의한 폼을 생성
    demoForm = DemoForm()
    #화면에 보여주기
    demoForm.show()
    #대기하면서 이벤트 처리하기
    sys.exit(app.exec_())
    
