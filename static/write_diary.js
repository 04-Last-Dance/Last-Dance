// 기본 감정 목록
const BASE_EMOTIONS = ['슬픔', '분노', '기쁨', '불안', '무기력'];

// AI 보조 질문 목록
const AI_QUESTIONS = [
    "오늘 가장 기억에 남는 순간은 언제인가요?",
    "오늘 하루 동안 어떤 감정을 가장 많이 느끼셨나요?",
    "내일은 어떤 하루가 되었으면 좋겠나요?",
    "오늘 하루 동안 누군가에게 감사한 마음을 느낀 적이 있나요?",
    "오늘 하루 동안 가장 힘들었던 순간은 언제인가요?"
];

// DOM 요소
const diaryForm = document.getElementById('diary-form');
const diaryContent = document.getElementById('diary-content');
const charCount = document.querySelector('.char-count');
const emotionButtons = document.getElementById('emotion-buttons');
const aiQuestions = document.getElementById('ai-questions');
const tempSaveBtn = document.getElementById('temp-save-btn');
const submitBtn = document.getElementById('submit-btn');

// 선택된 감정들을 저장할 배열
let selectedEmotions = [];

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    initializeEmotionButtons();
    initializeAIQuestions();
    loadTempSave();
});

// 감정 버튼 초기화
function initializeEmotionButtons() {
    BASE_EMOTIONS.forEach(emotion => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'emotion-btn';
        button.textContent = emotion;
        button.addEventListener('click', () => toggleEmotion(button, emotion));
        emotionButtons.appendChild(button);
    });
}

// AI 질문 초기화
function initializeAIQuestions() {
    AI_QUESTIONS.forEach(question => {
        const div = document.createElement('div');
        div.className = 'ai-question';
        div.textContent = question;
        div.addEventListener('click', () => insertAIQuestion(question));
        aiQuestions.appendChild(div);
    });
}

// 감정 토글
function toggleEmotion(button, emotion) {
    const index = selectedEmotions.indexOf(emotion);
    if (index === -1) {
        selectedEmotions.push(emotion);
        button.classList.add('selected');
    } else {
        selectedEmotions.splice(index, 1);
        button.classList.remove('selected');
    }
}

// AI 질문 삽입
function insertAIQuestion(question) {
    const currentText = diaryContent.value;
    const newText = currentText + '\n\n' + question + '\n';
    diaryContent.value = newText;
    updateCharCount();
}

// 글자 수 업데이트
function updateCharCount() {
    const count = diaryContent.value.length;
    charCount.textContent = `${count}/50자`;
    charCount.style.color = count < 50 ? '#dc3545' : '#28a745';
}

// 임시 저장
function saveTemp() {
    const tempData = {
        content: diaryContent.value,
        emotions: selectedEmotions,
        timestamp: new Date().toISOString()
    };
    localStorage.setItem('tempDiary', JSON.stringify(tempData));
    alert('임시 저장되었습니다.');
}

// 임시 저장 불러오기
function loadTempSave() {
    const tempData = localStorage.getItem('tempDiary');
    if (tempData) {
        const data = JSON.parse(tempData);
        diaryContent.value = data.content;
        data.emotions.forEach(emotion => {
            const button = Array.from(emotionButtons.children)
                .find(btn => btn.textContent === emotion);
            if (button) {
                button.classList.add('selected');
                selectedEmotions.push(emotion);
            }
        });
        updateCharCount();
    }
}

// 일기 제출
async function submitDiary(e) {
    e.preventDefault();
    
    if (diaryContent.value.length < 50) {
        alert('일기는 50자 이상 작성해주세요.');
        return;
    }
    
    if (selectedEmotions.length === 0) {
        alert('최소 하나 이상의 감정을 선택해주세요.');
        return;
    }

    try {
        const response = await fetch('/api/diary/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: diaryContent.value,
                emotions: selectedEmotions
            })
        });

        if (response.ok) {
            localStorage.removeItem('tempDiary');
            alert('일기가 저장되었습니다.');
            window.location.href = '/dashboard';
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || '일기 저장에 실패했습니다.');
        }
    } catch (error) {
        alert(error.message);
    }
}

// 이벤트 리스너
diaryContent.addEventListener('input', updateCharCount);
tempSaveBtn.addEventListener('click', saveTemp);
diaryForm.addEventListener('submit', submitDiary); 