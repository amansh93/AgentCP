document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-container');

    // Add a welcome message
    appendMessage("Hello! I'm NEXA. How can I help you with your data today?", 'bot');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = chatInput.value.trim();
        if (!query) return;

        appendMessage(query, 'user');
        chatInput.value = '';
        
        const thinkingMessage = appendMessage('Thinking...', 'bot');

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query }),
            });

            chatContainer.removeChild(thinkingMessage);

            if (!response.ok) {
                const errorData = await response.json();
                appendMessage(`Error: ${errorData.error || 'Something went wrong.'}`, 'bot');
                return;
            }

            const data = await response.json();
            appendMessage(data.answer, 'bot', data.reasoning_steps);

        } catch (error) {
            chatContainer.removeChild(thinkingMessage);
            appendMessage('An error occurred while fetching the response.', 'bot');
        }
    });

    function appendMessage(text, type, reasoningSteps = null) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${type}-message`);

        // Use marked.js to render markdown content for bot messages
        const contentDiv = document.createElement('div');
        if (type === 'bot') {
            contentDiv.innerHTML = marked.parse(text);
        } else {
            contentDiv.textContent = text;
        }
        messageDiv.appendChild(contentDiv);


        if (reasoningSteps && reasoningSteps.length > 0) {
            const toggle = document.createElement('div');
            toggle.classList.add('reasoning-toggle');
            toggle.textContent = 'Show Reasoning';
            
            const stepsContainer = document.createElement('div');
            stepsContainer.classList.add('reasoning-steps');
            
            reasoningSteps.forEach(step => {
                const p = document.createElement('p');
                p.textContent = `• ${step}`;
                stepsContainer.appendChild(p);
            });

            toggle.addEventListener('click', () => {
                stepsContainer.classList.toggle('visible');
                toggle.textContent = stepsContainer.classList.contains('visible') ? 'Hide Reasoning' : 'Show Reasoning';
            });
            
            messageDiv.appendChild(toggle);
            messageDiv.appendChild(stepsContainer);
        }

        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight; // Auto-scroll to bottom
        return messageDiv;
    }
}); 