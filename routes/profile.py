from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services.auth import auth_required
from firebase_admin import auth, firestore
from repositories.user_repository import UserRepository

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')
user_repository = UserRepository()

@profile_bp.route('/')
@auth_required
def profile():
    """사용자 프로필 페이지"""
    # 세션에서 사용자 정보 가져오기
    user = session.get('user', {})
    user_id = user.get('uid', '')
    email = user.get('email', '')
    
    # 로그인 제공자 확인 (이메일/비밀번호 또는 Google)
    provider_id = user.get('firebase', {}).get('sign_in_provider', '')
    is_email_signin = provider_id == 'password'
    
    # Firestore에서 사용자 데이터 가져오기
    user_data = user_repository.get_user_data(user_id)  


    nickname = user_data.get('nickname', email.split('@')[0])
    
    # 감정 상태 가져오기 (더미 데이터)
    emotion_data = get_user_emotion_status(user_id)
    
    return render_template('profile.html', 
                           email=email, 
                           nickname=nickname, 
                           is_email_signin=is_email_signin,
                           #이후로는 더미 감정 라우터와 연결되는 코드 
                           latest_emotion=emotion_data.get('emotion', 'neutral'),
                           emotion_color=emotion_data.get('color', '#A9A9A9'),
                           emotion_description=emotion_data.get('description', '중립'),
                           emotion_score=emotion_data.get('score', 0))

@profile_bp.route('/update-nickname', methods=['POST'])
@auth_required
def update_nickname():
    """닉네임 업데이트"""
    user = session.get('user', {})
    user_id = user.get('uid', '')
    
    data = request.get_json()
    if not data or 'nickname' not in data:
        return jsonify({'success': False, 'error': '닉네임이 제공되지 않았습니다.'}), 400
    
    nickname = data['nickname']
    
    # Firestore에 닉네임 업데이트
    user_repository.update_nickname(user_id, nickname)
    
    return jsonify({'success': True, 'nickname': nickname})

@profile_bp.route('/change-password', methods=['POST'])
@auth_required
def change_password():
    """비밀번호 직접 변경"""
    user = session.get('user', {})
    user_id = user.get('uid', '')
    
    data = request.get_json()
    if not data or 'new_password' not in data:
        return jsonify({'success': False, 'error': '새 비밀번호가 제공되지 않았습니다.'}), 400
    
    new_password = data['new_password']
    
    try:
        # Admin SDK로 직접 비밀번호 변경
        auth.update_user(user_id, password=new_password)
        return jsonify({'success': True, 'message': '비밀번호가 변경되었습니다.'})
    except Exception as e:
        print(f"Password change error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@profile_bp.route('/delete-account', methods=['POST'])
@auth_required
def delete_account():
    """사용자 계정 삭제"""
    user = session.get('user', {})
    user_id = user.get('uid', '')
    
    try:
        # 사용자 데이터 삭제
        user_repository.delete_user_data(user_id) 
        
        # Firebase Auth에서 사용자 삭제
        auth.delete_user(user_id)
        
        # 세션에서 사용자 정보 삭제
        session.pop('user', None)
        
        return jsonify({'success': True, 'message': '계정이 성공적으로 삭제되었습니다.'})
    except Exception as e:
        print(f"Account deletion error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500






#추후 기능 구현 바람. 현재는 더미 기능 
@profile_bp.route('/get-emotion-status', methods=['GET'])
@auth_required
def get_emotion_status():
    """사용자의 현재 감정 상태 API"""
    user = session.get('user', {})
    user_id = user.get('uid', '')
    
    # 감정 상태 데이터 가져오기
    emotion_data = get_user_emotion_status(user_id)
    
    return jsonify(emotion_data)

# 더미 함수: 사용자의 감정 상태 가져오기 (나중에 실제 구현으로 대체될 예정)
def get_user_emotion_status(user_id):
    """
    사용자의 감정 상태를 가져오는 더미 함수
    
    나중에 구현할 때는:
    1. Firestore에서 사용자의 최근 일기 가져오기
    2. 감정 분석 결과 반환
    3. 감정에 따른 색상, 설명 등 매핑
    """
    
    # 임시 하드코딩된 값 (나중에 실제 데이터로 대체)
    emotion_data = {
        'emotion': 'neutral',
        'color': '#A9A9A9',
        'description': '중립',
        'score': 0.8,
        'timestamp': firestore.SERVER_TIMESTAMP
    }
    
    # 이 함수는 나중에 실제 데이터로 구현될 예정
    return emotion_data