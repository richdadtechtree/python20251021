# db1.py

import sqlite3

con = sqlite3.connect(":memory:")

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



cur.execute("SELECT * FROM PhoneBook;")
print("---fetchone()---")
print(cur.fetchone())  #한 건씩 가져오기
print("---fetchmany(2)---")    
print(cur.fetchmany(2))  #한 건씩 가져오기
print("---fetchall()---")
cur.execute("SELECT * FROM PhoneBook;")
print(cur.fetchall())    #한 건씩 가져오기






