import { initializeFirebase } from './auth-config.js';
import { 
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signInWithPopup,
} from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";

// Firebase 인스턴스를 담을 변수
let auth = null;
let provider = null;

// DOM 요소들
const signInWithGoogleButtonEl = document.getElementById("sign-in-with-google-btn");
const signUpWithGoogleButtonEl = document.getElementById("sign-up-with-google-btn");
const emailInputEl = document.getElementById("email-input");
const passwordInputEl = document.getElementById("password-input");
const signInButtonEl = document.getElementById("sign-in-btn");
const createAccountButtonEl = document.getElementById("create-account-btn");
const errorMsgEmail = document.getElementById("email-error-message");
const errorMsgPassword = document.getElementById("password-error-message");
const errorMsgGoogleSignIn = document.getElementById("google-signin-error-message");

// 페이지 로드 시 Firebase 초기화
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const firebaseInstances = await initializeFirebase();
        auth = firebaseInstances.auth;
        provider = firebaseInstances.provider;
        
        // Google 로그인 제공자 설정
        provider.setCustomParameters({
            'prompt': 'select_account'
        });
        
        // 이벤트 리스너 설정
        if (signInWithGoogleButtonEl) {
            signInWithGoogleButtonEl.addEventListener("click", authSignInWithGoogle);
        }
        
        if (signInButtonEl) {
            signInButtonEl.addEventListener("click", authSignInWithEmail);
        }

        if (createAccountButtonEl) {
            createAccountButtonEl.addEventListener("click", authCreateAccountWithEmail);
        }

        if (signUpWithGoogleButtonEl) {
            signUpWithGoogleButtonEl.addEventListener("click", authSignUpWithGoogle);
        }
    } catch (error) {
        console.error('Firebase initialization failed:', error);
        alert('Failed to initialize authentication. Please refresh the page.');
    }
});

async function authSignInWithGoogle() {
    if (!auth || !provider) {
        console.error('Firebase not initialized');
        return;
    }
    
    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        const idToken = await user.getIdToken();
        
        await loginUser(user, idToken);
    } catch (error) {
        // Firebase 에러 처리
        const errorCode = error.code;
        const errorMessage = error.message;
        
        console.error("Error during Google sign-in:");
        console.error("Code:", errorCode);
        console.error("Message:", errorMessage);
        
        if (errorCode === 'auth/unauthorized-domain') {
            alert('This domain is not authorized for Google sign-in. Please contact the administrator.');
        } else if (errorCode === 'auth/popup-closed-by-user') {
            console.log('User closed the popup');
        } else {
            if (errorMsgGoogleSignIn) {
                errorMsgGoogleSignIn.textContent = errorMessage;
            }
        }
    }
}

async function authSignUpWithGoogle() {
    if (!auth || !provider) {
        console.error('Firebase not initialized');
        return;
    }
    
    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        const idToken = await user.getIdToken();
        
        await loginUser(user, idToken);
    } catch (error) {
        // Firebase 에러 처리
        const errorCode = error.code;
        const errorMessage = error.message;
        
        console.error("Error during Google sign-in:");
        console.error("Code:", errorCode);
        console.error("Message:", errorMessage);
        
        if (errorCode === 'auth/unauthorized-domain') {
            alert('This domain is not authorized for Google sign-in. Please contact the administrator.');
        } else if (errorCode === 'auth/popup-closed-by-user') {
            console.log('User closed the popup');
        } else {
            if (errorMsgGoogleSignIn) {
                errorMsgGoogleSignIn.textContent = errorMessage;
            }
        }
    }
    await authSignInWithGoogle();
}

async function authSignInWithEmail() {
    if (!auth) {
        console.error('Firebase not initialized');
        return;
    }
    
    const email = emailInputEl.value;
    const password = passwordInputEl.value;

    if (!email || !password) {
        if (!email && errorMsgEmail) errorMsgEmail.textContent = "Please enter your email";
        if (!password && errorMsgPassword) errorMsgPassword.textContent = "Please enter your password";
        return;
    }

    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        const idToken = await user.getIdToken();
        
        await loginUser(user, idToken);
    } catch (error) {
        console.error("Error signing in:", error);
        handleAuthError(error);
    }
}

async function authCreateAccountWithEmail() {
    if (!auth) {
        console.error('Firebase not initialized');
        return;
    }
    
    const email = emailInputEl.value;
    const password = passwordInputEl.value;

    if (!email || !password) {
        if (!email && errorMsgEmail) errorMsgEmail.textContent = "Please enter your email";
        if (!password && errorMsgPassword) errorMsgPassword.textContent = "Please enter your password";
        return;
    }

    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        
        // Firestore 사용이 필요하면 여기에 추가, 하지만 현재는 제거
        const idToken = await user.getIdToken();
        await loginUser(user, idToken);
    } catch (error) {
        console.error("Error creating account:", error);
        handleAuthError(error);
    }
}

function handleAuthError(error) {
    const errorCode = error.code;
    
    if (errorCode === "auth/invalid-email" && errorMsgEmail) {
        errorMsgEmail.textContent = "Invalid email address";
    } else if (errorCode === "auth/weak-password" && errorMsgPassword) {
        errorMsgPassword.textContent = "Password should be at least 6 characters";
    } else if (errorCode === "auth/email-already-in-use" && errorMsgEmail) {
        errorMsgEmail.textContent = "Email already in use";
    } else if (errorCode === "auth/user-not-found" && errorMsgEmail) {
        errorMsgEmail.textContent = "User not found";
    } else if (errorCode === "auth/wrong-password" && errorMsgPassword) {
        errorMsgPassword.textContent = "Incorrect password";
    } else if (errorCode === "auth/invalid-credential" && errorMsgPassword) {
        errorMsgPassword.textContent = "Invalid email or password";
    } else {
        if (errorMsgPassword) errorMsgPassword.textContent = "Authentication failed";
    }
}

async function loginUser(user, idToken) {
    try {
        const response = await fetch('/auth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${idToken}`
            },
            credentials: 'same-origin'
        });

        if (response.ok) {
            //iframe에서 실행 중인지 확인
            if (window.parent !== window) {
                //홈페이지에 인증 성공 메시지 전송
                window.parent.postMessage({
                    type: 'AUTH_SUCCESS',
                    user: {
                        uid: user.uid,
                        email: user.email
                    }
                }, '*');
            } else {
                // 기존: 직접 페이지 접근인 경우
                window.location.href = '/dashboard';
            }
        } else {
            console.error('Failed to authenticate with backend');
            if (errorMsgPassword) {
                errorMsgPassword.textContent = "Authentication failed. Please try again.";
            }
        }
    } catch (error) {
        console.error('Error during authentication:', error);
        if (errorMsgPassword) {
            errorMsgPassword.textContent = "Connection error. Please try again.";
        }
    }
}

// Clear error messages when user starts typing
if (emailInputEl) {
    emailInputEl.addEventListener('input', () => {
        if (errorMsgEmail) errorMsgEmail.textContent = '';
    });
}

if (passwordInputEl) {
    passwordInputEl.addEventListener('input', () => {
        if (errorMsgPassword) errorMsgPassword.textContent = '';
    });
}

// Clear input fields
function clearInputField(field) {
    if (field) field.value = "";
}

function clearAuthFields() {
    clearInputField(emailInputEl);
    clearInputField(passwordInputEl);
}