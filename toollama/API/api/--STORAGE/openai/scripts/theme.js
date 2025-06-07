export class ThemeManager {
  constructor() {
    try {
      this.themeToggle = document.getElementById('themeToggle');
      if (!this.themeToggle) throw new Error('Theme toggle element not found');
      this.init();
    } catch (error) {
      console.error('ThemeManager initialization failed:', error);
    }
  }

  init() {
    this.setInitialTheme();
    this.themeToggle.addEventListener('click', () => this.toggleTheme());
  }

  setInitialTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    this.updateToggleIcon(savedTheme);
  }

  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    this.updateToggleIcon(newTheme);
  }

  updateToggleIcon(theme) {
    const icon = this.themeToggle.querySelector('svg');
    icon.style.transition = 'transform 0.3s ease';
    icon.style.transform = theme === 'dark' ? 'rotate(0deg)' : 'rotate(180deg)';
  }
} 