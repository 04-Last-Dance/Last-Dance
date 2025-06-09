from repositories.diary_repository import DiaryRepository
from models.diary import Diary
from transformers import pipeline
from typing import List, Optional, Dict
import json

class DiaryService:
    def __init__(self):
        self.repository = DiaryRepository()
        self.emotion_analyzer = pipeline(
            "sentiment-analysis",
            model="j-hartmann/emotion-english-distilroberta-base"
        )

    def analyze_emotions(self, text: str) -> List[Dict]:
        """텍스트의 감정을 분석"""
        results = self.emotion_analyzer(text)
        return [
            {
                "label": result["label"],
                "score": float(result["score"])
            }
            for result in results
        ]

    def create_diary(self, user_id: str, content: str) -> Diary:
        """일기 생성 및 감정 분석"""
        emotions = self.analyze_emotions(content)
        diary = Diary(
            user_id=user_id,
            content=content,
            emotions=emotions
        )
        self.repository.create(diary)
        return diary

    def get_diary(self, diary_id: str) -> Optional[Diary]:
        """일기 조회"""
        return self.repository.get_by_id(diary_id)

    def get_user_diaries(self, user_id: str, limit: int = 10) -> List[Diary]:
        """사용자의 일기 목록 조회"""
        return self.repository.get_by_user_id(user_id, limit)

    def update_diary(self, diary_id: str, content: str) -> Optional[Diary]:
        """일기 수정 및 감정 재분석"""
        diary = self.repository.get_by_id(diary_id)
        if not diary:
            return None

        emotions = self.analyze_emotions(content)
        diary.content = content
        diary.emotions = emotions
        
        if self.repository.update(diary_id, diary):
            return diary
        return None

    def delete_diary(self, diary_id: str) -> bool:
        """일기 삭제"""
        return self.repository.delete(diary_id)

    def save_temporary(self, user_id: str, content: str) -> str:
        """임시 저장"""
        return self.repository.save_temporary(user_id, content)

    def get_temporary(self, user_id: str) -> Optional[Diary]:
        """임시 저장된 일기 조회"""
        return self.repository.get_temporary(user_id) 