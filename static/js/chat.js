// JavaScript for the chat functionality

document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const refreshChatBtn = document.getElementById('refresh-chat');
    const newChatBtn = document.getElementById('new-chat');
    
    let chatHistory = [];
    
    // Load chat history on page load
    loadChatHistory();
    
    // Send message when form is submitted
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, true);
            
            // Clear input
            chatInput.value = '';
            chatInput.style.height = 'auto';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Send to server and get response
            sendMessage(message);
        });
    }
    
    // Refresh chat button (now creates a new chat)
    if (refreshChatBtn) {
        refreshChatBtn.addEventListener('click', function() {
            if (confirm('Start a new chat? This will end your current conversation.')) {
                startNewChat();
            }
        });
    }
    
    // Function to load chat history
    function loadChatHistory() {
        fetch('/api/chat_history')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Clear current messages
                chatMessages.innerHTML = '';
                
                // Add welcome message
                const welcomeDiv = document.createElement('div');
                welcomeDiv.className = 'welcome-message';
                // Get the username from the chat header
                const usernameElement = document.querySelector('.chat-header h2');
                const username = usernameElement ? usernameElement.textContent.split(',')[1]?.split('!')[0]?.trim() || 'User' : 'User';
                
                welcomeDiv.innerHTML = `
                    <h3>Welcome, ${username}</h3>
                    <p>I'm here to support you with your mental health concerns. Please tell me what specific mental health issue you're experiencing today.</p>
                `;
                chatMessages.appendChild(welcomeDiv);
                
                // Store history for context
                chatHistory = data;
                
                // Add messages to chat
                data.forEach(msg => {
                    addMessage(msg.content, msg.is_user, false);
                });
                
                // Scroll to bottom
                scrollToBottom();
            })
            .catch(error => {
                console.error('Error loading chat history:', error);
            });
    }
    
    // Function to send message to server
    function sendMessage(message) {
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add bot response to chat
            addMessage(data.response, false);
            
            // Update chat history with new response
            chatHistory.push({
                id: data.message_id,
                content: data.response,
                is_user: false
            });
            
            // Scroll to bottom
            scrollToBottom();
        })
        .catch(error => {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            addMessage('Sorry, I experienced a technical issue. Please try again.', false);
        });
    }
    
    // Function to add message to chat
    function addMessage(content, isUser, updateHistory = true) {
        const templateId = isUser ? 'user-message-template' : 'bot-message-template';
        const messageElement = createElementFromTemplate(templateId, { content });
        
        if (messageElement) {
            chatMessages.appendChild(messageElement);
            
            if (updateHistory && isUser) {
                // Add to chat history for context
                chatHistory.push({
                    content: content,
                    is_user: true
                });
            }
            
            // Scroll to new message
            scrollToBottom();
        }
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const typingIndicator = createElementFromTemplate('typing-indicator-template');
        if (typingIndicator) {
            chatMessages.appendChild(typingIndicator);
            scrollToBottom();
        }
    }
    
    // Function to remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Function to scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to start a new chat
    function startNewChat() {
        fetch('/api/new_chat', {
            method: 'POST',
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(() => {
            // Clear chat history
            chatHistory = [];
            
            // Clear current messages and show welcome
            chatMessages.innerHTML = '';
            
            // Add welcome message
            const welcomeDiv = document.createElement('div');
            welcomeDiv.className = 'welcome-message';
            
            // Get the username from the chat header
            const usernameElement = document.querySelector('.chat-header h2');
            const username = usernameElement ? usernameElement.textContent.split(',')[1]?.split('!')[0]?.trim() || 'User' : 'User';
            
            welcomeDiv.innerHTML = `
                <h3>Welcome, ${username}</h3>
                <p>I'm here to support you with your mental health concerns. Please tell me what specific mental health issue you're experiencing today.</p>
            `;
            chatMessages.appendChild(welcomeDiv);
        })
        .catch(error => {
            console.error('Error starting new chat:', error);
        });
    }
});
