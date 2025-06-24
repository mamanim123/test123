const express = require('express');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const { YoutubeTranscript } = require('youtube-transcript');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

function extractVideoId(url) {
  const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
}

app.post('/api/summarize', async (req, res) => {
  try {
    const { youtubeUrl } = req.body;
    
    if (!youtubeUrl) {
      return res.status(400).json({ error: 'YouTube URL is required' });
    }

    const videoId = extractVideoId(youtubeUrl);
    if (!videoId) {
      return res.status(400).json({ error: 'Invalid YouTube URL' });
    }

    console.log('Extracting transcript for video:', videoId);
    
    const transcript = await YoutubeTranscript.fetchTranscript(videoId, {
      lang: 'ko'
    }).catch(async () => {
      return await YoutubeTranscript.fetchTranscript(videoId, {
        lang: 'en'
      });
    });

    if (!transcript || transcript.length === 0) {
      return res.status(404).json({ error: 'No transcript available for this video' });
    }

    const fullText = transcript.map(item => item.text).join(' ');
    
    console.log('Generating summary...');
    
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    
    const prompt = `다음 YouTube 영상의 자막을 분석하고 한국어로 요약해주세요:

자막 내용:
${fullText}

다음 형식으로 요약해주세요:
1. 주요 내용 (3-5개 핵심 포인트)
2. 상세 요약 (2-3 문단)
3. 핵심 키워드

요약은 명확하고 이해하기 쉽게 작성해주세요.`;

    const result = await model.generateContent(prompt);
    const summary = result.response.text();

    res.json({
      success: true,
      videoId: videoId,
      summary: summary,
      transcriptLength: transcript.length
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ 
      error: 'Failed to process video',
      details: error.message 
    });
  }
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, '0.0.0.0', () => {
  console.log(`YouTube Summarizer running at http://localhost:${port}`);
  console.log('Make sure to set your GEMINI_API_KEY in the .env file');
});