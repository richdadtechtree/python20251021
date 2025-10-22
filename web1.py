# web1.py

from bs4 import BeautifulSoup   

#웹페이지를 로딩
page = open("Chap09_test.html", "r", encoding="utf-8")


#검색이 용이한 객체 생성
soup  = BeautifulSoup(page, "html.parser")


#전체 문서 보기
# print(soup.prettify())
#<p>태그 모두 검색
# plist = soup.find_all("p")
# print(plist)


# <p>하나만 검색
# print(soup.find("p"))


# #조건검색 : <p class="outer-text">
# print(soup.find_all("p", class_="outer-text"))

#attrs 속성으로 검색
# print(soup.find_all("p", attrs={"class":"outer-text"})) 


# 태그 내부의 문자열만 검색: .text속성
for tag in soup.find_all("p"):
    title = tag.text.strip()
    print(title).replace("\n", " ")
    print(title)

