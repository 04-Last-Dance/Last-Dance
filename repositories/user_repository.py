from firebase_admin import firestore
from cryptography.fernet import Fernet
import os
import base64
from dotenv import load_dotenv
load_dotenv()

class UserRepository:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('users')

        #환경변수에서 키 가져오기 
        key = os.getenv('FIRESTORE_ENCRYPTION_KEY')
        if not key:
             raise ValueError("FIRESTORE_ENCRYPTION_KEY 환경변수가 설정되지 않았습니다.")
    
        self.encryption_key = key.encode() if isinstance(key, str) else key
        self.cipher = Fernet(self.encryption_key)

    def _encrypt_data(self, data):
        """데이터 암호화"""
        if isinstance(data, str):
            encrypted_bytes = self.cipher.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        return data
    
    def _decrypt_data(self, data):
        """데이터 복호화"""
        if isinstance(data, str):
            try:
                encrypted_bytes = base64.b64decode(data.encode('utf-8'))
                decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
                return decrypted_bytes.decode('utf-8')
            except:
                return data  # 복호화 실패 시 원본 반환
        return data
    
    def _encrypt_user_data(self, user_data):
        """사용자 데이터의 민감한 필드들을 암호화"""
        encrypted_data = user_data.copy()
        
        # 암호화할 필드들
        sensitive_fields = ['email', 'nickname']
        
        for field in sensitive_fields:
            if field in encrypted_data:
                encrypted_data[field] = self._encrypt_data(encrypted_data[field])
        
        return encrypted_data
    
    def _decrypt_user_data(self, user_data):
        """사용자 데이터의 민감한 필드들을 복호화"""
        if not user_data:
            return {}
            
        decrypted_data = user_data.copy()
        
        # 복호화할 필드들
        sensitive_fields = ['email', 'nickname']
        
        for field in sensitive_fields:
            if field in decrypted_data:
                decrypted_data[field] = self._decrypt_data(decrypted_data[field])
        
        return decrypted_data


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
        encrypted_data = self._encrypt_user_data(user_data)  #암호화 
        self.collection.document(user_id).set(encrypted_data)

    def get_user_data(self, user_id):
        """사용자 데이터 가져오기"""
        doc = self.collection.document(user_id).get()
        if doc.exists:
            encrypted_data = doc.to_dict()   #복호화 
            return self._decrypt_user_data(encrypted_data)
        return {}


    def update_nickname(self, user_id, nickname):
         """사용자 닉네임 업데이트"""
         encrypted_nickname = self._encrypt_data(nickname)  #암호화 
         self.collection.document(user_id).update({
         'nickname': encrypted_nickname
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

    

    