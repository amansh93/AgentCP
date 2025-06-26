document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-container');
    const workflowToggle = document.getElementById('workflow-toggle');
    const toggleTexts = document.querySelectorAll('.toggle-text');
    const footerContainer = document.getElementById('footer-container');
    const resizeHandle = document.getElementById('resize-handle');

    // Initialize toggle state
    updateToggleLabels();

    // Add toggle change listener
    workflowToggle.addEventListener('change', updateToggleLabels);

    // Auto-expanding textarea functionality
    function autoExpandTextarea() {
        chatInput.style.height = 'auto';
        const scrollHeight = chatInput.scrollHeight;
        const maxHeight = parseFloat(window.getComputedStyle(chatInput).maxHeight);
        
        if (scrollHeight <= maxHeight) {
            chatInput.style.height = Math.max(48, scrollHeight) + 'px';
        } else {
            chatInput.style.height = maxHeight + 'px';
        }
    }

    // Add input event listener for auto-expanding
    chatInput.addEventListener('input', autoExpandTextarea);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Resizable footer functionality
    let isResizing = false;
    let startY = 0;
    let startHeight = 0;

    function startResize(clientY) {
        isResizing = true;
        startY = clientY;
        startHeight = footerContainer.offsetHeight;
        document.body.style.cursor = 'ns-resize';
        document.body.style.userSelect = 'none';
    }

    function doResize(clientY) {
        if (!isResizing) return;
        
        const deltaY = startY - clientY;
        const newHeight = Math.max(80, Math.min(window.innerHeight * 0.4, startHeight + deltaY));
        
        footerContainer.style.height = newHeight + 'px';
        autoExpandTextarea(); // Readjust textarea height
    }

    function endResize() {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    }

    // Mouse events
    resizeHandle.addEventListener('mousedown', (e) => {
        startResize(e.clientY);
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        doResize(e.clientY);
    });

    document.addEventListener('mouseup', endResize);

    // Touch events for mobile
    resizeHandle.addEventListener('touchstart', (e) => {
        startResize(e.touches[0].clientY);
        e.preventDefault();
    }, { passive: false });

    document.addEventListener('touchmove', (e) => {
        if (isResizing) {
            doResize(e.touches[0].clientY);
            e.preventDefault();
        }
    }, { passive: false });

    document.addEventListener('touchend', endResize);

    function updateToggleLabels() {
        const isPerformanceFlows = workflowToggle.checked;
        toggleTexts[0].classList.toggle('active', !isPerformanceFlows); // Balances/Revs/Capital
        toggleTexts[1].classList.toggle('active', isPerformanceFlows);   // Performance/Flows
    }

    // Add a welcome message
    appendMessage("Hello! I'm NEXA, your new next-gen client analytics digital assistant. How can I help you with your data today? Ask me anything....", 'bot');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = chatInput.value.trim();
        if (!query) return;

        appendMessage(query, 'user');
        chatInput.value = '';
        chatInput.style.height = '48px'; // Reset textarea height
        
        const workflowToggle = document.getElementById('workflow-toggle');
        const usePerformanceFlows = workflowToggle.checked;
        
        const thinkingMessage = appendMessage('Thinking...', 'bot');

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    query: query,
                    use_performance_flows: usePerformanceFlows 
                }),
            });

            chatContainer.removeChild(thinkingMessage);

            if (!response.ok) {
                const errorData = await response.json();
                appendMessage(`Error: ${errorData.error || 'Something went wrong.'}`, 'bot');
                return;
            }

            const data = await response.json();

            if (data.status === 'needs_human_input') {
                handleHumanIntervention(data.context);
            } else {
                appendMessage(data.answer, 'bot', data.reasoning_steps);
            }

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

    function handleHumanIntervention(context) {
        const interventionDiv = document.createElement('div');
        interventionDiv.classList.add('message', 'bot-message', 'intervention-message');

        const contextHtml = `
            <p>I'm having trouble with this request. Here's what went wrong:</p>
            <ul>
                <li><strong>Original Query:</strong> ${context.original_query}</li>
                <li><strong>Failed Step:</strong> ${context.failed_step}</li>
                <li><strong>Error:</strong> ${context.error_message}</li>
            </ul>
            <p>How would you like me to proceed?</p>
        `;
        interventionDiv.innerHTML = contextHtml;
        chatContainer.appendChild(interventionDiv);
    }
}); 