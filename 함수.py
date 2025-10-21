# 함수.py


def setValue(newValue):
    #지역변수
    x=newValue
    print("지역변수:",x)

#2)함수를 호출
result = setValue(5)
print(result)

#1)함수를 정의 
def swap(x,y):
    return y,x
#호출
result = swap(3,4)
print(result)


#지역변수와 전역변수 연습
x=1
def func(a):
    return a+x

#호출
print(func(1))


def func2(a):
    #지역변수
    x=5
    return a+x
#호출
print(func2(1))




