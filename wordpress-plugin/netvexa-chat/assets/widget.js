(function() {
    'use strict';
    
    // Check if widget is already initialized
    if (window.NetvexaChatWidget) {
        return;
    }
    
    // Widget configuration from WordPress
    var config = window.netvexa_config || {
        api_endpoint: 'http://localhost:8000',
        agent_id: 'default_agent',
        position: 'bottom-right',
        color: '#2563eb'
    };
    
    // Debug configuration
    console.log('NETVEXA Widget Config:', config);
    console.log('WordPress Config Available:', typeof window.netvexa_config !== 'undefined');
    
    // Create widget class
    window.NetvexaChatWidget = {
        isOpen: false,
        isLoaded: false,
        container: null,
        iframe: null,
        button: null,
        
        init: function() {
            this.createWidget();
            this.attachEventListeners();
        },
        
        createWidget: function() {
            // Create container
            this.container = document.createElement('div');
            this.container.id = 'netvexa-widget-container';
            this.container.style.cssText = this.getContainerStyles();
            
            // Create chat button
            this.button = document.createElement('button');
            this.button.id = 'netvexa-chat-button';
            this.button.style.cssText = this.getButtonStyles();
            this.button.innerHTML = this.getChatIcon();
            
            // Create iframe container
            var iframeContainer = document.createElement('div');
            iframeContainer.id = 'netvexa-iframe-container';
            iframeContainer.style.cssText = this.getIframeContainerStyles();
            
            // Create iframe
            this.iframe = document.createElement('iframe');
            this.iframe.id = 'netvexa-chat-iframe';
            this.iframe.src = config.api_endpoint + '/static/index.html?agent=' + config.agent_id;
            this.iframe.style.cssText = this.getIframeStyles();
            
            // Assemble widget
            iframeContainer.appendChild(this.iframe);
            this.container.appendChild(this.button);
            this.container.appendChild(iframeContainer);
            
            // Add to page
            document.body.appendChild(this.container);
        },
        
        attachEventListeners: function() {
            var self = this;
            
            // Toggle chat on button click
            this.button.addEventListener('click', function() {
                self.toggleChat();
            });
            
            // Close on escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && self.isOpen) {
                    self.closeChat();
                }
            });
            
            // Handle iframe load
            this.iframe.addEventListener('load', function() {
                self.isLoaded = true;
            });
        },
        
        toggleChat: function() {
            if (this.isOpen) {
                this.closeChat();
            } else {
                this.openChat();
            }
        },
        
        openChat: function() {
            this.isOpen = true;
            var iframeContainer = document.getElementById('netvexa-iframe-container');
            iframeContainer.style.display = 'block';
            
            // Animate in
            setTimeout(function() {
                iframeContainer.style.opacity = '1';
                iframeContainer.style.transform = 'translateY(0)';
            }, 10);
            
            // Update button
            this.button.innerHTML = this.getCloseIcon();
            
            // Focus iframe
            if (this.isLoaded) {
                this.iframe.contentWindow.focus();
            }
        },
        
        closeChat: function() {
            this.isOpen = false;
            var iframeContainer = document.getElementById('netvexa-iframe-container');
            
            // Animate out
            iframeContainer.style.opacity = '0';
            iframeContainer.style.transform = 'translateY(20px)';
            
            setTimeout(function() {
                iframeContainer.style.display = 'none';
            }, 300);
            
            // Update button
            this.button.innerHTML = this.getChatIcon();
        },
        
        getContainerStyles: function() {
            var position = config.position === 'bottom-left' ? 'left: 20px;' : 'right: 20px;';
            return 'position: fixed; bottom: 20px; ' + position + ' z-index: 999999;';
        },
        
        getButtonStyles: function() {
            return 'width: 60px; height: 60px; border-radius: 50%; background: ' + config.color + '; ' +
                   'color: white; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.15); ' +
                   'display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; ' +
                   'font-size: 24px;';
        },
        
        getIframeContainerStyles: function() {
            var position = config.position === 'bottom-left' ? 'left: 0;' : 'right: 0;';
            return 'position: absolute; bottom: 80px; ' + position + ' width: 380px; height: 600px; ' +
                   'background: white; border-radius: 16px; box-shadow: 0 5px 40px rgba(0,0,0,0.16); ' +
                   'display: none; opacity: 0; transform: translateY(20px); transition: all 0.3s ease; ' +
                   'overflow: hidden;';
        },
        
        getIframeStyles: function() {
            return 'width: 100%; height: 100%; border: none; border-radius: 16px;';
        },
        
        getChatIcon: function() {
            return '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
                   '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>' +
                   '</svg>';
        },
        
        getCloseIcon: function() {
            return '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
                   '<line x1="18" y1="6" x2="6" y2="18"></line>' +
                   '<line x1="6" y1="6" x2="18" y2="18"></line>' +
                   '</svg>';
        }
    };
    
    // Initialize widget when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            window.NetvexaChatWidget.init();
        });
    } else {
        window.NetvexaChatWidget.init();
    }
    
    // Add responsive styles
    var style = document.createElement('style');
    style.textContent = `
        #netvexa-chat-button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }
        
        @media (max-width: 480px) {
            #netvexa-iframe-container {
                width: calc(100vw - 40px) !important;
                height: calc(100vh - 120px) !important;
                max-height: 600px;
            }
        }
    `;
    document.head.appendChild(style);
})();