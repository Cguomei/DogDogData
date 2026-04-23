/**
 * 图表页面 Alpine.js 组件
 * 用于增强图表页面的交互功能
 */

// ===== 图表页面组件 =====
function chartPage(chartType, chartTitle) {
    return {
        chartType,
        chartTitle,
        isLoading: true,
        hasError: false,
        errorMessage: '',
        chartData: null,
        refreshInterval: null,
        autoRefreshEnabled: false,

        async init() {
            console.log(`✅ 图表页面组件已初始化: ${this.chartType}`);
            
            // 加载图表数据
            await this.loadChart();
            
            // 监听页面可见性变化
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden && this.autoRefreshEnabled) {
                    this.refresh();
                }
            });
        },

        async loadChart() {
            this.isLoading = true;
            this.hasError = false;
            
            try {
                const response = await fetch(`/api/chart/${this.chartType}/data`);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                this.chartData = await response.json();
                
                // 渲染图表
                this.renderChart();
                
            } catch (error) {
                console.error('加载图表失败:', error);
                this.hasError = true;
                this.errorMessage = `加载失败: ${error.message}`;
            } finally {
                this.isLoading = false;
            }
        },

        renderChart() {
            if (!this.chartData || !window.echarts) {
                console.warn('图表数据或 ECharts 未就绪');
                return;
            }
            
            const chartDom = document.getElementById('chart-container');
            if (!chartDom) {
                console.error('图表容器不存在');
                return;
            }
            
            const myChart = echarts.init(chartDom);
            
            // 根据图表类型配置
            const option = this.getChartOption();
            myChart.setOption(option);
            
            // 响应式调整
            window.addEventListener('resize', () => {
                myChart.resize();
            });
            
            console.log('✅ 图表渲染成功');
        },

        getChartOption() {
            // 这里应该根据实际的 chartData 生成 ECharts 配置
            // 示例配置
            return {
                title: {
                    text: this.chartTitle,
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: 'category',
                    data: this.chartData.x_data || []
                },
                yAxis: {
                    type: 'value'
                },
                series: [{
                    data: this.chartData.y_data || [],
                    type: this.getSeriesType()
                }]
            };
        },

        getSeriesType() {
            const typeMap = {
                'scatter': 'scatter',
                'line': 'line',
                'bar': 'bar',
                'pie': 'pie'
            };
            return typeMap[this.chartType] || 'bar';
        },

        async refresh() {
            await this.loadChart();
            
            // 显示刷新提示
            this.showNotification('图表已刷新', 'success');
        },

        toggleAutoRefresh() {
            this.autoRefreshEnabled = !this.autoRefreshEnabled;
            
            if (this.autoRefreshEnabled) {
                // 每 30 秒自动刷新
                this.refreshInterval = setInterval(() => {
                    this.refresh();
                }, 30000);
                
                this.showNotification('自动刷新已开启（30秒）', 'info');
            } else {
                clearInterval(this.refreshInterval);
                this.showNotification('自动刷新已关闭', 'info');
            }
        },

        exportChart(format = 'png') {
            const chartDom = document.getElementById('chart-container');
            if (!chartDom) return;
            
            const myChart = echarts.getInstanceByDom(chartDom);
            if (!myChart) return;
            
            const url = myChart.getDataURL({
                type: format,
                pixelRatio: 2,
                backgroundColor: '#fff'
            });
            
            // 下载图片
            const link = document.createElement('a');
            link.download = `${this.chartTitle}_${new Date().getTime()}.${format}`;
            link.href = url;
            link.click();
            
            this.showNotification('图表已导出', 'success');
        },

        showNotification(message, type = 'info') {
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

        destroy() {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
        }
    };
}

// ===== 图表列表组件 =====
function chartList() {
    return {
        charts: [],
        isLoading: true,
        searchQuery: '',
        selectedCategory: 'all',
        
        categories: [
            { value: 'all', label: '全部', icon: '📊' },
            { value: 'basic', label: '基础图表', icon: '📈' },
            { value: 'advanced', label: '高级分析', icon: '🔍' },
            { value: 'map', label: '地图', icon: '🗺️' }
        ],

        async init() {
            console.log('✅ 图表列表组件初始化');
            await this.loadCharts();
        },

        async loadCharts() {
            this.isLoading = true;
            
            try {
                const response = await fetch('/api/charts/list');
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                this.charts = await response.json();
                console.log(`✅ 加载了 ${this.charts.length} 个图表`);
            } catch (error) {
                console.error('加载图表列表失败:', error);
                // 使用默认数据作为后备
                this.charts = this.getDefaultCharts();
            } finally {
                this.isLoading = false;
            }
        },
        
        getDefaultCharts() {
            return [
                {
                    id: 'scatter',
                    title: '价格散点图',
                    description: '展示狗狗价格分布情况',
                    category: 'basic'
                },
                {
                    id: 'line',
                    title: '体重折线图',
                    description: '展示狗狗体重趋势',
                    category: 'basic'
                },
                {
                    id: 'bar',
                    title: '级别柱状图',
                    description: '展示不同级别的狗狗数量',
                    category: 'basic'
                },
                {
                    id: 'hist',
                    title: 'TOP10 直方图',
                    description: '热门狗狗品种和店铺排行',
                    category: 'advanced'
                },
                {
                    id: 'funnel',
                    title: '价格漏斗图',
                    description: '价格区间转化分析',
                    category: 'advanced'
                },
                {
                    id: 'map',
                    title: '世界地图',
                    description: '狗狗家乡分布地图',
                    category: 'map'
                }
            ];
        },

        get filteredCharts() {
            let filtered = this.charts;
            
            // 按分类筛选
            if (this.selectedCategory !== 'all') {
                filtered = filtered.filter(chart => chart.category === this.selectedCategory);
            }
            
            // 按搜索词筛选
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                filtered = filtered.filter(chart => 
                    chart.title.toLowerCase().includes(query) ||
                    chart.description.toLowerCase().includes(query)
                );
            }
            
            return filtered;
        },

        navigateToChart(chartId) {
            console.log(`导航到图表: ${chartId}`);
            window.location.href = `/chart/${chartId}`;
        }
    };
}

// ===== 注册组件 =====
if (typeof Alpine !== 'undefined') {
    Alpine.data('chartPage', chartPage);
    Alpine.data('chartList', chartList);
    console.log('✅ 图表页面组件已注册');
}

// 导出工具函数
window.ChartUtils = {
    chartPage,
    chartList
};
