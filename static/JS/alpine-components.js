/**
 * Alpine.js 通用组件库
 * 提供常用的 UI 组件和工具函数
 */

// ===== 语言切换组件 =====
function languageSwitcher() {
    return {
        currentLang: 'zh_CN',
        supportedLangs: [
            { code: 'zh_CN', name: '中文', flag: '🇨🇳' },
            { code: 'en_US', name: 'English', flag: '🇺🇸' },
            { code: 'ja_JP', name: '日本語', flag: '🇯🇵' }
        ],
        isOpen: false,

        init() {
            // 从 localStorage 或 API 加载当前语言
            const saved = localStorage.getItem('preferred_language');
            if (saved) {
                this.currentLang = saved;
            } else {
                // 从 API 获取
                this.fetchCurrentLanguage();
            }
        },

        async fetchCurrentLanguage() {
            try {
                const response = await fetch('/api/get-language');
                const data = await response.json();
                this.currentLang = data.language;
                localStorage.setItem('preferred_language', this.currentLang);
            } catch (error) {
                console.error('获取语言设置失败:', error);
            }
        },

        async setLanguage(lang) {
            try {
                const response = await fetch('/api/set-language', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ language: lang })
                });

                if (response.ok) {
                    this.currentLang = lang;
                    localStorage.setItem('preferred_language', lang);
                    
                    // 显示成功提示
                    this.showNotification('语言已切换', 'success');
                    
                    // 刷新页面应用新语言
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                }
            } catch (error) {
                console.error('切换语言失败:', error);
                this.showNotification('切换失败，请重试', 'error');
            }
        },

        toggleDropdown() {
            this.isOpen = !this.isOpen;
        },

        closeDropdown() {
            this.isOpen = false;
        },

        get currentLangInfo() {
            return this.supportedLangs.find(lang => lang.code === this.currentLang) || this.supportedLangs[0];
        },

        showNotification(message, type = 'info') {
            // 创建通知元素
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300 ${
                type === 'success' ? 'bg-green-500' : 
                type === 'error' ? 'bg-red-500' : 'bg-blue-500'
            } text-white`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            // 3 秒后自动移除
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
    };
}

// ===== 反馈表单组件 =====
function feedbackForm() {
    return {
        formData: {
            type: 'bug',
            title: '',
            content: '',
            contact_email: '',
            priority: 'medium'
        },
        isSubmitting: false,
        submitResult: null,
        errors: {},

        types: [
            { value: 'bug', label: '🐛 Bug 报告', icon: '🐛' },
            { value: 'feature', label: '💡 功能建议', icon: '💡' },
            { value: 'improvement', label: '✨ 体验优化', icon: '✨' },
            { value: 'other', label: '📝 其他', icon: '📝' }
        ],

        priorities: [
            { value: 'low', label: '低优先级', color: 'gray' },
            { value: 'medium', label: '中优先级', color: 'blue' },
            { value: 'high', label: '高优先级', color: 'orange' },
            { value: 'critical', label: '紧急', color: 'red' }
        ],

        validate() {
            this.errors = {};

            if (!this.formData.content.trim()) {
                this.errors.content = '反馈内容不能为空';
            } else if (this.formData.content.length > 5000) {
                this.errors.content = '反馈内容不能超过 5000 字';
            }

            if (this.formData.title && this.formData.title.length > 200) {
                this.errors.title = '标题不能超过 200 字';
            }

            if (this.formData.contact_email && !this.isValidEmail(this.formData.contact_email)) {
                this.errors.contact_email = '邮箱格式不正确';
            }

            return Object.keys(this.errors).length === 0;
        },

        isValidEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        },

        async submit() {
            if (!this.validate()) {
                return;
            }

            this.isSubmitting = true;
            this.submitResult = null;

            try {
                const response = await fetch('/api/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.formData)
                });

                const data = await response.json();

                if (response.ok) {
                    this.submitResult = {
                        success: true,
                        message: data.message || '反馈提交成功！'
                    };
                    
                    // 重置表单
                    this.resetForm();
                } else {
                    this.submitResult = {
                        success: false,
                        message: data.error || '提交失败，请重试'
                    };
                }
            } catch (error) {
                console.error('提交反馈失败:', error);
                this.submitResult = {
                    success: false,
                    message: '网络错误，请检查连接'
                };
            } finally {
                this.isSubmitting = false;
            }
        },

        resetForm() {
            this.formData = {
                type: 'bug',
                title: '',
                content: '',
                contact_email: '',
                priority: 'medium'
            };
            this.errors = {};
        },

        get charCount() {
            return this.formData.content.length;
        },

        get remainingChars() {
            return 5000 - this.charCount;
        }
    };
}

// ===== 统计卡片组件 =====
function statCard(title, value, icon, trend = null) {
    return {
        title,
        value,
        icon,
        trend, // { value: '+5%', direction: 'up' | 'down' }
        isLoading: false,

        async refresh() {
            this.isLoading = true;
            
            // 模拟数据刷新（实际项目中调用 API）
            await new Promise(resolve => setTimeout(resolve, 500));
            
            this.isLoading = false;
        },

        get trendColor() {
            if (!this.trend) return '';
            return this.trend.direction === 'up' ? 'text-green-500' : 'text-red-500';
        },

        get trendIcon() {
            if (!this.trend) return '';
            return this.trend.direction === 'up' ? '↑' : '↓';
        }
    };
}

// ===== 图表容器组件 =====
function chartContainer(chartType, chartId) {
    return {
        chartType,
        chartId,
        isLoading: true,
        hasError: false,
        errorMessage: '',
        chartInstance: null,

        async init() {
            try {
                await this.loadChart();
            } catch (error) {
                console.error('图表加载失败:', error);
                this.hasError = true;
                this.errorMessage = '图表加载失败，请刷新重试';
            } finally {
                this.isLoading = false;
            }
        },

        async loadChart() {
            // 这里应该调用实际的图表渲染逻辑
            // 示例：使用 PyECharts 生成的 HTML
            const response = await fetch(`/api/chart/${this.chartType}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            
            // 渲染图表（具体实现取决于图表库）
            this.renderChart(data);
        },

        renderChart(data) {
            // 占位符：实际项目中集成 ECharts
            console.log(`Rendering ${this.chartType} chart:`, data);
        },

        async refresh() {
            this.isLoading = true;
            this.hasError = false;
            
            try {
                await this.loadChart();
            } catch (error) {
                this.hasError = true;
                this.errorMessage = '刷新失败';
            } finally {
                this.isLoading = false;
            }
        }
    };
}

// ===== 通知系统 =====
function notificationSystem() {
    return {
        notifications: [],

        add(message, type = 'info', duration = 3000) {
            const id = Date.now();
            const notification = {
                id,
                message,
                type,
                visible: true
            };

            this.notifications.push(notification);

            // 自动关闭
            if (duration > 0) {
                setTimeout(() => {
                    this.remove(id);
                }, duration);
            }
        },

        remove(id) {
            const index = this.notifications.findIndex(n => n.id === id);
            if (index > -1) {
                this.notifications[index].visible = false;
                setTimeout(() => {
                    this.notifications = this.notifications.filter(n => n.id !== id);
                }, 300); // 等待动画完成
            }
        },

        success(message) {
            this.add(message, 'success');
        },

        error(message) {
            this.add(message, 'error', 5000);
        },

        info(message) {
            this.add(message, 'info');
        }
    };
}

// ===== 全局工具函数 =====
window.AlpineUtils = {
    // 格式化数字
    formatNumber(num) {
        return new Intl.NumberFormat('zh-CN').format(num);
    },

    // 格式化日期
    formatDate(date, format = 'medium') {
        const d = new Date(date);
        
        if (format === 'short') {
            return d.toLocaleDateString('zh-CN');
        } else if (format === 'long') {
            return d.toLocaleString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        return d.toLocaleString('zh-CN');
    },

    // 防抖函数
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // 节流函数
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// 注册所有组件到 Alpine
if (typeof Alpine !== 'undefined') {
    Alpine.data('languageSwitcher', languageSwitcher);
    Alpine.data('feedbackForm', feedbackForm);
    Alpine.data('statCard', statCard);
    Alpine.data('chartContainer', chartContainer);
    Alpine.data('notificationSystem', notificationSystem);
    
    console.log('✅ Alpine.js 通用组件库已加载');
} else {
    console.warn('⚠️ Alpine.js 未加载，组件将无法使用');
}
