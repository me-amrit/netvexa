/**
 * NETVEXA Rich Message Renderer
 * Renders rich message format to HTML components
 */

class RichMessageRenderer {
    constructor(options = {}) {
        this.options = {
            theme: 'light',
            maxImageWidth: 300,
            enableAnimations: true,
            sanitizeHtml: true,
            ...options
        };
        
        this.markdownRenderer = new MarkdownRenderer();
        this.eventCallbacks = {};
    }

    /**
     * Main render function - converts message to HTML
     */
    render(message, container) {
        try {
            // Handle backward compatibility
            const richMessage = this.normalizeMessage(message);
            
            // Create message container
            const messageEl = document.createElement('div');
            messageEl.className = 'rich-message';
            messageEl.setAttribute('data-version', richMessage.version || '1.0');
            
            // Render content blocks
            richMessage.content.forEach((block, index) => {
                const blockEl = this.renderContentBlock(block, index);
                if (blockEl) {
                    messageEl.appendChild(blockEl);
                }
            });
            
            // Add to container
            if (container) {
                container.appendChild(messageEl);
            }
            
            return messageEl;
        } catch (error) {
            console.error('RichMessageRenderer: Error rendering message', error);
            return this.renderError('Failed to render message');
        }
    }

    /**
     * Normalize message format for backward compatibility
     */
    normalizeMessage(message) {
        // Plain string message
        if (typeof message === 'string') {
            return {
                type: 'rich_message',
                version: '1.0',
                content: [{ type: 'text', text: message }]
            };
        }
        
        // Object without rich message structure
        if (!message.type || message.type !== 'rich_message') {
            return {
                type: 'rich_message',
                version: '1.0',
                content: [{ type: 'text', text: message.content || message.text || 'Invalid message format' }]
            };
        }
        
        return message;
    }

    /**
     * Render individual content block
     */
    renderContentBlock(block, index) {
        const blockEl = document.createElement('div');
        blockEl.className = `content-block content-block-${block.type}`;
        blockEl.setAttribute('data-block-index', index);
        
        switch (block.type) {
            case 'text':
                return this.renderTextBlock(block);
            case 'button':
                return this.renderButtonBlock(block);
            case 'button_group':
                return this.renderButtonGroupBlock(block);
            case 'card':
                return this.renderCardBlock(block);
            case 'card_carousel':
                return this.renderCardCarouselBlock(block);
            case 'quick_replies':
                return this.renderQuickRepliesBlock(block);
            case 'list':
                return this.renderListBlock(block);
            case 'divider':
                return this.renderDividerBlock(block);
            case 'image':
                return this.renderImageBlock(block);
            case 'media':
                return this.renderMediaBlock(block);
            case 'emoji_picker':
                return this.renderEmojiPickerBlock(block);
            case 'reactions':
                return this.renderReactionsBlock(block);
            case 'typing_indicator':
                return this.renderTypingIndicatorBlock(block);
            case 'message_status':
                return this.renderMessageStatusBlock(block);
            default:
                console.warn(`Unknown block type: ${block.type}`);
                return this.renderTextBlock({ text: `[Unsupported content: ${block.type}]` });
        }
    }

    /**
     * Render text block with markdown support
     */
    renderTextBlock(block) {
        const textEl = document.createElement('div');
        textEl.className = 'text-block';
        
        // Apply custom styles if provided
        if (block.style) {
            Object.assign(textEl.style, block.style);
        }
        
        // Render markdown content
        const htmlContent = this.markdownRenderer.render(block.text);
        textEl.innerHTML = htmlContent;
        
        return textEl;
    }

    /**
     * Render button block
     */
    renderButtonBlock(block) {
        const button = document.createElement('button');
        button.className = `btn btn-${block.style?.variant || 'primary'} btn-${block.style?.size || 'medium'}`;
        button.textContent = block.text;
        
        if (block.style?.fullWidth) {
            button.classList.add('btn-full-width');
        }
        
        // Add click handler
        button.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleAction(block.action);
        });
        
        return button;
    }

    /**
     * Render button group
     */
    renderButtonGroupBlock(block) {
        const groupEl = document.createElement('div');
        groupEl.className = `button-group button-group-${block.layout || 'horizontal'}`;
        
        block.buttons.forEach(buttonData => {
            const button = this.renderButtonBlock({
                type: 'button',
                ...buttonData
            });
            groupEl.appendChild(button);
        });
        
        return groupEl;
    }

    /**
     * Render card block
     */
    renderCardBlock(block) {
        const cardEl = document.createElement('div');
        cardEl.className = 'card';
        
        // Card image
        if (block.image) {
            const imgEl = document.createElement('img');
            imgEl.src = block.image.url;
            imgEl.alt = block.image.alt || '';
            imgEl.className = 'card-image';
            cardEl.appendChild(imgEl);
        }
        
        // Card content
        const contentEl = document.createElement('div');
        contentEl.className = 'card-content';
        
        // Title
        if (block.title) {
            const titleEl = document.createElement('h3');
            titleEl.className = 'card-title';
            titleEl.textContent = block.title;
            contentEl.appendChild(titleEl);
        }
        
        // Subtitle  
        if (block.subtitle) {
            const subtitleEl = document.createElement('p');
            subtitleEl.className = 'card-subtitle';
            subtitleEl.textContent = block.subtitle;
            contentEl.appendChild(subtitleEl);
        }
        
        // Body with markdown
        if (block.body) {
            const bodyEl = document.createElement('div');
            bodyEl.className = 'card-body';
            bodyEl.innerHTML = this.markdownRenderer.render(block.body);
            contentEl.appendChild(bodyEl);
        }
        
        cardEl.appendChild(contentEl);
        
        // Card actions
        if (block.actions?.length) {
            const actionsEl = document.createElement('div');
            actionsEl.className = 'card-actions';
            
            block.actions.forEach(action => {
                const actionEl = this.renderContentBlock(action);
                actionsEl.appendChild(actionEl);
            });
            
            cardEl.appendChild(actionsEl);
        }
        
        return cardEl;
    }

    /**
     * Render card carousel
     */
    renderCardCarouselBlock(block) {
        const carouselEl = document.createElement('div');
        carouselEl.className = 'card-carousel';
        
        const containerEl = document.createElement('div');
        containerEl.className = 'card-carousel-container';
        
        block.cards.forEach(cardData => {
            const cardEl = this.renderCardBlock({ type: 'card', ...cardData });
            cardEl.classList.add('carousel-card');
            containerEl.appendChild(cardEl);
        });
        
        carouselEl.appendChild(containerEl);
        
        // Add navigation if more than one card
        if (block.cards.length > 1) {
            this.addCarouselNavigation(carouselEl, containerEl);
        }
        
        return carouselEl;
    }

    /**
     * Render quick replies
     */
    renderQuickRepliesBlock(block) {
        const containerEl = document.createElement('div');
        containerEl.className = 'quick-replies';
        
        // Optional text above replies
        if (block.text) {
            const textEl = document.createElement('p');
            textEl.className = 'quick-replies-text';
            textEl.textContent = block.text;
            containerEl.appendChild(textEl);
        }
        
        // Replies container
        const repliesEl = document.createElement('div');
        repliesEl.className = 'quick-replies-list';
        
        block.replies.forEach(reply => {
            const replyEl = document.createElement('button');
            replyEl.className = 'quick-reply-button';
            replyEl.textContent = reply.text;
            
            replyEl.addEventListener('click', () => {
                this.handleAction({
                    type: 'postback',
                    value: reply.payload
                });
            });
            
            repliesEl.appendChild(replyEl);
        });
        
        containerEl.appendChild(repliesEl);
        return containerEl;
    }

    /**
     * Render list block
     */
    renderListBlock(block) {
        const listEl = document.createElement('div');
        listEl.className = 'list-block';
        
        block.items.forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.className = 'list-item';
            
            if (item.image) {
                const imgEl = document.createElement('img');
                imgEl.src = item.image;
                imgEl.className = 'list-item-image';
                itemEl.appendChild(imgEl);
            }
            
            const contentEl = document.createElement('div');
            contentEl.className = 'list-item-content';
            
            const titleEl = document.createElement('h4');
            titleEl.className = 'list-item-title';
            titleEl.textContent = item.title;
            contentEl.appendChild(titleEl);
            
            if (item.subtitle) {
                const subtitleEl = document.createElement('p');
                subtitleEl.className = 'list-item-subtitle';
                subtitleEl.textContent = item.subtitle;
                contentEl.appendChild(subtitleEl);
            }
            
            itemEl.appendChild(contentEl);
            
            // Add click handler if action exists
            if (item.action) {
                itemEl.classList.add('list-item-clickable');
                itemEl.addEventListener('click', () => {
                    this.handleAction(item.action);
                });
            }
            
            listEl.appendChild(itemEl);
        });
        
        return listEl;
    }

    /**
     * Render divider
     */
    renderDividerBlock(block) {
        const dividerEl = document.createElement('hr');
        dividerEl.className = 'divider';
        
        if (block.style) {
            Object.assign(dividerEl.style, block.style);
        }
        
        return dividerEl;
    }

    /**
     * Render image block
     */
    renderImageBlock(block) {
        const containerEl = document.createElement('div');
        containerEl.className = 'image-block';
        
        const imgEl = document.createElement('img');
        imgEl.src = block.url;
        imgEl.alt = block.alt || '';
        imgEl.className = 'image-block-image';
        imgEl.style.maxWidth = `${this.options.maxImageWidth}px`;
        
        // Add click handler if action exists
        if (block.action) {
            imgEl.classList.add('image-clickable');
            imgEl.addEventListener('click', () => {
                this.handleAction(block.action);
            });
        }
        
        containerEl.appendChild(imgEl);
        
        // Caption
        if (block.caption) {
            const captionEl = document.createElement('div');
            captionEl.className = 'image-caption';
            captionEl.innerHTML = this.markdownRenderer.render(block.caption);
            containerEl.appendChild(captionEl);
        }
        
        return containerEl;
    }

    /**
     * Render media block
     */
    renderMediaBlock(block) {
        const containerEl = document.createElement('div');
        containerEl.className = 'media-block';
        
        // Media title
        if (block.title) {
            const titleEl = document.createElement('h4');
            titleEl.className = 'media-title';
            titleEl.textContent = block.title;
            containerEl.appendChild(titleEl);
        }
        
        // Media element based on type
        let mediaEl;
        switch (block.mediaType) {
            case 'video':
                mediaEl = document.createElement('video');
                mediaEl.controls = true;
                mediaEl.src = block.url;
                if (block.thumbnail) {
                    mediaEl.poster = block.thumbnail;
                }
                break;
            case 'audio':
                mediaEl = document.createElement('audio');
                mediaEl.controls = true;
                mediaEl.src = block.url;
                break;
            default:
                // File download link
                mediaEl = document.createElement('a');
                mediaEl.href = block.url;
                mediaEl.download = true;
                mediaEl.textContent = `Download ${block.title || 'file'}`;
                mediaEl.className = 'media-download-link';
        }
        
        mediaEl.className = 'media-element';
        containerEl.appendChild(mediaEl);
        
        // Media info
        const infoEl = document.createElement('div');
        infoEl.className = 'media-info';
        
        if (block.duration) {
            const durationEl = document.createElement('span');
            durationEl.textContent = this.formatDuration(block.duration);
            infoEl.appendChild(durationEl);
        }
        
        if (block.size) {
            const sizeEl = document.createElement('span');
            sizeEl.textContent = block.size;
            infoEl.appendChild(sizeEl);
        }
        
        if (infoEl.children.length > 0) {
            containerEl.appendChild(infoEl);
        }
        
        return containerEl;
    }

    /**
     * Handle action clicks
     */
    handleAction(action) {
        if (!action) return;
        
        switch (action.type) {
            case 'postback':
                this.triggerEvent('postback', {
                    payload: action.value,
                    data: action.data
                });
                break;
            case 'url':
                window.open(action.value, action.target || '_blank');
                break;
            case 'phone':
                window.location.href = `tel:${action.value}`;
                break;
            case 'email':
                const emailUrl = `mailto:${action.value}`;
                if (action.subject) emailUrl += `?subject=${encodeURIComponent(action.subject)}`;
                if (action.body) emailUrl += `&body=${encodeURIComponent(action.body)}`;
                window.location.href = emailUrl;
                break;
            case 'emoji':
                this.triggerEvent('emoji', {
                    emoji: action.value || action.emoji
                });
                break;
            case 'reaction':
                this.triggerEvent('reaction', action.value || action);
                break;
            default:
                console.warn(`Unknown action type: ${action.type}`);
        }
    }

    /**
     * Render emoji picker block
     */
    renderEmojiPickerBlock(block) {
        const containerEl = document.createElement('div');
        containerEl.className = 'emoji-picker-block';
        
        // Title
        if (block.title) {
            const titleEl = document.createElement('div');
            titleEl.className = 'emoji-picker-title';
            titleEl.textContent = block.title;
            containerEl.appendChild(titleEl);
        }
        
        // Emoji grid
        const gridEl = document.createElement('div');
        gridEl.className = 'emoji-grid';
        
        const emojis = block.emojis || [
            '😀', '😂', '😍', '🤔', '👍', '👎', '❤️', '🎉',
            '😊', '😢', '😡', '😴', '🤗', '🙄', '😎', '🤖',
            '👋', '👏', '🔥', '💯', '✅', '❌', '⭐', '💡'
        ];
        
        emojis.forEach(emoji => {
            const emojiEl = document.createElement('button');
            emojiEl.className = 'emoji-button';
            emojiEl.textContent = emoji;
            emojiEl.title = `Send ${emoji}`;
            
            emojiEl.addEventListener('click', () => {
                this.handleAction({
                    type: 'emoji',
                    value: emoji
                });
                // Add visual feedback
                emojiEl.classList.add('emoji-selected');
                setTimeout(() => emojiEl.classList.remove('emoji-selected'), 200);
            });
            
            gridEl.appendChild(emojiEl);
        });
        
        containerEl.appendChild(gridEl);
        return containerEl;
    }

    /**
     * Render message reactions block
     */
    renderReactionsBlock(block) {
        const containerEl = document.createElement('div');
        containerEl.className = 'message-reactions';
        
        // Message reference
        if (block.messageId) {
            containerEl.setAttribute('data-message-id', block.messageId);
        }
        
        // Reactions
        const reactionsEl = document.createElement('div');
        reactionsEl.className = 'reactions-list';
        
        if (block.reactions && block.reactions.length > 0) {
            block.reactions.forEach(reaction => {
                const reactionEl = document.createElement('button');
                reactionEl.className = 'reaction-button';
                if (reaction.userReacted) {
                    reactionEl.classList.add('user-reacted');
                }
                
                reactionEl.innerHTML = `
                    <span class="reaction-emoji">${reaction.emoji}</span>
                    <span class="reaction-count">${reaction.count}</span>
                `;
                
                reactionEl.addEventListener('click', () => {
                    this.handleAction({
                        type: 'reaction',
                        value: { emoji: reaction.emoji, messageId: block.messageId, action: 'toggle' }
                    });
                });
                
                reactionsEl.appendChild(reactionEl);
            });
        }
        
        // Add reaction button
        const addReactionEl = document.createElement('button');
        addReactionEl.className = 'add-reaction-button';
        addReactionEl.innerHTML = '😊+';
        addReactionEl.title = 'Add reaction';
        
        addReactionEl.addEventListener('click', () => {
            this.showEmojiPickerForReaction(block.messageId);
        });
        
        reactionsEl.appendChild(addReactionEl);
        containerEl.appendChild(reactionsEl);
        
        return containerEl;
    }

    /**
     * Show emoji picker for adding reactions
     */
    showEmojiPickerForReaction(messageId) {
        // Create inline emoji picker
        const existingPicker = document.querySelector('.inline-emoji-picker');
        if (existingPicker) {
            existingPicker.remove();
        }
        
        const pickerEl = document.createElement('div');
        pickerEl.className = 'inline-emoji-picker';
        
        const quickEmojis = ['😀', '😂', '😍', '👍', '❤️', '🎉', '🤔', '😢'];
        
        quickEmojis.forEach(emoji => {
            const emojiBtn = document.createElement('button');
            emojiBtn.className = 'quick-emoji-button';
            emojiBtn.textContent = emoji;
            
            emojiBtn.addEventListener('click', () => {
                this.handleAction({
                    type: 'reaction',
                    value: { emoji, messageId, action: 'add' }
                });
                pickerEl.remove();
            });
            
            pickerEl.appendChild(emojiBtn);
        });
        
        // Position near the add reaction button
        const addButton = document.querySelector(`[data-message-id="${messageId}"] .add-reaction-button`);
        if (addButton) {
            addButton.parentNode.insertBefore(pickerEl, addButton.nextSibling);
        }
        
        // Auto-close after 5 seconds
        setTimeout(() => {
            if (pickerEl.parentNode) {
                pickerEl.remove();
            }
        }, 5000);
    }

    /**
     * Render typing indicator block
     */
    renderTypingIndicatorBlock(block) {
        const containerEl = document.createElement('div');
        containerEl.className = 'typing-indicator';
        
        if (block.avatar) {
            const avatarEl = document.createElement('img');
            avatarEl.className = 'typing-avatar';
            avatarEl.src = block.avatar;
            avatarEl.alt = block.name || 'Agent';
            containerEl.appendChild(avatarEl);
        }
        
        const bubbleEl = document.createElement('div');
        bubbleEl.className = 'typing-bubble';
        
        // Typing dots animation
        const dotsEl = document.createElement('div');
        dotsEl.className = 'typing-dots';
        
        for (let i = 0; i < 3; i++) {
            const dotEl = document.createElement('span');
            dotEl.className = 'typing-dot';
            dotsEl.appendChild(dotEl);
        }
        
        bubbleEl.appendChild(dotsEl);
        
        // Optional typing text
        if (block.text) {
            const textEl = document.createElement('div');
            textEl.className = 'typing-text';
            textEl.textContent = block.text;
            bubbleEl.appendChild(textEl);
        }
        
        containerEl.appendChild(bubbleEl);
        
        // Auto-remove after specified duration or 5 seconds
        const duration = block.duration || 5000;
        setTimeout(() => {
            if (containerEl.parentNode) {
                containerEl.remove();
            }
        }, duration);
        
        return containerEl;
    }

    /**
     * Render message status block
     */
    renderMessageStatusBlock(block) {
        const containerEl = document.createElement('div');
        containerEl.className = 'message-status';
        
        if (block.messageId) {
            containerEl.setAttribute('data-message-id', block.messageId);
        }
        
        // Status indicator
        const statusEl = document.createElement('div');
        statusEl.className = `status-indicator status-${block.status || 'sent'}`;
        
        // Status icons
        switch (block.status) {
            case 'sending':
                statusEl.innerHTML = '<span class="status-icon">⏳</span><span class="status-text">Sending...</span>';
                break;
            case 'sent':
                statusEl.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Sent</span>';
                break;
            case 'delivered':
                statusEl.innerHTML = '<span class="status-icon">✓✓</span><span class="status-text">Delivered</span>';
                break;
            case 'read':
                statusEl.innerHTML = '<span class="status-icon status-read">✓✓</span><span class="status-text">Read</span>';
                break;
            case 'failed':
                statusEl.innerHTML = '<span class="status-icon">⚠️</span><span class="status-text">Failed</span>';
                break;
            default:
                statusEl.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Sent</span>';
        }
        
        containerEl.appendChild(statusEl);
        
        // Timestamp
        if (block.timestamp) {
            const timeEl = document.createElement('div');
            timeEl.className = 'message-timestamp';
            timeEl.textContent = this.formatTimestamp(block.timestamp);
            containerEl.appendChild(timeEl);
        }
        
        return containerEl;
    }

    /**
     * Format timestamp for display
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        // Less than a minute
        if (diff < 60000) {
            return 'Just now';
        }
        
        // Less than an hour
        if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes}m ago`;
        }
        
        // Less than a day
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}h ago`;
        }
        
        // More than a day - show date
        if (date.toDateString() === now.toDateString()) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else {
            return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        }
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator(options = {}) {
        const typingBlock = {
            type: 'typing_indicator',
            name: options.name || 'Agent',
            avatar: options.avatar,
            text: options.text,
            duration: options.duration || 3000
        };
        
        const typingEl = this.renderTypingIndicatorBlock(typingBlock);
        
        // Find chat container and append
        const chatContainer = document.querySelector('.chat-messages') || document.body;
        chatContainer.appendChild(typingEl);
        
        return typingEl;
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        const typingIndicators = document.querySelectorAll('.typing-indicator');
        typingIndicators.forEach(indicator => {
            indicator.remove();
        });
    }

    /**
     * Update message status
     */
    updateMessageStatus(messageId, status, timestamp) {
        const statusEl = document.querySelector(`[data-message-id="${messageId}"] .status-indicator`);
        if (statusEl) {
            statusEl.className = `status-indicator status-${status}`;
            
            // Update status content
            switch (status) {
                case 'sending':
                    statusEl.innerHTML = '<span class="status-icon">⏳</span><span class="status-text">Sending...</span>';
                    break;
                case 'sent':
                    statusEl.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Sent</span>';
                    break;
                case 'delivered':
                    statusEl.innerHTML = '<span class="status-icon">✓✓</span><span class="status-text">Delivered</span>';
                    break;
                case 'read':
                    statusEl.innerHTML = '<span class="status-icon status-read">✓✓</span><span class="status-text">Read</span>';
                    break;
                case 'failed':
                    statusEl.innerHTML = '<span class="status-icon">⚠️</span><span class="status-text">Failed</span>';
                    break;
            }
            
            // Update timestamp if provided
            if (timestamp) {
                const timestampEl = statusEl.parentNode.querySelector('.message-timestamp');
                if (timestampEl) {
                    timestampEl.textContent = this.formatTimestamp(timestamp);
                }
            }
        }
    }

    /**
     * Add carousel navigation
     */
    addCarouselNavigation(carouselEl, containerEl) {
        const navEl = document.createElement('div');
        navEl.className = 'carousel-nav';
        
        const prevBtn = document.createElement('button');
        prevBtn.className = 'carousel-nav-btn carousel-prev';
        prevBtn.innerHTML = '‹';
        prevBtn.addEventListener('click', () => this.scrollCarousel(containerEl, -1));
        
        const nextBtn = document.createElement('button');
        nextBtn.className = 'carousel-nav-btn carousel-next';
        nextBtn.innerHTML = '›';
        nextBtn.addEventListener('click', () => this.scrollCarousel(containerEl, 1));
        
        navEl.appendChild(prevBtn);
        navEl.appendChild(nextBtn);
        carouselEl.appendChild(navEl);
    }

    /**
     * Scroll carousel
     */
    scrollCarousel(container, direction) {
        const cardWidth = container.querySelector('.carousel-card')?.offsetWidth || 0;
        const scrollAmount = cardWidth * direction;
        container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }

    /**
     * Format duration in seconds to MM:SS
     */
    formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Event system
     */
    on(event, callback) {
        if (!this.eventCallbacks[event]) {
            this.eventCallbacks[event] = [];
        }
        this.eventCallbacks[event].push(callback);
    }

    triggerEvent(event, data) {
        const callbacks = this.eventCallbacks[event] || [];
        callbacks.forEach(callback => callback(data));
    }

    /**
     * Render error message
     */
    renderError(message) {
        const errorEl = document.createElement('div');
        errorEl.className = 'message-error';
        errorEl.textContent = message;
        return errorEl;
    }
}

/**
 * Simple Markdown Renderer for text formatting
 */
class MarkdownRenderer {
    constructor() {
        this.rules = [
            // Bold
            { pattern: /\*\*(.*?)\*\*/g, replace: '<strong>$1</strong>' },
            // Italic
            { pattern: /\*(.*?)\*/g, replace: '<em>$1</em>' },
            // Strikethrough
            { pattern: /~~(.*?)~~/g, replace: '<del>$1</del>' },
            // Links
            { pattern: /\[([^\]]+)\]\(([^)]+)\)/g, replace: '<a href="$2" target="_blank" rel="noopener">$1</a>' },
            // Inline code
            { pattern: /`([^`]+)`/g, replace: '<code>$1</code>' },
            // Line breaks
            { pattern: /\n/g, replace: '<br>' }
        ];
    }

    render(text) {
        if (!text) return '';
        
        let html = this.escapeHtml(text);
        
        // Apply markdown rules
        this.rules.forEach(rule => {
            html = html.replace(rule.pattern, rule.replace);
        });
        
        return html;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Export for use
window.RichMessageRenderer = RichMessageRenderer;