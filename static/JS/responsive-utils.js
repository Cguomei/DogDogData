/**
 * 移动端响应式优化
 * 针对小屏幕设备的布局优化
 */

// ===== 检测设备类型 =====
function detectDevice() {
    const width = window.innerWidth;
    
    if (width < 768) {
        return 'mobile';
    } else if (width < 1024) {
        return 'tablet';
    } else {
        return 'desktop';
    }
}

// ===== 响应式工具函数 =====
const ResponsiveUtils = {
    // 检测设备类型
    getDevice: detectDevice,
    
    // 是否为移动设备
    isMobile: () => detectDevice() === 'mobile',
    
    // 是否为平板设备
    isTablet: () => detectDevice() === 'tablet',
    
    // 是否为桌面设备
    isDesktop: () => detectDevice() === 'desktop',
    
    // 获取视口宽度
    getViewportWidth: () => window.innerWidth,
    
    // 获取视口高度
    getViewportHeight: () => window.innerHeight,
    
    // 是否为横屏模式
    isLandscape: () => window.innerWidth > window.innerHeight,
    
    // 是否为竖屏模式
    isPortrait: () => window.innerHeight > window.innerWidth
};

// ===== Alpine.js 响应式组件 =====
function responsiveLayout() {
    return {
        deviceType: detectDevice(),
        isMobile: false,
        isTablet: false,
        isDesktop: true,
        sidebarOpen: false,
        
        init() {
            this.updateDeviceType();
            
            // 监听窗口大小变化
            window.addEventListener('resize', this.debounce(() => {
                this.updateDeviceType();
            }, 250));
            
            console.log(`✅ 响应式布局已初始化，当前设备: ${this.deviceType}`);
        },
        
        updateDeviceType() {
            this.deviceType = detectDevice();
            this.isMobile = this.deviceType === 'mobile';
            this.isTablet = this.deviceType === 'tablet';
            this.isDesktop = this.deviceType === 'desktop';
            
            // 移动设备默认关闭侧边栏
            if (this.isMobile) {
                this.sidebarOpen = false;
            }
        },
        
        toggleSidebar() {
            this.sidebarOpen = !this.sidebarOpen;
        },
        
        closeSidebar() {
            if (this.isMobile) {
                this.sidebarOpen = false;
            }
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
        }
    };
}

// ===== 触摸优化 =====
function optimizeForTouch() {
    // 检测是否为触摸设备
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    if (isTouchDevice) {
        document.body.classList.add('touch-device');
        
        // 增加触摸目标大小
        const style = document.createElement('style');
        style.textContent = `
            .touch-device button,
            .touch-device a,
            .touch-device input,
            .touch-device select {
                min-height: 44px;
                min-width: 44px;
            }
            
            .touch-device .card {
                margin-bottom: 1rem;
            }
            
            .touch-device .btn {
                padding: 0.75rem 1.5rem;
            }
        `;
        document.head.appendChild(style);
        
        console.log('✅ 触摸优化已启用');
    }
}

// ===== 移动端菜单优化 =====
function setupMobileMenu() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    const toggleButton = document.createElement('button');
    toggleButton.className = 'mobile-menu-toggle';
    toggleButton.innerHTML = '☰';
    toggleButton.setAttribute('aria-label', '切换菜单');
    
    // 仅在移动设备显示
    const style = document.createElement('style');
    style.textContent = `
        .mobile-menu-toggle {
            display: none;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.5rem;
        }
        
        @media (max-width: 768px) {
            .mobile-menu-toggle {
                display: block;
            }
            
            .navbar-nav {
                display: none;
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                flex-direction: column;
                padding: 1rem;
            }
            
            .navbar-nav.show {
                display: flex;
            }
        }
    `;
    document.head.appendChild(style);
    
    navbar.insertBefore(toggleButton, navbar.firstChild);
    
    toggleButton.addEventListener('click', () => {
        const nav = document.querySelector('.navbar-nav');
        if (nav) {
            nav.classList.toggle('show');
        }
    });
    
    console.log('✅ 移动端菜单已优化');
}

// ===== 图片响应式优化 =====
function optimizeImages() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        // 添加响应式类
        img.classList.add('img-fluid');
        
        // 设置最大宽度
        if (!img.style.maxWidth) {
            img.style.maxWidth = '100%';
            img.style.height = 'auto';
        }
        
        // 懒加载（如果还没有）
        if (!img.hasAttribute('loading')) {
            img.setAttribute('loading', 'lazy');
        }
    });
    
    console.log(`✅ 已优化 ${images.length} 张图片`);
}

// ===== 表格响应式优化 =====
function optimizeTables() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        // 包裹在可滚动容器中
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        wrapper.style.overflowX = 'auto';
        wrapper.style.webkitOverflowScrolling = 'touch';
        
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
    
    console.log(`✅ 已优化 ${tables.length} 个表格`);
}

// ===== 字体大小自适应 =====
function adjustFontSize() {
    const baseFontSize = Math.min(16, Math.max(14, window.innerWidth / 100));
    document.documentElement.style.fontSize = `${baseFontSize}px`;
}

// ===== 视口单位修复（iOS Safari）=====
function fixViewportUnits() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
    
    window.addEventListener('resize', () => {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    });
}

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
    // 注册 Alpine 组件
    if (typeof Alpine !== 'undefined') {
        Alpine.data('responsiveLayout', responsiveLayout);
        console.log('✅ 响应式布局组件已注册');
    }
    
    // 触摸优化
    optimizeForTouch();
    
    // 移动端菜单
    setupMobileMenu();
    
    // 图片优化
    optimizeImages();
    
    // 表格优化
    optimizeTables();
    
    // 字体大小调整
    adjustFontSize();
    window.addEventListener('resize', adjustFontSize);
    
    // 视口单位修复
    fixViewportUnits();
});

// 导出全局对象
window.ResponsiveUtils = ResponsiveUtils;
