import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
#from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from webdriver_manager.microsoft import EdgeChromiumDriverManager
import traceback
import re
from login_manager import LoginManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from datetime import datetime
import random
import config  # 설정 파일 import 추가
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 날짜 네비게이션 XPath 상수 추가
PREV_DATE_BUTTON_XPATH = '//*[@id="r_padding"]/div[3]/div/div/div[2]/div/span[1]/img'
NEXT_DATE_BUTTON_XPATH = '//*[@id="r_padding"]/div[3]/div/div/div[2]/div/span[4]/img'

# URL 상수들
LOGIN_URL = "https://www.carefor.co.kr/login.php"
ALL_PATIENT_URL = "https://dn.carefor.co.kr/#cGFnZXx7J3R5cGUnOidsZWZ0X3N1YjEnLCAndmlldyc6Jy9zaGFyZS9wYXRpZW50L3ZpZXcucGF0aWVudF9tYW5hZ2UnfSV7InRpdGxlIjoiMS0xLuyImOq4ieyekCDsoJXrs7TqtIDrpqwiLCJldmFsIjoiNDciLCJtb3ZlX3Njcm9sbCI6dHJ1ZX18bGVmdF9zdWIx"
ATTENDANCE_URL = "https://dn.carefor.co.kr/#cGFnZXx7J3R5cGUnOidsZWZ0X3N1YjInLCAndmlldyc6Jy90cmFuc3BvcnQvdmlldy5wYXRpZW50X3N0YXRfZGFpbHknICAgICAgfSV7InRpdGxlIjoiMi0zLuy2nOyEneq0gOumrCjssKjrn4kg66%2B47J207JqpKSIsImdfcGFtbWdubyI6IjEyNjg1NTIiLCJtb3ZlX3Njcm9sbCI6dHJ1ZX18bGVmdF9zdWIy"
# 외출 리포트 URL 추가
OUTING_REPORT_URL = "https://dn.carefor.co.kr/#cGFnZXx7J3R5cGUnOidsZWZ0X3N1YjInLCAndmlldyc6Jy9zaGFyZS9wYXRpZW50L3ZpZXcucGF0aWVudF9vdXRfcmVwb3J0JyAgfSV7InRpdGxlIjoiMi05LuyImOq4ieyekCDsmbjstpwg66as7Y%2Bs7Yq4IiwibW92ZV9zY3JvbGwiOnRydWV9fGxlZnRfc3ViMg%3D%3D"
STAFF_WORK_MANAGE_URL = "https://dn.carefor.co.kr/#cGFnZXx7J3R5cGUnOidsZWZ0X3N1YjgnLCAndmlldyc6Jy9zaGFyZS9zdGFmZi92aWV3LnN0YWZmX3dvcmtfbWFuYWdlJ30leyJ0aXRsZSI6IjgtNC7stpzth7Tqt7wg67CPIOq3vOustOq0gOumrCIsImdfcGFtbWdubyI6IjEzMzc5MTYiLCJtb3ZlX3Njcm9sbCI6dHJ1ZX18bGVmdF9zdWI4"
# 선택자 상수들
ALL_PATIENT_SELECTOR = "#ctnr_patient_list_table"
TABLE_SELECTOR = "#div_patient_list"
DATE_TEXT_SELECTOR = "#r_padding > div.left_list_div > div > div > div:nth-child(2) > div > span.s2"
ATTENDANCE_SELECTOR = "#attendance_table"
# 사용자 제공 출석 테이블 XPath 추가
ATTENDANCE_TBODY_XPATH = '//*[@id="div_patient_list"]/div/table/tbody'

# 전역 설정
DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3
DEBUG_MODE = False
COOKIE_FILE = "cookies.pkl"

# 디버그 로그 함수 제거 - 성능 최적화
# def debug_log(message):
#     if DEBUG_MODE:
#         timestamp = datetime.now().strftime("%H:%M:%S")
#         log_message = f"[DEBUG {timestamp}] {message}"
#         
#         print(log_message)
#         
#         try:
#             log_dir = "logs"
#             if not os.path.exists(log_dir):
#                 os.makedirs(log_dir)
#             
#             log_file = os.path.join(log_dir, f"debug_{datetime.now().strftime('%Y%m%d')}.log")
#             with open(log_file, "a", encoding="utf-8") as f:
#                 f.write(log_message + "\n")
#         except Exception as e:
#             print(f"로그 파일 저장 실패: {e}")

class CareforDataCollector:
    """케어포 프로그램 데이터 수집 클래스"""
    
    def __init__(self, headless=False):
        self.driver = None
        self.login_manager = LoginManager()
        self.all_patients = []
        self.attendance_data = []
        self.headless = headless  # 헤드리스 모드 설정
    
    def init_driver(self):
        """웹드라이버 초기화 - 수정된 Edge"""
        print("🌐 Edge 브라우저로 실행합니다...")
        
        from selenium.webdriver.edge.service import Service
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        
        options = webdriver.EdgeOptions()
        options.use_chromium = True
        options.add_argument('--log-level=3')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        
        if self.headless:
            options.add_argument('--headless')
        
        try:
            service = Service(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=options)
            
            # 즉시 구글로 이동하여 data: URL 문제 해결
            self.driver.get("https://www.google.com")
            time.sleep(1)
            
            print("✅ Edge 브라우저 초기화 완료")
            return self.driver
            
        except Exception as e:
            print(f"Edge 초기화 실패: {e}")
            raise

    def close_any_popup(self):
        """모든 팝업 닫기 - 강화 버전"""
        try:
            print("🔄 팝업 닫기 시도...")
            
            # 평균 입소자 수 팝업의 "창닫기" 버튼 찾기
            close_buttons = [
                "//button[contains(text(), '창닫기')]",
                "//button[contains(text(), '닫기')]",
                "//button[contains(text(), '확인')]",
                "//button[contains(text(), '취소')]",
                "//button[contains(@class, 'close')]",
                "//span[contains(@class, 'close')]",
                ".close",
                "//div[@class='popup']//button",
            ]
            
            for selector in close_buttons:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            print(f"✅ 팝업 닫기 성공: {selector}")
                            time.sleep(1)
                            return True
                except:
                    continue
            
            # ESC 키로 닫기 시도
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys('\x1b')
                print("✅ ESC 키로 팝업 닫기")
                time.sleep(1)
                return True
            except:
                pass
                
            print("⚠️ 팝업을 찾을 수 없거나 닫을 수 없음")
            return False
            
        except Exception as e:
            print(f"❌ 팝업 닫기 오류: {e}")
            return False
    
    def login(self):
        """자동 로그인 처리"""
        try:
            # 쿠키 파일이 있으면 먼저 시도
            if os.path.exists(COOKIE_FILE):
                try:
                    # 디버그 로그 제거
                    self.driver.get("https://www.carefor.co.kr")
                    WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    with open(COOKIE_FILE, "rb") as f:
                        for c in pickle.load(f):
                            self.driver.add_cookie(c)
                    
                    # 로그인 상태 확인을 위해 메인 페이지로 이동
                    self.driver.get("https://www.carefor.co.kr")
                    time.sleep(2)
                    
                    # 로그인 상태 확인 (로그인 링크가 없으면 로그인된 상태)
                    try:
                        login_link = self.driver.find_element(By.XPATH, "//a[contains(text(), '로그인')]")
                        # 디버그 로그 제거
                    except:
                        # 디버그 로그 제거
                        return True
                        
                except Exception as e:
                    # 디버그 로그 제거
                    pass
            
            # 새로 로그인
            login_info = self.login_manager.get_or_prompt_login_info()
            if not login_info:
                # 디버그 로그 제거
                return False
            
            self.driver.get(LOGIN_URL)
            
            try:
                # 로그인 폼 입력
                id_field = WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
                )
                id_field.clear()
                id_field.send_keys(login_info['institution_id'])
                
                pw_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                pw_field.clear()
                pw_field.send_keys(login_info['password'])
                
                login_button = self.driver.find_element(By.CSS_SELECTOR, ".btn")
                login_button.click()
                
                # 로그인 완료 대기
                time.sleep(3)
                
                # 로그인 성공 확인
                current_url = self.driver.current_url
                if "login.php" not in current_url:
                    # 디버그 로그 제거
                    
                    # 쿠키 저장
                    with open(COOKIE_FILE, "wb") as f:
                        pickle.dump(self.driver.get_cookies(), f)
                    
                    return True
                else:
                    # 디버그 로그 제거
                    return False
                
            except Exception as e:
                # 디버그 로그 제거
                return False
                
        except Exception as e:
            # 디버그 로그 제거
            return False
    
    def execute_xpath_click_sequence(self):
        """
        config에 정의된 XPath 순서대로 클릭을 실행하고 팝업 데이터를 추출합니다.
        평균 입소자 수, 총 입소자 수, 반올림된 값을 모두 추출하여 반환합니다.
        """
        popup_average_number = ""  # 평균 입소자 수 (26.50)
        popup_total_residents = ""  # 총 입소자 수 (53)
        popup_rounded_number = ""  # 반올림된 값 (27)

        try:
            # 1단계: 첫 번째 XPath 클릭
            # 디버그 로그 제거
            if not self.click_xpath_element(config.XPATH_STEP1, "1단계"):
                # 디버그 로그 제거
                return None
            time.sleep(config.XPATH_STEP_DELAY)

            # 2단계: 두 번째 XPath 클릭
            # 디버그 로그 제거
            if not self.click_xpath_element(config.XPATH_STEP2, "2단계"):
                # 디버그 로그 제거
                return None
            time.sleep(config.XPATH_STEP_DELAY)

            # 3단계: 세 번째 XPath 클릭 (팝업 열기)
            # 디버그 로그 제거
            if not self.click_xpath_element(config.XPATH_STEP3, "3단계"):
                # 디버그 로그 제거
                return None
            
            # 팝업이 나타날 때까지 대기
            time.sleep(config.POPUP_WAIT_TIMEOUT)
            # 디버그 로그 제거

            # 팝업에서 데이터 추출
            popup_text = self.driver.page_source # 전체 페이지 소스에서 팝업 내용 포함
            # 디버그 로그 제거

            # 평균 입소자 수 추출 (= 26.50 형태)
            match_average = re.search(config.POPUP_NUMBER_PATTERN, popup_text)
            if match_average:
                popup_average_number = match_average.group(1)
                # 디버그 로그 제거
            else:
                # 디버그 로그 제거
                pass
            
            # 총 입소자 수 추출 (입소자 합계(53명) 형태)
            match_total = re.search(config.POPUP_SECOND_NUMBER_PATTERN, popup_text)
            if match_total:
                popup_total_residents = match_total.group(1)
                # 디버그 로그 제거
            else:
                # 디버그 로그 제거
                pass

            # 반올림된 값 추출 (반올림한 27 형태)
            match_rounded = re.search(config.POPUP_THIRD_NUMBER_PATTERN, popup_text)
            if match_rounded:
                popup_rounded_number = match_rounded.group(1)
                # 디버그 로그 제거
            else:
                # 디버그 로그 제거
                pass

            # 팝업 텍스트 일부를 로그에 출력 (디버깅용) - 제거
            # if "입소자 합계" in popup_text:
            #     start_idx = popup_text.find("입소자 합계")
            #     sample_text = popup_text[start_idx:start_idx+100]
            #     debug_log(f"팝업 텍스트 샘플: {sample_text}")

            # 세 개의 숫자 모두 딕셔너리로 반환
            return {
                'average_number': popup_average_number,  # 평균 입소자 수 (26.50)
                'total_residents': popup_total_residents,  # 총 입소자 수 (53)
                'rounded_number': popup_rounded_number   # 반올림된 값 (27)
            }

        except Exception as e:
            # 디버그 로그 제거
            return None
    
    def click_xpath_element(self, xpath, step_name):
        """지정된 XPath 요소 클릭 (재시도 로직 포함)"""
        for attempt in range(config.XPATH_RETRY_COUNT):
            try:
                # 디버그 로그 제거
                
                # 요소가 클릭 가능할 때까지 대기
                element = WebDriverWait(self.driver, config.XPATH_CLICK_TIMEOUT).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                
                # 일반 클릭 시도
                try:
                    element.click()
                    # 디버그 로그 제거
                    return True
                except ElementClickInterceptedException:
                    # JavaScript 클릭 시도
                    self.driver.execute_script("arguments[0].click();", element)
                    # 디버그 로그 제거
                    return True
                    
            except TimeoutException:
                # 디버그 로그 제거
                if attempt < config.XPATH_RETRY_COUNT - 1:
                    time.sleep(1)  # 재시도 전 대기
                    continue
            except Exception as e:
                # 디버그 로그 제거
                if attempt < config.XPATH_RETRY_COUNT - 1:
                    time.sleep(1)  # 재시도 전 대기
                    continue
        
        # 디버그 로그 제거
        return False
    
    def extract_popup_number_data(self):
        """팝업에서 숫자.숫자 형태의 데이터 추출 (평균 입소자 수 계산 화면에서)"""
        try:
            # 디버그 로그 제거
            
            # 다양한 선택자로 팝업 요소 찾기
            popup_element = None
            popup_text = ""
            
            # 먼저 특정 텍스트가 포함된 요소들을 찾아보기
            for selector in config.POPUP_TEXT_SELECTORS:
                try:
                    if selector.startswith('//'):
                        # XPath 선택자
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS 선택자
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed():
                            text = element.text
                            if text and ("입소자" in text or "계산" in text or "반올림" in text or re.search(config.POPUP_NUMBER_PATTERN, text)):
                                popup_element = element
                                popup_text = text
                                # 디버그 로그 제거
                                break
                    
                    if popup_element:
                        break
                        
                except Exception as e:
                    # 디버그 로그 제거
                    continue
            
            # 팝업을 찾지 못한 경우 페이지 전체에서 검색
            if not popup_text:
                # 디버그 로그 제거
                try:
                    body_element = self.driver.find_element(By.TAG_NAME, "body")
                except:
                    # 디버그 로그 제거
                    return None
            
            # 팝업 텍스트에서 숫자.숫자 패턴 추출
            if popup_text:
                # 디버그 로그 제거
                
                # 정규표현식으로 숫자.숫자 패턴 찾기
                matches = re.findall(config.POPUP_NUMBER_PATTERN, popup_text)
                
                if matches:
                    # 디버그 로그 제거
                    # 가장 의미있어 보이는 숫자를 선택 (보통 계산 결과값)
                    for match in matches:
                        # 29.00 같은 값이 있으면 우선 선택
                        if float(match) > 1:  # 1보다 큰 값 (의미있는 입소자 수)
                            # 디버그 로그 제거
                            return match
                    
                    # 조건에 맞는 것이 없으면 첫 번째 값
                    # 디버그 로그 제거
                    return matches[0]
                else:
                    # 디버그 로그 제거
                    return None
            else:
                # 디버그 로그 제거
                return None
                
        except Exception as e:
            # 디버그 로그 제거
            return None
    
    def get_attendance_data_with_popup_info(self, date_str=None):
        """기존 출석 데이터 수집에 팝업 정보 추가"""
        try:
            # 디버그 로그 제거
            
            # 기존 출석 데이터 수집 (딕셔너리 형태)
            attendance_result = self.collect_data_for_gui(date_str)
            
            if not attendance_result or not attendance_result.get('success'):
                # 디버그 로그 제거
                return attendance_result
            
            # XPath 클릭 시퀀스 실행 및 팝업 데이터 추출
            popup_data = self.execute_xpath_click_sequence()
            
            # 팝업 데이터가 있는 경우 처리
            if popup_data and isinstance(popup_data, dict):
                # 전체 결과에 팝업 데이터 추가
                attendance_result['popup_data'] = popup_data.get('average_number', '')  # 평균 입소자 수를 메인 표시용으로
                attendance_result['total_residents'] = popup_data.get('total_residents', '')  # 총 입소자 수
                attendance_result['rounded_number'] = popup_data.get('rounded_number', '')  # 반올림된 값
                
                # 디버그 로그 제거
                
                # 출석 데이터(attendance)가 리스트인 경우에만 개별 데이터에도 팝업 정보 추가
                if 'attendance' in attendance_result and isinstance(attendance_result['attendance'], list):
                    for person in attendance_result['attendance']:
                        if isinstance(person, dict):
                            person['popup_average'] = popup_data.get('average_number', '')
                            person['popup_total'] = popup_data.get('total_residents', '')
                            person['popup_rounded'] = popup_data.get('rounded_number', '')
                    # 디버그 로그 제거
                else:
                    # 팝업 데이터가 없을 경우 빈 값으로 설정
                    for person in attendance_result['attendance']:
                        if isinstance(person, dict):
                            person['popup_average'] = ""
                            person['popup_total'] = ""
                            person['popup_rounded'] = ""
                    # 디버그 로그 제거
            else:
                # 팝업 데이터가 없을 경우 빈 값으로 설정
                attendance_result['popup_data'] = ""
                attendance_result['total_residents'] = ""
                attendance_result['rounded_number'] = ""
                
                if 'attendance' in attendance_result and isinstance(attendance_result['attendance'], list):
                    for person in attendance_result['attendance']:
                        if isinstance(person, dict):
                            person['popup_average'] = ""
                            person['popup_total'] = ""
                            person['popup_rounded'] = ""
                # 디버그 로그 제거
            
            return attendance_result
            
        except Exception as e:
            # 디버그 로그 제거
            return {
                'success': False,
                'error': f'출석 데이터 및 팝업 정보 수집 실패: {e}',
                'date': date_str,
                'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def login_with_credentials(self, org_id, user_name, password):
        """
        기관ID, 이름, 비밀번호로 로그인
        """
        try:
            print(f"로그인 시도: 기관ID={org_id}, 이름={user_name}")
            
            # 케어포 로그인 페이지로 이동
            self.driver.get("https://www.carefor.co.kr/login")  # 실제 케어포 로그인 URL로 변경
            
            # 페이지 로딩 대기
            wait = WebDriverWait(self.driver, 10)
            
            # 기관ID 입력 필드 대기 및 입력
            org_id_field = wait.until(EC.presence_of_element_located((By.NAME, "org_id")))  # 실제 필드명으로 변경
            org_id_field.clear()
            org_id_field.send_keys(org_id)
            
            # 사용자 이름 입력
            name_field = self.driver.find_element(By.NAME, "user_name")  # 실제 필드명으로 변경
            name_field.clear()
            name_field.send_keys(user_name)
            
            # 비밀번호 입력
            password_field = self.driver.find_element(By.NAME, "password")  # 실제 필드명으로 변경
            password_field.clear()
            password_field.send_keys(password)
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.XPATH, "///*[@id=login_outline]/div[1]/div/form/ul/li[4]/input']")  # 실제 버튼 선택자로 변경
            login_button.click()
            
            # 로그인 결과 대기
            time.sleep(3)
            
            # 로그인 성공 여부 확인
            current_url = self.driver.current_url
            
            # 로그인 성공 조건 (실제 케어포 사이트에 맞게 수정)
            if "dashboard" in current_url or "main" in current_url or "home" in current_url:
                print("로그인 성공")
                # 로그인 성공 시 쿠키 자동 저장
                self.save_cookies(org_id)
                return True
            elif "login" in current_url:
                # 로그인 페이지에 그대로 있으면 실패
                print("로그인 실패 - 로그인 페이지에 머물러 있음")
                return False
            else:
                print(f"로그인 상태 불확실 - 현재 URL: {current_url}")
                # 일단 성공으로 간주하고 쿠키 저장
                self.save_cookies(org_id)
                return True
                
        except Exception as e:
            print(f"로그인 중 오류: {e}")
            return False
    
    def login_with_cookies(self, cookie_file):
        """
        저장된 쿠키로 로그인
        """
        try:
            if not os.path.exists(cookie_file):
                print(f"쿠키 파일이 존재하지 않음: {cookie_file}")
                return False
            
            # 케어포 메인 페이지로 이동
            self.driver.get("https://carefor.co.kr")  # 실제 케어포 URL로 변경
            
            # 쿠키 로드
            with open(cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
            # 쿠키 적용
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"쿠키 추가 실패: {e}")
                    continue
            
            # 페이지 새로고침
            self.driver.refresh()
            time.sleep(2)
            
            # 로그인 상태 확인
            current_url = self.driver.current_url
            
            if "login" not in current_url:
                print("쿠키 로그인 성공")
                return True
            else:
                print("쿠키 로그인 실패")
                return False
                
        except Exception as e:
            print(f"쿠키 로그인 오류: {e}")
            return False
    
    def save_cookies(self, org_id):
        """
        현재 세션의 쿠키 저장
        """
        try:
            cookie_file = f"carefor_cookies_{org_id}.pkl"
            cookies = self.driver.get_cookies()
            
            with open(cookie_file, 'wb') as f:
                pickle.dump(cookies, f)
            
            print(f"쿠키 저장 완료: {cookie_file}")
            return True
            
        except Exception as e:
            print(f"쿠키 저장 실패: {e}")
            return False

    def get_all_patients(self):
        """전체 수급자 목록 수집"""
        try:
            # 디버그 로그 제거
            
            # 메인 페이지에서 수급자 관리 메뉴 찾기
            self.driver.get("https://www.carefor.co.kr")
            time.sleep(3)
            
            # 수급자 관리 관련 링크 찾기
            try:
                # 다양한 방법으로 수급자 관리 메뉴 찾기
                menu_selectors = []
                    
                
                patient_menu = None
                for selector in menu_selectors:
                    try:
                        patient_menu = self.driver.find_element(By.XPATH, selector)
                        # 디버그 로그 제거
                        break
                    except:
                        continue
                
                if patient_menu:
                    patient_menu.click()
                    time.sleep(3)
                else:
                    # 디버그 로그 제거
                    # 직접 URL로 시도
                    # 디버그 로그 제거
                    self.driver.get(ALL_PATIENT_URL)
                    time.sleep(3)
                
            except Exception as e:
                # 디버그 로그 제거
                # 직접 URL로 시도
                self.driver.get(ALL_PATIENT_URL)
                time.sleep(3)
            
            self.close_any_popup()
            
            # 수급자 테이블 찾기 - 다양한 선택자 시도
            table_selectors = [
                ALL_PATIENT_SELECTOR,
                "#ctnr_patient_list_table",
                ".patient_list_table",
                "table",
                ".table",
                "#patient_table",
                ".list_table"
            ]
            
            patients = []
            table_found = False
            
            for selector in table_selectors:
                try:
                    # 디버그 로그 제거
                    table = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # 테이블 행 추출
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    # 디버그 로그 제거
                    
                    if len(rows) > 1:  # 헤더 행 제외하고 데이터가 있는지 확인
                        for i, row in enumerate(rows):
                            if i == 0:  # 헤더 행 건너뛰기
                                continue
                            
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) >= 2:
                                # 이름이 있을 만한 셀들 확인 (상태값 제외)
                                patient_name = None
                                status = '미확인'
                                
                                for j, cell in enumerate(cells[:8]):  # 처음 8개 셀 확인
                                    text = cell.text.strip()
                                    
                                    # 상태값들 제외
                                    if text in ['수급중', '수급종료', '대기중', '승인', '거부', '미승인', '활성', '비활성']:
                                        status = text
                                        continue
                                    
                                    # 숫자만 있는 경우 제외 (ID나 순번)
                                    if text.isdigit():
                                        continue
                                    
                                    # 빈 텍스트 제외
                                    if not text:
                                        continue
                                    
                                    # 한글 이름 패턴 확인 (2-4글자 한글)
                                    if len(text) >= 2 and len(text) <= 4 and all(ord('가') <= ord(c) <= ord('힣') for c in text):
                                        patient_name = text
                                        break
                                    
                                    # 영문 이름 패턴 확인 (2-20글자 영문)
                                    elif len(text) >= 2 and len(text) <= 20 and text.replace(' ', '').isalpha():
                                        patient_name = text
                                        break
                                
                                if patient_name:
                                    patients.append({
                                        'name': patient_name,
                                        'row_index': i,
                                        'cell_index': j,
                                        'status': status
                                    })
                                    # 디버그 로그 제거
                        
                        if patients:
                            table_found = True
                            break
                    
                except Exception as e:
                    # 디버그 로그 제거
                    continue
            
            if not table_found:
                # 디버그 로그 제거
                
                # 페이지의 모든 테이블 확인
                all_tables = self.driver.find_elements(By.TAG_NAME, "table")
                # 디버그 로그 제거
                
                for i, table in enumerate(all_tables):
                    try:
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        if len(rows) > 1:
                            # 디버그 로그 제거
                            # 첫 번째 데이터 행의 내용 확인
                            if len(rows) > 1:
                                first_row = rows[1]
                                cells = first_row.find_elements(By.TAG_NAME, "td")
                                cell_texts = [cell.text.strip() for cell in cells[:5]]
                                # 디버그 로그 제거
                    except:
                        pass
                
                # 더미 데이터 제거 - 성능 최적화
                # patients = [
                #     {'name': '홍길동', 'row_index': 1, 'status': '미확인'},
                #     {'name': '김철수', 'row_index': 2, 'status': '미확인'},
                #     {'name': '이영희', 'row_index': 3, 'status': '미확인'}
                # ]
                patients = []  # 실제 데이터를 찾지 못하면 빈 리스트 반환
            
            self.all_patients = patients
            # 디버그 로그 제거
            
            return patients
                
        except Exception as e:
            # 디버그 로그 제거
            traceback.print_exc()
            return []
    
    def get_attendance_data(self, date_str=None):
        """출석 데이터 수집"""
        try:
            if not date_str:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # 디버그 로그 제거
            
            # 출석 관리 페이지로 이동
            try:
                # 디버그 로그 제거
                self.driver.get(ATTENDANCE_URL)
                time.sleep(3)
                self.close_any_popup()
                
                # 페이지 로딩 대기
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 디버그 로그 제거
                
            except Exception as e:
                # 디버그 로그 제거
                return []
            
            # 새로운 날짜 네비게이션 방식 사용
            try:
                # 디버그 로그 제거
                navigation_success = self.navigate_to_date_using_buttons(date_str)
                
                if navigation_success:
                    # 디버그 로그 제거
                    pass
                else:
                    # 디버그 로그 제거
                    # 기존 날짜 입력 방식으로 폴백
                    self.set_date_using_input_field(date_str)
                    
            except Exception as e:
                # 디버그 로그 제거
                # 기존 방식으로 폴백
                self.set_date_using_input_field(date_str)
            
            # 출석 데이터 수집
            attendance_data = self.extract_attendance_data()
            
            # 디버그 로그 제거
            return attendance_data
            
        except Exception as e:
            # 디버그 로그 제거
            traceback.print_exc()
            return []
    
    def set_date_using_input_field(self, date_str):
        """기존 방식의 날짜 입력 필드 사용"""
        try:
            # 디버그 로그 제거
            
            # 날짜 입력 필드 찾기
            date_selectors = [
                "input[type='date']",
                "input[name*='date']",
                "input[id*='date']",
                "input[name*='Date']",
                "input[id*='Date']",
                ".date-picker input",
                "#attendance_date",
                ".datepicker input",
                "input[placeholder*='날짜']",
                "input[placeholder*='date']",
                "input.form-control[type='text']"
            ]
            
            date_input = None
            for selector in date_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            date_input = element
                            # 디버그 로그 제거
                            break
                    if date_input:
                        break
                except:
                    continue
            
            # 날짜 입력 시도
            if date_input:
                try:
                    # 기존 값 클리어
                    date_input.clear()
                    time.sleep(0.5)
                    
                    # JavaScript로 값 설정 시도
                    self.driver.execute_script("arguments[0].value = '';", date_input)
                    time.sleep(0.5)
                    
                    # 다양한 날짜 형식으로 시도
                    date_formats = [
                        date_str,  # 2024-01-01
                        date_str.replace('-', '/'),  # 2024/01/01
                        date_str.replace('-', '.'),  # 2024.01.01
                        datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일"),  # 2024년 01월 01일
                        datetime.strptime(date_str, "%Y-%m-%d").strftime("%m/%d/%Y"),  # 01/01/2024
                    ]
                    
                    success = False
                    for date_format in date_formats:
                        try:
                            # 키보드 입력으로 시도
                            date_input.clear()
                            date_input.send_keys(date_format)
                            time.sleep(0.5)
                            
                            # JavaScript로 값 설정 시도
                            self.driver.execute_script("arguments[0].value = arguments[1];", date_input, date_format)
                            time.sleep(0.5)
                            
                            # 값이 제대로 설정되었는지 확인
                            current_value = date_input.get_attribute('value')
                            # 디버그 로그 제거
                            
                            if current_value and (date_str in current_value or date_format in current_value):
                                # 디버그 로그 제거
                                success = True
                                break
                                
                        except Exception as e:
                            # 디버그 로그 제거
                            continue
                    
                    if not success:
                        # 디버그 로그 제거
                        pass
                    
                    # Enter 키 또는 Tab 키로 입력 완료
                    try:
                        date_input.send_keys(Keys.TAB)
                        time.sleep(1)
                    except:
                        pass
                        
                except Exception as e:
                    # 디버그 로그 제거
                    pass
            
            # 검색/조회 버튼 찾기 및 클릭
            self.click_search_button()
            
        except Exception as e:
            # 디버그 로그 제거
            pass
    
    def click_search_button(self):
        """검색/조회 버튼 클릭"""
        try:
            search_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button.search",
                "button.btn-search",
                ".btn-search",
                "//button[contains(text(), '검색')]",
                "//button[contains(text(), '조회')]",
                "//input[contains(@value, '검색')]",
                "//input[contains(@value, '조회')]",
                "//a[contains(text(), '검색')]",
                "//a[contains(text(), '조회')]"
            ]
            
            search_clicked = False
            for selector in search_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            try:
                                element.click()
                                # 디버그 로그 제거
                                search_clicked = True
                                time.sleep(3)
                                break
                            except ElementClickInterceptedException:
                                # JavaScript로 클릭 시도
                                self.driver.execute_script("arguments[0].click();", element)
                                # 디버그 로그 제거
                                search_clicked = True
                                time.sleep(3)
                                break
                            except Exception as e:
                                # 디버그 로그 제거
                                continue
                    
                    if search_clicked:
                        break
                        
                except Exception as e:
                    # 디버그 로그 제거
                    continue
            
            if not search_clicked:
                # 디버그 로그 제거
                pass
                
        except Exception as e:
            # 디버그 로그 제거
            pass
    
    def extract_attendance_data(self):
        """출석 테이블에서 데이터 추출 - 간단한 형태로 수급자명과 출석일정만"""
        try:
            attendance_data = []
            
            # 지정된 XPath로 tbody 요소 찾기
            # 디버그 로그 제거
            try:
                # //*[@id="patient_list"]/tbody 경로로 tbody 찾기
                tbody_xpath = '//*[@id="patient_list"]/tbody'
                tbody = self.driver.find_element(By.XPATH, tbody_xpath)
                # 디버그 로그 제거
                
                # tbody 내의 모든 행 찾기
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                # 디버그 로그 제거
                
                # 각 행에서 수급자명과 출석일정 추출
                for i, row in enumerate(rows):
                    try:
                        row_index = i + 1
                                
                        # 행의 모든 셀 확인
                        th_cells = row.find_elements(By.TAG_NAME, "th")
                        td_cells = row.find_elements(By.TAG_NAME, "td")
                        all_cells = th_cells + td_cells
                            
                        # 디버그 로그 제거
                            
                        # 수급자명 (2번째 셀)
                        name = None
                        if len(all_cells) >= 2:
                            name = all_cells[1].text.strip()
                        
                        # 출석일정 (5번째 셀)
                        schedule = "일정없음"
                        if len(all_cells) >= 5:
                            schedule = all_cells[4].text.strip()
                        
                        # 디버그 로그 제거
                        
                        # 헤더 키워드 필터링
                        header_keywords = [
                            '수급자명', '출석일정', '일정', '동승자', '연번', '등급', 
                            '케어그룹', '확인자', '이동서비스', '시작', '종료', '일정변경'
                        ]
                        
                        # 유효한 이름인지 확인
                        if (name and len(name) >= 2 and 
                            name not in header_keywords and 
                            schedule not in header_keywords and
                            not name.isdigit()):
                            
                            # 한글 이름 패턴 체크
                            korean_name_pattern = re.compile(r'^[가-힣]{2,4}$')
                
                            if korean_name_pattern.match(name):
                                # 출석 상태 판단
                                status = self.determine_attendance_status(schedule)
                                
                                record = {
                                    'name': name,
                                    'status': status,
                                    'schedule': schedule
                                }
                                
                                attendance_data.append(record)
                                # 디버그 로그 제거
                            else:
                                # 디버그 로그 제거
                                pass
                        else:
                            # 디버그 로그 제거
                            pass
                            
                    except Exception as e:
                        # 디버그 로그 제거
                        continue
                    
                # 디버그 로그 제거
                return attendance_data
                
            except Exception as e:
                # 디버그 로그 제거
                # 폴백으로 기존 방식 시도
                return self.extract_attendance_data_fallback()
                
        except Exception as e:
            # 디버그 로그 제거
            return []

    def extract_attendance_data_fallback(self):
        """폴백 방식으로 출석 데이터 추출"""
        try:
            attendance_data = []
            # 디버그 로그 제거
            
            # 기존 방식으로 section 요소 찾기
            section_xpath = '//*[@id="r_padding"]/div[3]/section'
            section = self.driver.find_element(By.XPATH, section_xpath)
            # 디버그 로그 제거
            
            # section 내의 table 찾기
            table_elements = section.find_elements(By.TAG_NAME, "table")
            if not table_elements:
                # 디버그 로그 제거
                return []
            
            table = table_elements[0]
            # 디버그 로그 제거
            
            # tbody 찾기
            tbody_elements = table.find_elements(By.TAG_NAME, "tbody")
            if not tbody_elements:
                # 디버그 로그 제거
                return []
            
            tbody = tbody_elements[0]
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            # 디버그 로그 제거
            
            # 각 행에서 수급자명과 출석일정 추출
            for i, row in enumerate(rows):
                try:
                    row_index = i + 1
                    
                    # 행의 모든 셀 확인
                    th_cells = row.find_elements(By.TAG_NAME, "th")
                    td_cells = row.find_elements(By.TAG_NAME, "td")
                    all_cells = th_cells + td_cells
                    
                    # 수급자명 (2번째 셀)
                    name = None
                    if len(all_cells) >= 2:
                        name = all_cells[1].text.strip()
                    
                    # 출석일정 (5번째 셀)
                    schedule = "일정없음"
                    if len(all_cells) >= 5:
                        schedule = all_cells[4].text.strip()
                    
                    # 헤더 키워드 필터링
                    header_keywords = [
                        '수급자명', '출석일정', '일정', '동승자', '연번', '등급', 
                        '케어그룹', '확인자', '이동서비스', '시작', '종료', '일정변경'
                    ]
                    
                    # 유효한 이름인지 확인
                    if (name and len(name) >= 2 and 
                        name not in header_keywords and 
                        schedule not in header_keywords and
                        not name.isdigit()):
                        
                        # 한글 이름 패턴 체크
                        korean_name_pattern = re.compile(r'^[가-힣]{2,4}$')
                
                        if korean_name_pattern.match(name):
                            # 출석 상태 판단
                            status = self.determine_attendance_status(schedule)
                            
                            record = {
                                'name': name,
                                'status': status,
                                'schedule': schedule
                            }
                            
                            attendance_data.append(record)
                            # 디버그 로그 제거
                                
                except Exception as e:
                    # 디버그 로그 제거
                    continue
                    
            # 디버그 로그 제거
            return attendance_data
            
        except Exception as e:
            # 디버그 로그 제거
            return []
            
    def determine_attendance_status(self, schedule_text):
        """출석일정 텍스트에서 출석 상태 판단"""
        if not schedule_text or schedule_text == "일정없음":
            return "일정없음"
        
        schedule_lower = schedule_text.lower()
        
        # 출석 상태 키워드 매핑 - 미이용을 결석과 분리
        status_keywords = {
            '출석': ['출석', '참석', '도착'],
            '결석': ['결석', '불참', '휴무'],
            '미이용': ['미이용', '이용안함'],
            '지각': ['지각', '늦음'],
            '조퇴': ['조퇴', '일찍'],
            '외출': ['외출', '나감']
        }
        
        for status, keywords in status_keywords.items():
            for keyword in keywords:
                if keyword in schedule_lower:
                    return status
        
        # 시간 정보가 있으면 출석으로 간주
        if re.search(r'\d{1,2}:\d{2}', schedule_text):
            return "출석"
        
        return "미확인"

    def extract_time_from_schedule(self, schedule_text):
        """출석일정에서 시간 정보 추출"""
        if not schedule_text:
            return None
        
        # 시간 패턴 찾기 (HH:MM 형식)
        time_match = re.search(r'(\d{1,2}:\d{2})', schedule_text)
        if time_match:
            return time_match.group(1)
        
        return None

    def extract_destination_from_schedule(self, schedule_text):
        """출석일정에서 외출 행선지 정보 추출"""
        if not schedule_text or '외출' not in schedule_text:
            return None
        
        # 외출 뒤의 텍스트를 행선지로 간주
        parts = schedule_text.split('외출')
        if len(parts) > 1:
            destination = parts[1].strip()
            # 괄호나 특수문자 제거
            destination = re.sub(r'[()[\]{}]', '', destination).strip()
            if destination:
                return destination
        
        return "행선지 미확인"
    
    def compare_attendance(self, date_str=None):
        """출석 비교 분석"""
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # 디버그 로그 제거
            
            # 전체 수급자 목록과 출석 데이터가 없으면 수집
            if not hasattr(self, 'all_patients') or not self.all_patients:
                # 디버그 로그 제거
                self.get_all_patients()
            
            # 출석 데이터 수집
            # 디버그 로그 제거
            attendance_data = self.get_attendance_data(date_str)
            
            # 출석자 이름 목록 생성
            attended_names = set()
            attendance_dict = {}
            
            for record in attendance_data:
                name = record['name']
                status = record['status']
                attended_names.add(name)
                attendance_dict[name] = record  # 전체 record를 저장하여 destination 정보도 포함
            
            # 디버그 로그 제거
            
            # 비교 결과 생성
            comparison_result = []
            
            for patient in self.all_patients:
                patient_name = patient['name']
                
                if patient_name in attendance_dict:
                    # 출석 기록이 있는 경우
                    record = attendance_dict[patient_name]
                    status = record['status']
                    result_item = {
                        'name': patient_name,
                        'status': status,
                        'attendance_status': '기록있음',
                        'date': date_str
                    }
                    # 외출인 경우 행선지 정보 추가
                    if status == '외출' and 'destination' in record:
                        result_item['destination'] = record['destination']
                    
                    comparison_result.append(result_item)
                else:
                    # 출석 기록이 없는 경우 (일정없음으로 분류)
                    comparison_result.append({
                        'name': patient_name,
                        'status': '일정없음',
                        'attendance_status': '기록없음',
                        'date': date_str
                    })
            
            # 통계 계산
            total_patients = len(comparison_result)
            attended_count = len([r for r in comparison_result if r['status'] in ['출석', '참석']])
            absent_count = len([r for r in comparison_result if r['status'] in ['결석', '불참']])
            late_count = len([r for r in comparison_result if r['status'] == '지각'])
            early_leave_count = len([r for r in comparison_result if r['status'] == '조퇴'])
            unknown_count = len([r for r in comparison_result if r['status'] == '미확인'])
            no_schedule_count = len([r for r in comparison_result if r['status'] == '일정없음'])
            
            attendance_rate = (attended_count / total_patients * 100) if total_patients > 0 else 0
            
            summary = {
                'date': date_str,
                'total_patients': total_patients,
                'attended': attended_count,
                'absent': absent_count,
                'late': late_count,
                'early_leave': early_leave_count,
                'unknown': unknown_count,
                'no_schedule': no_schedule_count,
                'attendance_rate': round(attendance_rate, 1)
            }
            
            # 디버그 로그 제거 (통계 출력 부분)
            
            return {
                'summary': summary,
                'details': comparison_result
            }
            
        except Exception as e:
            # 디버그 로그 제거
            traceback.print_exc()
            return {
                'summary': {
                    'date': date_str or datetime.now().strftime("%Y-%m-%d"),
                    'total_patients': 0,
                    'attended': 0,
                    'absent': 0,
                    'late': 0,
                    'early_leave': 0,
                    'unknown': 0,
                    'no_schedule': 0,
                    'attendance_rate': 0
                },
                'details': []
            }
    
    def collect_all_data(self, date_str=None):
        """모든 데이터 수집 및 분석"""
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # 디버그 로그 제거
            
            # 1. 전체 수급자 목록 수집
            # 디버그 로그 제거
            patients = self.get_all_patients()
            
            if not patients:
                # 디버그 로그 제거
                return None
            
            # 2. 출석 데이터 수집
            # 디버그 로그 제거
            attendance_data = self.get_attendance_data(date_str)
            
            # 3. 출석 비교 분석
            # 디버그 로그 제거
            comparison_result = self.compare_attendance(date_str)
            
            # 4. 결과 정리
            result = {
                'collection_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'target_date': date_str,
                'patients': patients,
                'attendance_data': attendance_data,
                'comparison': comparison_result,
                'success': True
            }
            
            # 디버그 로그 제거 (결과 출력 부분)
            
            return result
            
        except Exception as e:
            # 디버그 로그 제거
            traceback.print_exc()
            return {
                'collection_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'target_date': date_str or datetime.now().strftime("%Y-%m-%d"),
                'patients': [],
                'attendance_data': [],
                'comparison': {
                    'summary': {
                        'total_patients': 0,
                        'attended': 0,
                        'absent': 0,
                        'attendance_rate': 0
                    },
                    'details': []
                },
                'success': False,
                'error': str(e)
            }
        finally:
            if self.driver:
                self.driver.quit()
    
    def collect_data_for_gui(self, date_str=None):
        """GUI용 데이터 수집 (브라우저 세션 유지)"""
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # 주말 체크
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = target_date.weekday()  # 0=월요일, 6=일요일
            
            if weekday >= 5:  # 토요일(5) 또는 일요일(6)
                day_name = "토요일" if weekday == 5 else "일요일"
                # 디버그 로그 제거
            
            # 디버그 로그 제거
            
            # 브라우저 초기화 (필요한 경우에만)
            if not hasattr(self, 'driver') or self.driver is None:
                # 디버그 로그 제거
                self.init_driver()
                
                # 로그인
                if not self.login():
                    return {
                        'success': False,
                        'error': '로그인 실패',
                        'date': date_str,
                        'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
            
            # 1단계: 전체 수급자 목록 수집
            # 디버그 로그 제거
            patients = self.get_all_patients()
            if not patients:
                return {
                    'success': False,
                    'error': '수급자 목록 수집 실패',
                    'date': date_str,
                    'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # 디버그 로그 제거
            
            # 2단계: 출석 데이터 수집
            # 디버그 로그 제거
            attendance_data = self.get_attendance_data(date_str)
            # 디버그 로그 제거
            
            # 주말이고 출석 데이터가 없는 경우 특별 처리
            if weekday >= 5 and len(attendance_data) == 0:
                day_name = "토요일" if weekday == 5 else "일요일"
                return {
                    'success': True,
                    'patients': patients,
                    'attendance': [],
                    'comparison': {
                        'total_patients': len(patients),
                        'attended': 0,
                        'absent': 0,  # 주말에는 결석이 아님
                        'late': 0,
                        'early_leave': 0,
                        'unknown': 0,
                        'no_schedule': len(patients),  # 주말에는 모두 일정없음
                        'attendance_rate': 0.0
                    },
                    'date': date_str,
                    'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'note': f"{day_name}은 휴무일입니다."
                }
            
            # 3단계: 출석 비교 분석
            # 디버그 로그 제거
            comparison_result = self.compare_attendance(date_str)
            
            # 디버그 로그 제거 (완료 메시지 부분)
            
            return {
                'success': True,
                'patients': patients,
                'attendance': attendance_data,
                'comparison': comparison_result['summary'],  # summary 부분만 전달
                'details': comparison_result['details'],     # details는 별도로 전달
                'date': date_str,
                'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            # 디버그 로그 제거
            return {
                'success': False,
                'error': str(e),
                'date': date_str,
                'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def close_browser(self):
        """브라우저 종료 (GUI에서 명시적으로 호출)"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                # 디버그 로그 제거
            except Exception as e:
                # 디버그 로그 제거
                pass
    
    def navigate_to_date_using_buttons(self, target_date_str):
        """이전/다음 버튼을 사용해서 특정 날짜로 이동"""
        try:
            # 디버그 로그 제거
            
            # 현재 날짜 확인
            current_date = self.get_current_date_from_page()
            if not current_date:
                # 디버그 로그 제거
                return False
            
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
            current_date_obj = datetime.strptime(current_date, "%Y-%m-%d")
            
            # 디버그 로그 제거
            
            # 날짜 차이 계산
            date_diff = (target_date - current_date_obj).days
            
            if date_diff == 0:
                # 디버그 로그 제거
                return True
            elif date_diff > 0:
                # 미래 날짜 - 다음 버튼 클릭
                # 디버그 로그 제거
                return self.click_date_navigation_button("next", date_diff)
            else:
                # 과거 날짜 - 이전 버튼 클릭
                # 디버그 로그 제거
                return self.click_date_navigation_button("prev", abs(date_diff))
                
        except Exception as e:
            # 디버그 로그 제거
            return False
    
    def get_current_date_from_page(self):
        """페이지에서 현재 선택된 날짜 가져오기"""
        try:
            # 날짜 표시 영역에서 현재 날짜 추출
            date_selectors = [
                "#r_padding > div.left_list_div > div > div > div:nth-child(2) > div > span.s2",
                ".s2",
                "span.s2",
                "//span[contains(@class, 's2')]",
                "//div[contains(text(), '20')]"  # 2024, 2025 등이 포함된 텍스트
            ]
            
            for selector in date_selectors:
                try:
                    if selector.startswith("//"):
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    date_text = element.text.strip()
                    # 디버그 로그 제거
                    
                    # 날짜 형식 파싱 시도
                    date_patterns = [
                        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2024-01-01
                        r'(\d{4})\.(\d{1,2})\.(\d{1,2})',  # 2024.01.01
                        r'(\d{4})/(\d{1,2})/(\d{1,2})',  # 2024/01/01
                        r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일',  # 2024년 01월 01일
                    ]
                    
                    for pattern in date_patterns:
                        match = re.search(pattern, date_text)
                        if match:
                            year, month, day = match.groups()
                            formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            # 디버그 로그 제거
                            return formatted_date
                            
                except Exception as e:
                    # 디버그 로그 제거
                    continue
            
            # 디버그 로그 제거
            return None
            
        except Exception as e:
            # 디버그 로그 제거
            return None
    
    def click_date_navigation_button(self, direction, count):
        """날짜 네비게이션 버튼 클릭"""
        try:
            if direction == "prev":
                xpath = PREV_DATE_BUTTON_XPATH
                button_name = "이전"
            elif direction == "next":
                xpath = NEXT_DATE_BUTTON_XPATH
                button_name = "다음"
            else:
                # 디버그 로그 제거
                return False
            
            # 디버그 로그 제거
            
            for i in range(count):
                try:
                    # 버튼 찾기
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    
                    # 클릭 시도
                    try:
                        button.click()
                        # 디버그 로그 제거
                    except ElementClickInterceptedException:
                        # JavaScript로 클릭 시도
                        self.driver.execute_script("arguments[0].click();", button)
                        # 디버그 로그 제거
                    
                    # 페이지 로딩 대기
                    time.sleep(2)
                    
                    # 팝업 닫기
                    self.close_any_popup()
                    
                except TimeoutException:
                    # 디버그 로그 제거
                    return False
                except Exception as e:
                    # 디버그 로그 제거
                    return False
            
            # 디버그 로그 제거
            return True

        except Exception as e:  # ← 이 부분을 추가하세요!
            # 디버그 로그 제거
            return False

    def get_outing_data(self, date_str=None):
        """외출 데이터 수집 - 직접 URL 방식"""
        try:
            if not date_str:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            print(f"🚶 외출 데이터 수집 시작: {date_str}")

            # 외출 리포트 페이지로 직접 이동
            print("🔄 외출 리포트 페이지로 이동 중...")
            self.driver.get(OUTING_REPORT_URL)
            time.sleep(3)
            
            # 팝업 닫기
            print("🔄 팝업 닫기...")
            self.close_any_popup()
            time.sleep(2)
            
            # 페이지 로딩 완료 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print(f"현재 페이지 URL: {self.driver.current_url}")
            
            # 외출 테이블에서 데이터 추출
            outing_data = self.extract_outing_table_data()
            
            if outing_data:
                print(f"✅ 외출 데이터 발견: {len(outing_data)}명")
                for data in outing_data:
                    print(f"  - {data['name']}: {data['date']} {data['time']} → {data['destination']}")
            else:
                print("ℹ️ 외출 예정자가 없습니다")
            
            return {
                'success': True,
                'outing_list': outing_data,
                'date': date_str,
                'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ 외출 데이터 수집 오류: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'date': date_str,
                'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
    def get_inherited_date(self, current_row, current_date_text, table_data):
        """날짜 상속 로직 - 현재 행에 날짜가 없으면 위쪽 행들을 순차적으로 참조"""
        try:
            # 1. 현재 행에 날짜가 있는지 확인
            if current_date_text and current_date_text.strip():
                formatted_date = self.format_date(current_date_text)
                print(f"      현재 행({current_row})에 날짜 있음: '{current_date_text}' → '{formatted_date}'")
                return formatted_date
            
            # 2. 현재 행에 날짜가 없으면 위쪽 행들을 순차적으로 확인
            print(f"      현재 행({current_row})에 날짜 없음, 상위 행 탐색 시작...")
            
            # 현재 행보다 작은 행 번호들을 역순으로 확인
            for check_row in range(current_row - 1, -1, -1):
                if check_row in table_data:
                    check_cells = table_data[check_row]
                    check_date = check_cells.get(1, "")  # 컬럼 1의 날짜
                    
                    if check_date and check_date.strip():
                        formatted_date = self.format_date(check_date)
                        print(f"      행 {check_row}에서 날짜 발견: '{check_date}' → '{formatted_date}'")
                        return formatted_date
                    else:
                        print(f"      행 {check_row}: 날짜 없음, 계속 탐색...")
            
            # 3. 모든 상위 행을 확인했는데도 날짜를 찾지 못한 경우
            print(f"      모든 상위 행 탐색 완료, 날짜를 찾을 수 없음")
            return "미확인"
            
        except Exception as e:
            print(f"      날짜 상속 오류: {e}")
            return "미확인"

    def extract_outing_table_data(self):
        
        """외출 테이블에서 데이터 추출 - 연번 역순 10개만 표시"""
        try:
            outing_data = []
            print("🔍 외출 테이블 데이터 추출 중...")
            
            # 테이블이 완전히 로딩될 때까지 충분히 대기
            print("⏳ 테이블 완전 로딩 대기 중...")
            time.sleep(10)
            
            # g-td 요소들 찾기
            selectors = [
                'g-td[data-gt-row][data-gt-col]',
                'g-td[data-gt-row]',
                'g-td',
                'g-t g-td'
            ]
            
            gtd_elements = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"  ✅ {selector}로 {len(elements)}개 g-td 발견")
                        gtd_elements = elements
                        break
                except Exception as e:
                    continue
            
            if not gtd_elements:
                return []
            
            print(f"📊 총 {len(gtd_elements)}개 g-td 요소 발견")
            
            # 각 g-td에서 데이터 추출
            table_data = {}
            
            for i, gtd in enumerate(gtd_elements):
                try:
                    row_attr = gtd.get_attribute('data-gt-row')
                    col_attr = gtd.get_attribute('data-gt-col')
                    text_content = gtd.text.strip()
                    
                    if row_attr is not None and col_attr is not None:
                        row_num = int(row_attr)
                        col_num = int(col_attr)
                        
                        if row_num not in table_data:
                            table_data[row_num] = {}
                        
                        table_data[row_num][col_num] = text_content
                    
                except Exception as e:
                    continue
            
            print(f"📋 {len(table_data)}개 행 데이터 수집됨")

            # 행별로 데이터 정리하고 외출 데이터 생성
            for row_num in sorted(table_data.keys()):
                try:
                    row_cells = table_data[row_num]
                    
                    if not row_cells:
                        continue
                    
                    # 컬럼 데이터 추출
                    연번 = row_cells.get(0, "")
                    외출일_원본 = row_cells.get(1, "")
                    시간1 = row_cells.get(2, "")
                    시간2 = row_cells.get(3, "")
                    수급자명 = row_cells.get(4, "")
                    성별 = row_cells.get(5, "")
                    생년월일 = row_cells.get(6, "")
                    목적 = row_cells.get(7, "")
                    행선지 = row_cells.get(8, "")
                    
                    print(f"    행 {row_num}: 연번='{연번}', 날짜='{외출일_원본}', 이름='{수급자명}', 행선지='{행선지}'")
                    
                    # 수급자명이 한글인지 확인
                    if 수급자명 and re.match(r'^[가-힣]{2,4}$', 수급자명):
                        # 시간 정보 조합
                        if 시간1 and 시간2:
                            시간정보 = f"{시간1}~{시간2}"
                        else:
                            시간정보 = 시간1 or 시간2 or "미확인"
                        
                        # 행선지 처리
                        최종행선지 = 행선지 if 행선지 else (목적 if 목적 else "미확인")
                        
                        # 날짜 처리 (간단하게)
                        if 외출일_원본 and 외출일_원본.strip():
                            외출일 = self.format_date(외출일_원본)
                        else:
                            외출일 = "미확인"
                        
                        # 연번 처리
                        try:
                            if 연번 and 연번.strip().isdigit():
                                연번_숫자 = int(연번.strip())
                                print(f"      연번 추출 성공: '{연번}' → {연번_숫자}")
                            else:
                                연번_숫자 = 0
                                print(f"      연번 추출 실패: '{연번}' → 0")
                        except Exception as e:
                            연번_숫자 = 0
                            print(f"      연번 변환 오류: '{연번}' → 0 (오류: {e})")
                        
                        outing_record = {
                            'name': 수급자명,
                            'date': 외출일,
                            'time': 시간정보,
                            'destination': 최종행선지,
                            'row_num': row_num,
                            '연번': 연번_숫자
                        }
                        
                        outing_data.append(outing_record)
                        print(f"      ✅ 외출 데이터 추가: [연번:{연번_숫자}] {수급자명} | {외출일} | {시간정보} | {최종행선지}")
                            
                except Exception as e:
                    print(f"    ❌ 행 {row_num} 처리 오류: {e}")
                    continue
            
            # 연번 기준 역순 정렬 및 최신 10개만 선택
            if outing_data:
                print("🔄 정렬 전 원본 데이터:")
                for data in outing_data:
                    print(f"  연번:{data['연번']} - {data['name']}")
                
                # 연번 기준 내림차순 정렬 (가장 큰 번호가 첫 번째)
                outing_data = sorted(outing_data, key=lambda x: x['연번'], reverse=True)
                
                # 상위 10개만 선택
                outing_data = outing_data[:10]
                
                print(f"✅ 연번 내림차순 정렬 완료 ({len(outing_data)}개 선택)")
                print("📋 최종 정렬 결과:")
                for i, data in enumerate(outing_data, 1):
                    print(f"  {i}. [연번:{data['연번']}] {data['name']}")
                
                print(f"✅ 총 {len(outing_data)}명의 외출 데이터 추출 완료")
                
                # 최종 결과 출력
                print("\n📋 추출된 외출 데이터 (연번 역순, 최신 10개):")
                for i, data in enumerate(outing_data, 1):
                    연번 = data.get('연번', 0)
                    print(f"  {i}. [연번:{연번}] {data['name']} - {data['date']} {data['time']} → {data['destination']}")
            else:
                print("ℹ️ 외출 데이터가 없습니다")
            
            return outing_data
            
        except Exception as e:
            print(f"❌ 외출 테이블 데이터 추출 오류: {e}")
            import traceback
            traceback.print_exc()
            return []
        
    def format_date(self, date_text):
        """날짜 텍스트를 표준 형식으로 변환"""
        try:
            if not date_text or date_text.strip() == "":
                return "미확인"
            
            date_text = date_text.strip()
            
            # 다양한 날짜 형식 처리
            date_patterns = [
                (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', r'\1-\2-\3'),      # 2025.05.13 → 2025-05-13
                (r'(\d{4})/(\d{1,2})/(\d{1,2})', r'\1-\2-\3'),       # 2025/05/13 → 2025-05-13
                (r'(\d{4})-(\d{1,2})-(\d{1,2})', r'\1-\2-\3'),       # 2025-5-13 → 2025-05-13
                (r'(\d{2})\.(\d{1,2})\.(\d{1,2})', r'20\1-\2-\3'),   # 25.05.13 → 2025-05-13
            ]
            
            for pattern, replacement in date_patterns:
                match = re.search(pattern, date_text)
                if match:
                    result = re.sub(pattern, replacement, date_text)
                    # 월, 일을 2자리로 맞추기
                    parts = result.split('-')
                    if len(parts) == 3:
                        year, month, day = parts
                        formatted = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        print(f"    날짜 변환: '{date_text}' → '{formatted}'")
                        return formatted
            
            # 패턴에 맞지 않으면 원본 반환
            print(f"    날짜 변환 실패: '{date_text}' (패턴 불일치)")
            return date_text
            
        except Exception as e:
            print(f"    날짜 변환 오류: '{date_text}' - {e}")
            return date_text or "미확인"

    def sort_by_date(self, outing_data):
        """외출 데이터를 날짜 기준으로 최신순 정렬"""
        try:
            def date_sort_key(item):
                date_str = item.get('date', '')
                
                # 날짜 파싱 시도
                try:
                    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    elif re.match(r'\d{4}\.\d{1,2}\.\d{1,2}', date_str):
                        return datetime.strptime(date_str, '%Y.%m.%d')
                    else:
                        # 파싱 실패시 아주 오래된 날짜 반환 (맨 뒤로)
                        return datetime(1900, 1, 1)
                except:
                    return datetime(1900, 1, 1)
            
            # 최신순 정렬 (내림차순)
            sorted_data = sorted(outing_data, key=date_sort_key, reverse=True)
            print(f"🔄 {len(sorted_data)}개 데이터 최신순 정렬 완료")
            
            return sorted_data
            
        except Exception as e:
            print(f"❌ 정렬 오류: {e}")
            return outing_data

    def get_staff_absence_data(self, date_str=None):
        """직원 휴무 현황 수집"""
        try:
            if not date_str:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            print(f"👨‍🏫 직원 휴무 현황 수집 시작: {date_str}")

            # 1단계: 직원 근무 관리 페이지로 이동
            print("🔄 직원 근무 관리 페이지로 이동 중...")
            self.driver.get(STAFF_WORK_MANAGE_URL)
            time.sleep(3)
            self.close_any_popup()
            time.sleep(2)
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 2단계: "일일 근무현황" 버튼 클릭
            print("🔄 일일 근무현황 버튼 클릭 중...")
            daily_work_button_clicked = False

            # 정확한 XPath 주소 사용
            exact_xpath = '//*[@id="r_padding"]/div[3]/div[3]/div[1]'

            try:
                # 정확한 XPath로 버튼 찾기
                button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, exact_xpath))
                )
                
                # 버튼 클릭 시도
                try:
                    button.click()
                    print(f"✅ 일일 근무현황 버튼 클릭 성공: {exact_xpath}")
                    daily_work_button_clicked = True
                    time.sleep(3)
                except ElementClickInterceptedException:
                    # JavaScript로 클릭 시도
                    self.driver.execute_script("arguments[0].click();", button)
                    print(f"✅ 일일 근무현황 버튼 JavaScript 클릭 성공: {exact_xpath}")
                    daily_work_button_clicked = True
                    time.sleep(3)
                    
            except TimeoutException:
                print(f"❌ 버튼을 찾을 수 없음: {exact_xpath}")
            except Exception as e:
                print(f"❌ 버튼 클릭 오류: {e}")

            # 폴백: 다른 방법들도 시도
            if not daily_work_button_clicked:
                print("🔄 폴백 방법으로 버튼 찾기 시도...")
                
                fallback_selectors = [
                    '//*[@id="r_padding"]/div[3]/div[3]/div[1]',  # 정확한 주소
                    "//div[contains(text(), '일일근무현황')]",       # 텍스트 포함 (공백 없음)
                    "//div[contains(@onclick, 'daily')]",          # onclick 속성 포함
                    "//div[contains(@class, 'btn') and contains(text(), '일일')]"  # 버튼 클래스 + 텍스트
                ]
                
                for selector in fallback_selectors:
                    try:
                        button = self.driver.find_element(By.XPATH, selector)
                        
                        if button.is_displayed() and button.is_enabled():
                            try:
                                button.click()
                            except ElementClickInterceptedException:
                                self.driver.execute_script("arguments[0].click();", button)
                            
                            print(f"✅ 폴백 방법으로 버튼 클릭 성공: {selector}")
                            daily_work_button_clicked = True
                            time.sleep(3)
                            break
                            
                    except Exception as e:
                        print(f"❌ 폴백 시도 실패 ({selector}): {e}")
                        continue

            if not daily_work_button_clicked:
                print("❌ 모든 방법으로 일일 근무현황 버튼을 찾을 수 없습니다.")
                return {
                    'success': False,
                    'error': '일일 근무현황 버튼을 찾을 수 없음',
                    'date': date_str,
                    'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # 3단계: 팝업 로딩 대기
            print("⏳ 팝업 로딩 대기 중...")
            time.sleep(5)
            
            # 4단계: 직원 휴무 데이터 추출
            absence_data = self.extract_staff_absence_data()
            
            return {
                'success': True,
                'absence_list': absence_data,
                'date': date_str,
                'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ 직원 휴무 데이터 수집 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'date': date_str,
                'collection_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def extract_staff_absence_data(self):
        """직원 휴무 데이터 추출 - 5번째 컬럼(근무일정시간)이 빈값인 직원만"""
        try:
            absence_data = []
            print("🔍 팝업에서 직원 휴무 데이터 추출 중...")
            
            # 올바른 일일근무현황 테이블 찾기
            correct_table = None
            
            all_tables = self.driver.find_elements(By.TAG_NAME, "table")
            print(f"📊 팝업에서 총 {len(all_tables)}개 테이블 발견")
            
            for i, table in enumerate(all_tables):
                try:
                    table_text = table.text
                    
                    # 일일근무현황 테이블 특징: 직원명과 시간 패턴이 함께 있음
                    has_time_pattern = ("07:30~17:00" in table_text or 
                                    "08:00~17:00" in table_text or
                                    "08:30~17:30" in table_text)
                    has_staff_names = ("신현희" in table_text and "이진미" in table_text)
                    
                    if has_time_pattern and has_staff_names:
                        correct_table = table
                        print(f"✅ 올바른 일일근무현황 테이블 발견: 테이블 {i}")
                        break
                        
                except Exception as e:
                    continue
            
            if not correct_table:
                print("❌ 일일근무현황 테이블을 찾을 수 없습니다.")
                return []
            
            # 테이블에서 데이터 추출
            try:
                tbody = correct_table.find_element(By.TAG_NAME, "tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
            except:
                rows = correct_table.find_elements(By.TAG_NAME, "tr")
            
            print(f"📋 일일근무현황 테이블에서 {len(rows)}개 행 발견")
            
            for i, row in enumerate(rows):
                try:
                    cells = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) < 5:  # 최소 5개 컬럼 필요
                        continue
                    
                    # 첫 번째 컬럼: 직원명
                    staff_name = cells[0].text.strip()
                    
                    # 다섯 번째 컬럼(인덱스 4): 근무일정시간
                    work_schedule = cells[4].text.strip()
                    
                    # 한글 직원명인지 확인 (2-4글자)
                    if staff_name and re.match(r'^[가-힣]{2,4}$', staff_name):
                        print(f"  ✅ 직원: '{staff_name}' - 근무일정시간(5번째 컬럼): '{work_schedule}'")
                        
                        # 휴무 조건: 5번째 컬럼이 빈 문자열인 경우만
                        if work_schedule == "":
                            absence_record = {
                                'name': staff_name,
                                'absence_type': "대체휴일",
                                'original_schedule': "일정없음"
                            }
                            absence_data.append(absence_record)
                            print(f"      🎯 휴무 직원 추가: {staff_name}")
                        else:
                            print(f"      ✅ 근무 직원: {staff_name} (일정: {work_schedule[:20]}...)")
                    else:
                        # 유효하지 않은 직원명은 무시
                        pass
                            
                except Exception as e:
                    print(f"  행 {i} 처리 오류: {e}")
                    continue
            
            # 결과 요약 출력
            if absence_data:
                absence_names = [staff['name'] for staff in absence_data]
                print(f"\n📋 휴무: {len(absence_data)}명")
                print(f"휴무자: {', '.join(absence_names)}")
            else:
                print(f"\n📋 휴무: 0명")
                print("휴무자: 없음")
            
            print(f"✅ 총 {len(absence_data)}명의 휴무 직원 추출 완료")
            return absence_data
            
        except Exception as e:
            print(f"❌ 직원 휴무 데이터 추출 오류: {e}")
            import traceback
            traceback.print_exc()
            return []
            
        except Exception as e:
            print(f"❌ 직원 휴무 데이터 추출 오류: {e}")
            import traceback
            traceback.print_exc()
            return []

    def is_absence_schedule(self, schedule):
        """일정 텍스트가 휴무인지 판단"""
        if not schedule:
            return True
        
        absence_keywords = [
            '휴무', '휴일', '대체휴일', '연차', '병가', '휴가', 
            '출장', '교육', '미출근', '결근'
        ]
        
        for keyword in absence_keywords:
            if keyword in schedule:
                return True
        
        return False

    def determine_absence_type(self, schedule):
        """휴무 유형 결정"""
        if not schedule or schedule in ['', '-', '없음']:
            return "대체휴일"
        
        absence_types = {
            '연차': ['연차', '연가'],
            '병가': ['병가', '병원'],
            '대체휴일': ['대체', '휴일', '휴무'],
            '출장': ['출장', '외근'],
            '교육': ['교육', '연수', '세미나'],
            '기타휴무': ['조퇴', '지각', '미출근', '결근']
        }
        
        for absence_type, keywords in absence_types.items():
            for keyword in keywords:
                if keyword in schedule:
                    return absence_type
        
        return "기타휴무"