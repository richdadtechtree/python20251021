# web2.py
#웹사이트 요청
import urllib.request

#크롤링
from bs4 import BeautifulSoup   
#정규표현식: 특정 문자열 패턴 찾기
import re

#파일에 저장
f= open("clien.txt", "wt", encoding="utf-8")

for n in range(0,10):
     url = "https://www.clien.net/service/board/sold?&od=T31&category=0&po=" + str(n)
     print(url)

     data = urllib.request.urlopen(url).read()   

     soup = BeautifulSoup(data, 'html.parser')
     list = soup.find_all("span", attrs={"data-role":"list-title-text"})
     for item in list:   
         title = item.text.strip()
         print(title)        
         f.write(title + "\n")


f.close()




# <span class="subject_fixed" data-role="list-title-text" title="아이폰17 256g 화이트 미개봉">
#     아이폰17 256g 화이트 미개봉
# </span>