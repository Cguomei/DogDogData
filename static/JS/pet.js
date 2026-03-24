/**
 * 网页小宠物 - 2.5D 增强版
 * 基于序列帧动画的伪 3D 效果
 * 
 * 功能特性：
 * - 2.5D 旋转视角（鼠标移动控制）
 * - 序列帧动画（吃饭、抚摸等）
 * - 状态系统（饥饿、活力、心情）
 * - 交互反馈（点击、悬停）
 */

class VirtualPet {
    constructor(options = {}) {
        // 默认配置
        this.config = {
            containerId: options.containerId || 'virtual-pet-container',
            petName: options.petName || '汪汪',
            petType: options.petType || 'dog',
            autoHideTimeout: options.autoHideTimeout || 60000,
            spritePath: options.spritePath || '/static/img/pet_sprites/',
            ...options
        };

        // 宠物状态
        this.state = {
            mood: 'happy',
            hunger: 30,
            energy: 80,
            affection: 50,
            isSleeping: false,
            isVisible: true,
            lastInteraction: Date.now(),
            currentAction: null,
            rotationAngle: 0 // -45 到 45 度
        };

        // DOM 元素
        this.petElement = null;
        this.container = null;
        this.bubbleElement = null;
        this.spriteElement = null;

        // 动画帧管理
        this.animationFrames = {};
        this.currentFrame = 0;
        this.animationInterval = null;

        // 初始化
        this.init();
    }

    /**
     * 初始化宠物
     */
    init() {
        // 创建容器
        this.createContainer();
        
        // 加载精灵图
        this.loadSprites();
        
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
        
        console.log('🐶 2.5D 小宠物已初始化！');
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
     * 加载精灵图资源
     */
    async loadSprites() {
        const spritePath = this.config.spritePath;
        
        // 预加载所有精灵图
        const spritesToLoad = [
            { name: 'eat_cycle', url: spritePath + 'eat_cycle.png' },
            { name: 'pet_cycle', url: spritePath + 'pet_cycle.png' },
            { name: 'eating_rotation', url: spritePath + 'eating_rotation.png' },
            { name: 'petting_smooth', url: spritePath + 'petting_smooth.png' },
            { name: 'idle', url: spritePath + 'idle.png' }
        ];

        const loadPromises = spritesToLoad.map(sprite => {
            return new Promise((resolve) => {
                const img = new Image();
                img.src = sprite.url;
                img.onload = () => {
                    this.animationFrames[sprite.name] = img;
                    console.log(`✅ 加载精灵图：${sprite.name}`);
                    resolve(img);
                };
                img.onerror = () => {
                    console.warn(`⚠️ 精灵图加载失败：${sprite.url}`);
                    resolve(null);
                };
            });
        });

        await Promise.all(loadPromises);
        console.log('🎨 所有精灵图加载完成');
    }

    /**
     * 创建宠物元素（2.5D 版本）
     */
    createPet() {
        this.petElement = document.createElement('div');
        this.petElement.className = 'pet-body-2d5';
        
        // 创建精灵图显示元素
        this.spriteElement = document.createElement('div');
        this.spriteElement.className = 'pet-sprite';
        
        // 设置默认显示（待机状态）
        if (this.animationFrames['idle']) {
            this.spriteElement.style.backgroundImage = `url(${this.animationFrames['idle'].src})`;
        } else {
            // 如果精灵图未加载，使用 emoji 占位
            this.spriteElement.innerHTML = `
                <div class="pet-emoji">🐶</div>
                <div class="pet-name">${this.config.petName}</div>
            `;
        }
        
        // 添加投影效果
        const shadowElement = document.createElement('div');
        shadowElement.className = 'pet-shadow';
        
        this.petElement.appendChild(this.spriteElement);
        this.petElement.appendChild(shadowElement);
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
     * 播放序列帧动画
     */
    playSpriteAnimation(spriteName, frameCount, fps = 10, loop = true) {
        const spriteImg = this.animationFrames[spriteName];
        if (!spriteImg || !this.spriteElement) return;

        // 计算单帧尺寸（假设精灵图是横向排列）
        const frameWidth = spriteImg.width / frameCount;
        const frameHeight = spriteImg.height;

        let currentFrame = 0;

        // 清除之前的动画
        if (this.animationInterval) {
            clearInterval(this.animationInterval);
        }

        // 设置背景图为精灵图
        this.spriteElement.style.backgroundImage = `url(${spriteImg.src})`;

        // 开始播放动画
        this.animationInterval = setInterval(() => {
            // 计算背景图位置
            const offsetX = -(currentFrame * frameWidth);
            this.spriteElement.style.backgroundPosition = `${offsetX}px 0`;
            this.spriteElement.style.backgroundSize = `${frameCount * 100}% 100%`;

            currentFrame++;

            if (currentFrame >= frameCount) {
                if (loop) {
                    currentFrame = 0;
                } else {
                    clearInterval(this.animationInterval);
                    this.animationInterval = null;
                    return;
                }
            }
        }, 1000 / fps);
    }

    /**
     * 更新 2.5D 旋转角度
     */
    updateRotation(angleX = 0, angleY = 0) {
        if (!this.petElement) return;

        // 限制旋转角度在合理范围内
        angleX = Math.max(-30, Math.min(30, angleX));
        angleY = Math.max(-45, Math.min(45, angleY));

        // 应用旋转变换
        this.petElement.style.transform = `rotateX(${angleX}deg) rotateY(${angleY}deg)`;

        // 根据旋转角度调整亮度模拟光照
        const brightness = 1 + (Math.abs(angleY) / 90) * 0.2;
        this.spriteElement.style.filter = `brightness(${brightness}) drop-shadow(0 8px 16px rgba(0, 0, 0, 0.3))`;
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 鼠标移动控制视角（2.5D 核心功能）
        document.addEventListener('mousemove', (e) => {
            if (!this.state.isVisible || this.state.isSleeping) return;

            const { clientX, clientY } = e;
            const { innerWidth, innerHeight } = window;

            // 计算鼠标位置相对于屏幕中心的偏移
            const offsetX = (clientX - innerWidth / 2) / (innerWidth / 2);
            const offsetY = (clientY - innerHeight / 2) / (innerHeight / 2);

            // 转换为旋转角度（-45 到 45 度）
            const angleY = offsetX * 45;
            const angleX = -offsetY * 30;

            // 平滑更新旋转
            this.updateRotation(angleX, angleY);
        });

        // 点击宠物
        this.petElement.addEventListener('click', (e) => {
            if (!e.target.classList.contains('action-btn')) {
                this.handlePetClick();
            }
        });

        // 双击触发特殊动作
        this.petElement.addEventListener('dblclick', () => {
            this.performAction('spin');
        });

        // 鼠标悬停
        this.petElement.addEventListener('mouseenter', () => {
            this.showBubble('想要和我玩吗？');
        });

        // 鼠标离开
        this.petElement.addEventListener('mouseleave', () => {
            if (!this.state.currentAction) {
                this.playSpriteAnimation('idle', 1, 1, true);
            }
        });

        // 页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.hide();
            } else {
                this.show();
            }
        });
        
        // 监听召唤宠物事件
        window.addEventListener('summonPet', () => {
            this.show();
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

        // 播放点击涟漪特效
        this.createClickRipple();
        
        // 播放弹跳动画
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
     * 创建点击涟漪特效
     */
    createClickRipple() {
        const ripple = document.createElement('div');
        ripple.className = 'pet-click-ripple';
        this.petElement.appendChild(ripple);
        
        // 动画结束后移除
        setTimeout(() => {
            ripple.remove();
        }, 600);
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
            case 'spin':
                // 双击旋转（2.5D 特效）
                this.spin3D();
                break;
        }
    }

    /**
     * 喂食（播放吃饭动画）
     */
    feed() {
        if (this.state.hunger <= 10) {
            this.showBubble('已经吃饱啦！');
            return;
        }

        // 播放吃饭序列帧动画
        this.playSpriteAnimation('eat_cycle', 4, 12, true);
        this.state.currentAction = 'feed';

        setTimeout(() => {
            this.updateState({
                hunger: Math.max(0, this.state.hunger - 20),
                energy: Math.min(100, this.state.energy + 5)
            });
            this.state.currentAction = null;
            this.playSpriteAnimation('idle', 1, 1, true);
        }, 2000);

        const foods = ['好吃的！', '美味！', '嗷呜~', '还要吃！'];
        this.showBubble(foods[Math.floor(Math.random() * foods.length)]);
        
        this.saveState();
    }

    /**
     * 玩耍（播放抚摸动画）
     */
    play() {
        if (this.state.energy < 20) {
            this.showBubble('好累...不想动...');
            return;
        }

        // 播放平滑过渡动画
        this.playSpriteAnimation('petting_smooth', 19, 15, true);
        this.state.currentAction = 'play';

        setTimeout(() => {
            this.updateState({
                energy: Math.max(0, this.state.energy - 15),
                hunger: Math.min(100, this.state.hunger + 10),
                mood: 'happy',
                affection: Math.min(100, this.state.affection + 5)
            });
            this.state.currentAction = null;
            this.playSpriteAnimation('idle', 1, 1, true);
        }, 2000);

        const plays = ['好开心！', '真好玩！', '再来一次！', '嘿嘿~'];
        this.showBubble(plays[Math.floor(Math.random() * plays.length)]);
        
        this.saveState();
    }

    /**
     * 抚摸（舒适反应）
     */
    pet() {
        // 添加 CSS 动画类
        this.spriteElement.classList.add('animate-pet');
        
        this.updateState({
            mood: 'happy',
            affection: Math.min(100, this.state.affection + 3)
        });

        const pets = ['好舒服~', '喜欢主人！', '咕噜咕噜~', '蹭蹭~'];
        this.showBubble(pets[Math.floor(Math.random() * pets.length)]);
        
        setTimeout(() => {
            this.spriteElement.classList.remove('animate-pet');
        }, 2000);
        
        this.saveState();
    }

    /**
     * 3D 旋转特效（双击触发）
     */
    spin3D() {
        let angle = 0;
        const spinInterval = setInterval(() => {
            angle += 30;
            this.updateRotation(0, angle);
            
            if (angle >= 360) {
                clearInterval(spinInterval);
                this.updateRotation(0, 0);
            }
        }, 50);

        this.showBubble('哇！转圈圈！');
        this.updateState({ affection: Math.min(100, this.state.affection + 10) });
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
    // 延迟 500ms 初始化，确保页面完全加载
    setTimeout(() => {
        try {
            // 创建全局实例
            window.virtualPet = new VirtualPet({
                petName: '汪汪',
                petType: 'dog',
                autoHideTimeout: 60000,
                spritePath: '/static/img/pet_sprites/'
            });
            console.log('✅ 小宠物初始化成功');
        } catch (error) {
            console.error('❌ 小宠物初始化失败:', error);
        }
    }, 500);
});

// 导出类（供外部使用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VirtualPet;
}
