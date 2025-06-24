# YouTube 영상 요약기

Gemini AI를 사용하여 YouTube 영상을 자동으로 요약하는 웹 애플리케이션입니다.

## 기능

- YouTube 영상 URL 입력
- 자동 자막 추출 (한국어/영어)
- Gemini AI를 통한 스마트 요약
- 깔끔한 웹 인터페이스

## 설치 및 실행

1. 의존성 설치
```bash
npm install
```

2. 환경 변수 설정
```bash
cp .env.example .env
```
`.env` 파일을 열고 Gemini API 키를 입력하세요:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

3. 서버 실행
```bash
npm start
```

4. 브라우저에서 `http://localhost:3000` 접속

## API 키 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 방문
2. 새 API 키 생성
3. `.env` 파일에 키 입력

## 사용법

1. YouTube 영상 URL 입력
2. '요약하기' 버튼 클릭
3. AI가 생성한 요약 확인

## 주의사항

- 자막이 있는 영상만 요약 가능
- 비공개 영상은 요약 불가
- API 사용량에 따라 요금 발생 가능