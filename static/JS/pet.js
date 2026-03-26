/**
 * 网页小宠物 - 2D Q 版专业版 v4.0.0
 * 2D Q 版卡通风格，头大身小，治愈系配色
 * 
 * 功能特性：
 * - 严格的单例模式（全局唯一实例）
 * - 2D Q 版 SVG 绘制
 * - 扁平 + 轻微渐变质感
 * - 透明背景（只显示狗狗本身）
 * - 状态系统（饥饿、活力、心情）
 * - 交互反馈（点击、悬停）
 */

// 注意：不再自动初始化，由 base.html 手动初始化

class VirtualPet {
    constructor(options = {}) {
        console.log('🔍 [构造函数] 开始执行，petInitializing:', window.petInitializing, 'petInitDone:', window.petInitDone, 'virtualPet:', !!window.virtualPet);
        
        // 严格防止重复初始化（三重检查）
        if (window.petInitializing && window.virtualPet) {
            console.error('❌ [构造函数] 宠物正在初始化中，拒绝重复创建！');
            return;
        }
        if (window.petInitDone && window.virtualPet) {
            console.error('❌ [构造函数] 宠物已经初始化，拒绝重复创建！');
            return;
        }
        
        console.log('✅ [构造函数] 检查通过，开始初始化');
        
        // 默认配置
        this.config = {
            containerId: options.containerId || 'virtual-pet-container',
            petName: options.petName || '团团',  // Q 版名字
            petType: options.petType || 'q-version',  // Q 版类型
            autoHideTimeout: options.autoHideTimeout || 60000,
            spritePath: options.spritePath || '/static/img/pet_sprites/',
            ...options
        };
        console.log('🔧 [构造函数] 配置:', this.config);

        // 宠物状态
        this.state = {
            mood: 'happy',
            hunger: 30,
            energy: 80,
            affection: 50,
            isSleeping: false,
            isVisible: true,
            lastInteraction: Date.now(),
            currentAction: null
        };
        console.log('🔧 [构造函数] 状态:', this.state);

        // DOM 元素
        this.petElement = null;
        this.container = null;
        this.bubbleElement = null;
        this.spriteElement = null;

        // 动画帧管理
        this.animationFrames = {};
        this.currentFrame = 0;
        this.animationInterval = null;
        
        // 设置标志位
        window.petInitDone = true;
        console.log('✅ [构造函数] 设置 petInitDone = true');
        
        console.log('🚀 [构造函数] 开始调用 init()');
        // 初始化
        this.init();
    }

    /**
     * 初始化宠物（异步版本）
     */
    async init() {
        console.log('🚀 [init] 开始执行');
        // 1. 创建容器
        console.log('📦 [init] 步骤 1: 创建容器');
        this.createContainer();
        
        // 2. 先加载精灵图（确保可用）
        console.log('🎨 [init] 步骤 2: 加载精灵图');
        await this.loadSprites();
        
        // 3. 图片加载完成后再创建宠物
        console.log('🐾 [init] 步骤 3: 创建宠物元素');
        this.createPet();
        
        // 4. 创建对话气泡
        console.log('💬 [init] 步骤 4: 创建对话气泡');
        this.createBubble();
        
        // 5. 绑定事件
        console.log('🎯 [init] 步骤 5: 绑定事件');
        this.bindEvents();
        
        // 6. 启动状态循环
        console.log('⏱️ [init] 步骤 6: 启动状态循环');
        this.startStateLoop();
        
        // 7. 加载保存的状态
        console.log('💾 [init] 步骤 7: 加载保存的状态');
        this.loadState();
        
        console.log('✅ [init] 初始化完成');
    }

    /**
     * 创建容器
     */
    createContainer() {
        console.log('📦 [createContainer] 开始执行');
        // 先清理已存在的容器
        const existing = document.getElementById(this.config.containerId);
        if (existing) {
            console.log('🗑️ [createContainer] 发现已存在的容器:', existing);
            existing.remove();
        }
        
        this.container = document.createElement('div');
        this.container.id = this.config.containerId;
        this.container.className = 'virtual-pet-container';
        document.body.appendChild(this.container);
        console.log('✅ [createContainer] 容器创建完成:', this.container);
    }

    /**
     * 加载精灵图资源（2D Q 版 - SVG 绘制）
     */
    async loadSprites() {
        console.log('🎨 宠物显示模式：2D Q 版 SVG');
    }

    /**
     * 创建宠物元素（2D Q 版 SVG 绘制）
     */
    createPet() {
        console.log('🐾 [createPet] 开始创建宠物元素');

        // 先清理容器中已有的宠物
        const existingPets = this.container.querySelectorAll('.virtual-pet');
        console.log('🗑️ [createPet] 发现旧宠物数量:', existingPets.length);
        existingPets.forEach(pet => pet.remove());

        this.petElement = document.createElement('div');
        this.petElement.className = 'virtual-pet';

        // 创建宠物主体（SVG 绘制简笔画侧身小狗风格）
        this.spriteElement = document.createElement('div');
        this.spriteElement.className = 'pet-sprite-svg';
        this.spriteElement.innerHTML = `
          <div class="pet-name-tag">${this.config.petName}</div>
          <svg width="100" height="120" viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <radialGradient id="bodyGrad" cx="50%" cy="40%" r="70%">
                <stop offset="0%" stop-color="#F7D9A3"/>
                <stop offset="100%" stop-color="#E3B87C"/>
              </radialGradient>
              <radialGradient id="earGrad" cx="50%" cy="50%" r="60%">
                <stop offset="0%" stop-color="#D99E4E"/>
                <stop offset="100%" stop-color="#B87A3C"/>
              </radialGradient>
              <linearGradient id="noseGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#4D3522"/>
                <stop offset="100%" stop-color="#2C1D12"/>
              </linearGradient>
            </defs>

            <!-- 身体 -->
            <ellipse cx="50" cy="75" rx="30" ry="26" fill="url(#bodyGrad)" stroke="#B87A3C" stroke-width="1.5"/>
            <ellipse cx="50" cy="80" rx="20" ry="16" fill="#FFEAC5" stroke="#C48B4B" stroke-width="1"/>

            <!-- 后腿 -->
            <ellipse cx="32" cy="96" rx="7" ry="10" fill="#E3B87C" stroke="#B87A3C" stroke-width="1.2"/>
            <ellipse cx="68" cy="96" rx="7" ry="10" fill="#E3B87C" stroke="#B87A3C" stroke-width="1.2"/>

            <!-- 前腿 -->
            <ellipse cx="40" cy="84" rx="5" ry="9" fill="#E3B87C" stroke="#B87A3C" stroke-width="1.2"/>
            <ellipse cx="60" cy="84" rx="5" ry="9" fill="#E3B87C" stroke="#B87A3C" stroke-width="1.2"/>

            <!-- 尾巴（卷曲向上） -->
            <path d="M78 66 L88 60 L84 70 L78 66 Z" fill="#D99E4E" stroke="#B87A3C" stroke-width="1.2"/>
            <path d="M84 62 L92 58 L88 68 L84 62 Z" fill="#E3B87C"/>

            <!-- 头部 -->
            <circle cx="50" cy="43" r="25" fill="url(#bodyGrad)" stroke="#B87A3C" stroke-width="1.5"/>
            <ellipse cx="50" cy="52" rx="14" ry="9" fill="#FFF2DF" stroke="#C48B4B" stroke-width="1"/>

            <!-- 立耳（三角形，像狗耳朵） -->
            <polygon points="26,28 35,8 44,28" fill="url(#earGrad)" stroke="#B87A3C" stroke-width="1.2"/>
            <polygon points="56,28 65,8 74,28" fill="url(#earGrad)" stroke="#B87A3C" stroke-width="1.2"/>
            <polygon points="30,26 35,14 40,26" fill="#F7D9A3"/>
            <polygon points="60,26 65,14 70,26" fill="#F7D9A3"/>

            <!-- 眼睛 -->
            <circle cx="38" cy="41" r="4" fill="white" stroke="#4D3522" stroke-width="1"/>
            <circle cx="62" cy="41" r="4" fill="white" stroke="#4D3522" stroke-width="1"/>
            <ellipse cx="40" cy="43" rx="2.2" ry="2.8" fill="#2C1D12" class="pet-eye"/>
            <ellipse cx="64" cy="43" rx="2.2" ry="2.8" fill="#2C1D12" class="pet-eye"/>
            <circle cx="41" cy="40" r="1" fill="white"/>
            <circle cx="65" cy="40" r="1" fill="white"/>

            <!-- 鼻子 -->
            <ellipse cx="50" cy="57" rx="4.5" ry="3.5" fill="url(#noseGrad)" stroke="#1F130C" stroke-width="1"/>
            <circle cx="47" cy="56" r="1" fill="#1F130C"/>
            <circle cx="53" cy="56" r="1" fill="#1F130C"/>

            <!-- 嘴巴 -->
            <path d="M43 62 Q50 66 57 62" stroke="#B87A3C" stroke-width="1.2" fill="none" stroke-linecap="round"/>

            <!-- 舌头 -->
            <path d="M49 65 L51 65 Q53 69 50 70 Q47 69 49 65 Z" fill="#FF8A7A"/>

            <!-- 腮红 -->
            <circle cx="30" cy="49" r="2" fill="#FFB7A8" opacity="0.6"/>
            <circle cx="70" cy="49" r="2" fill="#FFB7A8" opacity="0.6"/>
          </svg>
        `;
        
        // 创建动作按钮
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'pet-actions';
        actionsDiv.innerHTML = `
            <button class="action-btn" title="喂食">🍖</button>
            <button class="action-btn" title="抚摸">❤️</button>
            <button class="action-btn" title="玩耍">🎾</button>
        `;
        
        // 组装
        this.petElement.appendChild(this.spriteElement);
        this.petElement.appendChild(actionsDiv);
        this.container.appendChild(this.petElement);

        // 绑定按钮事件
        const actionBtns = this.petElement.querySelectorAll('.action-btn');
        actionBtns[0].onclick = () => this.feed();
        actionBtns[1].onclick = () => this.pet();
        actionBtns[2].onclick = () => this.play();
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
     * 播放序列帧动画（可爱版 - 使用 CSS 动画）
     */
    playSpriteAnimation(spriteName, frameCount, fps = 10, loop = true) {
        // 可爱版使用 CSS 动画，不再使用精灵图
        console.log(`🎭 播放动画：${spriteName}`);
    }

    /**
     * 更新 2.5D 旋转角度（可爱版 - 不再使用旋转）
     */
    updateRotation(angleX = 0, angleY = 0) {
        // 可爱版不再支持旋转，保持正面朝向
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

        // 双击宠物 - 特殊动作
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
                this.playAnimation('idle');
            }
        });
        
        // ===== 新增：拖动功能 =====
        let isDragging = false;
        let startX, startY, initialX, initialY;
        
        // 鼠标按下开始拖动
        this.petElement.addEventListener('mousedown', (e) => {
            // 如果点击的是按钮，不拖动
            if (e.target.classList.contains('action-btn')) return;
            
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            
            const rect = this.container.getBoundingClientRect();
            initialX = rect.left;
            initialY = rect.top;
            
            // 添加拖动中样式
            this.petElement.style.cursor = 'grabbing';
        });
        
        // 鼠标移动
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            this.container.style.left = `${initialX + deltaX}px`;
            this.container.style.top = `${initialY + deltaY}px`;
            this.container.style.right = 'auto';  // 清除 right
            this.container.style.bottom = 'auto'; // 清除 bottom
        });
        
        // 鼠标释放停止拖动
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                this.petElement.style.cursor = 'pointer';
                
                // 保存新位置到 localStorage
                const rect = this.container.getBoundingClientRect();
                this.savePetPosition({
                    left: rect.left,
                    top: rect.top
                });
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
            '咕噜~'
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
                // 双击旋转（可爱版 - 简单的 CSS 旋转）
                this.spinCute();
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

        // 播放 CSS 吃饭动画
        this.playAnimation('eat');
        this.state.currentAction = 'feed';

        setTimeout(() => {
            this.updateState({
                hunger: Math.max(0, this.state.hunger - 20),
                energy: Math.min(100, this.state.energy + 5)
            });
            this.state.currentAction = null;
        }, 2000);

        const foods = ['好吃的！', '美味！', '嗷呜~', '还要吃！'];
        this.showBubble(foods[Math.floor(Math.random() * foods.length)]);
        
        this.saveState();
    }

    /**
     * 玩耍（播放玩耍动画）
     */
    play() {
        if (this.state.energy < 20) {
            this.showBubble('好累...不想动...');
            return;
        }

        // 播放 CSS 玩耍动画
        this.playAnimation('happy');
        this.state.currentAction = 'play';

        setTimeout(() => {
            this.updateState({
                energy: Math.max(0, this.state.energy - 15),
                hunger: Math.min(100, this.state.hunger + 10),
                mood: 'happy',
                affection: Math.min(100, this.state.affection + 5)
            });
            this.state.currentAction = null;
        }, 2000);

        const plays = ['好开心！', '真好玩！', '再来一次！', '嘿嘿~'];
        this.showBubble(plays[Math.floor(Math.random() * plays.length)]);
        
        this.saveState();
    }

    /**
     * 抚摸（舒适反应）
     */
    pet() {
        // 添加 CSS 动画
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
     * 旋转动画（可爱版）
     */
    spinCute() {
        if (!this.petElement) return;
        
        let angle = 0;
        const spinInterval = setInterval(() => {
            angle += 30;
            this.petElement.style.transform = `rotate(${angle}deg)`;
            
            if (angle >= 360) {
                clearInterval(spinInterval);
                this.petElement.style.transform = 'rotate(0deg)';
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
        if (!this.spriteElement) return;
        
        // 移除所有动画类
        this.spriteElement.classList.remove('animate-bounce', 'animate-eat', 'animate-happy', 'animate-sleep');
        
        // 添加新的动画类
        this.spriteElement.classList.add(`animate-${animationName}`);
        
        setTimeout(() => {
            this.spriteElement.classList.remove(`animate-${animationName}`);
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
     * 更新心情显示（可爱版 - 改变眼睛表情）
     */
    updateMoodDisplay() {
        const eyes = this.spriteElement?.querySelectorAll('.pet-eye');
        if (!eyes) return;

        if (this.state.mood === 'happy') {
            eyes.forEach(eye => {
                eye.setAttribute('rx', '3');
                eye.setAttribute('ry', '4');
            });
        } else if (this.state.mood === 'sad') {
            eyes.forEach(eye => {
                eye.setAttribute('rx', '1.5');
                eye.setAttribute('ry', '1');
            });
        } else if (this.state.mood === 'sleepy') {
            eyes.forEach(eye => {
                eye.setAttribute('rx', '3');
                eye.setAttribute('ry', '1.2');
            });
        } else {
            // 正常状态
            eyes.forEach(eye => {
                eye.setAttribute('rx', '2.2');
                eye.setAttribute('ry', '2.8');
            });
        }
        
        console.log(`💭 ${this.config.petName}的心情：${this.state.mood}`);
    }

    /**
     * 更新 UI
     */
    updateUI() {
        // 可爱版没有状态条，简化处理
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
        // 检查是否已存在
        const existingBtn = document.getElementById('summon-pet-btn');
        if (existingBtn) return;
        
        const summonBtn = document.createElement('button');
        summonBtn.id = 'summon-pet-btn';
        summonBtn.className = 'summon-pet-btn';
        summonBtn.innerHTML = '';
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
            
            // 加载保存的位置
            const savedPosition = localStorage.getItem('virtualPetPosition');
            if (savedPosition) {
                const position = JSON.parse(savedPosition);
                // 应用位置
                setTimeout(() => {
                    this.container.style.left = `${position.left}px`;
                    this.container.style.top = `${position.top}px`;
                    this.container.style.right = 'auto';
                    this.container.style.bottom = 'auto';
                    console.log('📍 加载保存的位置:', position);
                }, 100);
            }
        } catch (e) {
            console.warn('无法加载宠物状态:', e);
        }
    }
    
    /**
     * 保存宠物位置
     */
    savePetPosition(position) {
        try {
            localStorage.setItem('virtualPetPosition', JSON.stringify(position));
            console.log('💾 保存宠物位置:', position);
        } catch (e) {
            console.warn('无法保存宠物位置:', e);
        }
    }
    
    /**
     * 销毁宠物实例（用于页面跳转或重新初始化）
     */
    destroy() {
        console.log('🗑️ 销毁宠物实例');
        
        // 清除定时器
        if (this.animationInterval) {
            clearInterval(this.animationInterval);
        }
        
        // 移除 DOM 元素
        if (this.container) {
            this.container.remove();
        }
        
        // 移除全局引用
        window.virtualPet = null;
        // 重置标志位（允许重新初始化）
        window.petInitDone = false;
    }
}

// 导出类（供外部使用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VirtualPet;
}
