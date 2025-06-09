from firebase_admin import firestore

class UserRepository:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('users')
    
    def exists(self, user_id):
        """사용자 문서 존재 여부 확인"""
        doc = self.collection.document(user_id).get()
        return doc.exists
    
    def create(self, user_id, email):
        """새 사용자 문서 생성"""
        user_data = {
            'email': email,
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        self.collection.document(user_id).set(user_data)


    def update_nickname(self, user_id, nickname):
         """사용자 닉네임 업데이트"""
         self.collection.document(user_id).update({
         'nickname': nickname
         })
         return True
    
    def delete(self, user_id):
        """사용자 문서 삭제"""
        self.collection.document(user_id).delete()
        print(f"User document deleted for {user_id}")


    def delete_user_data(self, user_id):
        """사용자 관련 모든 데이터 삭제"""
        # 1. 사용자 문서 삭제
        self.delete(user_id)
        
        print(f"All data for user {user_id} has been deleted")

    