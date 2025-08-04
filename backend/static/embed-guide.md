# NETVEXA Chat Widget Integration Guide

## Quick Start

Add the NETVEXA chat widget to any website with just one line of code:

```html
<script src="https://your-domain.com/static/embed.js" 
        data-agent-id="YOUR_AGENT_ID"></script>
```

## Configuration Options

Customize the widget appearance and behavior using data attributes:

```html
<script src="https://your-domain.com/static/embed.js" 
        data-agent-id="YOUR_AGENT_ID"
        data-position="bottom-right"
        data-primary-color="#4f46e5"
        data-title="Chat with us"
        data-subtitle="We're here to help!"
        data-button-text="Chat"
        data-button-icon="💬"
        data-theme="light"
        data-auto-open="false"
        data-hide-mobile="false"
        data-welcome-message="Hello! How can I help you today?"
        data-placeholder="Type your message..."
        data-api-url="https://your-api-domain.com">
</script>
```

### Available Options

| Option | Default | Description |
|--------|---------|-------------|
| `data-agent-id` | 'default' | Your unique agent ID from NETVEXA dashboard |
| `data-position` | 'bottom-right' | Widget position: 'bottom-right', 'bottom-left', 'top-right', 'top-left' |
| `data-primary-color` | '#4f46e5' | Primary color for buttons and headers (hex format) |
| `data-title` | 'Chat with us' | Header title text |
| `data-subtitle` | 'We're here to help!' | Header subtitle text |
| `data-button-text` | 'Chat' | Text shown on hover (optional) |
| `data-button-icon` | '💬' | Icon shown in the chat button |
| `data-theme` | 'light' | Color theme: 'light' or 'dark' |
| `data-auto-open` | 'false' | Automatically open chat on page load |
| `data-hide-mobile` | 'false' | Hide widget on mobile devices |
| `data-welcome-message` | 'Hello! How can...' | Initial message shown to users |
| `data-placeholder` | 'Type your message...' | Input field placeholder text |
| `data-api-url` | Current domain | Your NETVEXA API endpoint URL |

## Installation Examples

### Basic Installation

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Website</title>
</head>
<body>
    <!-- Your website content -->
    
    <!-- Add NETVEXA Chat Widget -->
    <script src="https://api.netvexa.com/static/embed.js" 
            data-agent-id="agent_123456"></script>
</body>
</html>
```

### Custom Styling

```html
<!-- Blue theme with custom messages -->
<script src="https://api.netvexa.com/static/embed.js" 
        data-agent-id="agent_123456"
        data-primary-color="#2563eb"
        data-title="Support Center"
        data-subtitle="Average response time: 30 seconds"
        data-welcome-message="Hi! What can I help you with today?"
        data-button-icon="🤝">
</script>
```

### E-commerce Integration

```html
<!-- E-commerce optimized configuration -->
<script src="https://api.netvexa.com/static/embed.js" 
        data-agent-id="agent_ecommerce"
        data-primary-color="#10b981"
        data-title="Shopping Assistant"
        data-subtitle="Get help with your order"
        data-welcome-message="Welcome! Need help finding the perfect product?"
        data-button-icon="🛒"
        data-position="bottom-left">
</script>
```

### Enterprise Setup

```html
<!-- Enterprise configuration with dark theme -->
<script src="https://api.netvexa.com/static/embed.js" 
        data-agent-id="agent_enterprise"
        data-primary-color="#6366f1"
        data-title="Enterprise Support"
        data-subtitle="Priority assistance available"
        data-theme="dark"
        data-welcome-message="Welcome to Enterprise Support. How may I assist you?"
        data-api-url="https://enterprise.netvexa.com">
</script>
```

## JavaScript API

Control the widget programmatically using the global `NETVEXA` object:

```javascript
// Open the chat window
NETVEXA.open();

// Close the chat window
NETVEXA.close();

// Toggle the chat window
NETVEXA.toggle();

// Send a message programmatically
NETVEXA.sendMessage('Hello, I need help with my order');

// Update configuration dynamically
NETVEXA.updateConfig({
    primaryColor: '#ef4444',
    title: 'Urgent Support'
});
```

### Event Integration

```javascript
// Open chat when user clicks a custom button
document.getElementById('contact-button').addEventListener('click', function() {
    NETVEXA.open();
});

// Send context when opening chat
document.getElementById('product-help').addEventListener('click', function() {
    NETVEXA.open();
    NETVEXA.sendMessage('I need help with Product SKU: 12345');
});
```

## Platform-Specific Integration

### React/Next.js

```jsx
// components/NetvexaChat.js
import { useEffect } from 'react';

export default function NetvexaChat() {
    useEffect(() => {
        const script = document.createElement('script');
        script.src = 'https://api.netvexa.com/static/embed.js';
        script.setAttribute('data-agent-id', 'YOUR_AGENT_ID');
        script.setAttribute('data-primary-color', '#4f46e5');
        document.body.appendChild(script);

        return () => {
            document.body.removeChild(script);
        };
    }, []);

    return null;
}
```

### Vue.js

```vue
<!-- components/NetvexaChat.vue -->
<template>
  <div></div>
</template>

<script>
export default {
  mounted() {
    const script = document.createElement('script');
    script.src = 'https://api.netvexa.com/static/embed.js';
    script.setAttribute('data-agent-id', 'YOUR_AGENT_ID');
    script.setAttribute('data-primary-color', '#4f46e5');
    document.body.appendChild(script);
  },
  beforeDestroy() {
    const script = document.querySelector('script[src*="embed.js"]');
    if (script) {
      document.body.removeChild(script);
    }
  }
}
</script>
```

### Angular

```typescript
// netvexa-chat.service.ts
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class NetvexaChatService {
  constructor() { }

  loadScript() {
    const script = document.createElement('script');
    script.src = 'https://api.netvexa.com/static/embed.js';
    script.setAttribute('data-agent-id', 'YOUR_AGENT_ID');
    script.setAttribute('data-primary-color', '#4f46e5');
    document.body.appendChild(script);
  }
}
```

## Advanced Features

### Conditional Loading

```javascript
// Load chat only for logged-in users
if (user.isLoggedIn) {
    const script = document.createElement('script');
    script.src = 'https://api.netvexa.com/static/embed.js';
    script.setAttribute('data-agent-id', 'agent_members');
    script.setAttribute('data-welcome-message', `Welcome back, ${user.name}!`);
    document.body.appendChild(script);
}
```

### Dynamic Agent Selection

```javascript
// Use different agents for different pages
const agentMap = {
    '/products': 'agent_sales',
    '/support': 'agent_support',
    '/pricing': 'agent_billing'
};

const currentPath = window.location.pathname;
const agentId = agentMap[currentPath] || 'agent_general';

const script = document.createElement('script');
script.src = 'https://api.netvexa.com/static/embed.js';
script.setAttribute('data-agent-id', agentId);
document.body.appendChild(script);
```

### Custom Positioning

```css
/* Custom CSS to override widget position */
#netvexa-chat-widget {
    bottom: 100px !important; /* Add space for cookie banner */
}

/* Hide on specific pages */
body.checkout-page #netvexa-chat-widget {
    display: none !important;
}
```

## Mobile Considerations

The widget is fully responsive and optimized for mobile devices:

- Automatically adjusts to full-screen on small devices
- Touch-friendly interface with larger tap targets
- Optional hiding on mobile with `data-hide-mobile="true"`
- Reduced animations for better performance

## Performance Tips

1. **Async Loading**: The widget loads asynchronously and won't block page rendering
2. **Lazy Loading**: Chat interface only loads when user clicks the button
3. **Caching**: Static assets are cached for fast subsequent loads
4. **Small Footprint**: Initial script is <5KB gzipped

## Security

- All communication uses HTTPS
- Messages are encrypted in transit
- No sensitive data is stored in local storage
- CORS headers properly configured

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions  
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 12+, Chrome Android

## Troubleshooting

### Widget Not Appearing

1. Check console for JavaScript errors
2. Verify agent ID is correct
3. Ensure API URL is accessible
4. Check for CSS conflicts

### Connection Issues

1. Verify CORS is enabled on your API
2. Check network tab for failed requests
3. Ensure WebSocket support
4. Test with different network conditions

### Styling Issues

1. Check for CSS specificity conflicts
2. Ensure primary color is valid hex
3. Test in different browsers
4. Verify mobile responsiveness

## Getting Your Agent ID

1. Log in to your NETVEXA dashboard
2. Navigate to Agents section
3. Click on your agent
4. Copy the Agent ID from the details panel

## Support

For additional help:
- Documentation: https://docs.netvexa.com
- Support: support@netvexa.com
- Community: https://community.netvexa.com