# NETVEXA Rich Message Format Specification

## Overview
This specification defines the JSON format for rich messages in NETVEXA chat system, enabling support for interactive elements, markdown formatting, cards, buttons, and media content.

## Message Structure

### Basic Message Format
```json
{
  "type": "rich_message",
  "version": "1.0",
  "content": [
    // Array of content blocks
  ],
  "metadata": {
    "timestamp": "2025-08-04T10:30:00Z",
    "agent_id": "string",
    "conversation_id": "string"
  }
}
```

### Content Block Types

#### 1. Text Block (with Markdown Support)
```json
{
  "type": "text",
  "text": "This is **bold** and *italic* text with [links](https://example.com)",
  "style": {
    "color": "#333333",
    "fontSize": "14px",
    "alignment": "left"
  }
}
```

#### 2. Button Block
```json
{
  "type": "button",
  "text": "Get Started",
  "action": {
    "type": "postback|url|phone",
    "value": "get_started_payload|https://example.com|+1234567890"
  },
  "style": {
    "variant": "primary|secondary|outline|danger",
    "size": "small|medium|large",
    "fullWidth": false
  }
}
```

#### 3. Button Group
```json
{
  "type": "button_group",
  "layout": "horizontal|vertical",
  "buttons": [
    {
      "text": "Option 1",
      "action": {"type": "postback", "value": "option_1"}
    },
    {
      "text": "Option 2", 
      "action": {"type": "postback", "value": "option_2"}
    }
  ]
}
```

#### 4. Card Block
```json
{
  "type": "card",
  "title": "Product Name",
  "subtitle": "Brief description",
  "image": {
    "url": "https://example.com/image.jpg",
    "alt": "Alt text"
  },
  "body": "Detailed description with **markdown** support",
  "actions": [
    {
      "type": "button",
      "text": "Buy Now",
      "action": {"type": "url", "value": "https://buy.example.com"}
    },
    {
      "type": "button",
      "text": "Learn More",
      "action": {"type": "postback", "value": "learn_more_product"}
    }
  ]
}
```

#### 5. Card Carousel
```json
{
  "type": "card_carousel",
  "cards": [
    // Array of card objects
  ]
}
```

#### 6. Quick Replies
```json
{
  "type": "quick_replies",
  "text": "What would you like to do?",
  "replies": [
    {
      "text": "View Pricing",
      "payload": "view_pricing"
    },
    {
      "text": "Schedule Demo",
      "payload": "schedule_demo"
    },
    {
      "text": "Contact Sales",
      "payload": "contact_sales"
    }
  ]
}
```

#### 7. List Block
```json
{
  "type": "list",
  "items": [
    {
      "title": "Feature 1",
      "subtitle": "Description of feature 1",
      "image": "https://example.com/icon1.png",
      "action": {"type": "postback", "value": "feature_1"}
    },
    {
      "title": "Feature 2", 
      "subtitle": "Description of feature 2",
      "image": "https://example.com/icon2.png",
      "action": {"type": "postback", "value": "feature_2"}
    }
  ]
}
```

#### 8. Divider
```json
{
  "type": "divider",
  "style": {
    "color": "#e0e0e0",
    "thickness": "1px",
    "margin": "16px 0"
  }
}
```

#### 9. Image Block
```json
{
  "type": "image",
  "url": "https://example.com/image.jpg",
  "alt": "Image description",
  "caption": "Optional caption with **markdown**",
  "action": {
    "type": "url",
    "value": "https://example.com/full-image"
  }
}
```

#### 10. Media Block
```json
{
  "type": "media",
  "mediaType": "video|audio|file",
  "url": "https://example.com/media.mp4",
  "thumbnail": "https://example.com/thumbnail.jpg",
  "title": "Media Title",
  "duration": 120,
  "size": "5.2MB"
}
```

## Backward Compatibility

### Plain Text Messages
Simple string messages are automatically converted:
```json
// Input: "Hello world"
// Output:
{
  "type": "rich_message",
  "version": "1.0", 
  "content": [
    {
      "type": "text",
      "text": "Hello world"
    }
  ]
}
```

### Legacy Format Detection
The system detects message format and applies appropriate rendering:
- String input → Plain text rendering
- Object with `type: "rich_message"` → Rich rendering
- Object without type → Treat as legacy, convert to text

## Validation Rules

### Required Fields
- `type` is required for all content blocks
- `text` is required for text, button, and quick_reply blocks
- `cards` is required for card_carousel blocks
- `items` is required for list blocks

### Content Limits
- Maximum 20 content blocks per message
- Maximum 10 buttons per button_group
- Maximum 10 cards per carousel
- Maximum 13 quick replies (Facebook Messenger limit)
- Text blocks: 2000 characters max
- Button text: 20 characters max
- Card title: 80 characters max
- Card subtitle: 80 characters max

### URL Validation
- All URLs must be HTTPS (except localhost for development) 
- Image URLs must return valid image content-type
- Media URLs must be accessible and under 25MB

## Styling System

### Theme Variables
```json
{
  "colors": {
    "primary": "#2563eb",
    "secondary": "#64748b", 
    "success": "#10b981",
    "danger": "#ef4444",
    "warning": "#f59e0b",
    "text": "#1f2937",
    "textSecondary": "#6b7280",
    "background": "#ffffff",
    "border": "#e5e7eb"
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px", 
    "md": "16px",
    "lg": "24px",
    "xl": "32px"
  },
  "borderRadius": {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px"
  }
}
```

### Responsive Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px  
- Desktop: > 1024px

## Action Types

### Postback Actions
Trigger specific functionality within the chat:
```json
{
  "type": "postback",
  "value": "action_identifier",
  "data": {
    "additional": "data"
  }
}
```

### URL Actions
Open external links:
```json
{
  "type": "url", 
  "value": "https://example.com",
  "target": "_blank|_self"
}
```

### Phone Actions
Initiate phone calls:
```json
{
  "type": "phone",
  "value": "+1234567890"
}
```

### Email Actions
Open email client:
```json
{
  "type": "email",
  "value": "contact@example.com",
  "subject": "Inquiry from NETVEXA",
  "body": "Hello, I would like to..."
}
```

## Examples

### Business Pricing Message
```json
{
  "type": "rich_message",
  "version": "1.0",
  "content": [
    {
      "type": "text", 
      "text": "Here are our **pricing plans** tailored for your business:"
    },
    {
      "type": "card_carousel",
      "cards": [
        {
          "title": "🚀 Starter Plan",
          "subtitle": "Perfect for small businesses",
          "body": "• 1 AI Agent\n• 2,000 messages/month\n• Email support\n• WordPress plugin",
          "actions": [
            {
              "type": "button",
              "text": "Choose Plan",
              "action": {"type": "postback", "value": "select_starter"}
            }
          ]
        },
        {
          "title": "📈 Growth Plan", 
          "subtitle": "Scale your customer service",
          "body": "• 5 AI Agents\n• 10,000 messages/month\n• Priority support\n• Advanced analytics",
          "actions": [
            {
              "type": "button",
              "text": "Choose Plan", 
              "action": {"type": "postback", "value": "select_growth"}
            }
          ]
        }
      ]
    },
    {
      "type": "quick_replies",
      "text": "Need help choosing?",
      "replies": [
        {"text": "Compare Plans", "payload": "compare_plans"},
        {"text": "Custom Quote", "payload": "custom_quote"},  
        {"text": "Schedule Demo", "payload": "schedule_demo"}
      ]
    }
  ]
}
```

### Support Response with Actions
```json
{
  "type": "rich_message",
  "version": "1.0",
  "content": [
    {
      "type": "text",
      "text": "I can help you with that! Here are your options:"
    },
    {
      "type": "button_group",
      "layout": "vertical",
      "buttons": [
        {
          "text": "📞 Call Support",
          "action": {"type": "phone", "value": "+1-800-NETVEXA"}
        },
        {
          "text": "💬 Start Live Chat", 
          "action": {"type": "postback", "value": "start_live_chat"}
        },
        {
          "text": "📧 Email Us",
          "action": {"type": "email", "value": "support@netvexa.com"}
        },
        {
          "text": "📚 View Documentation",
          "action": {"type": "url", "value": "https://docs.netvexa.com"}
        }
      ]
    }
  ]
}
```

## Implementation Notes

### Performance Considerations
- Lazy load images and media content
- Cache rendered components for repeated content
- Limit concurrent media downloads
- Implement image compression and optimization

### Accessibility
- Include alt text for all images
- Ensure proper color contrast ratios
- Support keyboard navigation for interactive elements
- Provide text alternatives for media content

### Security
- Sanitize all text content to prevent XSS
- Validate all URLs before rendering
- Implement CSP headers for media content
- Rate limit message rendering operations

This specification provides the foundation for creating rich, interactive, and beautiful chat experiences in NETVEXA.