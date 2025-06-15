"""
상수 정의 모듈
"""

class UIConstants:
    """UI 관련 상수"""
    
    # 창 크기
    MIN_WIDTH = 350
    MIN_HEIGHT = 800
    
    # 폰트 크기
    FONT_SIZE_EXTRA_LARGE = 48
    FONT_SIZE_LARGE = 28
    FONT_SIZE_MEDIUM = 18
    FONT_SIZE_NORMAL = 16
    FONT_SIZE_SMALL = 14
    FONT_SIZE_TINY = 12
    FONT_SIZE_MICRO = 10
    
    # 색상
    COLOR_SUCCESS = "#28a745"
    COLOR_ERROR = "#dc3545"
    COLOR_WARNING = "#ff8c00"
    COLOR_INFO = "#17a2b8"
    COLOR_SECONDARY = "#6c757d"
    COLOR_PRIMARY = "#0066CC"
    COLOR_DANGER = "#8b0000"
    
    # 새로고침 간격 (초)
    REFRESH_INTERVALS = [10, 30, 60, 120, 300]
    DEFAULT_REFRESH_INTERVAL = 30
    
    # 레이아웃
    PADDING_LARGE = 15
    PADDING_MEDIUM = 10
    PADDING_SMALL = 8
    PADDING_TINY = 5

class SystemConstants:
    """시스템 관련 상수"""
    
    # 타임아웃
    DEFAULT_TIMEOUT = 10
    PAGE_LOAD_TIMEOUT = 30
    ELEMENT_WAIT_TIMEOUT = 5
    
    # 재시도
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    # 파일명
    COOKIE_FILE = "cookies.pkl"
    LOG_DIR = "logs"
