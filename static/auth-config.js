// auth-config.js
async function initializeFirebase() {
    try {
        const response = await fetch('/api/firebase-config');
        const config = await response.json();
        
        const { initializeApp } = await import('https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js');
        const { getAuth, GoogleAuthProvider } = await import('https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js');
        
        const app = initializeApp(config);
        const auth = getAuth(app);
        const provider = new GoogleAuthProvider();
        
        // 도메인 설정 추가
        provider.addScope('profile');
        provider.addScope('email');
        
        return { auth, provider };
    } catch (error) {
        console.error('Failed to initialize Firebase:', error);
        throw error;
    }
}

export { initializeFirebase };