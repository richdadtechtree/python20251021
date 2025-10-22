import openpyxl as op
import random

wb = op.Workbook()
ws = wb.active
ws.title = "Products"

# 헤더
ws.append(["제품ID", "제품명", "가격", "수량"])

brands = ["SAMSUNG", "LG", "SONY", "PANASONIC", "SHARP", "PHILIPS", "DELL", "HP", "ASUS", "APPLE"]
types = ["TV", "스마트폰", "노트북", "태블릿", "무선이어폰", "스피커", "모니터", "카메라", "냉장고", "세탁기"]
models = ["A", "B", "X", "S", "Pro", "Plus", "Mini", "Max", "Z", "Elite"]

for i in range(1, 101):
    product_id = f"P{1000 + i}"
    product_name = f"{random.choice(brands)} {random.choice(types)} {random.choice(models)}{random.randint(1,99)}"
    price = random.randint(30000, 2500000)  # 원 단위 가격
    quantity = random.randint(0, 100)
    ws.append([product_id, product_name, price, quantity])

wb.save("ProductList.xlsx")
print("ProductList.xlsx 저장 완료 (100개 항목)")