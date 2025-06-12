from firebase_admin import firestore
from models.diary import Diary
from typing import List, Optional
from datetime import datetime
from flask import current_app, has_app_context

class DiaryRepository:
    def __init__(self):
        if has_app_context():
            self.db = current_app.config['db']
        else:
            self.db = firestore.client()
        self.collection = self.db.collection('diaries')

    def create(self, diary: Diary) -> str:
        """일기 생성"""
        doc_ref = self.collection.document()
        diary_data = diary.to_dict()
        diary_data['id'] = doc_ref.id
        doc_ref.set(diary_data)
        return doc_ref.id

    def get_by_id(self, diary_id: str) -> Optional[Diary]:
        """ID로 일기 조회"""
        doc = self.collection.document(diary_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        return Diary.from_dict(data)

    def get_by_user_id(self, user_id: str, limit: int = 10) -> List[Diary]:
        """사용자의 일기 목록 조회"""
        docs = self.collection.where('user_id', '==', user_id)\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .stream()
        
        return [Diary.from_dict(doc.to_dict()) for doc in docs]

    def update(self, diary_id: str, diary: Diary) -> bool:
        """일기 수정"""
        doc_ref = self.collection.document(diary_id)
        if not doc_ref.get().exists:
            return False
        
        diary_data = diary.to_dict()
        diary_data['updated_at'] = datetime.now().isoformat()
        doc_ref.update(diary_data)
        return True

    def delete(self, diary_id: str) -> bool:
        """일기 삭제"""
        doc_ref = self.collection.document(diary_id)
        if not doc_ref.get().exists:
            return False
        
        doc_ref.delete()
        return True

    def save_temporary(self, user_id: str, content: str) -> str:
        """임시 저장"""
        diary = Diary(
            user_id=user_id,
            content=content,
            emotions=[],
            is_temporary=True
        )
        return self.create(diary)

    def get_temporary(self, user_id: str) -> Optional[Diary]:
        """임시 저장된 일기 조회"""
        docs = self.collection.where('user_id', '==', user_id)\
            .where('is_temporary', '==', True)\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(1)\
            .stream()
        
        for doc in docs:
            return Diary.from_dict(doc.to_dict())
        return None 