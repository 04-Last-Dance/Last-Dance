document.addEventListener('DOMContentLoaded', function() {
    const updateNicknameBtn = document.getElementById('updateNicknameBtn');
    const nicknameInput = document.getElementById('nickname');
    const nicknameMessage = document.getElementById('nicknameMessage'); 
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const passwordMessage = document.getElementById('passwordMessage');
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');
    const deleteMessage = document.getElementById('deleteMessage');

    // 닉네임 업데이트 기능
    if (updateNicknameBtn) {
        updateNicknameBtn.addEventListener('click', function() {
            const nickname = nicknameInput.value.trim();
            
            if (!nickname) {
                showMessage(nicknameMessage, '닉네임을 입력해주세요.', 'error');
                return;
            }
            
            fetch('/profile/update-nickname', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ nickname: nickname })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(nicknameMessage, '닉네임이 업데이트되었습니다.', 'success');
                } else {
                    showMessage(nicknameMessage, '닉네임 업데이트 실패: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showMessage(nicknameMessage, '오류가 발생했습니다: ' + error, 'error');
            });
        });
    }

    // 비밀번호 변경 기능
    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', function() {
            const newPassword = newPasswordInput.value;
            const confirmPassword = confirmPasswordInput.value;
            
            if (!newPassword) {
                showMessage(passwordMessage, '새 비밀번호를 입력해주세요.', 'error');
                return;
            }
            
            if (newPassword !== confirmPassword) {
                showMessage(passwordMessage, '비밀번호가 일치하지 않습니다.', 'error');
                return;
            }
            
            fetch('/profile/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ new_password: newPassword })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(passwordMessage, '비밀번호가 성공적으로 변경되었습니다.', 'success');
                    newPasswordInput.value = '';
                    confirmPasswordInput.value = '';
                } else {
                    showMessage(passwordMessage, '비밀번호 변경 실패: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showMessage(passwordMessage, '오류가 발생했습니다: ' + error, 'error');
            });
        });
    }

    // 계정 삭제 기능
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', function() {
            // 확인 대화상자 표시
            if (!confirm('정말로 계정을 삭제하시겠습니까? 이 작업은 취소할 수 없습니다.')) {
                return;
            }
            
            fetch('/profile/delete-account', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(deleteMessage, '계정이 성공적으로 삭제되었습니다. 잠시 후 로그인 페이지로 이동합니다.', 'success');
                    
                    // 3초 후 로그인 페이지로 리디렉션
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 3000);
                } else {
                    showMessage(deleteMessage, '계정 삭제 실패: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showMessage(deleteMessage, '오류가 발생했습니다: ' + error, 'error');
            });
        });
    }

    // 공통 메시지 표시 함수
    function showMessage(element, message, type) {
        element.textContent = message;
        element.className = 'message ' + type;
        element.style.display = 'block';
        
        // 성공 메시지는 3초 후 자동으로 사라짐
        if (type === 'success') {
            setTimeout(() => {
                element.style.display = 'none';
            }, 3000);
        }
    }
});