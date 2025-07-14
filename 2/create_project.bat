@echo off
setlocal

set "PROJECT_DIR=youtube-summary-app"
set "STATIC_DIR=%PROJECT_DIR%\static"
set "CSS_DIR=%STATIC_DIR%\css"
set "JS_DIR=%STATIC_DIR%\js"
set "TEMPLATES_DIR=%PROJECT_DIR%\templates"

echo.
echo ====================================================
echo  유튜브 영상 요약 앱 프로젝트 구조 생성
echo ====================================================
echo.

REM 프로젝트 최상위 폴더 생성
echo 1. Creating project directory: %PROJECT_DIR%
md %PROJECT_DIR% 2>nul
if %errorlevel% neq 0 (
    echo Error: Failed to create %PROJECT_DIR%. It might already exist.
    goto :eof
)

REM static 폴더 및 하위 폴더 생성
echo 2. Creating static assets directories...
md %CSS_DIR% 2>nul
md %JS_DIR% 2>nul

REM templates 폴더 생성
echo 3. Creating templates directory: %TEMPLATES_DIR%
md %TEMPLATES_DIR% 2>nul

REM 파일 생성 (빈 파일)
echo 4. Creating empty files...
type nul > %PROJECT_DIR%\app.py
type nul > %CSS_DIR%\style.css
type nul > %JS_DIR%\script.js
type nul > %TEMPLATES_DIR%\index.html

echo.
echo ====================================================
echo  프로젝트 구조 생성이 완료되었습니다!
echo ====================================================
echo.
echo 다음 단계를 진행해 주세요:
echo 1. '%PROJECT_DIR%\app.py' 파일에 Python Flask 코드를 붙여넣으세요.
echo 2. '%CSS_DIR%\style.css' 파일에 CSS 코드를 붙여넣으세요.
echo 3. '%JS_DIR%\script.js' 파일에 JavaScript 코드를 붙여넣으세요.
echo 4. '%TEMPLATES_DIR%\index.html' 파일에 HTML 코드를 붙여넣으세요.
echo.
echo 각 파일에 코드를 붙여넣은 후, '%PROJECT_DIR%' 폴더로 이동하여
echo 'pip install Flask yt-dlp transformers youtube-transcript-api google-cloud-language'
echo 명령어로 필요한 라이브러리를 설치하고, 'python app.py' 명령어로 서버를 실행하세요.
echo.
pause