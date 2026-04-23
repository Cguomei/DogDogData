/**
 * 首页 Alpine.js 组件
 * 用于增强首页的交互功能
 */

// ===== 首页数据看板组件 =====
function dashboardPage() {
    return {
        isLoading: false,
        lastUpdate: new Date().toLocaleString('zh-CN'),
        
        // 统计数据
        stats: {
            total_dogs: 0,
            avg_price: 0,
            total_shops: 0,
            total_breeds: 0
        },

        async init() {
            console.log('✅ 首页组件已初始化');
            
            // 从服务器加载最新数据
            await this.loadStats();
            
            // 每 5 分钟自动刷新
            setInterval(() => this.autoRefresh(), 300000);
        },

        async loadStats() {
            this.isLoading = true;
            
            try {
                const response = await fetch('/api/dashboard/stats');
                
                if (response.ok) {
                    const data = await response.json();
                    this.stats = data;
                    this.lastUpdate = new Date().toLocaleString('zh-CN');
                }
            } catch (error) {
                console.error('加载统计数据失败:', error);
            } finally {
                this.isLoading = false;
            }
        },

        async refresh() {
            await this.loadStats();
            
            // 显示成功提示
            this.showNotification('数据已刷新', 'success');
        },

        async autoRefresh() {
            // 仅在页面可见时自动刷新
            if (!document.hidden) {
                await this.loadStats();
            }
        },

        toggleCardDetails(cardId) {
            const card = document.getElementById(cardId);
            const icon = document.getElementById(cardId.replace('Card', 'Icon'));
            
            if (card.style.display === 'none') {
                card.style.display = 'block';
                if (icon) {
                    icon.style.transform = 'rotate(180deg)';
                }
            } else {
                card.style.display = 'none';
                if (icon) {
                    icon.style.transform = 'rotate(0deg)';
                }
            }
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
            
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        },

        formatNumber(num) {
            return new Intl.NumberFormat('zh-CN').format(num);
        },

        formatPrice(price) {
            return '¥' + new Intl.NumberFormat('zh-CN').format(price);
        }
    };
}

// ===== 图片懒加载 =====
function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // 加载图片
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    
                    // 添加淡入效果
                    img.classList.add('loaded');
                    
                    // 停止观察
                    observer.unobserve(img);
                }
            });
        });

        // 观察所有带 data-src 的图片
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });

        console.log('✅ 图片懒加载已启用');
    } else {
        // 降级方案：直接加载所有图片
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
        
        console.log('⚠️ 浏览器不支持 IntersectionObserver，使用降级方案');
    }
}

// ===== 滚动动画 =====
function setupScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if ('IntersectionObserver' in window) {
        const scrollObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                    scrollObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        animatedElements.forEach(el => {
            scrollObserver.observe(el);
        });

        console.log('✅ 滚动动画已启用');
    } else {
        // 降级方案：直接显示
        animatedElements.forEach(el => {
            el.classList.add('animated');
        });
    }
}

// ===== 数字动画 =====
function animateNumber(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 16); // 60 FPS
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        element.textContent = Math.floor(current).toLocaleString('zh-CN');
    }, 16);
}

// ===== 页面可见性检测 =====
function setupVisibilityDetection() {
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            console.log('📄 页面隐藏，暂停自动刷新');
        } else {
            console.log('📄 页面可见，恢复自动刷新');
            // 可以在这里触发数据刷新
        }
    });
}

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
    // 注册 Alpine 组件
    if (typeof Alpine !== 'undefined') {
        Alpine.data('dashboardPage', dashboardPage);
        console.log('✅ 首页 Alpine 组件已注册');
    }
    
    // 设置图片懒加载
    setupLazyLoading();
    
    // 设置滚动动画
    setupScrollAnimations();
    
    // 设置页面可见性检测
    setupVisibilityDetection();
    
    // 为统计卡片添加数字动画
    setTimeout(() => {
        document.querySelectorAll('.stat-number').forEach(el => {
            const target = parseInt(el.dataset.value);
            if (target) {
                animateNumber(el, target);
            }
        });
    }, 500);
});

// 导出工具函数供其他脚本使用
window.DashboardUtils = {
    animateNumber,
    setupLazyLoading,
    setupScrollAnimations
};
