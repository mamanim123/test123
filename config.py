# -*- coding: utf-8 -*-
"""
설정 파일 - 다중 사용자 지원 버전
다른 PC에서 사용할 때 이 파일만 수정하면 됩니다.
"""

# 웹사이트 설정
WEBSITE_URL = "https://carefor.kr"  # 접속할 웹사이트 URL
LOGIN_TIMEOUT = 30  # 로그인 대기 시간 (초)

# 브라우저 설정
HEADLESS_MODE = True  # True: 브라우저 숨김, False: 브라우저 표시
BROWSER_TIMEOUT = 30  # 페이지 로딩 대기 시간 (초)

# UI 설정
WINDOW_WIDTH = 800  # 창 너비
WINDOW_HEIGHT = 600  # 창 높이
WINDOW_MIN_WIDTH = 600  # 최소 창 너비
WINDOW_MIN_HEIGHT = 400  # 최소 창 높이

# 폰트 크기 설정
FONT_SIZE_LARGE = 18  # 큰 폰트 (제목 등)
FONT_SIZE_MEDIUM = 16  # 중간 폰트 (일반 텍스트)
FONT_SIZE_SMALL = 14  # 작은 폰트 (버튼 등)
FONT_SIZE_TINY = 12  # 매우 작은 폰트

# 자동 새로고침 설정
DEFAULT_REFRESH_INTERVAL = 30  # 기본 새로고침 간격 (초)
REFRESH_INTERVALS = ["10초", "30초", "60초", "120초", "300초"]  # 선택 가능한 간격

# 색상 설정
COLOR_SUCCESS = "#28a745"  # 성공 (녹색)
COLOR_WARNING = "#FF4500"  # 경고 (주황색)
COLOR_DANGER = "#dc3545"  # 위험 (빨간색)
COLOR_INFO = "#17a2b8"  # 정보 (파란색)
COLOR_SECONDARY = "#6c757d"  # 보조 (회색)

# 로그 설정
LOG_ENABLED = True  # 로그 활성화 여부
LOG_LEVEL = "INFO"  # 로그 레벨 (DEBUG, INFO, WARNING, ERROR)

# 이미지 설정
LOADING_IMAGE_NAME = "스크린샷 2025-06-01 085443.png"  # 로딩 이미지 파일명
LOADING_IMAGE_SIZE = 80  # 로딩 이미지 크기

# 기타 설정
AUTO_LOGIN_ON_START = True  # 시작 시 자동 로그인 여부
SHOW_EXIT_CONFIRMATION = False  # 종료 시 확인창 표시 여부

# XPath 기반 웹 자동화 설정
# 사용자가 요청한 3단계 XPath 경로
XPATH_STEP1 = '//*[@id="left_area"]/div[4]/ul/li[2]'  # 첫 번째 클릭 경로
XPATH_STEP2 = '//*[@id="left_sub2"]/div[2]/table/tbody/tr[2]/td/div/ul/li[9]'  # 두 번째 클릭 경로  
XPATH_STEP3 = '//*[@id="div_monthly_attend_stat_info"]/section/g-t/g-f/g-th[8]/img'  # 세 번째 클릭 경로

# 웹 자동화 타임아웃 설정
XPATH_CLICK_TIMEOUT = 10  # XPath 요소 대기 시간 (초)
XPATH_STEP_DELAY = 2  # 각 단계 사이 대기 시간 (초)
POPUP_WAIT_TIMEOUT = 5  # 팝업 대기 시간 (초)
XPATH_RETRY_COUNT = 3  # XPath 클릭 재시도 횟수

# 팝업 데이터 추출 설정
POPUP_NUMBER_PATTERN = r'=\s*(\d+\.\d+)'  # "= 26.50" 형태에서 평균 입소자 수 추출
POPUP_SECOND_NUMBER_PATTERN = r'입소자 합계\((\d+)명\)' # "입소자 합계(53명)" 패턴에서 총 입소자 수 추출
POPUP_THIRD_NUMBER_PATTERN = r'반올림한\s*(\d+)'  # "반올림한 27" 패턴에서 반올림된 값 추출
POPUP_TEXT_SELECTORS = [  # 팝업 텍스트를 찾을 CSS/XPath 선택자들
    '//div[contains(text(), "평균 입소자")]',  # "평균 입소자" 텍스트가 포함된 div
    '//div[contains(text(), "계산")]',  # "계산" 텍스트가 포함된 div
    '//div[contains(text(), "값의 반올림한")]',  # "값의 반올림한" 텍스트가 포함된 div
    '//div[contains(text(), "입소자 합계")]',  # "입소자 합계" 텍스트가 포함된 div
    '//div[@class="popup-content"]',  # 일반적인 팝업 컨텐츠
    '//div[@class="modal-body"]',  # 모달 바디
    '//div[@role="dialog"]',  # 다이얼로그 역할의 div
    'div[role="dialog"]',  # CSS 선택자
    '.popup',
    '.modal',
    '.tooltip',
    '//div[contains(@class, "popup")]',
    '//div[contains(@class, "modal")]',
    '//div[contains(@class, "tooltip")]',
    'body'  # 마지막 폴백: 전체 페이지에서 검색
] 

# 외출 관련 설정
OUTING_TABLE_SELECTORS = [
    '#patient_out_list_table',  # 새로운 XPath 기반 ID 선택자
    '//*[@id="patient_out_list_table"]',  # XPath 선택자
    'table[id="patient_out_list_table"]',  # CSS 선택자
    '.patient_out_list_table', 
    'table[id*="out"]',
    'table[class*="out"]'
]

OUTING_COLUMN_INDICES = {
    'date': 1,
    'time': 2,
    'name': 4,
    'destination': 8
}

DEBUG_OUTING_DATA = True
VALIDATE_KOREAN_NAME = True
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 4

OUTING_TIME_PATTERNS = [
    r'\d{1,2}:\d{2}\s*~\s*\d{1,2}:\d{2}',
    r'\d{1,2}:\d{2}-\d{1,2}:\d{2}',
    r'\d{1,2}:\d{2}'
]

# 외출 데이터 수집을 위한 XPath 경로들
OUTING_XPATH_STEP1 = '//*[@id="left_sub2"]/div[1]'
OUTING_XPATH_STEP2 = '//*[@id="left_sub2"]/div[2]/table/tbody/tr[2]/td/div/ul/li[10]'
OUTING_TABLE_XPATH = '//*[@id="patient_out_list_table"]'

# 외출 메뉴 네비게이션 타임아웃 설정
OUTING_NAVIGATION_TIMEOUT = 10
OUTING_NAVIGATION_DELAY = 2

# 다중 사용자 지원 설정
MULTI_USER_ENABLED = True  # 다중 사용자 지원 활성화
SESSION_DIRECTORY = "sessions"  # 세션 저장 디렉토리
SESSION_EXPIRY_DAYS = 30  # 세션 만료 기간 (일)
COOKIE_EXPIRY_HOURS = 168  # 쿠키 만료 기간 (시간, 7일)

# 보안 설정
ENCRYPT_SESSION_DATA = True  # 세션 데이터 암호화 여부
MASTER_KEY_FILE = "master.key"  # 마스터 키 파일명
AUTO_CLEAR_EXPIRED_SESSIONS = True  # 만료된 세션 자동 정리

# 로그인 관련 설정
MAX_LOGIN_ATTEMPTS = 3  # 최대 로그인 시도 횟수
LOGIN_RETRY_DELAY = 5  # 로그인 재시도 대기 시간 (초)
REMEMBER_LOGIN_INFO = True  # 로그인 정보 기억 여부

# 데이터 수집 설정
DATA_COLLECTION_TIMEOUT = 30  # 데이터 수집 타임아웃 (초)
MAX_RETRY_ATTEMPTS = 3  # 최대 재시도 횟수
RETRY_DELAY = 2  # 재시도 대기 시간 (초)

# 외출 데이터 표시 설정
MAX_OUTING_DISPLAY_COUNT = 10  # 최대 외출 데이터 표시 개수
OUTING_SORT_BY_SEQUENCE = True  # 연번순 정렬 여부
OUTING_SORT_DESCENDING = True  # 내림차순 정렬 여부

# 에러 처리 설정
SHOW_DETAILED_ERRORS = False  # 상세 에러 메시지 표시 여부
LOG_ERRORS_TO_FILE = True  # 에러 로그 파일 저장 여부
ERROR_LOG_DIRECTORY = "logs"  # 에러 로그 디렉토리

# 성능 최적화 설정
ENABLE_DEBUG_LOGGING = False  # 디버그 로깅 활성화 (성능에 영향)
OPTIMIZE_MEMORY_USAGE = True  # 메모리 사용량 최적화
CACHE_WEB_ELEMENTS = False  # 웹 요소 캐시 (안정성을 위해 비활성화)

# 사용자 인터페이스 설정
SHOW_USER_INFO = True  # 사용자 정보 표시 여부
SHOW_SESSION_STATUS = True  # 세션 상태 표시 여부
ENABLE_TOOLTIPS = False  # 툴팁 활성화 여부

# 브라우저 관련 설정
BROWSER_TYPE = "edge"  # 기본 브라우저 타입 (edge, chrome)
BROWSER_WINDOW_SIZE = "1920,1080"  # 브라우저 창 크기
BROWSER_USER_AGENT = None  # 사용자 정의 User Agent (None이면 기본값 사용)

# 백업 및 복구 설정
AUTO_BACKUP_SESSIONS = False  # 세션 자동 백업
BACKUP_DIRECTORY = "backups"  # 백업 디렉토리
BACKUP_RETENTION_DAYS = 7  # 백업 보관 기간 (일)

# 네트워크 설정
CONNECTION_TIMEOUT = 30  # 연결 타임아웃 (초)
READ_TIMEOUT = 60  # 읽기 타임아웃 (초)
MAX_REDIRECTS = 5  # 최대 리다이렉트 횟수

# 개발자 설정 (일반 사용자는 수정하지 마세요)
DEVELOPMENT_MODE = False  # 개발 모드 (추가 디버그 정보 표시)
SKIP_CERTIFICATE_VALIDATION = False  # SSL 인증서 검증 건너뛰기 (보안상 권장하지 않음)
FORCE_RECREATE_SESSIONS = False  # 세션 강제 재생성 (테스트용)

# 버전 정보
VERSION = "2.0.0"  # 프로그램 버전
BUILD_DATE = "2025-01-15"  # 빌드 날짜
AUTHOR = "청담재활 IT팀"  # 개발자 정보

# 라이선스 정보
LICENSE = "Private Use Only"  # 라이선스 정보
COPYRIGHT = "© 2025 청담재활. All rights reserved."  # 저작권 정보

def get_session_filename(institution_id, username):
    """
    기관ID와 사용자명으로 고유한 세션 파일명 생성
    
    Args:
        institution_id (str): 기관 ID
        username (str): 사용자명
    
    Returns:
        str: 세션 파일명
    """
    import hashlib
    import os
    
    # 고유 식별자 생성
    combined = f"{institution_id}_{username}"
    session_hash = hashlib.md5(combined.encode()).hexdigest()[:12]
    
    # 세션 디렉토리 확인
    if not os.path.exists(SESSION_DIRECTORY):
        os.makedirs(SESSION_DIRECTORY)
    
    return os.path.join(SESSION_DIRECTORY, f"session_{session_hash}.dat")

def get_backup_filename(institution_id, username):
    """
    백업 파일명 생성
    
    Args:
        institution_id (str): 기관 ID
        username (str): 사용자명
    
    Returns:
        str: 백업 파일명
    """
    import hashlib
    import os
    from datetime import datetime
    
    # 고유 식별자 생성
    combined = f"{institution_id}_{username}"
    session_hash = hashlib.md5(combined.encode()).hexdigest()[:12]
    
    # 백업 디렉토리 확인
    if not os.path.exists(BACKUP_DIRECTORY):
        os.makedirs(BACKUP_DIRECTORY)
    
    # 날짜 포함 백업 파일명
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(BACKUP_DIRECTORY, f"backup_{session_hash}_{date_str}.dat")

def validate_config():
    """
    설정 값 검증
    
    Returns:
        bool: 설정이 유효한지 여부
    """
    errors = []
    
    # 필수 설정 확인
    if not WEBSITE_URL:
        errors.append("WEBSITE_URL이 설정되지 않았습니다.")
    
    if LOGIN_TIMEOUT <= 0:
        errors.append("LOGIN_TIMEOUT은 0보다 커야 합니다.")
    
    if XPATH_RETRY_COUNT <= 0:
        errors.append("XPATH_RETRY_COUNT는 0보다 커야 합니다.")
    
    if SESSION_EXPIRY_DAYS <= 0:
        errors.append("SESSION_EXPIRY_DAYS는 0보다 커야 합니다.")
    
    # 디렉토리 설정 확인
    import os
    try:
        if not os.path.exists(SESSION_DIRECTORY):
            os.makedirs(SESSION_DIRECTORY)
    except Exception as e:
        errors.append(f"SESSION_DIRECTORY 생성 실패: {e}")
    
    if AUTO_BACKUP_SESSIONS:
        try:
            if not os.path.exists(BACKUP_DIRECTORY):
                os.makedirs(BACKUP_DIRECTORY)
        except Exception as e:
            errors.append(f"BACKUP_DIRECTORY 생성 실패: {e}")
    
    if LOG_ERRORS_TO_FILE:
        try:
            if not os.path.exists(ERROR_LOG_DIRECTORY):
                os.makedirs(ERROR_LOG_DIRECTORY)
        except Exception as e:
            errors.append(f"ERROR_LOG_DIRECTORY 생성 실패: {e}")
    
    # 에러가 있으면 출력
    if errors:
        print("❌ 설정 검증 실패:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ 설정 검증 완료")
    return True

def get_config_summary():
    """
    현재 설정 요약 반환
    
    Returns:
        dict: 설정 요약 정보
    """
    return {
        'version': VERSION,
        'build_date': BUILD_DATE,
        'multi_user_enabled': MULTI_USER_ENABLED,
        'headless_mode': HEADLESS_MODE,
        'auto_login': AUTO_LOGIN_ON_START,
        'session_expiry_days': SESSION_EXPIRY_DAYS,
        'max_outing_display': MAX_OUTING_DISPLAY_COUNT,
        'browser_type': BROWSER_TYPE,
        'development_mode': DEVELOPMENT_MODE
    }

def print_config_info():
    """설정 정보 출력"""
    print("=" * 50)
    print("📋 청담재활 출석 관리 시스템 설정 정보")
    print("=" * 50)
    
    summary = get_config_summary()
    for key, value in summary.items():
        print(f"{key:20}: {value}")
    
    print("=" * 50)

# 설정 검증 실행 (모듈 import 시)
if __name__ == "__main__":
    print_config_info()
    validate_config()
else:
    # 모듈로 import될 때 자동 검증
    validate_config()