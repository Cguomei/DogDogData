/**
 * 宠物功能日志记录系统
 * 自动记录所有关键操作和状态变化到 log 文件夹
 */

(function() {
    // 日志存储
    const logs = [];
    const startTime = Date.now();
    const sessionId = generateSessionId();
    
    // 生成会话 ID
    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    // 获取相对时间（毫秒）
    function getRelativeTime() {
        return Date.now() - startTime;
    }
    
    // 添加日志
    function log(level, module, message, data = null) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            relativeTime: getRelativeTime(),
            level: level,
            module: module,
            message: message,
            data: data,
            sessionId: sessionId,
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        
        logs.push(logEntry);
        
        // 只在控制台输出，不自动保存
        const prefix = `[PET ${logEntry.relativeTime}ms]`;
        const logMsg = `${prefix} [${module}] ${message}`;
        
        switch(level) {
            case 'error':
                console.error(logMsg, data || '');
                break;
            case 'warn':
                console.warn(logMsg, data || '');
                break;
            case 'debug':
                console.log('%c' + logMsg, 'color: #888;', data || '');
                break;
            default:
                console.log(logMsg, data || '');
        }
        
        // 不再自动保存，改为只在控制台显示
        // 如果需要保存，手动调用 window.PetLogger.saveLogs()
    }
    
    // 快捷方法
    function info(module, message, data) {
        return log('INFO', module, message, data);
    }
    
    function warn(module, message, data) {
        return log('WARN', module, message, data);
    }
    
    function error(module, message, data) {
        return log('ERROR', module, message, data);
    }
    
    function debug(module, message, data) {
        return log('DEBUG', module, message, data);
    }
    
    // 保存日志到后端（通过 API）
    async function saveLogs() {
        if (logs.length === 0) return;
        
        try {
            const logContent = logs.map(entry => 
                `[${entry.timestamp}] [${entry.relativeTime}ms] [${entry.level}] [${entry.module}] ${entry.message}` + 
                (entry.data ? ' - ' + JSON.stringify(entry.data) : '')
            ).join('\n');
            
            // 发送到后端 API 保存到 log 文件夹
            await fetch('/api/save_pet_logs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/plain'
                },
                body: `session=${sessionId}\n${logContent}`
            });
            
            console.log(`✅ 日志已保存到服务器，共 ${logs.length} 条`);
            
            // 清空已保存的日志
            logs.length = 0;
        } catch (e) {
            console.error('保存日志失败:', e);
        }
    }
    
    // 手动保存日志
    function saveLogsManual() {
        saveLogs();
        alert('日志已开始下载，请查看下载文件夹');
    }
    
    // 导出到全局
    window.PetLogger = {
        info,
        warn,
        error,
        debug,
        log,
        saveLogs: saveLogsManual,
        getLogs: () => logs,
        getSessionId: () => sessionId
    };
    
    // 记录页面加载
    info('SYSTEM', '页面加载完成', {
        url: window.location.href,
        referrer: document.referrer,
        petInitDone: window.petInitDone,
        petInitializing: window.petInitializing,
        virtualPet: window.virtualPet ? '已存在' : '不存在'
    });
    
    // 页面关闭前保存日志
    window.addEventListener('beforeunload', () => {
        saveLogs();
    });
    
    // 每 30 秒自动保存一次
    setInterval(saveLogs, 30000);
    
    console.log('✅ 宠物日志系统已启动，会话 ID:', sessionId);
    console.log('💡 使用 window.PetLogger.saveLogs() 手动保存日志');
})();
