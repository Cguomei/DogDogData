# AI助手前端删除功能 - 修改说明

## 需要修改的文件
`templates/ai_chat.html`

---

## 修改1: 添加删除按钮CSS样式

在 `<style>` 标签内,`.session-meta` 样式后面(约第113行后)添加:

```css
        /* 会话删除按钮 */
        .session-delete-btn {
            padding: 4px 8px;
            background: #fed7d7;
            border: none;
            border-radius: 4px;
            color: #c53030;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
            opacity: 0;
        }
        
        .session-item:hover .session-delete-btn {
            opacity: 1;
        }
        
        .session-delete-btn:hover {
            background: #fc8181;
            color: white;
        }
```

---

## 修改2: 修改会话列表渲染函数

找到 `renderSessionList` 函数(约第650-668行),替换为:

```javascript
        function renderSessionList(sessions) {
            const sessionList = document.getElementById('sessionList');
            
            if (sessions.length === 0) {
                sessionList.innerHTML = '<div style="text-align: center; padding: 20px; color: #a0aec0;">暂无对话历史</div>';
                return;
            }
            
            sessionList.innerHTML = sessions.map(session => `
                <div class="session-item ${session.id === currentSessionId ? 'active' : ''}" 
                     onclick="switchSession(${session.id})">
                    <div class="session-title">${escapeHtml(session.title)}</div>
                    <div class="session-meta">
                        <span>${formatTime(session.last_message_at)}</span>
                        <span>${session.message_count || 0}条消息</span>
                        <button class="session-delete-btn" 
                                onclick="event.stopPropagation(); deleteSession(${session.id})"
                                title="删除会话">
                            🗑️ 删除
                        </button>
                    </div>
                </div>
            `).join('');
        }
```

**关键改动**:
- 在 `.session-meta` 内添加了删除按钮
- 使用 `event.stopPropagation()` 防止触发会话切换
- 调用 `deleteSession(sessionId)` 函数

---

## 修改3: 添加删除会话函数

在 `switchSession` 函数后面(约第743行后)添加新函数:

```javascript
        // 删除会话
        async function deleteSession(sessionId) {
            // 确认对话框
            if (!confirm('确定要删除这个会话吗？此操作不可恢复！')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/ai/sessions/${sessionId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    showNotification('会话已删除', 'success');
                    
                    // 如果删除的是当前会话，创建新会话
                    if (sessionId === currentSessionId) {
                        currentSessionId = null;
                        localStorage.removeItem('currentSessionId');
                        await createNewSession();
                    } else {
                        // 否则只刷新会话列表
                        await loadSessions();
                    }
                } else {
                    throw new Error(data.error || '删除失败');
                }
            } catch (error) {
                console.error('删除会话失败:', error);
                showNotification('删除会话失败：' + error.message, 'error');
            }
        }
```

---

## 测试步骤

1. 打开AI聊天页面
2. 创建几个测试会话
3. 鼠标悬停在会话上,应该显示"🗑️ 删除"按钮
4. 点击删除按钮,弹出确认对话框
5. 确认后,会话应该被删除
6. 如果删除的是当前会话,会自动创建新会话

---

## 注意事项

⚠️ **后端API需要先完成修改**:
- 确保 `routes/ai_assistant.py` 中的删除API支持游客访问
- 确保权限检查使用 `getattr` 安全访问 `current_user`

⚠️ **浏览器兼容性**:
- `event.stopPropagation()` 在所有现代浏览器中都支持
- 如果需要支持IE,可能需要额外处理

---

## 完成标志

✅ 删除按钮显示正常  
✅ 点击删除弹出确认对话框  
✅ 删除后会话从列表中消失  
✅ 删除当前会话后自动创建新会话  
✅ 游客和登录用户都能正常删除自己的会话
