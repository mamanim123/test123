# login_manager.py
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from pathlib import Path
import getpass

class LoginManager:
    """로그인 정보 관리 클래스"""
    
    def __init__(self):
        self.config_dir = Path("user_profiles")
        self.config_dir.mkdir(exist_ok=True)
        
    def get_or_prompt_login_info(self, force_new=False, default_values=None):
        """로그인 정보 가져오기 또는 입력 받기"""
        if force_new:
            return self.prompt_login_info(default_values)
        
        # 기본값이 있으면 비밀번호만 입력받기
        if default_values and 'institution_id' in default_values and 'username' in default_values:
            password = self.prompt_password_only(
                default_values['institution_id'],
                default_values['username']
            )
            if password:
                default_values['password'] = password
                return default_values
            return None
        
        # 전체 정보 입력받기
        return self.prompt_login_info()
    
    def prompt_password_only(self, institution_id, username):
        """비밀번호만 입력받기"""
        root = tk.Tk()
        root.withdraw()  # 메인 윈도우 숨기기
        
        password = simpledialog.askstring(
            "비밀번호 입력",
            f"기관: {institution_id}\n사용자: {username}\n\n비밀번호를 입력하세요:",
            show='*',
            parent=root
        )
        
        root.destroy()
        return password
    
    def prompt_login_info(self, default_values=None):
        """로그인 정보 입력 다이얼로그"""
        login_info = {}
        
        # 커스텀 다이얼로그 생성
        dialog = LoginDialog(default_values)
        dialog.mainloop()
        
        if dialog.result:
            return dialog.result
        return None
    
    def clear_login_info(self):
        """저장된 로그인 정보 삭제"""
        # 필요시 구현
        pass


class LoginDialog(tk.Tk):
    """로그인 정보 입력 다이얼로그"""
    
    def __init__(self, default_values=None):
        super().__init__()
        
        self.title("케어포 로그인 정보")
        self.geometry("350x250")
        self.resizable(False, False)
        
        # 중앙 배치
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.winfo_screenheight() // 2) - (250 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.result = None
        self.default_values = default_values or {}
        
        self.create_widgets()
        
        # ESC 키로 닫기
        self.bind('<Escape>', lambda e: self.cancel())
        
        # 첫 번째 빈 필드에 포커스
        if not self.inst_entry.get():
            self.inst_entry.focus()
        elif not self.name_entry.get():
            self.name_entry.focus()
        else:
            self.pass_entry.focus()
    
    def create_widgets(self):
        # 타이틀
        title_label = tk.Label(
            self,
            text="케어포 로그인 정보를 입력하세요",
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=15)
        
        # 입력 필드 프레임
        fields_frame = tk.Frame(self)
        fields_frame.pack(pady=10)
        
        # 기관 ID
        tk.Label(fields_frame, text="기관 ID:", width=10, anchor="e").grid(row=0, column=0, padx=5, pady=5)
        self.inst_entry = tk.Entry(fields_frame, width=25)
        self.inst_entry.grid(row=0, column=1, padx=5, pady=5)
        if 'institution_id' in self.default_values:
            self.inst_entry.insert(0, self.default_values['institution_id'])
        
        # 사용자명
        tk.Label(fields_frame, text="사용자명:", width=10, anchor="e").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(fields_frame, width=25)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        if 'username' in self.default_values:
            self.name_entry.insert(0, self.default_values['username'])
        
        # 비밀번호
        tk.Label(fields_frame, text="비밀번호:", width=10, anchor="e").grid(row=2, column=0, padx=5, pady=5)
        self.pass_entry = tk.Entry(fields_frame, width=25, show="*")
        self.pass_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 엔터 키 바인딩
        self.pass_entry.bind('<Return>', lambda e: self.ok())
        
        # 버튼 프레임
        button_frame = tk.Frame(self)
        button_frame.pack(pady=15)
        
        ok_button = tk.Button(
            button_frame,
            text="확인",
            command=self.ok,
            width=10,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        ok_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = tk.Button(
            button_frame,
            text="취소",
            command=self.cancel,
            width=10,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold")
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

    def get_saved_password(self, user_id):
        """저장된 비밀번호 확인 (선택적 기능)"""
        try:
            from secure_password_manager import SecurePasswordManager
            spm = SecurePasswordManager()
            return spm.get_password(user_id)
        except:
            return None

    def save_password_option(self, user_id, password):
        """비밀번호 저장 옵션 (선택적 기능)"""
        result = messagebox.askyesno(
            "비밀번호 저장",
            "다음 로그인을 위해 비밀번호를 안전하게 저장하시겠습니까?"
        )
        
        if result:
            try:
                from secure_password_manager import SecurePasswordManager
                spm = SecurePasswordManager()
                spm.save_password(user_id, password)
                messagebox.showinfo("성공", "비밀번호가 안전하게 저장되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"비밀번호 저장 실패: {str(e)}")
    
    def ok(self):
        institution_id = self.inst_entry.get().strip()
        username = self.name_entry.get().strip()
        password = self.pass_entry.get()
        
        if not all([institution_id, username, password]):
            messagebox.showerror("오류", "모든 필드를 입력해주세요.", parent=self)
            return
        
        self.result = {
            'institution_id': institution_id,
            'username': username,
            'password': password
        }
        
        self.destroy()
    
    def cancel(self):
        self.destroy()