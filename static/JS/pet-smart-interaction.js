/**
 * Live2D 宠物智能交互增强
 * 提供时间问候、数据提示、页面感知等功能
 */

class SmartPetInteraction {
    constructor() {
        this.lastGreeting = null;
        this.lastDataTip = null;
        this.init();
    }

    /**
     * 初始化智能交互
     */
    init() {
        console.log('🐾 Smart Pet Interaction 已启动');
        
        // 页面加载完成后显示问候
        window.addEventListener('load', () => {
            setTimeout(() => this.showGreeting(), 4000);
            // 初始化宠物显示状态
            this.initPetVisibility();
        });
        
        // 每5分钟更新一次数据提示
        setInterval(() => this.showDataTip(), 300000);
        
        // 监听页面变化
        this.observePageChanges();
        
        // 添加自定义点击事件
        this.addCustomInteractions();
        
        // 绑定按钮点击事件
        this.bindButtonEvents();
    }

    /**
     * 显示时间问候
     */
    async showGreeting() {
        try {
            const response = await fetch('/api/pet/greeting');
            const data = await response.json();
            
            if (data.greeting && data.greeting !== this.lastGreeting) {
                this.showMessage(data.greeting, 3000);
                this.lastGreeting = data.greeting;
                
                // 根据心情调整透明度
                this.adjustOpacityByMood(data.mood);
            }
        } catch (error) {
            console.error('获取问候语失败:', error);
        }
    }

    /**
     * 显示数据摘要提示
     */
    async showDataTip() {
        try {
            const response = await fetch('/api/pet/data-summary');
            const data = await response.json();
            
            if (data.success && data.message !== this.lastDataTip) {
                this.showMessage(data.message, 4000);
                this.lastDataTip = data.message;
            }
        } catch (error) {
            console.error('获取数据提示失败:', error);
        }
    }

    /**
     * 观察页面变化，显示相关提示
     */
    observePageChanges() {
        let lastPath = window.location.pathname;
        
        // 使用 History API 监听路由变化
        const pushState = history.pushState;
        history.pushState = function() {
            pushState.apply(history, arguments);
            window.dispatchEvent(new Event('locationchange'));
        };
        
        window.addEventListener('locationchange', () => {
            if (window.location.pathname !== lastPath) {
                lastPath = window.location.pathname;
                setTimeout(() => this.showPageTip(lastPath), 1000);
            }
        });
        
        // 初始页面提示
        setTimeout(() => this.showPageTip(window.location.pathname), 5000);
    }

    /**
     * 根据页面显示提示
     */
    async showPageTip(path) {
        // 提取页面名称
        let pageName = 'home';
        
        if (path.includes('/charts')) {
            pageName = 'charts';
        } else if (path.includes('/breeds')) {
            pageName = 'breeds';
        } else if (path.includes('/food')) {
            pageName = 'food';
        } else if (path.includes('/custom-analysis')) {
            pageName = 'custom-analysis';
        } else if (path.includes('/ai-chat')) {
            pageName = 'ai-chat';
        }
        
        try {
            const response = await fetch(`/api/pet/page-tip/${pageName}`);
            const data = await response.json();
            
            if (data.tip) {
                this.showMessage(data.tip, 3500);
            }
        } catch (error) {
            console.error('获取页面提示失败:', error);
        }
    }

    /**
     * 添加自定义交互
     */
    addCustomInteractions() {
        // 监听Live2D点击事件（如果可用）
        document.addEventListener('click', (e) => {
            // 检查是否点击了Live2D容器
            const live2dContainer = document.querySelector('#live2d-widget');
            if (live2dContainer && live2dContainer.contains(e.target)) {
                this.recordInteraction('click');
            }
        });
        
        // 添加键盘快捷键
        document.addEventListener('keydown', (e) => {
            // Ctrl + P: 召唤/隐藏宠物
            if (e.ctrlKey && e.key === 'p') {
                e.preventDefault();
                this.togglePetVisibility();
            }
            // ESC: 快速隐藏宠物
            if (e.key === 'Escape') {
                const petContainer = document.querySelector('#live2d-widget');
                if (petContainer && petContainer.style.display !== 'none') {
                    this.togglePetVisibility();
                }
            }
        });
    }

    /**
     * 记录用户互动
     */
    async recordInteraction(action) {
        try {
            const response = await fetch('/api/pet/interaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action })
            });
            
            const data = await response.json();
            
            if (data.message) {
                this.showMessage(data.message, 2500);
            }
        } catch (error) {
            console.error('记录互动失败:', error);
        }
    }

    /**
     * 显示消息（模拟对话气泡）
     */
    showMessage(message, duration = 3000) {
        // 创建或获取消息元素
        let messageEl = document.getElementById('pet-message');
        
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.id = 'pet-message';
            messageEl.style.cssText = `
                position: fixed;
                bottom: 340px;
                right: 20px;
                background: white;
                padding: 12px 16px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                font-size: 14px;
                color: #333;
                z-index: 10000;
                max-width: 250px;
                opacity: 0;
                transform: translateY(10px);
                transition: all 0.3s ease;
            `;
            document.body.appendChild(messageEl);
        }
        
        // 显示消息
        messageEl.textContent = message;
        messageEl.style.opacity = '1';
        messageEl.style.transform = 'translateY(0)';
        
        // 自动隐藏
        setTimeout(() => {
            messageEl.style.opacity = '0';
            messageEl.style.transform = 'translateY(10px)';
        }, duration);
    }

    /**
     * 根据心情调整透明度
     */
    adjustOpacityByMood(mood) {
        const petContainer = document.querySelector('#live2d-widget');
        if (!petContainer) return;
        
        const opacities = {
            'happy': 1,
            'energetic': 1,
            'focused': 0.9,
            'relaxed': 0.8,
            'sleepy': 0.6,
            'tired': 0.7
        };
        
        const opacity = opacities[mood] || 0.8;
        petContainer.style.opacity = opacity;
    }

    /**
     * 切换宠物可见性（优化版 - 添加平滑动画）
     */
    togglePetVisibility() {
        const petContainer = document.querySelector('#live2d-widget');
        if (!petContainer) return;
        
        const isVisible = petContainer.style.display !== 'none';
        
        if (isVisible) {
            // 隐藏宠物 - 添加淡出动画
            petContainer.style.transition = 'opacity 0.3s ease';
            petContainer.style.opacity = '0';
            
            setTimeout(() => {
                petContainer.style.display = 'none';
            }, 300);
            
            this.showMessage('🐾 宠物已隐藏（按 Ctrl+P 重新显示）', 2000);
        } else {
            // 显示宠物 - 添加淡入动画
            petContainer.style.display = 'block';
            petContainer.style.opacity = '0';
            
            setTimeout(() => {
                petContainer.style.transition = 'opacity 0.5s ease';
                petContainer.style.opacity = '0.7';
            }, 10);
            
            this.showMessage('🐶 宠物已显示', 2000);
        }
        
        // 保存用户偏好
        localStorage.setItem('petVisible', !isVisible);
        
        // 更新按钮状态
        this.updatePetButton(!isVisible);
    }
    
    /**
     * 更新宠物按钮状态（优化版 - 更清晰的视觉反馈）
     */
    updatePetButton(isVisible) {
        const btn = document.getElementById('summon-pet-btn');
        if (!btn) return;
        
        if (isVisible) {
            btn.innerHTML = '<span style="font-size: 1.1em;">🐾</span> 小宠物';
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-outline-warning');
            btn.title = '隐藏小宠物（快捷键：Ctrl+P 或 ESC）';
        } else {
            btn.innerHTML = '<span style="font-size: 1.1em;">🐶</span> 召唤宠物';
            btn.classList.remove('btn-outline-warning');
            btn.classList.add('btn-outline-secondary');
            btn.title = '召唤小宠物（快捷键：Ctrl+P）';
        }
    }
    
    /**
     * 初始化宠物显示状态（优化版 - 避免闪烁）
     */
    initPetVisibility() {
        // 从 localStorage 读取用户偏好
        const savedVisibility = localStorage.getItem('petVisible');
        const petContainer = document.querySelector('#live2d-widget');
        
        if (!petContainer) return;
        
        // 如果用户之前选择了隐藏，则默认隐藏
        if (savedVisibility === 'false') {
            petContainer.style.display = 'none';
            petContainer.style.opacity = '0';
            // 不更新按钮状态，保持HTML中的初始状态
        } else {
            // 默认显示，但添加淡入效果
            petContainer.style.opacity = '0';
            setTimeout(() => {
                petContainer.style.transition = 'opacity 0.8s ease';
                petContainer.style.opacity = '0.7';
            }, 100);
            // 不更新按钮状态，保持HTML中的初始状态
        }
    }
    
    /**
     * 绑定按钮点击事件
     */
    bindButtonEvents() {
        const btn = document.getElementById('summon-pet-btn');
        if (!btn) return;
        
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            this.togglePetVisibility();
        });
    }
}

// 当Live2D加载完成后初始化
window.addEventListener('load', () => {
    // 延迟初始化，确保Live2D已加载
    setTimeout(() => {
        if (typeof L2Dwidget !== 'undefined') {
            window.smartPet = new SmartPetInteraction();
            console.log('✅ 智能宠物交互系统已就绪');
        } else {
            console.warn('⚠️ Live2D未加载，智能交互不可用');
        }
    }, 1000);
});
