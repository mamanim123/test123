#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
케어포 출석 상태 모니터 - 외출 기능 추가 완전판
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, timedelta
import threading
import time
from data_collector import CareforDataCollector
import os
import sys
import pickle

# 한글 인코딩 강제 설정
if sys.platform.startswith('win'):
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'Korean_Korea.949')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
        except:
            pass

# 환경변수 설정
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# 현대적인 테마 설정
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class SimpleAttendanceMonitor:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("청담재활")
        self.root.minsize(350, 800)

        # 현재 날짜
        self.current_date = datetime.now().date()

        # 데이터 수집기
        self.collector = None
        self.is_logged_in = False
        self.attendance_data = {}
        self.outing_data = {}  # 외출 데이터 저장
        self.staff_absence_data = {}  # 직원 휴무 데이터 저장

        # 자동새로고침 관련 변수
        self.auto_refresh_enabled = False
        self.auto_refresh_interval = 30
        self.auto_refresh_timer = None

        # 헤드리스 모드 관련 변수
        self.headless_mode = False

        # 로딩 상태 관련 변수
        self.is_loading_data = False
        
        # 현재 표시 모드 (출석 또는 외출)
        self.current_mode = "attendance"  # "attendance", "outing", "staff"

        # GUI 구성
        self.create_widgets()
        self.setup_layout()

        # 자동 로그인 시도
        self.auto_login()

    def create_widgets(self):
        """위젯 생성"""
        size_reduction_factor = 0.9

        # 1. 먼저 모든 프레임들을 생성
        self.main_frame = ctk.CTkFrame(self.root)
        self.bottom_frame = ctk.CTkFrame(self.root)  # 하단 프레임 먼저 생성
        self.date_nav_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame = ctk.CTkFrame(self.main_frame, height=40)
        self.status_frame.pack_propagate(False)
        self.attendance_header_frame = ctk.CTkFrame(self.main_frame)
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame)

        # 2. 날짜 네비게이션 버튼들
        self.prev_button = ctk.CTkButton(
            self.date_nav_frame,
            text="◀ 이전",
            width=int(80 * size_reduction_factor),
            height=int(40 * size_reduction_factor),
            command=self.prev_date,
            font=ctk.CTkFont(size=14, weight="bold")
        )

        self.date_label = ctk.CTkLabel(
            self.date_nav_frame,
            text=self.current_date.strftime("%Y년 %m월 %d일"),
            font=ctk.CTkFont(size=18, weight="bold")
        )

        self.next_button = ctk.CTkButton(
            self.date_nav_frame,
            text="다음 ▶",
            width=int(80 * size_reduction_factor),
            height=int(40 * size_reduction_factor),
            command=self.next_date,
            font=ctk.CTkFont(size=14, weight="bold")
        )

        self.refresh_button = ctk.CTkButton(
            self.date_nav_frame,
            text="새로고침",
            width=int(100 * size_reduction_factor),
            height=int(40 * size_reduction_factor),
            command=self.refresh_data,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745"
        )

        # 3. 상태 표시 관련
        self.loading_text_label = ctk.CTkLabel(
            self.status_frame,
            text="🔄 데이터 조회 중...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FF4500"
        )
        self.loading_text_label.place_forget()

        self.stats_label = ctk.CTkLabel(
            self.status_frame,
            text="전체: 0명, 출석: 0명, 결석: 0명\n미이용: 0명, 일정없음: 0명, 휴무: 0명",
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center"  # 중앙 정렬
        )
        self.stats_label.place(relx=0.5, rely=0.5, anchor="center")

        # 4. 출석상태 헤더 관련
        self.attendance_label = ctk.CTkLabel(
            self.attendance_header_frame,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )

        self.residents_value_label = ctk.CTkLabel(
            self.attendance_header_frame,
            text="",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#0066CC"
        )

        self.popup_value_label = ctk.CTkLabel(
            self.attendance_header_frame,
            text="",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#ff4500",
            anchor="w"
        )

        self.headless_button = ctk.CTkButton(
            self.attendance_header_frame,
            text="숨김 OFF",
            command=self.toggle_headless_mode,
            width=70,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#6c757d"
        )

        # 5. 하단 버튼들 (bottom_frame에 배치)
        self.login_button = ctk.CTkButton(
            self.bottom_frame,
            text="🔐 로그인",
            command=self.on_login_button_click,
            width=70,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#dc3545"
        )

        self.attendance_mode_button = ctk.CTkButton(
            self.bottom_frame,
            text="📝 출석",
            command=lambda: self.switch_to_mode("attendance"),
            width=60,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color="#28a745"
        )

        self.outing_mode_button = ctk.CTkButton(
            self.bottom_frame,
            text="🚶 외출",
            command=lambda: self.switch_to_mode("outing"),
            width=60,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color="#6c757d"
        )

        self.staff_mode_button = ctk.CTkButton(
            self.bottom_frame,
            text="👨‍🏫 휴무",
            command=lambda: self.switch_to_mode("staff"),
            width=60,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color="#6c757d"
        )

        self.exit_button = ctk.CTkButton(
            self.bottom_frame,
            text="❌ 종료",
            width=int(80 * size_reduction_factor),
            height=int(35 * size_reduction_factor),
            command=self.on_closing,
            font=ctk.CTkFont(size=12),
            fg_color="#dc3545"
        )

        # 6. 자동새로고침 관련 (bottom_frame에 배치)
        self.auto_refresh_button = ctk.CTkButton(
            self.bottom_frame,
            text="자동 OFF",
            command=self.toggle_auto_refresh,
            width=70,
            height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#6c757d"
        )

        self.interval_label = ctk.CTkLabel(
            self.bottom_frame,
            text="간격:",
            font=ctk.CTkFont(size=12, weight="bold")
        )

        self.interval_var = tk.StringVar(value="30초")
        self.interval_combo = ctk.CTkComboBox(
            self.bottom_frame,
            values=["10초", "30초", "60초", "120초", "300초"],
            variable=self.interval_var,
            command=self.update_refresh_interval,
            width=60,
            height=30,
            font=ctk.CTkFont(size=10)
        )

        self.auto_refresh_status = ctk.CTkLabel(
            self.bottom_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="#6c757d"
        )
    def setup_layout(self):
        """레이아웃 설정"""
        # 메인 프레임
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # 날짜 네비게이션
        self.date_nav_frame.pack(fill="x", pady=(0, 10))
        self.prev_button.pack(side="left", padx=10)
        self.date_label.pack(side="left", expand=True)
        self.next_button.pack(side="right", padx=10)

        # 상태 표시 프레임
        self.status_frame.pack(fill="x", pady=(0, 10))
        # 통계 라벨 위치 설정 (빠져있던 부분)
        self.stats_label.place(relx=0.5, rely=0.5, anchor="center")

        # 출석상태 헤더 프레임
        self.attendance_header_frame.pack(fill="x", pady=(0, 3))
        self.attendance_label.pack(side="left", padx=10)
        self.popup_value_label.pack(side="left", padx=(5, 0))
        self.residents_value_label.pack(side="left", padx=(5, 0))

        # 새로고침 버튼과 헤드리스 버튼만 헤더에 유지
        self.headless_button.pack(side="right", padx=(10, 5))
        self.refresh_button.pack(side="right", padx=(5, 10))

        # 출석 상태 스크롤 영역
        self.scroll_frame.pack(fill="both", expand=True, pady=(0, 8))

        # 하단 버튼 프레임
        self.bottom_frame.pack(fill="x", pady=(8, 0))
        self.login_button.pack(side="left", padx=5, pady=5)
        self.attendance_mode_button.pack(side="left", padx=2, pady=5)
        self.outing_mode_button.pack(side="left", padx=2, pady=5)
        self.staff_mode_button.pack(side="left", padx=2, pady=5)

        # 자동새로고침 관련 컨트롤들을 오른쪽에 배치
        self.exit_button.pack(side="right", padx=10, pady=5)
        self.auto_refresh_status.pack(side="right", padx=(5, 10), pady=5)
        self.interval_combo.pack(side="right", padx=2, pady=5)
        self.interval_label.pack(side="right", padx=2, pady=5)
        self.auto_refresh_button.pack(side="right", padx=(10, 5), pady=5)

        # 스크롤 감도 개선
        self.setup_scroll_sensitivity()

    def setup_scroll_sensitivity(self):
        """스크롤 감도 설정"""
        def on_mousewheel(event):
            scroll_speed_multiplier = 30
            import platform
            if platform.system() == "Windows":
                # 휠 한 번에 3-4줄 정도 움직이도록 설정
                scroll_amount = int(-1 * (event.delta / 40))  # 40으로 나누어서 적당히 빠르게
            else:
                # 다른 OS
                scroll_amount = int(-1 * event.delta * 8)  # 적당한 속도
            
            # 스크롤 실행
            self.scroll_frame._parent_canvas.yview_scroll(scroll_amount, "units")

        # 스크롤 이벤트 바인딩
        self.scroll_frame.bind("<MouseWheel>", on_mousewheel)
        self.scroll_frame._parent_canvas.bind("<MouseWheel>", on_mousewheel)

        # 마우스 포커스 설정
        def on_enter(event):
            self.scroll_frame._parent_canvas.focus_set()

        def on_leave(event):
            self.root.focus_set()

        self.scroll_frame.bind("<Enter>", on_enter)
        self.scroll_frame.bind("<Leave>", on_leave)

        # 키보드 스크롤도 추가 (상하 화살표키로 스크롤)
        def on_key_press(event):
            if event.keysym == "Up":
                self.scroll_frame._parent_canvas.yview_scroll(-5, "units")
            elif event.keysym == "Down":
                self.scroll_frame._parent_canvas.yview_scroll(5, "units")
            elif event.keysym == "Page_Up":
                self.scroll_frame._parent_canvas.yview_scroll(-10, "units")
            elif event.keysym == "Page_Down":
                self.scroll_frame._parent_canvas.yview_scroll(10, "units")

        self.scroll_frame.bind("<Key>", on_key_press)
        self.scroll_frame.focus_set()

    def prev_date(self):
        """이전 날짜로 이동"""
        self.current_date -= timedelta(days=1)
        self.update_date_display()

    def next_date(self):
        """다음 날짜로 이동"""
        self.current_date += timedelta(days=1)
        self.update_date_display()

    def update_date_display(self):
        """날짜 표시 업데이트"""
        date_str = self.current_date.strftime("%Y년 %m월 %d일")
        weekday = ["월", "화", "수", "목", "금", "토", "일"][self.current_date.weekday()]
        self.date_label.configure(text=f"{date_str} ({weekday})")

    def switch_to_mode(self, mode):
        """모드 전환 통합 함수"""
        # 기존 모든 버튼 색상 초기화
        self.attendance_mode_button.configure(fg_color="#6c757d")
        self.outing_mode_button.configure(fg_color="#6c757d")
        self.staff_mode_button.configure(fg_color="#6c757d")
        
        if mode == "attendance":
            self.current_mode = "attendance"
            self.attendance_mode_button.configure(fg_color="#28a745")
            self.update_attendance_display()
        elif mode == "outing":
            self.current_mode = "outing"
            self.outing_mode_button.configure(fg_color="#17a2b8")
            self.update_outing_display()
        elif mode == "staff":
            self.current_mode = "staff"
            self.staff_mode_button.configure(fg_color="#6f42c1")
            self.update_staff_absence_display()

    def refresh_data(self):
        """데이터 새로고침 - 현재 모드에 따라 적절한 데이터만 새로고침"""
        if not self.is_logged_in:
            self.auto_login()
            return

        if self.is_loading_data:
            return

        # 현재 모드에 따라 해당 데이터만 새로고침
        if self.current_mode == "attendance":
            self.load_attendance_data()
        elif self.current_mode == "outing":
            self.load_outing_data()
        elif self.current_mode == "staff":
            self.load_staff_absence_data()
        else:
            # 전체 새로고침
            self.load_all_initial_data()

    def load_outing_data(self):
        """외출 데이터 로드"""
        if not self.is_logged_in:
            messagebox.showwarning("로그인 필요", "먼저 로그인해주세요.")
            return

        if self.is_loading_data:
            return

        def load_thread():
            self.root.after(0, self.start_loading_animation)
            try:
                date_str = self.current_date.strftime("%Y-%m-%d")
                print(f"외출 데이터 로딩 시작: {date_str}")

                # 외출 데이터 수집
                result = self.collector.get_outing_data(date_str)
                print(f"외출 데이터 수집 완료: {result is not None}")
                
                if result and result.get('success'):
                    self.outing_data = result
                    self.root.after(0, self.update_outing_display)
                else:
                    self.root.after(0, self.clear_outing_display)

            except Exception as e:
                print(f"외출 데이터 로드 오류: {e}")
                import traceback
                traceback.print_exc()
                self.root.after(0, self.clear_outing_display)
            finally:
                self.root.after(0, self.stop_loading_animation)

        threading.Thread(target=load_thread, daemon=True).start()

    def update_outing_display(self):
        """외출 상태 표시 업데이트"""
        # 기존 위젯 제거
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.outing_data or not self.outing_data.get('success'):
            self.clear_outing_display()
            return

        # 외출 데이터 표시
        outing_list = self.outing_data.get('outing_list', [])
        
        if not outing_list:
            no_data_label = ctk.CTkLabel(
                self.scroll_frame,
                text="📅 외출 예정자가 없습니다.",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#6c757d"
            )
            no_data_label.pack(pady=20)
            
            # 통계 업데이트
            self.stats_label.configure(text=f"외출 예정: {len(outing_list)}명\n날짜: {self.current_date.strftime('%m월 %d일')}")
            return

        # 외출 헤더
        outing_header = ctk.CTkLabel(
            self.scroll_frame,
            text=f"🚶 외출 예정 ({len(outing_list)}명)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#17a2b8"
        )
        outing_header.pack(anchor="w", padx=8, pady=(5, 10))

        # 외출 목록 표시 (연번 역순으로 이미 정렬됨)
        for i, outing_info in enumerate(outing_list):
            self.create_outing_widget(outing_info, i)

        # 통계 업데이트
        self.stats_label.configure(text=f"외출 예정: {len(outing_list)}명 | 날짜: {self.current_date.strftime('%m월 %d일')}")

    def create_outing_widget(self, outing_info, index):
        """외출 정보 위젯 생성"""
        outing_frame = ctk.CTkFrame(self.scroll_frame)
        outing_frame.pack(fill="x", padx=8, pady=3)

        # 외출 정보 표시
        name = outing_info.get('name', '미확인')
        date = outing_info.get('date', '미확인')
        time = outing_info.get('time', '미확인')
        destination = outing_info.get('destination', '미확인')

        # 연번과 이름을 함께 표시 (연번이 있으면 사용, 없으면 순서)
        연번 = outing_info.get('연번', 0)
        if 연번 > 0:
            name_text = f"[{연번}] 👤 {name}"
        else:
            name_text = f"{index + 1}. 👤 {name}"
        
        # 이름 라벨 (더 큰 폰트)
        name_label = ctk.CTkLabel(
            outing_frame,
            text=name_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2c3e50",
            anchor="w"
        )
        name_label.pack(anchor="w", padx=10, pady=(8, 2))

        # 세부 정보 라벨
        details_text = f"📅 {date} | ⏰ {time}"
        details_label = ctk.CTkLabel(
            outing_frame,
            text=details_text,
            font=ctk.CTkFont(size=14),
            text_color="#34495e",
            anchor="w"
        )
        details_label.pack(anchor="w", padx=10, pady=(0, 2))

        # 목적지 라벨 (별도 라인)
        destination_text = f"📍 목적지: {destination}"
        destination_label = ctk.CTkLabel(
            outing_frame,
            text=destination_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e67e22",
            anchor="w"
        )
        destination_label.pack(anchor="w", padx=10, pady=(0, 8))

    def clear_outing_display(self):
        """외출 상태 표시 초기화"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.stats_label.configure(text="외출 데이터를 불러올 수 없습니다.")

        no_data_label = ctk.CTkLabel(
            self.scroll_frame,
            text="❌ 외출 데이터를 불러올 수 없습니다.",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#dc3545"
        )
        no_data_label.pack(pady=20)

        # 재시도 버튼 추가
        retry_button = ctk.CTkButton(
            self.scroll_frame,
            text="🔄 다시 시도",
            command=self.load_outing_data,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#17a2b8"
        )
        retry_button.pack(pady=10)

    def start_loading_animation(self):
        """로딩 애니메이션 시작"""
        if self.is_loading_data:
            return

        self.is_loading_data = True
        print("로딩 애니메이션 시작")
        
        # 버튼들 비활성화
        self.refresh_button.configure(state="disabled")
        self.auto_refresh_button.configure(state="disabled")
        self.interval_combo.configure(state="disabled")
        self.login_button.configure(state="disabled")
        self.attendance_mode_button.configure(state="disabled")
        self.outing_mode_button.configure(state="disabled")
        self.staff_mode_button.configure(state="disabled")
        
        # 현재 모드에 따라 로딩 메시지 변경
        if self.current_mode == "outing":
            self.loading_text_label.configure(text="🚶 외출 데이터 조회 중...")
        elif self.current_mode == "staff":
            self.loading_text_label.configure(text="👨‍🏫 직원 휴무 데이터 조회 중...")
        else:
            self.loading_text_label.configure(text="🔄 출석 데이터 조회 중...")
            
        self.loading_text_label.place(relx=0.5, rely=0.5, anchor="center")
        self.root.update_idletasks()

    def stop_loading_animation(self):
        """로딩 애니메이션 중지"""
        if not self.is_loading_data:
            return
            
        self.is_loading_data = False
        print("로딩 애니메이션 중지")
        
        # 버튼들 다시 활성화
        self.refresh_button.configure(state="normal")
        self.auto_refresh_button.configure(state="normal")
        self.interval_combo.configure(state="normal")
        self.login_button.configure(state="normal")
        self.attendance_mode_button.configure(state="normal")
        self.outing_mode_button.configure(state="normal")
        self.staff_mode_button.configure(state="normal")
        
        self.loading_text_label.place_forget()
        self.root.update_idletasks()

    def auto_login(self):
        """자동 로그인"""
        def login_thread():
            try:
                print("🚀 자동 로그인 시작...")
                self.root.update_idletasks()

                self.collector = CareforDataCollector(headless=self.headless_mode)
                self.collector.init_driver()

                success = self.collector.login()

                if success:
                    print("✅ 자동 로그인 성공!")
                    self.is_logged_in = True
                    self.root.after(0, self.update_login_button_text)
                    # 초기 로딩 시 모든 데이터 수집
                    self.load_all_initial_data()

                else:
                    print("❌ 자동 로그인 실패")
                    self.is_logged_in = False
                    self.root.after(0, self.update_login_button_text)
                    self.root.after(0, lambda: messagebox.showwarning(
                        "로그인 필요", 
                        "자동 로그인에 실패했습니다.\n'🔐 로그인' 버튼을 클릭하여 수동으로 로그인해주세요."
                    ))

            except Exception as e:
                print(f"❌ 자동 로그인 오류: {e}")
                self.is_logged_in = False
                self.root.after(0, self.update_login_button_text)

        threading.Thread(target=login_thread, daemon=True).start()

    def load_all_initial_data(self):
        """초기 로딩 시 모든 데이터 수집"""
        def initial_load_thread():
            self.root.after(0, self.start_loading_animation)
            try:
                date_str = self.current_date.strftime("%Y-%m-%d")
                print(f"📊 초기 데이터 수집 시작: {date_str}")

                # 1. 출석 데이터 수집
                print("🔄 출석 데이터 수집 중...")
                attendance_result = self.collector.get_attendance_data_with_popup_info(date_str)
                
                if attendance_result and attendance_result.get('success'):
                    self.attendance_data = attendance_result
                    print("✅ 출석 데이터 수집 완료")
                else:
                    print("❌ 출석 데이터 수집 실패")
                    self.attendance_data = {}

                # 2. 외출 데이터 수집
                print("🔄 외출 데이터 수집 중...")
                outing_result = self.collector.get_outing_data(date_str)
                
                if outing_result and outing_result.get('success'):
                    self.outing_data = outing_result
                    print("✅ 외출 데이터 수집 완료")
                else:
                    print("❌ 외출 데이터 수집 실패")
                    self.outing_data = {}

                # 3. 직원 휴무 데이터 수집
                print("🔄 직원 휴무 데이터 수집 중...")
                staff_result = self.collector.get_staff_absence_data(date_str)

                if staff_result and staff_result.get('success'):
                    self.staff_absence_data = staff_result
                    print("✅ 직원 휴무 데이터 수집 완료")
                else:
                    print("❌ 직원 휴무 데이터 수집 실패")
                    self.staff_absence_data = {}

                # 3. 현재 모드에 따라 화면 업데이트
                if self.current_mode == "attendance":
                    self.root.after(0, self.update_attendance_display)
                elif self.current_mode == "outing":
                    self.root.after(0, self.update_outing_display)
                elif self.current_mode == "staff":
                    self.root.after(0, self.update_staff_absence_display)

            except Exception as e:
                print(f"❌ 초기 데이터 로딩 오류: {e}")
                import traceback
                traceback.print_exc()
            finally:
                self.root.after(0, self.stop_loading_animation)

        threading.Thread(target=initial_load_thread, daemon=True).start()

    def manual_login(self):
        """수동 로그인"""
        def manual_login_thread():
            try:
                print("🔧 수동 로그인 시작...")
                self.root.update_idletasks()

                # 브라우저가 없으면 초기화
                if not hasattr(self, 'collector') or self.collector is None:
                    print(f"🔍 브라우저 초기화 중... (헤드리스: {self.headless_mode})")
                    self.collector = CareforDataCollector(headless=self.headless_mode)
                    self.collector.init_driver()
                
                # 강제로 새로운 로그인 정보 입력받기
                login_info = self.collector.login_manager.prompt_login_info(force_new=True)
                
                if login_info:
                    print(f"🔑 로그인 시도: {login_info['institution_id']}, {login_info['username']}")
                    
                    # 기존 로그인 방식 사용
                    success = self.collector.login()
                    
                    if success:
                        # 로그인 성공
                        self.is_logged_in = True
                        print("✅ 수동 로그인 성공!")
                        
                        # 쿠키 저장
                        try:
                            with open("cookies.pkl", "wb") as f:
                                pickle.dump(self.collector.driver.get_cookies(), f)
                            print("💾 로그인 정보 저장 완료")
                        except Exception as e:
                            print(f"⚠️ 쿠키 저장 실패: {e}")
                        
                        # UI 업데이트
                        self.root.after(0, self.update_login_button_text)
                        
                        # 성공 메시지 표시
                        self.root.after(0, lambda: messagebox.showinfo(
                            "로그인 성공", 
                            "로그인이 완료되었습니다!\n다음부터는 자동으로 로그인됩니다."
                        ))
                        
                        # 현재 모드에 따라 데이터 로드
                        if self.current_mode == "attendance":
                            self.load_attendance_data()
                        else:
                            self.load_outing_data()
                        
                    else:
                        # 로그인 실패
                        print("❌ 수동 로그인 실패")
                        self.root.after(0, lambda: messagebox.showerror(
                            "로그인 실패", 
                            "로그인에 실패했습니다.\n입력한 정보를 확인해주세요."
                        ))
                        
                else:
                    print("❌ 로그인 정보 입력이 취소되었습니다.")
                    
            except Exception as e:
                print(f"❌ 수동 로그인 오류: {e}")
                import traceback
                traceback.print_exc()
                self.root.after(0, lambda: messagebox.showerror(
                    "오류", 
                    f"로그인 중 오류가 발생했습니다:\n{str(e)}"
                ))

        threading.Thread(target=manual_login_thread, daemon=True).start()

    def on_login_button_click(self):
        """로그인 버튼 클릭 처리"""
        if self.is_logged_in:
            result = messagebox.askyesno(
                "로그인 상태", 
                "이미 로그인되어 있습니다.\n새로운 계정으로 다시 로그인하시겠습니까?"
            )
            if result:
                if hasattr(self, 'collector') and self.collector:
                    self.collector.login_manager.clear_login_info()
                self.manual_login()
        else:
            self.manual_login()

    def update_login_button_text(self):
        """로그인 상태에 따라 버튼 텍스트 변경"""
        if self.is_logged_in:
            self.login_button.configure(
                text="🔓 로그인됨", 
                fg_color="#28a745"
            )
        else:
            self.login_button.configure(
                text="🔐 로그인", 
                fg_color="#dc3545"
            )

    def load_attendance_data(self):
        """출석 데이터 로드"""
        if not self.is_logged_in:
            return

        if self.is_loading_data:
            return

        def load_thread():
            self.root.after(0, self.start_loading_animation)
            try:
                date_str = self.current_date.strftime("%Y-%m-%d")
                print(f"출석 데이터 로딩 시작: {date_str}")

                # GUI용 데이터 수집 (팝업 정보 포함, 브라우저 세션 유지)
                result = self.collector.get_attendance_data_with_popup_info(date_str)
                print(f"출석 데이터 수집 완료: {result is not None}")
                
                # 결과에 따라 UI 업데이트
                if result and result.get('success'):
                    self.attendance_data = result
                    self.root.after(0, self.update_attendance_display)
                else:
                    self.root.after(0, self.clear_attendance_display)

            except Exception as e:
                print(f"출석 데이터 로드 오류: {e}")
                import traceback
                traceback.print_exc()
                self.root.after(0, self.clear_attendance_display)
            finally:
                self.root.after(0, self.stop_loading_animation)

        threading.Thread(target=load_thread, daemon=True).start()

    def update_attendance_display(self):
        """출석 상태 표시 업데이트"""
        # 기존 위젯 제거
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.attendance_data or not self.attendance_data.get('success'):
            self.clear_attendance_display()
            return

        # 주말 메시지 표시
        if 'note' in self.attendance_data:
            note_label = ctk.CTkLabel(
                self.scroll_frame,
                text=f"ℹ️ {self.attendance_data['note']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ff8c00"
            )
            note_label.pack(anchor="w", padx=8, pady=(5, 2))

        comparison = self.attendance_data.get('comparison', {})

        # 통계 업데이트
        total = comparison.get('total_patients', 0)
        attended = comparison.get('attended', 0)
        absent = comparison.get('absent', 0)

        # 출석 기록이 없는 수급자들 (일정없음) 계산
        all_patients = self.attendance_data.get('patients', [])
        attendance_data = self.attendance_data.get('attendance', [])
        attendance_names = [d['name'] for d in attendance_data]
        no_schedule_count = 0

        for patient in all_patients:
            patient_name = patient['name'] if isinstance(patient, dict) else patient
            if patient_name not in attendance_names:
                no_schedule_count += 1

        # 상세 통계 계산 - 미이용과 결석 분리
        unused_count = len([d for d in attendance_data if d['status'] == '미이용'])
        absent_count = len([d for d in attendance_data if d['status'] in ['결석', '불참']])
        
        # 직원 휴무 정보 추가
        staff_absence_count = 0
        if hasattr(self, 'staff_absence_data') and self.staff_absence_data.get('success'):
            staff_absence_list = self.staff_absence_data.get('absence_list', [])
            staff_absence_count = len(staff_absence_list)

        # 팝업 데이터 값 추출 및 표시 (26.50 등의 값)
        popup_average = self.attendance_data.get('popup_data', '')  # 평균 입소자 수
        popup_total = self.attendance_data.get('total_residents', '')  # 총 입소자 수
        
        if popup_average:
            self.popup_value_label.configure(text=popup_average)
            if popup_total:
                self.residents_value_label.configure(text=f"({popup_total}명)")
            else:
                self.residents_value_label.configure(text="")
        else:
            self.popup_value_label.configure(text="")
            self.residents_value_label.configure(text="")
        
        # 상단 통계를 2줄로 분리하여 표시
        # 첫 번째 줄: 기본 출석 통계
        first_line = f"전체: {total}명, 출석: {attended}명, 결석: {absent_count}명"

        # 두 번째 줄: 세부 상태 통계
        second_line = f"미이용: {unused_count}명, 일정없음: {no_schedule_count}명"
        if staff_absence_count > 0:
            second_line += f", 휴무: {staff_absence_count}명"

        # 2줄로 결합
        combined_stats = f"{first_line}\n{second_line}"

        self.stats_label.configure(text=combined_stats)

        # 출석 데이터가 있는 경우에만 상세 표시
        if attendance_data:
            # 출석 상태별 분류
            attended_list = [d for d in attendance_data if d['status'] in ['출석', '참석']]
            absent_list = [d for d in attendance_data if d['status'] in ['결석', '불참']]
            unused_list = [d for d in attendance_data if d['status'] == '미이용']
            late_list = [d for d in attendance_data if d['status'] == '지각']
            early_leave_list = [d for d in attendance_data if d['status'] == '조퇴']
            outing_list = [d for d in attendance_data if d['status'] == '외출']

            # 출석자 표시
            if attended_list:
                attended_header = ctk.CTkLabel(
                    self.scroll_frame,
                    text=f"✅ 출석 ({len(attended_list)}명)",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#003d82"
                )
                attended_header.pack(anchor="w", padx=8, pady=(5, 2))
                self.create_grid_layout(attended_list, "#003d82", "출석")

            # 지각자 표시
            if late_list:
                late_header = ctk.CTkLabel(
                    self.scroll_frame,
                    text=f"⏰ 지각 ({len(late_list)}명)",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#ff8c00"
                )
                late_header.pack(anchor="w", padx=8, pady=(8, 2))
                self.create_grid_layout(late_list, "#ff8c00", "지각")

            # 조퇴자 표시
            if early_leave_list:
                early_leave_header = ctk.CTkLabel(
                    self.scroll_frame,
                    text=f"🏃 조퇴 ({len(early_leave_list)}명)",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#8b008b"
                )
                early_leave_header.pack(anchor="w", padx=8, pady=(8, 2))
                self.create_grid_layout(early_leave_list, "#8b008b", "조퇴")

            # 외출자 표시
            if outing_list:
                outing_header = ctk.CTkLabel(
                    self.scroll_frame,
                    text=f"🏃‍♂️ 외출 ({len(outing_list)}명)",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#008b8b"
                )
                outing_header.pack(anchor="w", padx=8, pady=(8, 2))
                self.create_grid_layout(outing_list, "#008b8b", "외출")

            # 결석자 표시
            if absent_list:
                absent_header = ctk.CTkLabel(
                    self.scroll_frame,
                    text=f"❌ 결석 ({len(absent_list)}명)",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#8b0000"
                )
                absent_header.pack(anchor="w", padx=8, pady=(8, 2))
                self.create_grid_layout(absent_list, "#8b0000", "결석")

            # 미이용자 표시
            if unused_list:
                unused_header = ctk.CTkLabel(
                    self.scroll_frame,
                    text=f"⚪ 미이용 ({len(unused_list)}명)",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#006400"
                )
                unused_header.pack(anchor="w", padx=8, pady=(8, 2))
                self.create_grid_layout(unused_list, "#006400", "미이용")

        # 일정없음 표시
        no_schedule_list = []
        for patient in all_patients:
            patient_name = patient['name'] if isinstance(patient, dict) else patient
            if patient_name not in attendance_names:
                no_schedule_list.append({'name': patient_name, 'status': '일정없음'})

        if no_schedule_list:
            no_schedule_header = ctk.CTkLabel(
                self.scroll_frame,
                text=f"📅 일정없음 ({len(no_schedule_list)}명)",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#2f2f2f"
            )
            no_schedule_header.pack(anchor="w", padx=8, pady=(8, 2))
            self.create_grid_layout(no_schedule_list, "#2f2f2f", "일정없음")

        # 직원 휴무 정보 표시
        if hasattr(self, 'staff_absence_data') and self.staff_absence_data.get('success'):
            staff_absence_list = self.staff_absence_data.get('absence_list', [])
            
            if staff_absence_list:
                # 휴무 헤더
                staff_absence_header = ctk.CTkLabel(
                    self.scroll_frame,
                    text=f"🔴 휴무 ({len(staff_absence_list)}명)",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#DC143C"  # 진한 빨간색
                )
                staff_absence_header.pack(anchor="w", padx=8, pady=(8, 2))

                # 휴무 직원 이름들 표시
                staff_names = [staff['name'] for staff in staff_absence_list]
                names_text = ", ".join(staff_names)
                
                staff_names_frame = ctk.CTkFrame(self.scroll_frame)
                staff_names_frame.pack(fill="x", padx=8, pady=(0, 5))

                staff_names_label = ctk.CTkLabel(
                    staff_names_frame,
                    text=f"👤 {names_text}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#DC143C",  # 진한 빨간색
                    anchor="w"
                )
                staff_names_label.pack(fill="both", expand=True, padx=6, pady=3)    

    def create_grid_layout(self, person_list, color, status_text):
        """세로 두 열 레이아웃으로 수급자 목록 표시"""
        if not person_list:
            return
            
        grid_container = ctk.CTkFrame(self.scroll_frame)
        grid_container.pack(fill="x", padx=8, pady=(0, 5))
        
        columns = 2
        
        for i, person in enumerate(person_list):
            col = i % columns
            row = i // columns
                
            person_widget = self.create_person_widget(person, color, status_text, grid_container)
            person_widget.grid(row=row, column=col, padx=2, pady=1, sticky="ew")
        
        for col in range(columns):
            grid_container.grid_columnconfigure(col, weight=1)
        
        return grid_container

    def create_person_widget(self, person, color, status_text, parent_frame=None):
        """개별 수급자 위젯 생성"""
        if parent_frame is None:
            parent_frame = self.scroll_frame
            
        person_frame = ctk.CTkFrame(parent_frame, height=30)
        person_frame.pack_propagate(False)
        
        display_text = f"{person['name']} → {status_text}"
        
        name_status_label = ctk.CTkLabel(
            person_frame,
            text=display_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color,
            anchor="w"
        )
        name_status_label.pack(fill="both", expand=True, padx=6, pady=3)
        
        return person_frame

    def clear_attendance_display(self):
        """출석 상태 표시 초기화"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.popup_value_label.configure(text="")
        self.residents_value_label.configure(text="")
        self.stats_label.configure(text="전체: 0명, 출석: 0명, 결석: 0명, 미이용: 0명, 일정없음: 0명, 휴무: 0명")

        no_data_label = ctk.CTkLabel(
            self.scroll_frame,
            text="❌ 출석 데이터를 불러올 수 없습니다.",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#dc3545"
        )
        no_data_label.pack(pady=20)

    def toggle_auto_refresh(self):
        """자동새로고침 토글"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled

        if self.auto_refresh_enabled:
            self.auto_refresh_button.configure(
                text="자동 ON",
                fg_color="#28a745"
            )
            self.start_auto_refresh()
        else:
            self.auto_refresh_button.configure(
                text="자동 OFF",
                fg_color="#6c757d"
            )
            self.stop_auto_refresh()

    def update_refresh_interval(self, value):
        """새로고침 간격 업데이트"""
        interval_map = {
            "10초": 10,
            "30초": 30,
            "60초": 60,
            "120초": 120,
            "300초": 300
        }
        self.auto_refresh_interval = interval_map.get(value, 30)

        if self.auto_refresh_enabled:
            self.stop_auto_refresh()
            self.start_auto_refresh()

    def start_auto_refresh(self):
        """자동새로고침 시작"""
        if self.auto_refresh_timer:
            self.root.after_cancel(self.auto_refresh_timer)

        def auto_refresh_task():
            if self.auto_refresh_enabled:
                self.refresh_data()
                self.auto_refresh_timer = self.root.after(
                    self.auto_refresh_interval * 1000,
                    auto_refresh_task
                )

        self.auto_refresh_timer = self.root.after(
            self.auto_refresh_interval * 1000,
            auto_refresh_task
        )

    def stop_auto_refresh(self):
        """자동새로고침 중지"""
        if self.auto_refresh_timer:
            self.root.after_cancel(self.auto_refresh_timer)
            self.auto_refresh_timer = None

    def toggle_headless_mode(self):
        """헤드리스 모드 토글"""
        self.headless_mode = not self.headless_mode

        if self.headless_mode:
            self.headless_button.configure(
                text="숨김 ON",
                fg_color="#28a745"
            )
        else:
            self.headless_button.configure(
                text="숨김 OFF",
                fg_color="#6c757d"
            )

        if self.collector and hasattr(self.collector, 'driver') and self.collector.driver:
            print("🔄 헤드리스 모드 변경으로 브라우저 재시작...")
            self.collector.close_browser()
            self.collector = None
            self.is_logged_in = False
            self.update_login_button_text()
            self.auto_login()

    def on_closing(self):
        """종료 처리"""
        self.stop_auto_refresh()
        self.stop_loading_animation()

        if self.collector:
            try:
                self.collector.close_browser()
            except:
                pass
        self.root.destroy()

    def run(self):
        """GUI 실행"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def update_staff_absence_display(self):
        """직원 휴무 현황 표시 업데이트"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.staff_absence_data or not self.staff_absence_data.get('success'):
            self.clear_staff_absence_display()
            return

        absence_list = self.staff_absence_data.get('absence_list', [])
        
        if not absence_list:
            no_data_label = ctk.CTkLabel(
                self.scroll_frame,
                text="👨‍🏫 오늘 휴무인 직원이 없습니다.",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#6c757d"
            )
            no_data_label.pack(pady=20)
            self.stats_label.configure(text="휴무 직원: 0명")
            return

        # 휴무 유형별로 분류
        absence_by_type = {}
        for staff in absence_list:
            absence_type = staff.get('absence_type', '기타휴무')
            if absence_type not in absence_by_type:
                absence_by_type[absence_type] = []
            absence_by_type[absence_type].append(staff)

        # 휴무 헤더
        staff_header = ctk.CTkLabel(
            self.scroll_frame,
            text=f"👨‍🏫 휴무 직원 ({len(absence_list)}명)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#6f42c1"
        )
        staff_header.pack(anchor="w", padx=8, pady=(5, 10))

        # 휴무 유형별로 표시
        type_colors = {
            '휴무': '#ff6b6b',
            '연차': '#4ecdc4',
            '병가': '#45b7d1',
            '출장': '#96ceb4',
            '교육': '#feca57',
            '기타휴무': '#9b59b6'
        }

        for absence_type, staff_list in absence_by_type.items():
            if staff_list:
                self.create_staff_absence_section(absence_type, staff_list, type_colors.get(absence_type, '#6c757d'))

        # 통계 업데이트
        summary_parts = []
        for absence_type, staff_list in absence_by_type.items():
            names = [staff['name'] for staff in staff_list]
            summary_parts.append(f"{absence_type}: {', '.join(names)}")
        
        summary_text = " | ".join(summary_parts) if summary_parts else "휴무 직원 없음"
        self.stats_label.configure(text=f"휴무 직원: {len(absence_list)}명\n{summary_text}")

    def create_staff_absence_section(self, absence_type, staff_list, color):
        """휴무 유형별 섹션 생성"""
        section_header = ctk.CTkLabel(
            self.scroll_frame,
            text=f"📋 {absence_type} ({len(staff_list)}명)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color
        )
        section_header.pack(anchor="w", padx=15, pady=(8, 5))

        names_text = ", ".join([staff['name'] for staff in staff_list])
        
        names_frame = ctk.CTkFrame(self.scroll_frame)
        names_frame.pack(fill="x", padx=15, pady=(0, 8))

        names_label = ctk.CTkLabel(
            names_frame,
            text=f"👤 {names_text}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=color,
            anchor="w",
            justify="left"
        )
        names_label.pack(fill="x", padx=10, pady=8)

    def clear_staff_absence_display(self):
        """직원 휴무 표시 초기화"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.stats_label.configure(text="직원 휴무 데이터를 불러올 수 없습니다.")
        
        no_data_label = ctk.CTkLabel(
            self.scroll_frame,
            text="❌ 직원 휴무 데이터를 불러올 수 없습니다.",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#dc3545"
        )
        no_data_label.pack(pady=20)

    def load_staff_absence_data(self):
        """직원 휴무 데이터만 별도 로드"""
        if not self.is_logged_in:
            messagebox.showwarning("로그인 필요", "먼저 로그인해주세요.")
            return

        if self.is_loading_data:
            return

        def load_thread():
            self.root.after(0, self.start_loading_animation)
            try:
                date_str = self.current_date.strftime("%Y-%m-%d")
                result = self.collector.get_staff_absence_data(date_str)
                
                if result and result.get('success'):
                    self.staff_absence_data = result
                    self.root.after(0, self.update_staff_absence_display)
                else:
                    self.root.after(0, self.clear_staff_absence_display)
            except Exception as e:
                print(f"직원 휴무 데이터 로드 오류: {e}")
                self.root.after(0, self.clear_staff_absence_display)
            finally:
                self.root.after(0, self.stop_loading_animation)

        threading.Thread(target=load_thread, daemon=True).start()


if __name__ == "__main__":
    app = SimpleAttendanceMonitor()
    app.run()