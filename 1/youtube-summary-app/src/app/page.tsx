'use client';

import { useState } from 'react';
import { ArrowPathIcon, PlayCircleIcon } from '@heroicons/react/24/outline';

export default function Home() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [summary, setSummary] = useState('');
  const [videoId, setVideoId] = useState('');

  const extractVideoId = (url: string): string | null => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const id = extractVideoId(url);
    
    if (!id) {
      alert('유효한 YouTube URL을 입력해주세요.');
      return;
    }

    setVideoId(id);
    setIsLoading(true);
    
    try {
      // 여기서는 임시 응답을 사용합니다.
      // 실제로는 API 라우트를 통해 백엔드에 요청을 보내야 합니다.
      await new Promise(resolve => setTimeout(resolve, 1500));
      setSummary(
        '이곳에 동영상 요약이 표시됩니다. 실제 구현에서는 YouTube 동영상의 자막을 추출하고, "
        + "추출한 텍스트를 요약하는 과정이 포함됩니다. 이 기능을 구현하려면 OpenAI API와 같은 "
        + "자연어 처리 API를 사용해야 합니다.'
      );
    } catch (error) {
      console.error('요약 중 오류가 발생했습니다:', error);
      alert('요약을 가져오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
        YouTube 요약 봇
      </h1>
      
      <div className="bg-white rounded-xl shadow-md p-6 mb-8">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex flex-col space-y-2">
            <label htmlFor="youtube-url" className="text-lg font-medium text-gray-700">
              YouTube 동영상 URL
            </label>
            <div className="flex space-x-2">
              <input
                id="youtube-url"
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="input-field flex-1"
                required
              />
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary flex items-center space-x-2 whitespace-nowrap"
              >
                {isLoading ? (
                  <>
                    <ArrowPathIcon className="h-5 w-5 animate-spin" />
                    <span>처리 중...</span>
                  </>
                ) : (
                  <>
                    <PlayCircleIcon className="h-5 w-5" />
                    <span>요약하기</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>

      {videoId && (
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <div className="p-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">동영상 미리보기</h2>
            <div className="aspect-w-16 aspect-h-9 mb-6">
              <iframe
                width="100%"
                height="400"
                src={`https://www.youtube.com/embed/${videoId}`}
                title="YouTube video player"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="rounded-lg"
              ></iframe>
            </div>
            
            <div className="mt-6">
              <h3 className="text-xl font-semibold mb-3 text-gray-800">요약 내용</h3>
              <div className="bg-gray-50 p-4 rounded-lg min-h-32">
                {isLoading ? (
                  <div className="flex justify-center items-center h-32">
                    <ArrowPathIcon className="h-8 w-8 text-blue-500 animate-spin" />
                  </div>
                ) : (
                  <p className="whitespace-pre-line text-gray-700">
                    {summary || '동영상 URL을 입력하고 요약하기 버튼을 클릭하세요.'}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
