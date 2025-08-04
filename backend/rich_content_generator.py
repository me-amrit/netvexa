"""
Rich Content Generator
Transforms AI responses into rich message formats with cards, buttons, quick replies, etc.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging
from datetime import datetime
from business_templates import BusinessTemplates, BusinessScenario

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content that can be generated"""
    PLAIN_TEXT = "plain_text"
    PRICING_INFO = "pricing_info"
    PRODUCT_DEMO = "product_demo"
    FEATURE_OVERVIEW = "feature_overview"
    CONTACT_INFO = "contact_info"
    FAQ_ANSWER = "faq_answer"
    TUTORIAL = "tutorial"
    COMPARISON = "comparison" 
    TESTIMONIAL = "testimonial"
    BUSINESS_SCENARIO = "business_scenario"

class RichContentGenerator:
    """Generates rich message content based on AI responses and user intent"""
    
    def __init__(self):
        self.content_templates = self._load_content_templates()
        self.intent_patterns = self._load_intent_patterns()
        
    def _load_content_templates(self) -> Dict[str, Any]:
        """Load content templates for different scenarios"""
        return {
            ContentType.PRICING_INFO: {
                "template": "pricing_cards",
                "trigger_keywords": ["pricing", "price", "cost", "plan", "subscription", "expensive", "cheap", "fee"],
                "template_data": {
                    "intro_text": "Here are our **pricing plans** designed for businesses of all sizes:",
                    "cards": [
                        {
                            "title": "🚀 Starter Plan",
                            "subtitle": "Perfect for small businesses",
                            "body": "• 1 AI Agent\n• 2,000 messages/month\n• Email support\n• WordPress integration\n\n**€99/month**",
                            "actions": [
                                {"text": "Choose Starter", "payload": "select_starter_plan"},
                                {"text": "Learn More", "payload": "starter_details"}
                            ]
                        },
                        {
                            "title": "📈 Growth Plan",
                            "subtitle": "Scale your customer service",
                            "body": "• 5 AI Agents\n• 10,000 messages/month\n• Priority support\n• Advanced analytics\n• API access\n\n**€299/month**",
                            "actions": [
                                {"text": "Choose Growth", "payload": "select_growth_plan"},
                                {"text": "Learn More", "payload": "growth_details"}
                            ]
                        },
                        {
                            "title": "🏢 Enterprise",
                            "subtitle": "Custom solutions for large teams",
                            "body": "• Unlimited agents\n• Unlimited messages\n• Dedicated support\n• Custom integrations\n• SLA guarantee\n\n**Custom pricing**",
                            "actions": [
                                {"text": "Contact Sales", "payload": "contact_enterprise_sales"},
                                {"text": "Schedule Demo", "payload": "enterprise_demo"}
                            ]
                        }
                    ],
                    "quick_replies": [
                        {"text": "Compare Plans", "payload": "compare_pricing"},
                        {"text": "Free Trial", "payload": "start_trial"},
                        {"text": "Talk to Sales", "payload": "contact_sales"}
                    ]
                }
            },
            
            ContentType.FEATURE_OVERVIEW: {
                "template": "feature_showcase",
                "trigger_keywords": ["features", "capabilities", "what can", "how does", "functionality"],
                "template_data": {
                    "intro_text": "NETVEXA offers powerful AI-driven features to transform your customer experience:",
                    "features": [
                        {
                            "title": "🤖 AI Chat Agents",
                            "subtitle": "Deploy intelligent agents in under 1 hour",
                            "description": "RAG-powered agents that understand your business context",
                            "action": {"text": "Learn More", "payload": "feature_ai_agents"}
                        },
                        {
                            "title": "📊 Lead Capture & Scoring",
                            "subtitle": "Automatically qualify and score prospects",
                            "description": "Intelligent forms with built-in lead scoring algorithms",
                            "action": {"text": "See Demo", "payload": "demo_lead_capture"}
                        },
                        {
                            "title": "🔗 Seamless Integrations",
                            "subtitle": "Connect with your existing tools",
                            "description": "WordPress, Slack, Zapier, and 100+ integrations",
                            "action": {"text": "View Integrations", "payload": "view_integrations"}
                        },
                        {
                            "title": "📈 Advanced Analytics",
                            "subtitle": "Detailed insights and performance metrics",
                            "description": "Track conversations, leads, and ROI with detailed reports",
                            "action": {"text": "See Analytics", "payload": "demo_analytics"}
                        }
                    ]
                }
            },
            
            ContentType.CONTACT_INFO: {
                "template": "contact_options",
                "trigger_keywords": ["contact", "talk", "speak", "call", "email", "support", "help"],
                "template_data": {
                    "intro_text": "I'd be happy to connect you with our team! Choose your preferred way to get in touch:",
                    "options": [
                        {
                            "title": "📞 Schedule a Call",
                            "subtitle": "Book a 15-minute discovery call",
                            "action": {"type": "url", "value": "https://calendly.com/netvexa/demo", "text": "Book Now"}
                        },
                        {
                            "title": "💬 Live Chat",
                            "subtitle": "Chat with our sales team now",
                            "action": {"type": "postback", "value": "start_live_chat", "text": "Start Chat"}
                        },
                        {
                            "title": "📧 Email Us",
                            "subtitle": "Send us your questions",
                            "action": {"type": "email", "value": "sales@netvexa.com", "text": "Send Email"}
                        },
                        {
                            "title": "🎯 Request Demo",
                            "subtitle": "See NETVEXA in action",
                            "action": {"type": "postback", "value": "request_demo", "text": "Get Demo"}
                        }
                    ],
                    "quick_replies": [
                        {"text": "Immediate Help", "payload": "urgent_support"},
                        {"text": "Sales Question", "payload": "sales_inquiry"},
                        {"text": "Technical Support", "payload": "tech_support"}
                    ]
                }
            },
            
            ContentType.PRODUCT_DEMO: {
                "template": "demo_showcase",
                "trigger_keywords": ["demo", "show", "example", "try", "test", "preview"],
                "template_data": {
                    "intro_text": "Experience NETVEXA's power with our **interactive demo**:",
                    "demo_options": [
                        {
                            "title": "🎯 Live Demo",
                            "subtitle": "See it in action with real data",
                            "image": "/static/images/demo-live.png",
                            "action": {"text": "Start Live Demo", "payload": "start_live_demo"}
                        },
                        {
                            "title": "📊 Analytics Dashboard",
                            "subtitle": "Explore our reporting capabilities",
                            "image": "/static/images/demo-analytics.png", 
                            "action": {"text": "View Dashboard", "payload": "demo_dashboard"}
                        },
                        {
                            "title": "⚡ Quick Setup",
                            "subtitle": "See how fast deployment really is",
                            "image": "/static/images/demo-setup.png",
                            "action": {"text": "Watch Setup", "payload": "demo_setup_video"}
                        }
                    ]
                }
            }
        }
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for detecting user intent"""
        return {
            "pricing_inquiry": [
                r"\b(price|cost|pricing|expensive|cheap|plan|subscription|fee|budget)\b",
                r"\bhow much\b",
                r"\$\d+",
                r"€\d+",
                r"\bfree\b.*\btrial\b"
            ],
            "demo_request": [
                r"\b(demo|show|example|try|test|preview)\b",
                r"\bsee.*action\b",
                r"\btry.*out\b",
                r"\bshow.*how\b"
            ],
            "feature_inquiry": [
                r"\b(feature|capability|function|what.*do|how.*work)\b",
                r"\bwhat.*can\b",
                r"\btell.*about\b",
                r"\blearn.*more\b"
            ],
            "contact_request": [
                r"\b(contact|talk|speak|call|email|sales|support)\b",
                r"\bget.*touch\b",
                r"\bhuman.*agent\b",
                r"\bspeak.*someone\b"
            ],
            "comparison_request": [
                r"\b(compare|vs|versus|difference|better|alternative)\b",
                r"\bhow.*different\b",
                r"\bwhich.*best\b"
            ]
        }
    
    def detect_content_type(self, 
                          user_message: str, 
                          ai_response: str, 
                          conversation_history: List[Dict[str, Any]] = None) -> ContentType:
        """Detect the type of content that should be generated"""
        
        # First check for business scenarios
        business_scenario = BusinessTemplates.detect_scenario_from_message(user_message)
        if business_scenario != BusinessScenario.ONBOARDING or any(word in user_message.lower() for word in ["setup", "get started", "onboard"]):
            return ContentType.BUSINESS_SCENARIO
        
        # Combine user message and AI response for analysis
        text_to_analyze = f"{user_message} {ai_response}".lower()
        
        # Check for pricing-related content
        if any(keyword in text_to_analyze for keyword in self.content_templates[ContentType.PRICING_INFO]["trigger_keywords"]):
            return ContentType.PRICING_INFO
        
        # Check for demo requests
        if any(keyword in text_to_analyze for keyword in self.content_templates[ContentType.PRODUCT_DEMO]["trigger_keywords"]):
            return ContentType.PRODUCT_DEMO
        
        # Check for feature inquiries
        if any(keyword in text_to_analyze for keyword in self.content_templates[ContentType.FEATURE_OVERVIEW]["trigger_keywords"]):
            return ContentType.FEATURE_OVERVIEW
        
        # Check for contact requests
        if any(keyword in text_to_analyze for keyword in self.content_templates[ContentType.CONTACT_INFO]["trigger_keywords"]):
            return ContentType.CONTACT_INFO
        
        # Check conversation history for context
        if conversation_history:
            recent_messages = conversation_history[-3:]
            for msg in recent_messages:
                content = msg.get('content', '').lower()
                if any(keyword in content for keyword in ["pricing", "price", "cost"]):
                    return ContentType.PRICING_INFO
                elif any(keyword in content for keyword in ["demo", "show", "example"]):
                    return ContentType.PRODUCT_DEMO
        
        return ContentType.PLAIN_TEXT
    
    def should_generate_rich_content(self, 
                                   user_message: str, 
                                   ai_response: str,
                                   content_type: ContentType) -> bool:
        """Determine if rich content should be generated"""
        
        # Always generate rich content for these types
        priority_types = [
            ContentType.PRICING_INFO,
            ContentType.PRODUCT_DEMO,
            ContentType.FEATURE_OVERVIEW,
            ContentType.CONTACT_INFO,
            ContentType.BUSINESS_SCENARIO
        ]
        
        if content_type in priority_types:
            return True
        
        # Don't generate rich content for very short responses
        if len(ai_response.split()) < 10:
            return False
        
        # Don't generate rich content for error responses
        error_indicators = ["sorry", "error", "apologize", "unable", "cannot"]
        if any(indicator in ai_response.lower() for indicator in error_indicators):
            return False
        
        return False
    
    def generate_rich_content(self, 
                            user_message: str,
                            ai_response: str,
                            content_type: ContentType,
                            conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate rich message content based on type and context"""
        
        try:
            if content_type == ContentType.BUSINESS_SCENARIO:
                return self._generate_business_scenario_content(user_message, ai_response)
            elif content_type == ContentType.PRICING_INFO:
                return self._generate_pricing_content(ai_response)
            elif content_type == ContentType.FEATURE_OVERVIEW:
                return self._generate_feature_content(ai_response)
            elif content_type == ContentType.CONTACT_INFO:
                return self._generate_contact_content(ai_response)
            elif content_type == ContentType.PRODUCT_DEMO:
                return self._generate_demo_content(ai_response)
            else:
                return self._generate_enhanced_text(ai_response)
                
        except Exception as e:
            logger.error(f"Error generating rich content: {e}")
            return self._generate_fallback_content(ai_response)
    
    def _generate_business_scenario_content(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """Generate content based on detected business scenario"""
        scenario = BusinessTemplates.detect_scenario_from_message(user_message)
        template = BusinessTemplates.get_template_by_scenario(scenario)
        
        # Add AI response as intro text if template doesn't conflict
        if template and 'content' in template and len(template['content']) > 0:
            # Prepend AI response as additional context
            ai_intro = {
                "type": "text",
                "text": ai_response
            }
            # Insert AI response before existing content but after first text block
            if template['content'][0]['type'] == 'text':
                template['content'].insert(1, {"type": "divider"})
                template['content'].insert(1, ai_intro)
            else:
                template['content'].insert(0, ai_intro)
                template['content'].insert(1, {"type": "divider"})
        
        return template
    
    def _generate_pricing_content(self, ai_response: str) -> Dict[str, Any]:
        """Generate pricing card layout"""
        template_data = self.content_templates[ContentType.PRICING_INFO]["template_data"]
        
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text",
                    "text": template_data["intro_text"]
                },
                {
                    "type": "card_carousel",
                    "cards": template_data["cards"]
                },
                {
                    "type": "quick_replies",
                    "text": "What would you like to do next?",
                    "replies": template_data["quick_replies"]
                }
            ]
        }
    
    def _generate_feature_content(self, ai_response: str) -> Dict[str, Any]:
        """Generate feature showcase layout"""
        template_data = self.content_templates[ContentType.FEATURE_OVERVIEW]["template_data"]
        
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text",
                    "text": template_data["intro_text"]
                },
                {
                    "type": "list",
                    "items": [
                        {
                            "title": feature["title"],
                            "subtitle": f"{feature['subtitle']} - {feature['description']}",
                            "action": {
                                "type": "postback",
                                "value": feature["action"]["payload"]
                            }
                        }
                        for feature in template_data["features"]
                    ]
                },
                {
                    "type": "quick_replies", 
                    "text": "Interested in learning more?",
                    "replies": [
                        {"text": "Schedule Demo", "payload": "book_demo"},
                        {"text": "View Pricing", "payload": "pricing_info"},
                        {"text": "Contact Sales", "payload": "contact_sales"}
                    ]
                }
            ]
        }
    
    def _generate_contact_content(self, ai_response: str) -> Dict[str, Any]:
        """Generate contact options layout"""
        template_data = self.content_templates[ContentType.CONTACT_INFO]["template_data"]
        
        return {
            "type": "rich_message",
            "version": "1.0", 
            "content": [
                {
                    "type": "text",
                    "text": template_data["intro_text"]
                },
                {
                    "type": "button_group",
                    "layout": "vertical",
                    "buttons": [
                        {
                            "text": option["title"],
                            "action": {
                                "type": option["action"]["type"],
                                "value": option["action"]["value"]
                            },
                            "style": {"variant": "outline"}
                        }
                        for option in template_data["options"]
                    ]
                },
                {
                    "type": "quick_replies",
                    "text": "Or choose a quick option:",
                    "replies": template_data["quick_replies"]
                }
            ]
        }
    
    def _generate_demo_content(self, ai_response: str) -> Dict[str, Any]:
        """Generate demo showcase layout"""
        template_data = self.content_templates[ContentType.PRODUCT_DEMO]["template_data"]
        
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text", 
                    "text": template_data["intro_text"]
                },
                {
                    "type": "card_carousel",
                    "cards": [
                        {
                            "title": demo["title"],
                            "subtitle": demo["subtitle"],
                            "image": {"url": demo.get("image", ""), "alt": demo["title"]},
                            "actions": [
                                {
                                    "type": "button",
                                    "text": demo["action"]["text"],
                                    "action": {
                                        "type": "postback",
                                        "value": demo["action"]["payload"]
                                    }
                                }
                            ]
                        }
                        for demo in template_data["demo_options"]
                    ]
                },
                {
                    "type": "quick_replies",
                    "text": "Prefer a different approach?",
                    "replies": [
                        {"text": "Schedule Live Demo", "payload": "book_live_demo"},
                        {"text": "Download Brochure", "payload": "download_brochure"},
                        {"text": "Contact Sales", "payload": "contact_sales"}
                    ]
                }
            ]
        }
    
    def _generate_enhanced_text(self, ai_response: str) -> Dict[str, Any]:
        """Generate enhanced text with smart quick replies"""
        
        # Detect if we should add quick replies based on content
        quick_replies = []
        
        if any(word in ai_response.lower() for word in ["feature", "capability", "more"]):
            quick_replies.extend([
                {"text": "Learn More", "payload": "learn_more"},
                {"text": "See Demo", "payload": "request_demo"}
            ])
        
        if any(word in ai_response.lower() for word in ["help", "question", "need"]):
            quick_replies.extend([
                {"text": "Contact Support", "payload": "contact_support"},
                {"text": "Talk to Sales", "payload": "contact_sales"}
            ])
        
        # Add pricing if talking about business value
        if any(word in ai_response.lower() for word in ["business", "ROI", "save", "improve"]):
            quick_replies.append({"text": "View Pricing", "payload": "pricing_info"})
        
        # Limit to 3 quick replies
        quick_replies = quick_replies[:3]
        
        content = [
            {
                "type": "text",
                "text": ai_response
            }
        ]
        
        if quick_replies:
            content.append({
                "type": "quick_replies",
                "text": "What would you like to know more about?",
                "replies": quick_replies
            })
        
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": content
        }
    
    def _generate_fallback_content(self, ai_response: str) -> Dict[str, Any]:
        """Generate fallback content when rich generation fails"""
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text",
                    "text": ai_response
                }
            ]
        }
    
    def process_ai_response(self, 
                          user_message: str,
                          ai_response: str,
                          conversation_history: List[Dict[str, Any]] = None,
                          force_rich: bool = False) -> Dict[str, Any]:
        """Main method to process AI response and generate rich content"""
        
        # Detect content type
        content_type = self.detect_content_type(user_message, ai_response, conversation_history)
        
        # Decide if we should generate rich content
        should_generate = force_rich or self.should_generate_rich_content(
            user_message, ai_response, content_type
        )
        
        if should_generate:
            logger.info(f"Generating rich content of type: {content_type.value}")
            return self.generate_rich_content(
                user_message, ai_response, content_type, conversation_history
            )
        else:
            # Return enhanced plain text
            return self._generate_enhanced_text(ai_response)


# Usage example
if __name__ == "__main__":
    generator = RichContentGenerator()
    
    # Test pricing inquiry
    user_msg = "What are your pricing plans?"
    ai_response = "We offer flexible pricing plans starting at €99/month for small businesses."
    
    rich_content = generator.process_ai_response(user_msg, ai_response)
    print(json.dumps(rich_content, indent=2))