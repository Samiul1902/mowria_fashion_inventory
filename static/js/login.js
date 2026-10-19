/**
 * Mowria Fashion (MFB) - External Login Script
 */

function loginApp() {
    return {
        darkMode: localStorage.getItem('theme') !== 'light',
        email: '',
        password: '',
        setQuickAccount(em, pwd) {
            this.email = em;
            this.password = pwd;
        }
    };
}

document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('theme') !== 'light') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    if (window.lucide) {
        lucide.createIcons();
    }
});
