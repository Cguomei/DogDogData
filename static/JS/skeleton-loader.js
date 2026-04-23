/**
 * 骨架屏组件
 * 提供优雅的加载状态展示
 */

// ===== 骨架屏生成器 =====
function createSkeleton(type = 'card', count = 1) {
    const skeletons = [];
    
    for (let i = 0; i < count; i++) {
        switch(type) {
            case 'card':
                skeletons.push(createCardSkeleton());
                break;
            case 'list':
                skeletons.push(createListSkeleton());
                break;
            case 'chart':
                skeletons.push(createChartSkeleton());
                break;
            case 'table':
                skeletons.push(createTableSkeleton());
                break;
            default:
                skeletons.push(createCardSkeleton());
        }
    }
    
    return skeletons.join('');
}

// ===== 卡片骨架屏 =====
function createCardSkeleton() {
    return `
        <div class="skeleton-card animate-pulse">
            <div class="skeleton-header"></div>
            <div class="skeleton-body">
                <div class="skeleton-line skeleton-line-short"></div>
                <div class="skeleton-line"></div>
                <div class="skeleton-line skeleton-line-medium"></div>
            </div>
            <div class="skeleton-footer">
                <div class="skeleton-button"></div>
            </div>
        </div>
    `;
}

// ===== 列表骨架屏 =====
function createListSkeleton(items = 5) {
    let listItems = '';
    for (let i = 0; i < items; i++) {
        listItems += `
            <div class="skeleton-list-item">
                <div class="skeleton-avatar"></div>
                <div class="skeleton-content">
                    <div class="skeleton-line skeleton-line-short"></div>
                    <div class="skeleton-line skeleton-line-medium"></div>
                </div>
            </div>
        `;
    }
    
    return `<div class="skeleton-list">${listItems}</div>`;
}

// ===== 图表骨架屏 =====
function createChartSkeleton() {
    return `
        <div class="skeleton-chart animate-pulse">
            <div class="skeleton-chart-header"></div>
            <div class="skeleton-chart-body">
                <div class="skeleton-chart-placeholder"></div>
            </div>
            <div class="skeleton-chart-footer">
                <div class="skeleton-legend"></div>
            </div>
        </div>
    `;
}

// ===== 表格骨架屏 =====
function createTableSkeleton(rows = 5, cols = 4) {
    let tableRows = '';
    for (let i = 0; i < rows; i++) {
        let cells = '';
        for (let j = 0; j < cols; j++) {
            cells += '<td><div class="skeleton-line"></div></td>';
        }
        tableRows += `<tr>${cells}</tr>`;
    }
    
    return `
        <table class="skeleton-table">
            <thead>
                <tr>
                    ${Array(cols).fill('<th><div class="skeleton-line skeleton-line-short"></div></th>').join('')}
                </tr>
            </thead>
            <tbody>${tableRows}</tbody>
        </table>
    `;
}

// ===== Alpine.js 骨架屏组件 =====
function skeletonLoader(config = {}) {
    return {
        isLoading: true,
        showSkeleton: true,
        skeletonType: config.type || 'card',
        skeletonCount: config.count || 3,
        minDisplayTime: config.minDisplayTime || 500, // 最小显示时间，避免闪烁
        
        async loadData(loadFn) {
            const startTime = Date.now();
            
            try {
                // 执行数据加载
                await loadFn();
                
                // 确保骨架屏至少显示指定时间
                const elapsed = Date.now() - startTime;
                if (elapsed < this.minDisplayTime) {
                    await new Promise(resolve => 
                        setTimeout(resolve, this.minDisplayTime - elapsed)
                    );
                }
                
                this.isLoading = false;
                
                // 淡出动画
                setTimeout(() => {
                    this.showSkeleton = false;
                }, 300);
                
            } catch (error) {
                console.error('数据加载失败:', error);
                this.isLoading = false;
                this.showSkeleton = false;
            }
        },
        
        get skeletonHTML() {
            return createSkeleton(this.skeletonType, this.skeletonCount);
        }
    };
}

// ===== 初始化骨架屏样式 =====
function injectSkeletonStyles() {
    const styles = `
        /* 骨架屏基础样式 */
        .animate-pulse {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: .5; }
        }
        
        /* 卡片骨架屏 */
        .skeleton-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .skeleton-header {
            height: 24px;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            border-radius: 4px;
            margin-bottom: 1rem;
            animation: shimmer 1.5s infinite;
        }
        
        .skeleton-body {
            margin-bottom: 1rem;
        }
        
        .skeleton-line {
            height: 16px;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            border-radius: 4px;
            margin-bottom: 0.5rem;
            animation: shimmer 1.5s infinite;
        }
        
        .skeleton-line-short { width: 40%; }
        .skeleton-line-medium { width: 70%; }
        
        .skeleton-footer {
            display: flex;
            justify-content: flex-end;
        }
        
        .skeleton-button {
            width: 80px;
            height: 32px;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            border-radius: 6px;
            animation: shimmer 1.5s infinite;
        }
        
        /* 列表骨架屏 */
        .skeleton-list-item {
            display: flex;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .skeleton-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            margin-right: 1rem;
            animation: shimmer 1.5s infinite;
        }
        
        .skeleton-content {
            flex: 1;
        }
        
        /* 图表骨架屏 */
        .skeleton-chart {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .skeleton-chart-header {
            height: 28px;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            border-radius: 4px;
            margin-bottom: 1.5rem;
            animation: shimmer 1.5s infinite;
        }
        
        .skeleton-chart-placeholder {
            height: 300px;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            border-radius: 8px;
            animation: shimmer 1.5s infinite;
        }
        
        .skeleton-legend {
            height: 20px;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            border-radius: 4px;
            margin-top: 1rem;
            animation: shimmer 1.5s infinite;
        }
        
        /* 表格骨架屏 */
        .skeleton-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .skeleton-table th,
        .skeleton-table td {
            padding: 0.75rem;
            text-align: left;
        }
        
        .skeleton-table th {
            background: #f8f9fa;
        }
        
        /* 流光动画 */
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        /* 淡入淡出过渡 */
        .skeleton-fade-enter-active,
        .skeleton-fade-leave-active {
            transition: opacity 0.3s ease;
        }
        
        .skeleton-fade-enter-from,
        .skeleton-fade-leave-to {
            opacity: 0;
        }
    `;
    
    const styleElement = document.createElement('style');
    styleElement.textContent = styles;
    document.head.appendChild(styleElement);
    
    console.log('✅ 骨架屏样式已注入');
}

// ===== 导出工具函数 =====
window.SkeletonUtils = {
    createSkeleton,
    createCardSkeleton,
    createListSkeleton,
    createChartSkeleton,
    createTableSkeleton,
    injectSkeletonStyles
};

// ===== 自动初始化 =====
if (typeof Alpine !== 'undefined') {
    Alpine.data('skeletonLoader', skeletonLoader);
    console.log('✅ 骨架屏组件已注册到 Alpine.js');
}

// 页面加载时注入样式
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectSkeletonStyles);
} else {
    injectSkeletonStyles();
}
