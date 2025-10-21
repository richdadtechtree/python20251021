# demoTupleSet.py


print("---set형식---")
a = {1,2,3,3}
b={3,4,4,5}
print(a)
print(b)
print(a.union(b))
print(a.intersection(b))
print(a.difference(b))

print("---tuple형식---")
tp = (10,20, 30)
print(len(tp))

#함수정의
def times(a,b):
    return a+b, a*b
#호출
result = times(3,4)
print(result)





print("---형식변환---")
a = set((1,2,3))
print(a)
b = list(a)
b.append(4)
print(b)


print("---dict형식---")
fruits = {"apple":"red", "banana":"yellow"}
#검색
print(fruits["apple"])
#입력
fruits["kiwi"]="green"
print(fruits)

#삭제
del fruits["apple"]
#반복문
for item in fruits.items():
    print(item)