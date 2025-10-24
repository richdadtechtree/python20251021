#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 부동산(fin.land.naver.com) Stealth 크롤링 스크립트
최고 수준의 차단 방지 기능을 갖춘 고급 부동산 매물 크롤러
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
try:
    import undetected_chromedriver as uc
    HAVE_UC = True
except Exception:
    HAVE_UC = False

from fake_useragent import UserAgent
from selenium.common.exceptions import MoveTargetOutOfBoundsException, NoSuchElementException

import logging
import requests
import random
import time
import re
import json
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StealthNaverLandCrawler:
    def __init__(self, headless=False, use_undetected=True):
        """
        네이버 부동산 Stealth 크롤러 초기화
        
        Args:
            headless (bool): 브라우저를 백그라운드에서 실행할지 여부
            use_undetected (bool): undetected-chromedriver 사용 여부
        """
        self.headless = headless
        self.use_undetected = use_undetected
        self.driver = None
        self.wait = None
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # 다양한 User-Agent 풀
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        
    def setup_driver(self):
        """Chrome 드라이버 설정 (Stealth 모드)"""
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless=new")

            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument(f"user-agent={random.choice(self.user_agents)}")

            if self.use_undetected and HAVE_UC:
                self.driver = uc.Chrome(options=options, service=Service(ChromeDriverManager().install()))
            else:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                try:
                    self.driver.execute_cdp_cmd(
                        "Page.addScriptToEvaluateOnNewDocument",
                        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"}
                    )
                except Exception:
                    pass

            self.wait = WebDriverWait(self.driver, 10)
            logger.info("드라이버 설정 완료")
            return True

        except Exception as e:
            logger.error(f"드라이버 설정 중 오류 발생: {e}")
            logger.error("드라이버 설정에 실패했습니다.")
            # 예외 재전파 대신 False 반환으로 호출자에게 상태를 알린다.
            return False
    
    def random_delay(self, min_seconds=1, max_seconds=4):
        """랜덤 지연으로 차단 방지"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        logger.debug(f"랜덤 지연: {delay:.2f}초")
    
    def human_like_behavior(self):
        """사람처럼 행동하기 — 요소가 뷰포트 밖일 때 예외 처리 포함"""
        try:
            actions = ActionChains(self.driver)

            # 안전하게 대상 요소 목록 확보 (버튼/링크 위주)
            try:
                candidates = self.driver.find_elements(By.CSS_SELECTOR, "a, button, [role='button']")
            except Exception:
                candidates = []

            # 마우스 이동: 먼저 요소를 화면 중앙으로 스크롤한 뒤 시도
            for _ in range(random.randint(2, 5)):
                if candidates:
                    el = random.choice(candidates)
                else:
                    # 후보가 없으면 바디에 대해 작동
                    try:
                        el = self.driver.find_element(By.TAG_NAME, "body")
                    except NoSuchElementException:
                        el = None

                if el:
                    try:
                        # 요소를 중앙에 스크롤 -> 요소가 뷰포트 내부에 있도록 보장
                        self.driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", el)
                        time.sleep(random.uniform(0.1, 0.4))
                        actions.move_to_element(el).perform()
                        time.sleep(random.uniform(0.2, 0.8))
                    except MoveTargetOutOfBoundsException:
                        logger.warning("MoveTargetOutOfBoundsException 발생 — 안전한 스크롤/페일오버 시도")
                        # 화면을 최상단/중앙으로 스크롤 후 다시 시도(성공하지 않으면 스킵)
                        try:
                            self.driver.execute_script("window.scrollTo(0, 0);")
                            time.sleep(0.2)
                            actions.move_to_element(el).perform()
                        except Exception:
                            # 마지막 페일오버: 그냥 마우스 이동 생략
                            logger.debug("마우스 이동 페일오버 실패, 스킵")
                    except Exception as e:
                        logger.debug(f"사람처럼 행동하기 중 오류(무시): {e}")

            # 랜덤 스크롤 (위/아래)
            for _ in range(random.randint(1, 3)):
                scroll_amount = random.randint(-400, 800)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.3, 1.0))

            # 약간의 딜레이로 사람 동작 흉내
            time.sleep(random.uniform(0.2, 0.6))

        except Exception as e:
            logger.warning(f"사람처럼 행동하기 중 오류: {e}")
    
    def bypass_cloudflare(self):
        """Cloudflare 우회 시도"""
        try:
            # Cloudflare 체크 페이지 감지
            if "cloudflare" in self.driver.page_source.lower() or "checking your browser" in self.driver.page_source.lower():
                logger.info("Cloudflare 감지됨. 우회 시도 중...")
                
                # 대기 시간 증가
                time.sleep(random.randint(10, 20))
                
                # 사람처럼 행동
                self.human_like_behavior()
                
                # 페이지 새로고침
                self.driver.refresh()
                time.sleep(random.randint(5, 10))
                
                return True
            return False
            
        except Exception as e:
            logger.warning(f"Cloudflare 우회 중 오류: {e}")
            return False
    
    def crawl_property_listings_stealth(self, url, max_pages=5):
        """
        Stealth 모드로 부동산 매물 목록 크롤링
        
        Args:
            url (str): 크롤링할 URL
            max_pages (int): 최대 페이지 수
            
        Returns:
            list: 매물 정보 리스트
        """
        try:
            logger.info(f"Stealth 모드 매물 목록 크롤링 시작: {url}")
            
            # 초기 페이지 로드
            self.random_delay(3, 6)
            self.driver.get(url)
            
            # 페이지 로딩 대기
            time.sleep(random.randint(8, 12))
            
            # Cloudflare 우회 시도
            self.bypass_cloudflare()
            
            # 페이지가 완전히 로드될 때까지 대기
            try:
                self.wait.until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
            except:
                logger.warning("페이지 로딩 완료를 기다리는 중 타임아웃 발생")
            
            # 사람처럼 행동
            self.human_like_behavior()
            
            all_properties = []
            
            for page in range(max_pages):
                logger.info(f"페이지 {page + 1}/{max_pages} 처리 중...")
                
                # 현재 페이지의 매물 정보 추출
                page_properties = self._extract_properties_stealth()
                all_properties.extend(page_properties)
                
                logger.info(f"페이지 {page + 1}에서 {len(page_properties)}개 매물 발견")
                
                # 사람처럼 행동
                self.human_like_behavior()
                
                # 다음 페이지로 이동 시도
                if not self._go_to_next_page_stealth():
                    logger.info("더 이상 페이지가 없습니다.")
                    break
                
                # 페이지 간 지연 (더 길게)
                self.random_delay(5, 10)
            
            logger.info(f"총 {len(all_properties)}개의 매물을 수집했습니다.")
            return all_properties
            
        except Exception as e:
            logger.error(f"Stealth 매물 목록 크롤링 중 오류 발생: {e}")
            return []
    
    def _extract_properties_stealth(self):
        """Stealth 모드로 현재 페이지에서 매물 정보 추출"""
        properties = []
        
        try:
            # 사람처럼 행동
            self.human_like_behavior()
            
            # 페이지 소스 분석
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 매물 관련 요소들 찾기 (더 많은 선택자)
            property_selectors = [
                ".item_list .item",
                ".list .item", 
                ".item",
                "[class*='item']",
                ".card",
                "[class*='card']",
                "li[class*='item']",
                "div[class*='property']",
                "tr[class*='item']",
                ".complex_item",
                "[data-testid*='item']",
                ".article_item",
                ".property_item",
                ".listing_item",
                "[class*='listing']",
                "[class*='article']",
                "[class*='property']"
            ]
            
            property_elements = []
            for selector in property_selectors:
                try:
                    elements = soup.select(selector)
                    if elements and len(elements) > 1:
                        property_elements = elements
                        logger.info(f"매물 요소 발견: {selector} ({len(elements)}개)")
                        break
                except:
                    continue
            
            if not property_elements:
                logger.warning("매물 요소를 찾을 수 없습니다. 전체 텍스트에서 정보 추출 시도...")
                return self._extract_from_text_analysis_stealth(soup)
            
            # 각 매물 정보 추출
            for i, element in enumerate(property_elements[:50]):  # 최대 50개만
                try:
                    property_info = self._extract_single_property_stealth(element, i + 1)
                    if property_info:
                        properties.append(property_info)
                except Exception as e:
                    logger.warning(f"매물 {i+1} 정보 추출 중 오류: {e}")
                    continue
            
            return properties
            
        except Exception as e:
            logger.error(f"Stealth 현재 페이지 매물 추출 중 오류: {e}")
            return []
    
    def _extract_from_text_analysis_stealth(self, soup):
        """Stealth 모드 텍스트 분석을 통한 매물 정보 추출"""
        properties = []
        
        try:
            all_text = soup.get_text()
            
            # 더 정교한 패턴 매칭
            price_patterns = [
                r'(\d+억\s*\d*만원)',
                r'(\d+,\d+만원)',
                r'(\d+억원)',
                r'(\d+만원)',
                r'(\d+억\s*\d*천만원)',
                r'(\d+억\s*\d*백만원)',
                r'(\d+억\s*\d*십만원)'
            ]
            
            area_patterns = [
                r'(\d+\.\d+㎡)',
                r'(\d+㎡)',
                r'(\d+평)',
                r'(\d+\.\d+평)',
                r'(\d+\.\d+py)',
                r'(\d+py)'
            ]
            
            # 텍스트를 라인별로 분석
            lines = all_text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if len(line) < 10:
                    continue
                
                # 가격과 면적이 모두 있는지 확인
                has_price = any(re.search(pattern, line) for pattern in price_patterns)
                has_area = any(re.search(pattern, line) for pattern in area_patterns)
                
                if has_price or has_area:
                    property_info = {
                        '매물번호': len(properties) + 1,
                        '전체텍스트': line[:200],
                        '가격': self._extract_price_from_text(line),
                        '면적': self._extract_area_from_text(line),
                        '매물타입': self._extract_type_from_text(line),
                        '추출방법': 'Stealth텍스트분석'
                    }
                    properties.append(property_info)
            
            return properties[:30]  # 최대 30개만
            
        except Exception as e:
            logger.error(f"Stealth 텍스트 분석 중 오류: {e}")
            return []
    
    def _extract_single_property_stealth(self, element, property_number):
        """Stealth 모드 개별 매물 정보 추출"""
        try:
            text = element.get_text().strip()
            if not text or len(text) < 5:
                return None
            
            property_info = {
                '매물번호': property_number,
                '전체텍스트': text[:300],
                '매물타입': '정보 없음',
                '가격': '정보 없음',
                '면적': '정보 없음',
                '층수': '정보 없음',
                '방향': '정보 없음',
                '주소': '정보 없음',
                '링크': '정보 없음',
                '추출방법': 'Stealth요소분석'
            }
            
            # 링크 추출
            try:
                link_elem = element.find('a')
                if link_elem and link_elem.get('href'):
                    href = link_elem.get('href')
                    if href.startswith('/'):
                        href = urljoin('https://fin.land.naver.com', href)
                    property_info['링크'] = href
            except:
                pass
            
            # 각종 정보 추출
            property_info['매물타입'] = self._extract_type_from_text(text)
            property_info['가격'] = self._extract_price_from_text(text)
            property_info['면적'] = self._extract_area_from_text(text)
            property_info['층수'] = self._extract_floor_from_text(text)
            property_info['방향'] = self._extract_direction_from_text(text)
            property_info['주소'] = self._extract_address_from_text(text)
            
            return property_info
            
        except Exception as e:
            logger.warning(f"Stealth 매물 정보 추출 중 오류: {e}")
            return None
    
    def _extract_type_from_text(self, text):
        """텍스트에서 매물 타입 추출"""
        types = ['매매', '전세', '월세', '아파트', '오피스텔', '빌라', '단독주택', '투룸', '원룸', '쓰리룸', '포룸']
        
        for prop_type in types:
            if prop_type in text:
                return prop_type
        
        return "정보 없음"
    
    def _extract_price_from_text(self, text):
        """텍스트에서 가격 추출"""
        patterns = [
            r'(\d+억\s*\d*만원)',
            r'(\d+,\d+만원)',
            r'(\d+억원)',
            r'(\d+만원)',
            r'(\d+억\s*\d*천만원)',
            r'(\d+억\s*\d*백만원)',
            r'(\d+억\s*\d*십만원)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "정보 없음"
    
    def _extract_area_from_text(self, text):
        """텍스트에서 면적 추출"""
        patterns = [
            r'(\d+\.\d+㎡)',
            r'(\d+㎡)',
            r'(\d+평)',
            r'(\d+\.\d+평)',
            r'(\d+\.\d+py)',
            r'(\d+py)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "정보 없음"
    
    def _extract_floor_from_text(self, text):
        """텍스트에서 층수 추출"""
        patterns = [
            r'(\d+)층',
            r'(\d+)F',
            r'(\d+)f'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1) + "층"
        
        return "정보 없음"
    
    def _extract_direction_from_text(self, text):
        """텍스트에서 방향 추출"""
        directions = ['남향', '북향', '동향', '서향', '남동향', '남서향', '북동향', '북서향']
        
        for direction in directions:
            if direction in text:
                return direction
        
        return "정보 없음"
    
    def _extract_address_from_text(self, text):
        """텍스트에서 주소 추출"""
        address_patterns = [
            r'([가-힣]+시\s*[가-힣]+구)',
            r'([가-힣]+구\s*[가-힣]+동)',
            r'([가-힣]+동)'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "정보 없음"
    
    def _go_to_next_page_stealth(self):
        """Stealth 모드로 다음 페이지로 이동"""
        try:
            # 사람처럼 행동
            self.human_like_behavior()
            
            # 다음 페이지 버튼 찾기
            next_button_selectors = [
                "a[class*='next']",
                "button[class*='next']",
                ".pagination .next",
                ".paging .next",
                "a[aria-label*='다음']",
                "button[aria-label*='다음']",
                ".page_next",
                "[data-testid*='next']",
                "a[title*='다음']",
                "button[title*='다음']"
            ]
            
            for selector in next_button_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button.is_enabled():
                        # 사람처럼 클릭
                        actions = ActionChains(self.driver)
                        actions.move_to_element(next_button).pause(random.uniform(0.5, 1.0)).click().perform()
                        self.random_delay(3, 6)
                        return True
                except:
                    continue
            
            # 스크롤로 더 많은 매물 로드 시도
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.random_delay(2, 4)
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            logger.warning(f"Stealth 다음 페이지 이동 중 오류: {e}")
            return False
    
    def save_results(self, data, filename="naver_land_stealth_result"):
        """결과 저장"""
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename_with_timestamp = f"{filename}_{timestamp}"
            
            # JSON 저장
            json_filename = f"{filename_with_timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"결과가 {json_filename}에 저장되었습니다.")
            
            # Excel 저장
            try:
                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    excel_filename = f"{filename_with_timestamp}.xlsx"
                    df.to_excel(excel_filename, index=False, encoding='utf-8-sig')
                    logger.info(f"데이터가 {excel_filename}에 저장되었습니다.")
                else:
                    logger.warning("저장할 데이터가 없습니다.")
            except Exception as e:
                logger.error(f"Excel 저장 중 오류: {e}")
                
        except Exception as e:
            logger.error(f"파일 저장 중 오류: {e}")
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            logger.info("브라우저가 종료되었습니다.")


def main():
    """메인 실행 함수"""
    target_url = "https://fin.land.naver.com/complexes/869?tab=article&transactionPyeongTypeNumber=1&transactionTradeType=A1&articleTradeTypes=A1"
    crawler = StealthNaverLandCrawler(headless=False, use_undetected=True)

    try:
        ok = crawler.setup_driver()
        if not ok:
            logger.error("드라이버 준비 실패로 크롤링을 중단합니다.")
            return

        # 페이지 열기 예시 (원래 crawl 함수 호출로 교체)
        crawler.driver.get(target_url)
        logger.info("타깃 페이지 로드 완료")
        # 여기에서 실제 크롤링 함수 호출
        # crawler.crawl_property_listings_stealth(target_url, max_pages=5)

    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {e}")
    finally:
        # 드라이버가 None이 아닐 때만 종료
        try:
            if getattr(crawler, "driver", None):
                crawler.close()
                logger.info("브라우저가 종료되었습니다.")
        except Exception as e:
            logger.warning(f"브라우저 종료 중 오류: {e}")
