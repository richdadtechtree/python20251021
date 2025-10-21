# demoloop.py

value = 5
while value < 0:
    print(value)
    value-= 1

print("---for in루프---")
for i in [1,2,3]:
    print(i)


d={"apple":100, "kiwi":200}
for k,v in d.items():
    print(k,v)


print("---range()함수---")
print(list(range(10)))
print(list(range(1,11)))
print(list(range(2000,2026)))


print("---리스트 컴프리핸션---")
lst = [1,2,3,4,5,6,7,8,9,10]
print([i**2 for i in lst if i > 5])
tp = ("apple", "kiwi")
print( [len(i) for i in tp])

print("---필터링 함수---")
lst= [10,25,30]

itemL = filter(None, lst)
for i in itemL:
    print("Item:{0}".format(i))

print("---필터링 함수 사용---")
def getBiggerThan20(i):
    return i >20

itemL = filter(getBiggerThan20, lst)
for i in itemL:
    print("Item:{0}".format(i))


print("---람다 함수---")

itemL = filter(lambda x:x>20, lst)
for i in itemL:
    print("Item:{0}".format(i))