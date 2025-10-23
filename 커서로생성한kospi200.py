#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 코스피200 편입종목상위 데이터 크롤링 스크립트
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
from typing import List, Dict, Optional
import re

class Kospi200Crawler:
    def __init__(self):
        """코스피200 크롤러 초기화"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.base_url = "https://finance.naver.com/sise/sise_index.naver?code=KPI200"
    
    def get_kospi200_data(self) -> List[Dict[str, str]]:
        """
        코스피200 편입종목상위 데이터를 크롤링합니다.
        
        Returns:
            List[Dict[str, str]]: 편입종목 데이터 리스트
        """
        try:
            print("코스피200 편입종목상위 페이지에 접속 중...")
            
            # 편입종목상위 페이지 URL 직접 사용
            entry_url = "https://finance.naver.com/sise/entryJongmok.naver?type=KPI200"
            
            # 페이지 요청
            response = requests.get(
                entry_url, 
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 편입종목상위 테이블 찾기
            stock_data = self._extract_stock_data(soup)
            
            print(f"총 {len(stock_data)}개의 편입종목 데이터를 추출했습니다.")
            return stock_data
            
        except requests.RequestException as e:
            print(f"페이지 요청 중 오류 발생: {e}")
            return []
        except Exception as e:
            print(f"데이터 추출 중 오류 발생: {e}")
            return []
    
    def _extract_stock_data(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        HTML에서 편입종목 데이터를 추출합니다.
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML 객체
            
        Returns:
            List[Dict[str, str]]: 편입종목 데이터 리스트
        """
        stock_data = []
        
        try:
            # 편입종목상위 페이지에서 테이블 찾기
            table = soup.find('table', class_='type_1')
            if not table:
                # 다른 테이블 클래스들 시도
                for class_name in ['type_4', 'type_2', 'type_3', 'type_5']:
                    table = soup.find('table', class_=class_name)
                    if table:
                        print(f"테이블을 찾았습니다: {class_name}")
                        break
            
            if not table:
                print("편입종목 테이블을 찾을 수 없습니다.")
                # 디버깅을 위해 모든 테이블 정보 출력
                tables = soup.find_all('table')
                print(f"페이지에서 발견된 테이블 수: {len(tables)}")
                for i, t in enumerate(tables):
                    print(f"테이블 {i+1}: {t.get('class', 'No class')} - {t.get('summary', 'No summary')}")
                return []
            
            print("편입종목상위 테이블을 찾았습니다.")
            
            # 테이블 행들 추출
            rows = table.find_all('tr')
            print(f"테이블에서 {len(rows)}개의 행을 찾았습니다.")
            
            # 데이터 행들 처리 (헤더와 빈 행 제외)
            data_rows = []
            for i, row in enumerate(rows):
                cells = row.find_all('td')
                
                # 종목명 링크가 있는 행만 데이터 행으로 간주 (컬럼 수에 관계없이)
                if len(cells) >= 3:  # 최소 3개 컬럼만 있으면 확인
                    # 다양한 링크 패턴 시도
                    stock_link = None
                    link_patterns = [
                        '/item/main.naver',
                        '/item/',
                        'main.naver'
                    ]
                    
                    for pattern in link_patterns:
                        stock_link = cells[0].find('a', href=lambda x: x and pattern in x)
                        if stock_link:
                            break
                    
                    if stock_link:
                        data_rows.append(row)
                    else:
                        # 텍스트가 종목명처럼 보이는지 확인
                        first_cell_text = cells[0].get_text(strip=True)
                        if first_cell_text and len(first_cell_text) > 1 and not first_cell_text.replace('.', '').replace('%', '').replace(',', '').isdigit():
                            data_rows.append(row)
            
            print(f"데이터 행 {len(data_rows)}개를 찾았습니다.")
            
            for i, row in enumerate(data_rows):
                try:
                    cells = row.find_all('td')
                    
                    # 종목명 추출 (링크 텍스트)
                    stock_name_cell = cells[0]
                    stock_name_link = stock_name_cell.find('a', href='/item/main.naver')
                    stock_name = stock_name_link.get_text(strip=True) if stock_name_link else ''
                    
                    # 링크가 없으면 첫 번째 셀의 텍스트를 종목명으로 사용
                    if not stock_name:
                        stock_name = stock_name_cell.get_text(strip=True)
                    
                    # 기본값 설정
                    current_price = ''
                    change_text = ''
                    change_direction = ''
                    change_rate = ''
                    volume = ''
                    amount = ''
                    market_cap = ''
                    
                    # 컬럼 수에 따라 데이터 추출
                    if len(cells) >= 2:
                        current_price = cells[1].get_text(strip=True)
                    
                    if len(cells) >= 3:
                        change_cell = cells[2]
                        change_text = change_cell.get_text(strip=True)
                        # 하락/상승 아이콘 확인
                        if change_cell.find('em', class_='bu_pdn'):
                            change_direction = '▼'
                        elif change_cell.find('em', class_='bu_pup'):
                            change_direction = '▲'
                        elif change_cell.find('em', class_='bu_pn'):
                            change_direction = '='
                    
                    if len(cells) >= 4:
                        change_rate = cells[3].get_text(strip=True)
                    
                    if len(cells) >= 5:
                        volume = cells[4].get_text(strip=True)
                    
                    if len(cells) >= 6:
                        amount = cells[5].get_text(strip=True)
                    
                    if len(cells) >= 7:
                        market_cap = cells[6].get_text(strip=True)
                    
                    # 데이터 정리
                    stock_info = {
                        '순위': i + 1,
                        '종목명': stock_name,
                        '현재가': current_price.replace(',', '') if current_price else '',
                        '전일비': f"{change_direction}{change_text}" if change_text else '',
                        '등락률': change_rate if change_rate else '',
                        '거래량': volume.replace(',', '') if volume else '',
                        '거래대금': amount.replace(',', '') if amount else '',
                        '시가총액': market_cap.replace(',', '') if market_cap else ''
                    }
                    
                    # 종목명이 있는 경우만 추가
                    if stock_info['종목명']:
                        stock_data.append(stock_info)
                    
                except Exception as e:
                    print(f"행 {i+1} 처리 중 오류: {e}")
                    continue
            
        except Exception as e:
            print(f"테이블 데이터 추출 중 오류: {e}")
        
        return stock_data
    
    def save_to_csv(self, data: List[Dict[str, str]], filename: str = "kospi200_top_stocks.csv"):
        """
        크롤링 결과를 CSV 파일로 저장합니다.
        
        Args:
            data (List[Dict[str, str]]): 크롤링 결과
            filename (str): 저장할 파일명
        """
        try:
            if not data:
                print("저장할 데이터가 없습니다.")
                return
            
            # CSV 파일에 저장
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['순위', '종목명', '현재가', '전일비', '등락률', '거래량', '거래대금', '시가총액']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 헤더 작성
                writer.writeheader()
                
                # 데이터 작성
                for stock in data:
                    writer.writerow(stock)
            
            print(f"데이터가 {filename} 파일에 저장되었습니다.")
            
        except Exception as e:
            print(f"CSV 파일 저장 중 오류 발생: {e}")
    
    def save_to_txt(self, data: List[Dict[str, str]], filename: str = "kospi200_top_stocks.txt"):
        """
        크롤링 결과를 텍스트 파일로 저장합니다.
        
        Args:
            data (List[Dict[str, str]]): 크롤링 결과
            filename (str): 저장할 파일명
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("코스피200 편입종목상위 데이터\n")
                f.write("=" * 100 + "\n")
                f.write(f"{'순위':<4} {'종목명':<12} {'현재가':<10} {'전일비':<10} {'등락률':<8} {'거래량':<12} {'거래대금':<10} {'시가총액':<10}\n")
                f.write("-" * 100 + "\n")
                
                for stock in data:
                    f.write(f"{stock['순위']:<4} {stock['종목명']:<12} {stock['현재가']:<10} {stock['전일비']:<10} {stock['등락률']:<8} {stock['거래량']:<12} {stock['거래대금']:<10} {stock['시가총액']:<10}\n")
            
            print(f"데이터가 {filename} 파일에 저장되었습니다.")
            
        except Exception as e:
            print(f"텍스트 파일 저장 중 오류 발생: {e}")
    
    def display_data(self, data: List[Dict[str, str]], limit: int = 20):
        """
        크롤링 결과를 콘솔에 출력합니다.
        
        Args:
            data (List[Dict[str, str]]): 크롤링 결과
            limit (int): 출력할 최대 개수
        """
        if not data:
            print("표시할 데이터가 없습니다.")
            return
        
        print(f"\n코스피200 편입종목상위 데이터 (상위 {min(limit, len(data))}개)")
        print("=" * 100)
        print(f"{'순위':<4} {'종목명':<12} {'현재가':<10} {'전일비':<10} {'등락률':<8} {'거래량':<12} {'거래대금':<10} {'시가총액':<10}")
        print("-" * 100)
        
        for i, stock in enumerate(data[:limit]):
            print(f"{stock['순위']:<4} {stock['종목명']:<12} {stock['현재가']:<10} {stock['전일비']:<10} {stock['등락률']:<8} {stock['거래량']:<12} {stock['거래대금']:<10} {stock['시가총액']:<10}")

def main():
    """메인 함수"""
    print("네이버 코스피200 편입종목상위 크롤러를 시작합니다.")
    print("=" * 60)
    
    # 크롤러 인스턴스 생성
    crawler = Kospi200Crawler()
    
    # 데이터 크롤링
    stock_data = crawler.get_kospi200_data()
    
    if not stock_data:
        print("데이터를 가져올 수 없습니다. 페이지 구조가 변경되었을 수 있습니다.")
        return
    
    # 결과 출력
    crawler.display_data(stock_data, limit=20)
    
    # 파일 저장 여부 확인
    print(f"\n총 {len(stock_data)}개의 종목 데이터를 가져왔습니다.")
    
    save_choice = input("\n데이터를 파일로 저장하시겠습니까? (1: CSV, 2: TXT, 3: 둘 다, 0: 저장 안함): ").strip()
    
    if save_choice == '1':
        crawler.save_to_csv(stock_data)
    elif save_choice == '2':
        crawler.save_to_txt(stock_data)
    elif save_choice == '3':
        crawler.save_to_csv(stock_data)
        crawler.save_to_txt(stock_data)
    else:
        print("데이터를 저장하지 않습니다.")
    
    print("\n크롤링이 완료되었습니다.")

if __name__ == "__main__":
    main()
