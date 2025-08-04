/**
 * NETVEXA Chat Widget Embed Script
 * Universal JavaScript widget for any website
 * 
 * Usage:
 * <script src="https://your-domain.com/static/embed.js" 
 *         data-agent-id="YOUR_AGENT_ID"
 *         data-position="bottom-right"
 *         data-primary-color="#4f46e5">
 * </script>
 */

(function() {
    'use strict';

    // Configuration from script tag
    const script = document.currentScript || document.querySelector('script[src*="embed.js"]');
    const config = {
        agentId: script.getAttribute('data-agent-id') || 'default',
        position: script.getAttribute('data-position') || 'bottom-right',
        primaryColor: script.getAttribute('data-primary-color') || '#4f46e5',
        title: script.getAttribute('data-title') || 'Chat with us',
        subtitle: script.getAttribute('data-subtitle') || 'We\'re here to help!',
        apiUrl: script.getAttribute('data-api-url') || window.location.origin,
        placeholder: script.getAttribute('data-placeholder') || 'Type your message...',
        welcomeMessage: script.getAttribute('data-welcome-message') || 'Hello! How can I help you today?',
        buttonText: script.getAttribute('data-button-text') || 'Chat',
        buttonIcon: script.getAttribute('data-button-icon') || '💬',
        theme: script.getAttribute('data-theme') || 'light',
        autoOpen: script.getAttribute('data-auto-open') === 'true',
        hideOnMobile: script.getAttribute('data-hide-mobile') === 'true'
    };

    // Check if widget already exists
    if (document.getElementById('netvexa-chat-widget')) {
        console.warn('NETVEXA Chat Widget already initialized');
        return;
    }

    // Widget styles
    const styles = `
        #netvexa-chat-widget {
            position: fixed;
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        #netvexa-chat-widget.bottom-right {
            bottom: 20px;
            right: 20px;
        }

        #netvexa-chat-widget.bottom-left {
            bottom: 20px;
            left: 20px;
        }

        #netvexa-chat-widget.top-right {
            top: 20px;
            right: 20px;
        }

        #netvexa-chat-widget.top-left {
            top: 20px;
            left: 20px;
        }

        .netvexa-chat-button {
            width: 60px;
            height: 60px;
            border-radius: 30px;
            background: ${config.primaryColor};
            color: white;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
            position: relative;
        }

        .netvexa-chat-button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        }

        .netvexa-chat-button.active {
            transform: scale(0.95);
        }

        .netvexa-unread-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            width: 20px;
            height: 20px;
            background: #ef4444;
            color: white;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: bold;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .netvexa-chat-window {
            position: absolute;
            width: 380px;
            height: 600px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            opacity: 0;
            transform: scale(0.9);
            pointer-events: none;
            transition: all 0.3s ease;
        }

        .netvexa-chat-window.open {
            opacity: 1;
            transform: scale(1);
            pointer-events: all;
        }

        #netvexa-chat-widget.bottom-right .netvexa-chat-window {
            bottom: 80px;
            right: 0;
        }

        #netvexa-chat-widget.bottom-left .netvexa-chat-window {
            bottom: 80px;
            left: 0;
        }

        #netvexa-chat-widget.top-right .netvexa-chat-window {
            top: 80px;
            right: 0;
        }

        #netvexa-chat-widget.top-left .netvexa-chat-window {
            top: 80px;
            left: 0;
        }

        .netvexa-chat-header {
            background: ${config.primaryColor};
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .netvexa-chat-header-content {
            flex: 1;
        }

        .netvexa-chat-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .netvexa-chat-subtitle {
            font-size: 14px;
            opacity: 0.9;
        }

        .netvexa-chat-close {
            width: 32px;
            height: 32px;
            border: none;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border-radius: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }

        .netvexa-chat-close:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        .netvexa-chat-iframe {
            flex: 1;
            width: 100%;
            border: none;
        }

        .netvexa-powered-by {
            padding: 8px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
            background: #f9fafb;
            border-top: 1px solid #e5e7eb;
        }

        .netvexa-powered-by a {
            color: ${config.primaryColor};
            text-decoration: none;
            font-weight: 500;
        }

        .netvexa-powered-by a:hover {
            text-decoration: underline;
        }

        /* Mobile styles */
        @media (max-width: 768px) {
            .netvexa-chat-window {
                width: 100%;
                height: 100%;
                border-radius: 0;
                max-width: 100vw;
                max-height: 100vh;
            }

            #netvexa-chat-widget.bottom-right .netvexa-chat-window,
            #netvexa-chat-widget.bottom-left .netvexa-chat-window,
            #netvexa-chat-widget.top-right .netvexa-chat-window,
            #netvexa-chat-widget.top-left .netvexa-chat-window {
                bottom: 0;
                left: 0;
                right: 0;
                top: 0;
            }

            .netvexa-chat-button {
                width: 56px;
                height: 56px;
            }

            ${config.hideOnMobile ? '#netvexa-chat-widget { display: none; }' : ''}
        }

        /* Dark theme */
        ${config.theme === 'dark' ? `
            .netvexa-chat-window {
                background: #1f2937;
                color: #f9fafb;
            }

            .netvexa-powered-by {
                background: #111827;
                color: #9ca3af;
                border-top-color: #374151;
            }
        ` : ''}

        /* Loading animation */
        .netvexa-loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #6b7280;
        }

        .netvexa-loading-spinner {
            width: 32px;
            height: 32px;
            border: 3px solid #e5e7eb;
            border-top-color: ${config.primaryColor};
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;

    // Create widget HTML
    function createWidget() {
        const widget = document.createElement('div');
        widget.id = 'netvexa-chat-widget';
        widget.className = config.position;

        widget.innerHTML = `
            <button class="netvexa-chat-button" id="netvexa-chat-toggle">
                <span id="netvexa-button-icon">${config.buttonIcon}</span>
                <span class="netvexa-unread-badge" id="netvexa-unread-count" style="display: none;">0</span>
            </button>
            <div class="netvexa-chat-window" id="netvexa-chat-window">
                <div class="netvexa-chat-header">
                    <div class="netvexa-chat-header-content">
                        <div class="netvexa-chat-title">${config.title}</div>
                        <div class="netvexa-chat-subtitle">${config.subtitle}</div>
                    </div>
                    <button class="netvexa-chat-close" id="netvexa-chat-close">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M12.5 3.5L3.5 12.5M3.5 3.5L12.5 12.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                <div class="netvexa-loading" id="netvexa-loading">
                    <div class="netvexa-loading-spinner"></div>
                </div>
                <iframe 
                    class="netvexa-chat-iframe" 
                    id="netvexa-chat-iframe"
                    style="display: none;"
                    title="NETVEXA Chat"
                ></iframe>
                <div class="netvexa-powered-by">
                    Powered by <a href="https://netvexa.com" target="_blank" rel="noopener">NETVEXA</a>
                </div>
            </div>
        `;

        return widget;
    }

    // Initialize widget
    function init() {
        // Add styles
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);

        // Create and add widget
        const widget = createWidget();
        document.body.appendChild(widget);

        // Get elements
        const toggleButton = document.getElementById('netvexa-chat-toggle');
        const chatWindow = document.getElementById('netvexa-chat-window');
        const closeButton = document.getElementById('netvexa-chat-close');
        const iframe = document.getElementById('netvexa-chat-iframe');
        const loading = document.getElementById('netvexa-loading');
        const unreadBadge = document.getElementById('netvexa-unread-count');

        let isOpen = false;
        let iframeLoaded = false;
        let unreadCount = 0;

        // Toggle chat window
        function toggleChat() {
            isOpen = !isOpen;
            chatWindow.classList.toggle('open', isOpen);
            toggleButton.classList.toggle('active', isOpen);

            if (isOpen) {
                loadIframe();
                resetUnreadCount();
            }
        }

        // Load iframe
        function loadIframe() {
            if (!iframeLoaded) {
                const params = new URLSearchParams({
                    agentId: config.agentId,
                    theme: config.theme,
                    primaryColor: config.primaryColor,
                    welcomeMessage: config.welcomeMessage,
                    placeholder: config.placeholder,
                    embedded: 'true'
                });

                iframe.src = `${config.apiUrl}/static/index.html?${params.toString()}`;
                
                iframe.onload = function() {
                    iframeLoaded = true;
                    loading.style.display = 'none';
                    iframe.style.display = 'block';
                    
                    // Send configuration to iframe
                    iframe.contentWindow.postMessage({
                        type: 'netvexa-config',
                        config: config
                    }, '*');
                };
            }
        }

        // Update unread count
        function updateUnreadCount(count) {
            unreadCount = count;
            unreadBadge.textContent = count;
            unreadBadge.style.display = count > 0 ? 'flex' : 'none';
        }

        // Reset unread count
        function resetUnreadCount() {
            updateUnreadCount(0);
        }

        // Event listeners
        toggleButton.addEventListener('click', toggleChat);
        closeButton.addEventListener('click', toggleChat);

        // Listen for messages from iframe
        window.addEventListener('message', function(event) {
            if (event.origin !== config.apiUrl) return;

            const { type, data } = event.data;

            switch (type) {
                case 'netvexa-unread':
                    if (!isOpen) {
                        updateUnreadCount(data.count);
                    }
                    break;
                case 'netvexa-resize':
                    // Handle resize if needed
                    break;
                case 'netvexa-close':
                    toggleChat();
                    break;
            }
        });

        // Auto-open if configured
        if (config.autoOpen) {
            setTimeout(toggleChat, 1000);
        }

        // Expose API
        window.NETVEXA = {
            open: function() {
                if (!isOpen) toggleChat();
            },
            close: function() {
                if (isOpen) toggleChat();
            },
            toggle: toggleChat,
            sendMessage: function(message) {
                if (iframe.contentWindow) {
                    iframe.contentWindow.postMessage({
                        type: 'netvexa-send',
                        message: message
                    }, '*');
                }
            },
            updateConfig: function(newConfig) {
                Object.assign(config, newConfig);
                if (iframe.contentWindow) {
                    iframe.contentWindow.postMessage({
                        type: 'netvexa-config',
                        config: config
                    }, '*');
                }
            }
        };
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();