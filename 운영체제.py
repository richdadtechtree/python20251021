#운영체제.py
import os
import glob


print("운영체제이름 :" , os.name)

fileName = " c\\python310\\python.exe:"

if os.path.exists(fileName):
    print("파일크기:". os.path.getsize(fileName))
else:
    print("파일이 존재하지 않습니다.")

print(os.path.abspath('python.exe'))
print(os.path.basename(fileName))


for fileName in glob.glob(r"c:\\work\\*.py"):
    print(fileName) 

    