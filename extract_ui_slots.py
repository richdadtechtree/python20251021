# -*- coding: utf-8 -*-
# 사용법: 작업 폴더(c:\work)에서 `python extract_ui_slots.py` 실행
import xml.etree.ElementTree as ET
import os
ui_path = os.path.join(os.getcwd(), "ProductList3.ui")
if not os.path.exists(ui_path):
    print("ProductList3.ui 파일을 찾을 수 없습니다:", ui_path)
    raise SystemExit(1)

tree = ET.parse(ui_path)
root = tree.getroot()

slots = set()
signals = set()
widgets = []

# .ui의 <connections> 안의 <connection> 요소에서 signal/slot 추출
for conn in root.findall(".//connection"):
    sig = conn.findtext("signal")
    slot = conn.findtext("slot")
    if sig:
        signals.add(sig.strip())
    if slot:
        slots.add(slot.strip().rstrip("()"))

# 모든 위젯의 objectName(=name)과 class 추출
for w in root.findall(".//widget"):
    name = w.get("name")
    cls = w.get("class")
    if name:
        widgets.append((name, cls))

print("== UI 파일:", ui_path)
print()
print("명시적 연결된 슬롯 (ui에 <slot>로 정의된 것):")
if slots:
    for s in sorted(slots):
        print(" -", s)
else:
    print(" (없음)")

print()
print("명시적 연결된 시그널 (ui에 <signal>로 정의된 것):")
if signals:
    for s in sorted(signals):
        print(" -", s)
else:
    print(" (없음)")

print()
print("위젯 목록 (objectName, class):")
for n, c in widgets:
    print(" -", n, ",", c)

print()
print("다음 단계: 출력 결과(특히 슬롯 이름)를 붙여 주시거나 ProductList3.ui 파일을 업로드해 주세요.")