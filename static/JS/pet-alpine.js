/**
 * 网页小宠物 - Alpine.js 重构版 v1.0.0
 * 
 * 优势：
 * - 响应式数据绑定，无需手动操作 DOM
 * - 代码更简洁，易维护
 * - 与现有 HTML 无缝集成
 * - 体积小（~15KB）
 * 
 * 使用方法：
 * 1. 在 base.html 中引入 Alpine.js CDN
 * 2. 使用 x-data 指令初始化宠物组件
 */

// Alpine.js 宠物组件工厂函数
function petComponent(options = {}) {
    return {
        // ===== 配置项 =====
        config: {
            petName: options.petName || '团团',
            autoHideTimeout: options.autoHideTimeout || 60000,
            ...options
        },

        // ===== 响应式状态 =====
        state: {
            mood: 'happy',
            hunger: 30,
            energy: 80,
            affection: 50,
            isSleeping: false,
            isVisible: true,
            currentAction: null,
            showBubble: false,
            bubbleText: ''
        },

        // ===== 生命周期 =====
        init() {
            console.log('🐾 [Alpine Pet] 初始化');
            
            // 加载保存的状态
            this.loadState();
            
            // 启动状态循环
            this.startStateLoop();
            
            // 监听用户活动
            this.bindUserActivity();
            
            // 延迟显示（3秒后出现）
            setTimeout(() => {
                this.state.isVisible = true;
            }, 3000);
        },

        // ===== 交互方法 =====
        
        /**
         * 喂食
         */
        feed() {
            if (this.state.hunger <= 10) {
                this.showBubble('已经吃饱啦！');
                return;
            }

            this.state.currentAction = 'eating';
            this.showBubble(['好吃的！', '美味！', '嗷呜~'][Math.floor(Math.random() * 3)]);

            setTimeout(() => {
                this.state.hunger = Math.max(0, this.state.hunger - 20);
                this.state.energy = Math.min(100, this.state.energy + 5);
                this.state.currentAction = null;
                this.saveState();
            }, 2000);
        },

        /**
         * 抚摸
         */
        pet() {
            this.showBubble(['好舒服~', '喜欢主人！', '咕噜咕噜~'][Math.floor(Math.random() * 3)]);
            this.state.affection = Math.min(100, this.state.affection + 3);
            this.state.mood = 'happy';
            this.saveState();
        },

        /**
         * 玩耍
         */
        play() {
            if (this.state.energy < 20) {
                this.showBubble('好累...不想动...');
                return;
            }

            this.state.currentAction = 'playing';
            this.showBubble(['好开心！', '真好玩！', '再来一次！'][Math.floor(Math.random() * 3)]);

            setTimeout(() => {
                this.state.energy = Math.max(0, this.state.energy - 15);
                this.state.hunger = Math.min(100, this.state.hunger + 10);
                this.state.mood = 'happy';
                this.state.affection = Math.min(100, this.state.affection + 5);
                this.state.currentAction = null;
                this.saveState();
            }, 2000);
        },

        /**
         * 点击宠物
         */
        handleClick() {
            if (this.state.isSleeping) {
                this.showBubble('zzz... 正在睡觉中...');
                return;
            }

            this.showBubble(['好开心！', '再来一次！', '嘿嘿嘿~'][Math.floor(Math.random() * 3)]);
            this.state.affection = Math.min(100, this.state.affection + 2);
        },

        /**
         * 双击旋转
         */
        handleDblClick() {
            if (!this.$refs.petElement) return;
            
            let angle = 0;
            const spinInterval = setInterval(() => {
                angle += 30;
                this.$refs.petElement.style.transform = `rotate(${angle}deg)`;
                
                if (angle >= 360) {
                    clearInterval(spinInterval);
                    this.$refs.petElement.style.transform = 'rotate(0deg)';
                }
            }, 50);

            this.showBubble('哇！转圈圈！');
            this.state.affection = Math.min(100, this.state.affection + 10);
        },

        /**
         * 切换睡眠
         */
        toggleSleep() {
            this.state.isSleeping = !this.state.isSleeping;
            
            if (this.state.isSleeping) {
                this.showBubble('晚安~ zzz');
            } else {
                this.showBubble('睡醒啦！精神满满！');
                this.state.energy = Math.min(100, this.state.energy + 30);
            }
            
            this.saveState();
        },

        /**
         * 隐藏宠物
         */
        hide() {
            this.state.isVisible = false;
            this.showSummonButton();
        },

        /**
         * 显示宠物
         */
        show() {
            this.state.isVisible = true;
            this.hideSummonButton();
        },

        /**
         * 显示对话气泡
         */
        showBubble(text, duration = 3000) {
            this.state.bubbleText = text;
            this.state.showBubble = true;

            setTimeout(() => {
                this.state.showBubble = false;
            }, duration);
        },

        // ===== 状态管理 =====

        /**
         * 更新心情显示
         */
        get eyeStyle() {
            if (this.state.mood === 'happy') {
                return { rx: '3', ry: '4' };
            } else if (this.state.mood === 'sad') {
                return { rx: '1.5', ry: '1' };
            } else if (this.state.mood === 'sleepy') {
                return { rx: '3', ry: '1.2' };
            }
            return { rx: '2.2', ry: '2.8' };
        },

        /**
         * 获取宠物 CSS 类
         */
        get petClasses() {
            return {
                'virtual-pet': true,
                'hidden': !this.state.isVisible,
                'sleeping': this.state.isSleeping,
                'eating': this.state.currentAction === 'eating',
                'playing': this.state.currentAction === 'playing'
            };
        },

        // ===== 持久化 =====

        /**
         * 保存状态
         */
        saveState() {
            try {
                localStorage.setItem('virtualPetState', JSON.stringify({
                    ...this.state,
                    lastSave: Date.now()
                }));
            } catch (e) {
                console.warn('无法保存宠物状态:', e);
            }
        },

        /**
         * 加载状态
         */
        loadState() {
            try {
                const savedState = localStorage.getItem('virtualPetState');
                if (savedState) {
                    const parsed = JSON.parse(savedState);
                    
                    // 计算离线时间流逝
                    const offlineTime = Date.now() - (parsed.lastSave || Date.now());
                    const hoursOffline = offlineTime / (1000 * 60 * 60);
                    
                    // 增加饥饿度
                    parsed.hunger = Math.min(100, parsed.hunger + Math.min(50, hoursOffline * 10));
                    // 减少能量
                    parsed.energy = Math.max(0, parsed.energy - Math.min(50, hoursOffline * 5));
                    
                    Object.assign(this.state, parsed);
                }
            } catch (e) {
                console.warn('无法加载宠物状态:', e);
            }
        },

        // ===== 后台任务 =====

        /**
         * 启动状态循环
         */
        startStateLoop() {
            // 每 10 秒更新状态
            setInterval(() => {
                if (!this.state.isSleeping) {
                    this.state.hunger = Math.min(100, this.state.hunger + 1);
                    this.state.energy = Math.max(0, this.state.energy - 0.5);
                    this.checkMoodChange();
                }
            }, 10000);

            // 每分钟保存一次
            setInterval(() => {
                this.saveState();
            }, 60000);
        },

        /**
         * 检查心情变化
         */
        checkMoodChange() {
            if (this.state.isSleeping) {
                this.state.mood = 'sleepy';
            } else if (this.state.hunger > 80) {
                this.state.mood = 'sad';
            } else if (this.state.energy < 30) {
                this.state.mood = 'sleepy';
            } else if (this.state.affection > 80) {
                this.state.mood = 'happy';
            } else {
                this.state.mood = 'normal';
            }
        },

        /**
         * 绑定用户活动监听
         */
        bindUserActivity() {
            let userActivityTimer;
            ['mousemove', 'keydown', 'click', 'scroll'].forEach(event => {
                document.addEventListener(event, () => {
                    clearTimeout(userActivityTimer);
                    userActivityTimer = setTimeout(() => {
                        this.checkAutoHide();
                    }, this.config.autoHideTimeout);
                });
            });
        },

        /**
         * 检查自动隐藏
         */
        checkAutoHide() {
            // 简化版本，暂不实现
        },

        /**
         * 显示召唤按钮
         */
        showSummonButton() {
            const existingBtn = document.getElementById('summon-pet-btn');
            if (existingBtn) return;
            
            const summonBtn = document.createElement('button');
            summonBtn.id = 'summon-pet-btn';
            summonBtn.className = 'summon-pet-btn';
            summonBtn.innerHTML = '🐾';
            summonBtn.title = '召唤小宠物';
            summonBtn.onclick = () => this.show();
            document.body.appendChild(summonBtn);
        },

        /**
         * 隐藏召唤按钮
         */
        hideSummonButton() {
            const summonBtn = document.getElementById('summon-pet-btn');
            if (summonBtn) {
                summonBtn.remove();
            }
        }
    };
}

// 导出组件（供外部使用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = petComponent;
}
