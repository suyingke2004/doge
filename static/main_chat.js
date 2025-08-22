// 无限滚动加载历史消息（向上滚动触发）
const chatHistory = document.getElementById('chat-history');
let loadingHistory = false;
chatHistory.addEventListener('scroll', function() {
    if (chatHistory.scrollTop === 0 && !loadingHistory) {
        loadingHistory = true;
        document.getElementById('history-loading').style.display = 'block';
        // TODO: 调用后端API加载更早消息，加载完成后插入到chat-history顶部
        // 示例：
        // fetch('/api/load_history?before=xxx').then(...);
        setTimeout(() => {
            document.getElementById('history-loading').style.display = 'none';
            loadingHistory = false;
        }, 1200);
    }
});

// // 发送消息
// document.getElementById('chat-form').addEventListener('submit', function(e) {
//     e.preventDefault();
//     const input = document.getElementById('chat-input');
//     const text = input.value.trim();
//     if (!text) return;
//     // TODO: 发送消息到后端，追加到chat-history
//     input.value = '';
//     input.style.height = 'auto';
// });

// 输入框自适应高度
document.getElementById('chat-input').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// 侧边栏切换
document.querySelectorAll('.session-item').forEach(function(item, idx) {
    item.onclick = function() {
        if(idx === 0) window.location.href = "/main_chat";
        if(idx === 1) window.location.href = "/diary";
        if(idx === 2) window.location.href = "/library";
    }
});

document.getElementById('chat-form').addEventListener('submit', async function(e) {
e.preventDefault();
const input = document.getElementById('chat-input');
const text = input.value.trim();
if (!text) return;

// 追加用户消息到消息区
const chatHistory = document.getElementById('chat-history');
const userBubble = document.createElement('div');
userBubble.className = 'chat-bubble user-bubble';
userBubble.innerHTML = `
    <div class="bubble-content"><span class="bubble-text">${text}</span></div>
    <img src="/static/user_avatar.png" alt="用户头像" class="bubble-avatar">
`;
chatHistory.appendChild(userBubble);
chatHistory.scrollTop = chatHistory.scrollHeight;

input.value = '';
input.style.height = 'auto';

// 显示小狗正在输入
const typingDiv = document.createElement('div');
typingDiv.className = 'chat-bubble dog-bubble';
typingDiv.id = 'dog-typing';
typingDiv.innerHTML = `
    <img src="/static/dog_avatar.png" alt="小狗头像" class="bubble-avatar">
    <div class="bubble-content"><span class="bubble-text">小狗正在思考...</span></div>
`;
chatHistory.appendChild(typingDiv);
chatHistory.scrollTop = chatHistory.scrollHeight;

// 发送到后端
try {
    const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text})
    });
    const data = await resp.json();
    // 移除“正在思考”
    typingDiv.remove();
    // 追加小狗回复
    const dogBubble = document.createElement('div');
    dogBubble.className = 'chat-bubble dog-bubble';
    dogBubble.innerHTML = `
        <img src="/static/dog_avatar.png" alt="小狗头像" class="bubble-avatar">
        <div class="bubble-content"><span class="bubble-text">${data.reply}</span></div>
    `;
    chatHistory.appendChild(dogBubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;
} catch (err) {
    typingDiv.remove();
    alert('小狗回复失败，请重试');
}
});