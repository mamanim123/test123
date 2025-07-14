import os
from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
import re
from collections import Counter
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import punctuation
from heapq import nlargest
import requests

# NLTK 데이터 다운로드
try:
    nltk.download('punkt')
    nltk.download('stopwords')
except Exception as e:
    print(f"NLTK 데이터 다운로드 실패: {e}")

# 로깅 설정
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def summarize_text(text, num_sentences=5):
    """텍스트 요약"""
    if not text or not text.strip():
        logger.error("Empty text provided for summarization")
        return ""
        
    try:
        # 문장 단위로 분리
        sentences = sent_tokenize(text)
        if not sentences:
            logger.error("No sentences found in the text")
            return ""
            
        # 단어 빈도수 계산
        word_freq = {}
        stop_words = set(stopwords.words('english'))
        
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            words = [word for word in words if word not in stop_words and word not in punctuation]
            
            for word in words:
                if word not in word_freq:
                    word_freq[word] = 1
                else:
                    word_freq[word] += 1
                    
        # 문장 점수 계산
        sent_scores = {}
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            words = [word for word in words if word not in stop_words and word not in punctuation]
            score = sum([word_freq.get(word, 0) for word in words])
            sent_scores[sentence] = score if words else 0
            
        # 상위 n개 문장 선택
        num_sentences = min(num_sentences, len(sentences))
        summary_sentences = nlargest(num_sentences, sent_scores, key=sent_scores.get)
        
        # 원래 순서대로 정렬
        summary_sentences.sort(key=lambda x: sentences.index(x))
        
        return " ".join(summary_sentences)
        
    except Exception as e:
        logger.error(f"Error during text summarization: {str(e)}")
        return ""

def extract_video_id(youtube_url):
    """유튜브 URL에서 영상 ID 추출"""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", youtube_url)
    return match.group(1) if match else None

def get_video_info(video_id):
    """유튜브 비디오 정보 가져오기"""
    try:
        # YouTube Data API v3 엔드포인트 (API 키 없이 기본 정보만 가져옴)
        response = requests.get(f'https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={video_id}&format=json')
        
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get('title', '제목 없음'),
                "channel_name": data.get('author_name', '채널명 없음'),
                "upload_date": "N/A",  # oembed API에서는 업로드 날짜를 제공하지 않음
                "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            }
        else:
            logger.error(f"비디오 정보 가져오기 실패: {response.status_code}")
            return {
                "title": "비디오 정보를 가져올 수 없습니다",
                "channel_name": "알 수 없음",
                "upload_date": "N/A",
                "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            }
    except Exception as e:
        logger.error(f"비디오 정보 가져오기 중 오류 발생: {str(e)}")
        return {
            "title": "비디오 정보를 가져올 수 없습니다",
            "channel_name": "알 수 없음",
            "upload_date": "N/A",
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        }

def get_video_transcript(video_id):
    """유튜브 영상 자막 가져오기"""
    logger.info(f"Fetching transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None

        # 1. 한국어 자막 시도
        try:
            transcript = transcript_list.find_transcript(['ko'])
            logger.info(f"Found Korean transcript for video {video_id}")
        except Exception as e:
            logger.warning(f"No Korean transcript found for {video_id}, trying English: {str(e)}")
            
            # 2. 영어 자막 시도
            try:
                transcript = transcript_list.find_transcript(['en'])
                logger.info(f"Found English transcript for video {video_id}")
            except Exception as e:
                logger.warning(f"No English transcript found for {video_id}, trying auto-generated: {str(e)}")
                
                # 3. 자동 생성된 자막 시도
                try:
                    transcript = transcript_list.find_generated_transcript(['ko', 'en'])
                    logger.info(f"Found auto-generated transcript for video {video_id}")
                except Exception as e:
                    logger.warning(f"No auto-generated ko/en transcript for {video_id}, trying first available: {str(e)}")
                    
                    # 4. 사용 가능한 첫 번째 자막 시도
                    available_languages = (
                        transcript_list._generated_languages +
                        transcript_list._manually_created_languages
                    )
                    if available_languages:
                        try:
                            transcript = transcript_list.find_transcript([available_languages[0]])
                            logger.info(f"Using first available transcript in {available_languages[0]} for {video_id}")
                        except Exception as e:
                            logger.error(f"Failed to get first available transcript: {str(e)}")
                            return None

        if transcript:
            try:
                transcript_data = transcript.fetch()
                if not transcript_data:
                    logger.error(f"Empty transcript data for video {video_id}")
                    return None
                    
                text = " ".join([t.get('text', '') for t in transcript_data if t.get('text')])
                if not text.strip():
                    logger.error(f"Empty transcript text for video {video_id}")
                    return None
                    
                logger.info(f"Successfully fetched transcript for video {video_id}")
                return text
            except Exception as e:
                logger.error(f"Error fetching transcript data: {str(e)}")
                return None
        
        logger.error(f"No suitable transcript found for video {video_id}")
        return None
        
    except VideoUnavailable:
        logger.error(f"Video {video_id} is unavailable")
        return None
    except TranscriptsDisabled:
        logger.error(f"Transcripts are disabled for video {video_id}")
        return None
    except NoTranscriptFound:
        logger.error(f"No transcript available for video {video_id}")
        return None
    except Exception as e:
        logger.error(f"Error getting transcript for video {video_id}: {str(e)}")
        return None

def analyze_programs_and_prompts(transcript_text):
    """
    영상 내용에서 프로그램 정보와 프롬프트 추출 (간단한 키워드 매칭)
    실제로는 더 복잡한 NLP (개체명 인식, 관계 추출)가 필요합니다.
    """
    programs = []
    prompts = []

    # 예시 키워드 (실제 영상 내용에 따라 더 정교화 필요)
    program_keywords = {
        "Python": {"description": "파이썬 프로그래밍 언어", "usage_tip": "주로 데이터 처리와 백엔드 로직 구현에 사용됩니다."},
        "Flask": {"description": "파이썬 웹 프레임워크", "usage_tip": "`pip install Flask`로 설치 후 `app.run()`으로 실행합니다."},
        "yt-dlp": {"description": "유튜브 영상 및 자막 다운로드 도구", "usage_tip": "`pip install yt-dlp` 후 `yt-dlp --write-auto-sub <URL>` 사용."},
        "Transformers": {"description": "Hugging Face AI 모델 라이브러리", "usage_tip": "`from transformers import pipeline`로 사용."},
        "Streamlit": {"description": "파이썬 웹 앱 프레임워크 (GUI)", "usage_tip": "`streamlit run app.py`로 앱 실행."},
        "VS Code": {"description": "마이크로소프트 코드 에디터", "usage_tip": "개발 환경 설정 시 사용됩니다."}
    }

    prompt_patterns = [
        r"pip install \S+",
        r"yt-dlp --\S+",
        r"from \S+ import \S+",
        r"summarizer = pipeline\(.*\)",
        r"streamlit run \S+",
        r"python \S+\.py",
        r"openai\.Completion\.create\(.*?\)" # OpenAI 프롬프트 예시
    ]

    # 프로그램 키워드 검색
    found_program_names = set() # 중복 방지
    for keyword, info in program_keywords.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', transcript_text, re.IGNORECASE):
            if keyword not in found_program_names:
                programs.append({"name": keyword, **info})
                found_program_names.add(keyword)
    
    # 프롬프트 패턴 검색
    for pattern in prompt_patterns:
        found_prompts_for_pattern = re.findall(pattern, transcript_text)
        prompts.extend(list(set(found_prompts_for_pattern))) # 중복 제거

    # 추가적으로 영상 제목이나 설명에서 유추할 수 있는 프로그램 정보 추가 (선택 사항)
    # 예를 들어, 특정 키워드가 제목에 있으면 추가하는 로직 등

    return programs, prompts

def analyze_comments(comments_text_list):
    """
    댓글 분석 및 추천 (매우 간략화된 예시)
    실제로는 자연어 처리 (감성 분석, 키워드 추출, 의미론적 유사성)가 필요합니다.
    """
    recommended_comments = []
    # 긍정적인 키워드 및 프롬프트 관련 키워드 예시
    positive_keywords = ["유용", "도움", "좋아요", "최고", "감사", "훌륭", "쉽게", "배웠", "추천", "대박", "인생"]
    prompt_keywords = ["프롬프트", "명령어", "코드", "예시", "팁", "문구", "스크립트", "설정", "방식"]

    for i, comment_text in enumerate(comments_text_list):
        # 대화형 모델의 경우, 실제 댓글은 API를 통해 가져와야 합니다.
        # 여기서는 임의의 작성자를 부여합니다.
        author_placeholder = f"유튜브 사용자 {i+1}" 
        
        is_positive = any(keyword in comment_text.lower() for keyword in positive_keywords)
        has_prompt_info = any(keyword in comment_text.lower() for keyword in prompt_keywords)

        if is_positive or has_prompt_info:
            prompt_example = None
            # 댓글 내에서 코드 블록이나 프롬프트로 보이는 부분을 추출 (백틱 ` ` 안에 있는 내용)
            match = re.search(r"`([^`]+)`", comment_text)
            if match:
                prompt_example = match.group(1).strip()
            
            # 더 일반적인 프롬프트 패턴 검색 (예: 특정 시작 단어, 명령어 형태)
            elif re.search(r'(?:pip install|yt-dlp|from \S+ import|streamlit run|python \S+\.py)', comment_text, re.IGNORECASE):
                 # 실제로는 여기에 더 복잡한 프롬프트 추출 로직을 넣어야 합니다.
                 # 여기서는 단순히 프롬프트 관련 키워드가 있으면 댓글 전체를 프롬프트 예시로 넣거나,
                 # 특정 패턴을 다시 찾는 방식으로 임시 처리합니다.
                 if has_prompt_info:
                     prompt_example = comment_text # 일단 댓글 전체를 프롬프트 예시로 간주
            
            recommended_comments.append({
                "author": author_placeholder,
                "text": comment_text,
                "prompt_example": prompt_example
            })
    return recommended_comments

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_video():
    try:
        data = request.get_json()
        if not data or 'video_url' not in data:
            return jsonify({
                'error': '비디오 URL이 제공되지 않았습니다.',
                'status': 'error'
            }), 400
            
        video_id = extract_video_id(data['video_url'])
        if not video_id:
            return jsonify({
                'error': '올바른 YouTube URL이 아닙니다.',
                'status': 'error'
            }), 400
            
        logger.info(f"Analyzing video ID: {video_id}")
        
        # 1. 영상 정보
        video_info = get_video_info(video_id)
        
        # 2. 자막 추출
        transcript = get_video_transcript(video_id)
        if not transcript:
            return jsonify({
                'error': '자막을 가져올 수 없습니다.',
                'video_info': video_info,
                'status': 'error'
            }), 404
            
        # 3. 텍스트 요약
        summary = summarize_text(transcript, num_sentences=10)  # 요약 문장 수 증가
        if not summary:
            return jsonify({
                'error': '텍스트 요약에 실패했습니다.',
                'video_info': video_info,
                'status': 'error'
            }), 500
            
        # 4. 프로그램 정보 및 프롬프트 추출
        programs, code_prompts = analyze_programs_and_prompts(transcript)
        
        # 5. 문맥 기반 프롬프트 생성
        context_prompts = generate_prompts(transcript)
        
        # 모든 프롬프트 통합 (코드 프롬프트 우선)
        all_prompts = code_prompts + [p for p in context_prompts if p not in code_prompts]
        
        return jsonify({
            'video_info': video_info,
            'summary': summary,
            'programs': programs,
            'prompts': all_prompts[:10],  # 최대 10개 프롬프트 반환
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error during video analysis: {str(e)}")
        return jsonify({
            'error': f'분석 중 오류가 발생했습니다: {str(e)}',
            'status': 'error'
        }), 500

def generate_prompts(text):
    """텍스트에서 프롬프트 생성"""
    try:
        sentences = sent_tokenize(text)
        if not sentences:
            return []
            
        # 문장 길이 기준으로 필터링 (너무 짧거나 긴 문장 제외)
        filtered_sentences = [s for s in sentences if 10 <= len(s.split()) <= 30]
        
        # 중복 제거
        filtered_sentences = list(set(filtered_sentences))
        
        # 최대 5개 프롬프트 선택
        prompts = filtered_sentences[:5] if filtered_sentences else []
        
        return prompts
        
    except Exception as e:
        logger.error(f"Error generating prompts: {str(e)}")
        return []

if __name__ == '__main__':
    app.run(debug=True)