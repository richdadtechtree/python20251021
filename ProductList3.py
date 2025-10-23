import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5 import uic
import sqlite3
import os

# DB 관련 로직을 분리
class ProductDB:
    def __init__(self, db_path=None):
        if db_path is None:
            base = os.path.dirname(__file__) if '__file__' in globals() else os.getcwd()
            db_path = os.path.join(base, "ProductList.db")
        self.db_path = db_path
        self.con = sqlite3.connect(self.db_path, isolation_level=None)
        self.cur = self.con.cursor()
        self._ensure_table()

    def _ensure_table(self):
        self.cur.execute(
            "create table if not exists Products (id integer primary key autoincrement, Name text, Price integer);"
        )

    def add(self, name, price):
        try:
            price_int = int(price)
        except (ValueError, TypeError):
            price_int = 0
        self.cur.execute("insert into Products (Name, Price) values (?, ?);", (name, price_int))

    def update(self, id_, name, price):
        try:
            id_int = int(id_)
        except (ValueError, TypeError):
            return
        try:
            price_int = int(price)
        except (ValueError, TypeError):
            price_int = 0
        self.cur.execute("update Products set Name=?, Price=? where id=?;", (name, price_int, id_int))

    def remove(self, id_):
        try:
            id_int = int(id_)
        except (ValueError, TypeError):
            return
        self.cur.execute("delete from Products where id=?;", (id_int,))

    def list_all(self):
        self.cur.execute("select id, Name, Price from Products order by id;")
        return self.cur.fetchall()

    def close(self):
        try:
            self.cur.close()
        except:
            pass
        try:
            self.con.close()
        except:
            pass


# 디자인 파일을 로딩
form_class = uic.loadUiType("ProductList3.ui")[0]

class Window(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # DB 인스턴스
        self.db = ProductDB()

        # 초기값
        self.id = 0
        self.name = ""
        self.price = 0

        # QTableWidget 설정
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.setHorizontalHeaderLabels(["제품ID", "제품명", "가격"])
        self.tableWidget.setTabKeyNavigation(False)

        # Enter 키 이동
        self.prodID.returnPressed.connect(lambda: self.focusNextChild())
        self.prodName.returnPressed.connect(lambda: self.focusNextChild())
        self.prodPrice.returnPressed.connect(lambda: self.focusNextChild())

        # 더블클릭 시그널은 UI 자동연결이나 수동연결 모두 지원
        self.tableWidget.doubleClicked.connect(self.on_tableWidget_doubleClicked)

        # 버튼이 UI에 있을 경우 안전하게 연결 (수동 연결; UI 자동연결도 동작함)
        if hasattr(self, "btnAdd"):
            self.btnAdd.clicked.connect(self.on_btnAdd_clicked)
        if hasattr(self, "btnUpdate"):
            self.btnUpdate.clicked.connect(self.on_btnUpdate_clicked)
        if hasattr(self, "btnRemove"):
            self.btnRemove.clicked.connect(self.on_btnRemove_clicked)
        if hasattr(self, "btnGet"):
            self.btnGet.clicked.connect(self.on_btnGet_clicked)

        # 초기 목록 로드
        self.on_btnGet_clicked()

    # UI 자동 연결 규칙에 맞춘 메서드들
    @pyqtSlot()
    def on_btnAdd_clicked(self):
        self.name = self.prodName.text()
        self.price = self.prodPrice.text()
        self.db.add(self.name, self.price)
        self.on_btnGet_clicked()
        # 입력 필드 초기화
        self.prodID.clear()
        self.prodName.clear()
        self.prodPrice.clear()

    @pyqtSlot()
    def on_btnUpdate_clicked(self):
        self.id = self.prodID.text()
        self.name = self.prodName.text()
        self.price = self.prodPrice.text()
        self.db.update(self.id, self.name, self.price)
        self.on_btnGet_clicked()

    @pyqtSlot()
    def on_btnRemove_clicked(self):
        self.id = self.prodID.text()
        self.db.remove(self.id)
        self.on_btnGet_clicked()
        self.prodID.clear()
        self.prodName.clear()
        self.prodPrice.clear()

    @pyqtSlot()
    def on_btnGet_clicked(self):
        # 기존 내용 제거
        self.tableWidget.clearContents()
        rows = self.db.list_all()
        self.tableWidget.setRowCount(len(rows))
        for row_idx, item in enumerate(rows):
            id_str = str(item[0])
            name_str = str(item[1])
            price_str = str(item[2])

            itemID = QTableWidgetItem(id_str)
            itemID.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            itemID.setFlags(itemID.flags() & ~Qt.ItemIsEditable)
            self.tableWidget.setItem(row_idx, 0, itemID)

            self.tableWidget.setItem(row_idx, 1, QTableWidgetItem(name_str))

            itemPrice = QTableWidgetItem(price_str)
            itemPrice.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableWidget.setItem(row_idx, 2, itemPrice)

    # QTableWidget.doubleClicked 자동 연결 규칙 (index 파라미터를 받을 수 있음)
    @pyqtSlot(object)
    def on_tableWidget_doubleClicked(self, index=None):
        # index가 제공되지 않아도 현재 선택 행을 사용
        row = -1
        try:
            if index is None:
                row = self.tableWidget.currentRow()
            else:
                row = index.row()
        except:
            row = self.tableWidget.currentRow()

        if row < 0:
            return
        id_item = self.tableWidget.item(row, 0)
        name_item = self.tableWidget.item(row, 1)
        price_item = self.tableWidget.item(row, 2)
        if id_item:
            self.prodID.setText(id_item.text().strip())
        if name_item:
            self.prodName.setText(name_item.text().strip())
        if price_item:
            self.prodPrice.setText(price_item.text().strip())

    # 기존 메서드명 호환용 래퍼 (필요시 호출되던 기존 이름들 유지)
    def addProduct(self):
        return self.on_btnAdd_clicked()

    def updateProduct(self):
        return self.on_btnUpdate_clicked()

    def removeProduct(self):
        return self.on_btnRemove_clicked()

    def getProduct(self):
        return self.on_btnGet_clicked()

    def closeEvent(self, event):
        # 프로그램 종료 시 DB 닫기
        try:
            self.db.close()
        except:
            pass
        super().closeEvent(event)


# 인스턴스 생성 및 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    sys.exit(app.exec_())



