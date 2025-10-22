# db1.py

import sqlite3

#실제 파일에 저장(파일명을 변경)
con = sqlite3.connect(r"c:\work\sample.db")

#구문을 실행할 커서 객체 생성

cur = con.cursor()  

#테이블 생성
cur.execute("CREATE TABLE PhoneBook (name text, phonenum text);")
            
#1건 입력
cur.execute("INSERT INTO PhoneBook VALUES ('홍길동', '010-1234-5678');")


#입력 파마메터로 처리
name = "전우치"
phonenum = "010-8765-4321"
cur.execute("INSERT INTO PhoneBook VALUES (?, ?);", (name, phonenum))


#다중의 행 입력
datalist = (("박문수", "010-1111-2222"),("김유신", "010-3333-4444"))
cur.executemany("INSERT INTO PhoneBook VALUES (?, ?);", datalist)

#데이터 검색
for row in cur.execute("SELECT * FROM PhoneBook;"):
    print(row)  
# CTRL + /   주석 처리 (선택한 블럭 주석 처리)


# 작업을 완료
con.commit()    
con.close()








