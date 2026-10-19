/**
 * Mowria Fashion (MFB) - External Activity & Audit Log Script
 */

function activityLogApp() {
    return { 
        darkMode: localStorage.getItem('theme') !== 'light',
        toggleTheme() {
            this.darkMode = !this.darkMode;
            if (this.darkMode) {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            }
            this.$nextTick(() => {
                if (window.lucide) lucide.createIcons();
            });
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

