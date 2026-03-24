/**
 * 网页小宠物 - 陪伴用户浏览网页的可爱小伙伴
 * 功能：可触摸、可喂食、会动、有状态
 * 
 * 状态系统：
 * - 心情：开心、普通、困倦、不开心
 * - 饥饿度：0-100 (0 为饱，100 为饿)
 * - 活力值：0-100 (活力越高越活跃)
 * - 亲密度：0-100 (互动越多越亲密)
 */

class VirtualPet {
    constructor(options = {}) {
        // 默认配置
        this.config = {
            containerId: options.containerId || 'virtual-pet-container',
            petName: options.petName || '汪汪',
            petType: options.petType || 'dog', // dog, cat, rabbit
            autoHideTimeout: options.autoHideTimeout || 60000, // 60 秒无操作自动隐藏
            animationSpeed: options.animationSpeed || 'normal', // slow, normal, fast
            ...options
        };

        // 宠物状态
        this.state = {
            mood: 'happy', // happy, normal, sleepy, sad
            hunger: 30, // 0-100
            energy: 80, // 0-100
            affection: 50, // 0-100
            isSleeping: false,
            isVisible: true,
            lastInteraction: Date.now()
        };

        // DOM 元素
        this.petElement = null;
        this.container = null;
        this.bubbleElement = null;

        // 初始化
        this.init();
    }

    /**
     * 初始化宠物
     */
    init() {
        // 创建容器
        this.createContainer();
        
        // 创建宠物元素
        this.createPet();
        
        // 创建对话气泡
        this.createBubble();
        
        // 绑定事件
        this.bindEvents();
        
        // 启动状态循环
        this.startStateLoop();
        
        // 加载保存的状态
        this.loadState();
        
        console.log('🐶 小宠物已初始化！');
    }

    /**
     * 创建容器
     */
    createContainer() {
        this.container = document.createElement('div');
        this.container.id = this.config.containerId;
        this.container.className = 'virtual-pet-container';
        document.body.appendChild(this.container);
    }

    /**
     * 创建宠物元素
     */
    createPet() {
        const petTypes = {
            dog: {
                emoji: '🐶',
                name: '汪汪',
                color: '#FFB347'
            },
            cat: {
                emoji: '🐱',
                name: '喵喵',
                color: '#FFB6C1'
            },
            rabbit: {
                emoji: '🐰',
                name: '兔兔',
                color: '#DDA0DD'
            }
        };

        const petInfo = petTypes[this.config.petType] || petTypes.dog;

        this.petElement = document.createElement('div');
        this.petElement.className = 'virtual-pet';
        this.petElement.innerHTML = `
            <div class="pet-body" style="background-color: ${petInfo.color}">
                <div class="pet-emoji">${petInfo.emoji}</div>
                <div class="pet-name">${this.config.petName || petInfo.name}</div>
                <div class="pet-status-indicators">
                    <div class="status-bar hunger-bar" title="饥饿度">
                        <div class="status-fill" style="width: ${this.state.hunger}%"></div>
                    </div>
                    <div class="status-bar energy-bar" title="活力值">
                        <div class="status-fill" style="width: ${this.state.energy}%"></div>
                    </div>
                </div>
            </div>
            <div class="pet-actions">
                <button class="action-btn" data-action="feed" title="喂食">🍖</button>
                <button class="action-btn" data-action="play" title="玩耍">🎾</button>
                <button class="action-btn" data-action="pet" title="抚摸">❤️</button>
                <button class="action-btn" data-action="sleep" title="睡觉">💤</button>
            </div>
        `;

        this.container.appendChild(this.petElement);
    }

    /**
     * 创建对话气泡
     */
    createBubble() {
        this.bubbleElement = document.createElement('div');
        this.bubbleElement.className = 'pet-bubble';
        this.bubbleElement.innerHTML = '<span class="bubble-text">你好呀！我是你的小宠物~</span>';
        this.container.appendChild(this.bubbleElement);
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 点击宠物
        this.petElement.addEventListener('click', (e) => {
            if (!e.target.classList.contains('action-btn')) {
                this.handlePetClick();
            }
        });

        // 动作按钮
        this.petElement.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                this.performAction(action);
            });
        });

        // 鼠标悬停
        this.petElement.addEventListener('mouseenter', () => {
            this.showBubble('想要和我玩吗？');
        });

        // 页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.hide();
            } else {
                this.show();
            }
        });

        // 监听用户活动
        let userActivityTimer;
        ['mousemove', 'keydown', 'click', 'scroll'].forEach(event => {
            document.addEventListener(event, () => {
                clearTimeout(userActivityTimer);
                userActivityTimer = setTimeout(() => {
                    this.checkAutoHide();
                }, this.config.autoHideTimeout);
            });
        });
    }

    /**
     * 处理宠物点击
     */
    handlePetClick() {
        if (this.state.isSleeping) {
            this.showBubble('zzz... 正在睡觉中...');
            return;
        }

        // 播放动画
        this.playAnimation('bounce');
        
        // 增加亲密度
        this.updateState({ affection: Math.min(100, this.state.affection + 2) });
        
        // 随机反应
        const reactions = [
            '好开心！',
            '再来一次！',
            '嘿嘿嘿~',
            '最喜欢你了！',
            '汪！'
        ];
        const reaction = reactions[Math.floor(Math.random() * reactions.length)];
        this.showBubble(reaction);
    }

    /**
     * 执行动作
     */
    performAction(action) {
        if (this.state.isSleeping && action !== 'sleep') {
            this.showBubble('zzz... 别吵我睡觉...');
            return;
        }

        switch (action) {
            case 'feed':
                this.feed();
                break;
            case 'play':
                this.play();
                break;
            case 'pet':
                this.pet();
                break;
            case 'sleep':
                this.toggleSleep();
                break;
        }
    }

    /**
     * 喂食
     */
    feed() {
        if (this.state.hunger <= 10) {
            this.showBubble('已经吃饱啦！');
            return;
        }

        this.playAnimation('eat');
        this.updateState({
            hunger: Math.max(0, this.state.hunger - 20),
            energy: Math.min(100, this.state.energy + 5)
        });

        const foods = ['好吃的！', '美味！', '嗷呜~', '还要吃！'];
        this.showBubble(foods[Math.floor(Math.random() * foods.length)]);
        
        this.saveState();
    }

    /**
     * 玩耍
     */
    play() {
        if (this.state.energy < 20) {
            this.showBubble('好累...不想动...');
            return;
        }

        this.playAnimation('play');
        this.updateState({
            energy: Math.max(0, this.state.energy - 15),
            hunger: Math.min(100, this.state.hunger + 10),
            mood: 'happy',
            affection: Math.min(100, this.state.affection + 5)
        });

        const plays = ['好开心！', '真好玩！', '再来一次！', '嘿嘿~'];
        this.showBubble(plays[Math.floor(Math.random() * plays.length)]);
        
        this.saveState();
    }

    /**
     * 抚摸
     */
    pet() {
        this.playAnimation('happy');
        this.updateState({
            mood: 'happy',
            affection: Math.min(100, this.state.affection + 3)
        });

        const pets = ['好舒服~', '喜欢主人！', '咕噜咕噜~', '蹭蹭~'];
        this.showBubble(pets[Math.floor(Math.random() * pets.length)]);
        
        this.saveState();
    }

    /**
     * 切换睡眠状态
     */
    toggleSleep() {
        this.state.isSleeping = !this.state.isSleeping;
        
        if (this.state.isSleeping) {
            this.petElement.classList.add('sleeping');
            this.showBubble('晚安~ zzz');
            this.playAnimation('sleep');
        } else {
            this.petElement.classList.remove('sleeping');
            this.showBubble('睡醒啦！精神满满！');
            this.updateState({
                energy: Math.min(100, this.state.energy + 30)
            });
        }
        
        this.saveState();
    }

    /**
     * 播放动画
     */
    playAnimation(animationName) {
        this.petElement.classList.add(`animate-${animationName}`);
        
        setTimeout(() => {
            this.petElement.classList.remove(`animate-${animationName}`);
        }, 1000);
    }

    /**
     * 显示对话气泡
     */
    showBubble(text, duration = 3000) {
        const bubbleText = this.bubbleElement.querySelector('.bubble-text');
        bubbleText.textContent = text;
        this.bubbleElement.classList.add('show');

        setTimeout(() => {
            this.bubbleElement.classList.remove('show');
        }, duration);
    }

    /**
     * 更新状态
     */
    updateState(newState) {
        Object.assign(this.state, newState);
        this.updateUI();
        this.checkMoodChange();
    }

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
        
        this.updateMoodDisplay();
    }

    /**
     * 更新心情显示
     */
    updateMoodDisplay() {
        const moods = {
            happy: '😊',
            normal: '😐',
            sleepy: '😴',
            sad: '😢'
        };
        
        const petEmoji = this.petElement.querySelector('.pet-emoji');
        const baseEmoji = petEmoji.textContent;
        
        // 临时显示心情表情
        petEmoji.textContent = moods[this.state.mood];
        
        setTimeout(() => {
            petEmoji.textContent = baseEmoji;
        }, 2000);
    }

    /**
     * 更新 UI
     */
    updateUI() {
        // 更新状态条
        const hungerBar = this.petElement.querySelector('.hunger-bar .status-fill');
        const energyBar = this.petElement.querySelector('.energy-bar .status-fill');
        
        hungerBar.style.width = `${this.state.hunger}%`;
        energyBar.style.width = `${this.state.energy}%`;
        
        // 根据状态改变颜色
        hungerBar.className = 'status-fill ' + 
            (this.state.hunger > 70 ? 'critical' : this.state.hunger > 40 ? 'warning' : 'good');
        energyBar.className = 'status-fill ' + 
            (this.state.energy < 30 ? 'critical' : this.state.energy < 60 ? 'warning' : 'good');
    }

    /**
     * 启动状态循环
     */
    startStateLoop() {
        // 每 10 秒更新一次状态
        setInterval(() => {
            if (!this.state.isSleeping) {
                this.updateState({
                    hunger: Math.min(100, this.state.hunger + 1),
                    energy: Math.max(0, this.state.energy - 0.5)
                });
            }
        }, 10000);

        // 每分钟保存一次状态
        setInterval(() => {
            this.saveState();
        }, 60000);
    }

    /**
     * 检查自动隐藏
     */
    checkAutoHide() {
        const idleTime = Date.now() - this.state.lastInteraction;
        if (idleTime >= this.config.autoHideTimeout && this.state.isVisible) {
            this.hide();
        }
    }

    /**
     * 隐藏宠物
     */
    hide() {
        this.petElement.classList.add('hidden');
        this.bubbleElement.classList.add('hidden');
        this.state.isVisible = false;
        
        // 显示召唤按钮
        this.showSummonButton();
    }

    /**
     * 显示宠物
     */
    show() {
        this.petElement.classList.remove('hidden');
        this.bubbleElement.classList.remove('hidden');
        this.state.isVisible = true;
        
        // 隐藏召唤按钮
        const summonBtn = document.getElementById('summon-pet-btn');
        if (summonBtn) {
            summonBtn.remove();
        }
    }

    /**
     * 显示召唤按钮
     */
    showSummonButton() {
        const summonBtn = document.createElement('button');
        summonBtn.id = 'summon-pet-btn';
        summonBtn.className = 'summon-pet-btn';
        summonBtn.innerHTML = '🐶';
        summonBtn.title = '召唤小宠物';
        summonBtn.onclick = () => this.show();
        document.body.appendChild(summonBtn);
    }

    /**
     * 保存状态到本地存储
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
    }

    /**
     * 从本地存储加载状态
     */
    loadState() {
        try {
            const savedState = localStorage.getItem('virtualPetState');
            if (savedState) {
                const parsed = JSON.parse(savedState);
                // 计算离线期间的时间流逝
                const offlineTime = Date.now() - (parsed.lastSave || Date.now());
                const hoursOffline = offlineTime / (1000 * 60 * 60);
                
                // 根据离线时间增加饥饿度
                const hungerIncrease = Math.min(50, hoursOffline * 10);
                parsed.hunger = Math.min(100, parsed.hunger + hungerIncrease);
                
                // 如果离线时间长，减少能量
                const energyDecrease = Math.min(50, hoursOffline * 5);
                parsed.energy = Math.max(0, parsed.energy - energyDecrease);
                
                Object.assign(this.state, parsed);
                this.updateUI();
                this.checkMoodChange();
            }
        } catch (e) {
            console.warn('无法加载宠物状态:', e);
        }
    }
}

// 页面加载完成后初始化宠物
document.addEventListener('DOMContentLoaded', () => {
    // 创建全局实例
    window.virtualPet = new VirtualPet({
        petName: '汪汪',
        petType: 'dog',
        autoHideTimeout: 60000
    });
});

// 导出类（供外部使用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VirtualPet;
}
