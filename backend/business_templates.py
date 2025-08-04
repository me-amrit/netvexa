"""
Business Content Templates
Pre-built templates for common business scenarios and use cases
"""

from typing import Dict, Any, List
from enum import Enum

class BusinessScenario(Enum):
    """Common business scenarios for rich content generation"""
    ONBOARDING = "onboarding"
    FEATURE_COMPARISON = "feature_comparison"
    TESTIMONIALS = "testimonials"
    INTEGRATION_GUIDE = "integration_guide"
    TROUBLESHOOTING = "troubleshooting"
    ROI_CALCULATOR = "roi_calculator"
    CASE_STUDY = "case_study"
    COMPETITIVE_ANALYSIS = "competitive_analysis"

class BusinessTemplates:
    """Business content templates for different scenarios"""
    
    @staticmethod
    def get_onboarding_flow() -> Dict[str, Any]:
        """Customer onboarding flow template"""
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text",
                    "text": "Welcome to **NETVEXA**! Let's get you set up in just a few steps:"
                },
                {
                    "type": "list",
                    "items": [
                        {
                            "title": "1️⃣ Account Setup",
                            "subtitle": "Configure your account and preferences",
                            "action": {"type": "postback", "value": "setup_account"}
                        },
                        {
                            "title": "2️⃣ Create Your First Agent",
                            "subtitle": "Build an AI agent for your business",
                            "action": {"type": "postback", "value": "create_agent"}
                        },
                        {
                            "title": "3️⃣ Add Knowledge Base",
                            "subtitle": "Upload your business information",
                            "action": {"type": "postback", "value": "add_knowledge"}
                        },
                        {
                            "title": "4️⃣ Install Widget",
                            "subtitle": "Add the chat widget to your website",
                            "action": {"type": "postback", "value": "install_widget"}
                        }
                    ]
                },
                {
                    "type": "quick_replies",
                    "text": "Ready to get started?",
                    "replies": [
                        {"text": "Start Setup", "payload": "begin_onboarding"},
                        {"text": "Watch Tutorial", "payload": "onboarding_video"},
                        {"text": "Talk to Expert", "payload": "onboarding_support"}
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_feature_comparison() -> Dict[str, Any]:
        """Feature comparison template"""
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text",
                    "text": "Compare **NETVEXA plans** to find the perfect fit for your business:"
                },
                {
                    "type": "card_carousel",
                    "cards": [
                        {
                            "title": "🚀 Starter",
                            "subtitle": "€99/month",
                            "body": "✅ 1 AI Agent\n✅ 2,000 messages/month\n✅ Basic analytics\n✅ Email support\n❌ API access\n❌ Custom integrations",
                            "actions": [
                                {"type": "button", "text": "Choose Starter", "action": {"type": "postback", "value": "select_starter"}}
                            ]
                        },
                        {
                            "title": "📈 Growth",
                            "subtitle": "€299/month",
                            "body": "✅ 5 AI Agents\n✅ 10,000 messages/month\n✅ Advanced analytics\n✅ Priority support\n✅ API access\n❌ White-label",
                            "actions": [
                                {"type": "button", "text": "Choose Growth", "action": {"type": "postback", "value": "select_growth"}}
                            ]
                        },
                        {
                            "title": "🏢 Enterprise",
                            "subtitle": "Custom pricing",
                            "body": "✅ Unlimited agents\n✅ Unlimited messages\n✅ Custom analytics\n✅ Dedicated support\n✅ Full API\n✅ White-label",
                            "actions": [
                                {"type": "button", "text": "Contact Sales", "action": {"type": "postback", "value": "enterprise_contact"}}
                            ]
                        }
                    ]
                },
                {
                    "type": "button_group",
                    "layout": "horizontal",
                    "buttons": [
                        {"text": "Detailed Comparison", "action": {"type": "url", "value": "https://netvexa.com/pricing"}},
                        {"text": "Calculate ROI", "action": {"type": "postback", "value": "roi_calculator"}}
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_testimonials() -> Dict[str, Any]:
        """Customer testimonials template"""
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text",
                    "text": "See what our **customers are saying** about NETVEXA:"
                },
                {
                    "type": "card_carousel",
                    "cards": [
                        {
                            "title": "TechCorp Solutions",
                            "subtitle": "Sarah Johnson, CEO",
                            "body": "\"NETVEXA transformed our customer support. We reduced response time by 70% and increased customer satisfaction to 95%.\"",
                            "image": {"url": "/static/images/testimonial-techcorp.jpg", "alt": "TechCorp Solutions"},
                            "actions": [
                                {"type": "button", "text": "Read Full Story", "action": {"type": "url", "value": "https://netvexa.com/case-studies/techcorp"}}
                            ]
                        },
                        {
                            "title": "E-Commerce Plus",
                            "subtitle": "Mike Chen, COO",
                            "body": "\"Our lead conversion increased by 40% after implementing NETVEXA. The AI perfectly qualifies prospects before handoff.\"",
                            "image": {"url": "/static/images/testimonial-ecommerce.jpg", "alt": "E-Commerce Plus"},
                            "actions": [
                                {"type": "button", "text": "View Results", "action": {"type": "url", "value": "https://netvexa.com/case-studies/ecommerce-plus"}}
                            ]
                        },
                        {
                            "title": "StartupFlow",
                            "subtitle": "Lisa Park, Founder",
                            "body": "\"With NETVEXA, we handle 10x more customer inquiries without hiring additional support staff. Game-changer for startups!\"",
                            "image": {"url": "/static/images/testimonial-startup.jpg", "alt": "StartupFlow"},
                            "actions": [
                                {"type": "button", "text": "See Impact", "action": {"type": "url", "value": "https://netvexa.com/case-studies/startupflow"}}
                            ]
                        }
                    ]
                },
                {
                    "type": "quick_replies",
                    "text": "Want to join them?", 
                    "replies": [
                        {"text": "Start Free Trial", "payload": "start_trial"},
                        {"text": "Request Demo", "payload": "book_demo"},
                        {"text": "More Case Studies", "payload": "view_case_studies"}
                    ]
                }
            ]
        }
    
    @staticmethod 
    def get_integration_guide() -> Dict[str, Any]:
        """Integration guide template"""
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text",
                    "text": "Connect **NETVEXA** with your favorite tools in minutes:"
                },
                {
                    "type": "list",
                    "items": [
                        {
                            "title": "🌐 Website Integration",
                            "subtitle": "WordPress, Shopify, custom HTML",
                            "image": "/static/images/integration-web.png",
                            "action": {"type": "postback", "value": "web_integration_guide"}
                        },
                        {
                            "title": "💬 Communication Tools",
                            "subtitle": "Slack, Microsoft Teams, Discord",
                            "image": "/static/images/integration-comm.png",
                            "action": {"type": "postback", "value": "comm_integration_guide"}
                        },
                        {
                            "title": "📊 CRM Systems",
                            "subtitle": "Salesforce, HubSpot, Pipedrive",
                            "image": "/static/images/integration-crm.png",
                            "action": {"type": "postback", "value": "crm_integration_guide"}
                        },
                        {
                            "title": "⚡ Automation",
                            "subtitle": "Zapier, Make.com, n8n",
                            "image": "/static/images/integration-auto.png",
                            "action": {"type": "postback", "value": "automation_guide"}
                        },
                        {
                            "title": "🔧 Custom API",
                            "subtitle": "REST API, webhooks, SDKs",
                            "image": "/static/images/integration-api.png",
                            "action": {"type": "postback", "value": "api_documentation"}
                        }
                    ]
                },
                {
                    "type": "button_group",
                    "layout": "horizontal",
                    "buttons": [
                        {"text": "Browse All Integrations", "action": {"type": "url", "value": "https://netvexa.com/integrations"}},
                        {"text": "Request Integration", "action": {"type": "postback", "value": "request_integration"}}
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_troubleshooting_guide() -> Dict[str, Any]:
        """Troubleshooting guide template"""
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text",
                    "text": "Having issues? Let's **troubleshoot** together:"
                },
                {
                    "type": "list",
                    "items": [
                        {
                            "title": "🔧 Agent Not Responding",
                            "subtitle": "Check connection and configuration",
                            "action": {"type": "postback", "value": "troubleshoot_agent_response"}
                        },
                        {
                            "title": "📊 Analytics Not Loading", 
                            "subtitle": "Dashboard and reporting issues",
                            "action": {"type": "postback", "value": "troubleshoot_analytics"}
                        },
                        {
                            "title": "🔗 Integration Problems",
                            "subtitle": "Third-party connection issues",
                            "action": {"type": "postback", "value": "troubleshoot_integrations"}
                        },
                        {
                            "title": "💬 Widget Not Appearing",
                            "subtitle": "Chat widget installation help",
                            "action": {"type": "postback", "value": "troubleshoot_widget"}
                        },
                        {
                            "title": "📱 Mobile Issues",
                            "subtitle": "Responsive design problems",
                            "action": {"type": "postback", "value": "troubleshoot_mobile"}
                        }
                    ]
                },
                {
                    "type": "quick_replies",
                    "text": "Still need help?",
                    "replies": [
                        {"text": "Contact Support", "payload": "contact_technical_support"},
                        {"text": "Schedule Call", "payload": "book_support_call"},
                        {"text": "Check Status Page", "payload": "system_status"}
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_roi_calculator() -> Dict[str, Any]:
        """ROI calculator template"""
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text",
                    "text": "Calculate your **potential ROI** with NETVEXA:"
                },
                {
                    "type": "card",
                    "title": "📊 ROI Calculator",
                    "subtitle": "See your potential savings and revenue increase",
                    "body": "Input your current metrics to see projected results:\n\n• Monthly customer inquiries\n• Average response time\n• Support team size\n• Lead conversion rate",
                    "actions": [
                        {"type": "button", "text": "Start Calculator", "action": {"type": "url", "value": "https://netvexa.com/roi-calculator"}},
                        {"type": "button", "text": "View Sample Results", "action": {"type": "postback", "value": "roi_examples"}}
                    ]
                },
                {
                    "type": "text",
                    "text": "**Typical results our customers see:**\n\n• 70% reduction in response time\n• 40% increase in lead conversion\n• 60% decrease in support costs\n• 3-6 month payback period"
                },
                {
                    "type": "quick_replies",
                    "text": "Want to discuss your specific case?",
                    "replies": [
                        {"text": "Book ROI Consultation", "payload": "book_roi_consultation"},
                        {"text": "Download ROI Guide", "payload": "download_roi_guide"},
                        {"text": "See Case Studies", "payload": "roi_case_studies"}
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_competitive_analysis() -> Dict[str, Any]:
        """Competitive analysis template"""
        return {
            "type": "rich_message",
            "version": "1.0",
            "content": [
                {
                    "type": "text",
                    "text": "See how **NETVEXA compares** to other solutions:"
                },
                {
                    "type": "card_carousel",
                    "cards": [
                        {
                            "title": "🆚 vs. Chatbot Platforms",
                            "subtitle": "Traditional rule-based bots",
                            "body": "✅ AI-powered vs rule-based\n✅ Context awareness\n✅ Natural conversations\n✅ Easy setup (1 hour vs weeks)",
                            "actions": [
                                {"type": "button", "text": "Detailed Comparison", "action": {"type": "postback", "value": "compare_chatbots"}}
                            ]
                        },
                        {
                            "title": "🆚 vs. Live Chat Tools",
                            "subtitle": "Human-only support systems",
                            "body": "✅ 24/7 availability\n✅ Instant responses\n✅ Scalable without hiring\n✅ Consistent quality",
                            "actions": [
                                {"type": "button", "text": "See Advantages", "action": {"type": "postback", "value": "compare_livechat"}}
                            ]
                        },
                        {
                            "title": "🆚 vs. Enterprise Solutions",
                            "subtitle": "Complex, expensive platforms",
                            "body": "✅ SME-friendly pricing\n✅ Quick deployment\n✅ No technical expertise needed\n✅ Immediate ROI",
                            "actions": [
                                {"type": "button", "text": "Cost Comparison", "action": {"type": "postback", "value": "compare_enterprise"}}
                            ]
                        }
                    ]
                },
                {
                    "type": "button_group",
                    "layout": "horizontal", 
                    "buttons": [
                        {"text": "Migration Guide", "action": {"type": "postback", "value": "migration_assistance"}},
                        {"text": "Switch to NETVEXA", "action": {"type": "postback", "value": "switch_consultation"}}
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_template_by_scenario(scenario: BusinessScenario) -> Dict[str, Any]:
        """Get template by business scenario"""
        template_map = {
            BusinessScenario.ONBOARDING: BusinessTemplates.get_onboarding_flow(),
            BusinessScenario.FEATURE_COMPARISON: BusinessTemplates.get_feature_comparison(),
            BusinessScenario.TESTIMONIALS: BusinessTemplates.get_testimonials(),
            BusinessScenario.INTEGRATION_GUIDE: BusinessTemplates.get_integration_guide(),
            BusinessScenario.TROUBLESHOOTING: BusinessTemplates.get_troubleshooting_guide(),
            BusinessScenario.ROI_CALCULATOR: BusinessTemplates.get_roi_calculator(),
            BusinessScenario.COMPETITIVE_ANALYSIS: BusinessTemplates.get_competitive_analysis()
        }
        
        return template_map.get(scenario, {
            "type": "rich_message",
            "version": "1.0",
            "content": [{"type": "text", "text": "Template not found for this scenario."}]
        })
    
    @staticmethod
    def detect_scenario_from_message(message: str) -> BusinessScenario:
        """Detect business scenario from user message"""
        message_lower = message.lower()
        
        # Onboarding indicators
        if any(word in message_lower for word in ["setup", "get started", "onboard", "begin", "how to start"]):
            return BusinessScenario.ONBOARDING
        
        # Feature comparison indicators  
        if any(word in message_lower for word in ["compare", "vs", "versus", "difference", "which plan"]):
            return BusinessScenario.FEATURE_COMPARISON
        
        # Testimonials/social proof indicators
        if any(word in message_lower for word in ["testimonial", "review", "customer", "success", "case study"]):
            return BusinessScenario.TESTIMONIALS
        
        # Integration indicators
        if any(word in message_lower for word in ["integrate", "connect", "api", "webhook", "zapier", "slack"]):
            return BusinessScenario.INTEGRATION_GUIDE
        
        # Troubleshooting indicators
        if any(word in message_lower for word in ["problem", "issue", "error", "not working", "troubleshoot", "help"]):
            return BusinessScenario.TROUBLESHOOTING
        
        # ROI/business value indicators
        if any(word in message_lower for word in ["roi", "return", "investment", "save", "cost", "value", "business case"]):
            return BusinessScenario.ROI_CALCULATOR
        
        # Competitive analysis indicators
        if any(word in message_lower for word in ["competitor", "alternative", "better than", "switch from"]):
            return BusinessScenario.COMPETITIVE_ANALYSIS
        
        return BusinessScenario.ONBOARDING  # Default fallback


# Usage example
if __name__ == "__main__":
    import json
    
    # Test scenario detection
    test_messages = [
        "How do I get started with NETVEXA?",
        "What's the difference between your plans?", 
        "Do you have any customer testimonials?",
        "How do I integrate with Slack?",
        "My agent is not responding, help!"
    ]
    
    for msg in test_messages:
        scenario = BusinessTemplates.detect_scenario_from_message(msg)
        print(f"Message: '{msg}' -> Scenario: {scenario.value}")
    
    # Test template generation
    template = BusinessTemplates.get_template_by_scenario(BusinessScenario.FEATURE_COMPARISON)
    print(f"\nSample template:\n{json.dumps(template, indent=2)}")