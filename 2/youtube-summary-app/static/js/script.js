document.addEventListener('DOMContentLoaded', function() {
    const youtubeUrlInput = document.getElementById('youtubeUrl');
    const analyzeButton = document.getElementById('analyzeButton');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const resultsSection = document.getElementById('resultsSection');
    
    // 결과 섹션의 각 요소
    const videoThumbnail = document.getElementById('videoThumbnail');
    const videoTitle = document.getElementById('videoTitle');
    const channelName = document.getElementById('channelName');
    const uploadDate = document.getElementById('uploadDate');
    const summaryContent = document.getElementById('summaryContent');
    const programsUsedContent = document.getElementById('programsUsedContent');
    const extractedPromptsContent = document.getElementById('extractedPromptsContent');
    const recommendedCommentsContent = document.getElementById('recommendedCommentsContent');

    analyzeButton.addEventListener('click', async function() {
        const youtubeUrl = youtubeUrlInput.value.trim();
        
        if (!youtubeUrl) {
            showError('YouTube URL을 입력해주세요.');
            return;
        }

        // UI 상태 업데이트
        showLoading(true);
        hideError();
        hideResults();

        try {
            const response = await fetch('/analyze-youtube', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ youtube_url: youtubeUrl })
            });

            const data = await response.json();

            if (data.status === 'error') {
                showError(data.error_message);
                return;
            }

            // 결과 표시
            displayResults(data);

        } catch (error) {
            showError('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
            console.error('Error:', error);
        } finally {
            showLoading(false);
        }
    });

    function displayResults(data) {
        // 비디오 정보 업데이트
        videoThumbnail.src = data.video_info.thumbnail_url;
        videoThumbnail.classList.remove('hidden');
        videoTitle.textContent = data.video_info.title;
        channelName.textContent = data.video_info.channel_name;
        uploadDate.textContent = data.video_info.upload_date;

        // 요약 내용
        summaryContent.textContent = data.summary;

        // 사용된 프로그램 목록
        displayProgramsUsed(data.programs_used);

        // 추출된 프롬프트
        displayExtractedPrompts(data.extracted_prompts);

        // 추천 댓글
        displayRecommendedComments(data.recommended_comments);

        // 결과 섹션 표시
        resultsSection.classList.remove('hidden');
    }

    function displayProgramsUsed(programs) {
        if (!programs || programs.length === 0) {
            programsUsedContent.innerHTML = '<p>프로그램 정보가 없습니다.</p>';
            return;
        }

        const html = programs.map(program => `
            <div class="program-item">
                <h3>${program.name}</h3>
                <p><strong>설명:</strong> ${program.description}</p>
                <p><strong>사용 팁:</strong> ${program.usage_tip}</p>
            </div>
        `).join('');

        programsUsedContent.innerHTML = html;
    }

    function displayExtractedPrompts(prompts) {
        if (!prompts || prompts.length === 0) {
            extractedPromptsContent.innerHTML = '<p>추출된 프롬프트가 없습니다.</p>';
            return;
        }

        const html = prompts.map(prompt => `
            <div class="code-block">${prompt}</div>
        `).join('');

        extractedPromptsContent.innerHTML = html;
    }

    function displayRecommendedComments(comments) {
        if (!comments || comments.length === 0) {
            recommendedCommentsContent.innerHTML = '<p>추천 댓글이 없습니다.</p>';
            return;
        }

        const html = comments.map(comment => `
            <div class="comment-item">
                <span class="comment-author">${comment.author}</span>
                <p class="comment-text">${comment.text}</p>
                ${comment.prompt_example ? `
                    <div class="comment-prompt-example">
                        <strong>프롬프트 예시:</strong>
                        <code>${comment.prompt_example}</code>
                    </div>
                ` : ''}
            </div>
        `).join('');

        recommendedCommentsContent.innerHTML = html;
    }

    function showLoading(show) {
        if (show) {
            loadingSpinner.classList.remove('hidden');
            analyzeButton.disabled = true;
        } else {
            loadingSpinner.classList.add('hidden');
            analyzeButton.disabled = false;
        }
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }

    function hideError() {
        errorMessage.textContent = '';
        errorMessage.classList.add('hidden');
    }

    function hideResults() {
        resultsSection.classList.add('hidden');
    }
});