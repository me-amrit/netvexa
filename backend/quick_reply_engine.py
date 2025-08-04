"""
Intelligent Quick Reply Engine
Generates contextual quick reply suggestions based on conversation state, user intent, and business goals.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import json
from datetime import datetime

class ConversationStage(Enum):
    WELCOME = "welcome"
    DISCOVERY = "discovery"
    QUALIFICATION = "qualification"
    PRESENTATION = "presentation"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    SUPPORT = "support"

class UserIntent(Enum):
    UNKNOWN = "unknown"
    PRICING_INQUIRY = "pricing_inquiry"
    PRODUCT_INFO = "product_info"
    TECHNICAL_SUPPORT = "technical_support"
    SALES_CONTACT = "sales_contact"
    DEMO_REQUEST = "demo_request"
    COMPLAINT = "complaint"
    FEATURE_REQUEST = "feature_request"

class QuickReplyEngine:
    def __init__(self):
        self.business_goals = {
            "lead_generation": 0.4,
            "product_education": 0.3,
            "support_resolution": 0.2,
            "sales_conversion": 0.1
        }
        
        # Standard quick reply templates
        self.reply_templates = {
            ConversationStage.WELCOME: {
                "new_visitor": [
                    {"text": "💰 View Pricing", "payload": "pricing_info", "intent": "pricing_inquiry"},
                    {"text": "🚀 See Demo", "payload": "request_demo", "intent": "demo_request"},
                    {"text": "📞 Talk to Sales", "payload": "contact_sales", "intent": "sales_contact"},
                    {"text": "📖 Learn More", "payload": "product_info", "intent": "product_info"}
                ],
                "returning_user": [
                    {"text": "Continue Setup", "payload": "continue_setup", "intent": "technical_support"},
                    {"text": "Check Status", "payload": "check_status", "intent": "support"},
                    {"text": "Contact Support", "payload": "get_support", "intent": "technical_support"},
                    {"text": "Upgrade Plan", "payload": "upgrade_plan", "intent": "sales_contact"}
                ]
            },
            ConversationStage.DISCOVERY: {
                "business_size": [
                    {"text": "Small Business (1-10)", "payload": "size_small", "intent": "qualification"},
                    {"text": "Medium (11-100)", "payload": "size_medium", "intent": "qualification"},
                    {"text": "Enterprise (100+)", "payload": "size_large", "intent": "qualification"}
                ],
                "use_case": [
                    {"text": "Customer Support", "payload": "usecase_support", "intent": "product_info"},
                    {"text": "Lead Generation", "payload": "usecase_leads", "intent": "product_info"},
                    {"text": "Sales Automation", "payload": "usecase_sales", "intent": "product_info"},
                    {"text": "All of the Above", "payload": "usecase_all", "intent": "product_info"}
                ]
            },
            ConversationStage.QUALIFICATION: {
                "budget_range": [
                    {"text": "Under €100/month", "payload": "budget_low", "intent": "pricing_inquiry"},
                    {"text": "€100-500/month", "payload": "budget_medium", "intent": "pricing_inquiry"},
                    {"text": "€500+ /month", "payload": "budget_high", "intent": "pricing_inquiry"},
                    {"text": "Need Custom Quote", "payload": "budget_custom", "intent": "sales_contact"}
                ],
                "timeline": [
                    {"text": "This Week", "payload": "timeline_urgent", "intent": "sales_contact"},
                    {"text": "This Month", "payload": "timeline_month", "intent": "demo_request"},
                    {"text": "Next Quarter", "payload": "timeline_quarter", "intent": "product_info"},
                    {"text": "Just Exploring", "payload": "timeline_exploring", "intent": "product_info"}
                ]
            },
            ConversationStage.PRESENTATION: {
                "feature_interest": [
                    {"text": "AI Chat Agents", "payload": "feature_ai", "intent": "product_info"},
                    {"text": "Lead Capture", "payload": "feature_leads", "intent": "product_info"},
                    {"text": "Analytics", "payload": "feature_analytics", "intent": "product_info"},
                    {"text": "Integrations", "payload": "feature_integrations", "intent": "product_info"}
                ],
                "next_steps": [
                    {"text": "Schedule Demo", "payload": "book_demo", "intent": "demo_request"},
                    {"text": "Start Free Trial", "payload": "start_trial", "intent": "sales_contact"},
                    {"text": "Get Pricing", "payload": "get_pricing", "intent": "pricing_inquiry"},
                    {"text": "Speak to Expert", "payload": "expert_call", "intent": "sales_contact"}
                ]
            },
            ConversationStage.SUPPORT: {
                "issue_type": [
                    {"text": "Setup Help", "payload": "help_setup", "intent": "technical_support"},
                    {"text": "Integration Issue", "payload": "help_integration", "intent": "technical_support"},
                    {"text": "Billing Question", "payload": "help_billing", "intent": "support"},
                    {"text": "Feature Request", "payload": "feature_request", "intent": "feature_request"}
                ]
            }
        }
    
    def generate_quick_replies(
        self, 
        conversation_history: List[Dict[str, Any]], 
        user_context: Dict[str, Any],
        stage: Optional[ConversationStage] = None,
        max_replies: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Generate contextual quick replies based on conversation state.
        """
        
        # Determine conversation stage if not provided
        if not stage:
            stage = self._detect_conversation_stage(conversation_history, user_context)
        
        # Detect user intent from recent messages
        user_intent = self._detect_user_intent(conversation_history)
        
        # Get user type (new vs returning)
        user_type = self._get_user_type(user_context)
        
        # Generate replies based on stage and context
        replies = self._get_stage_replies(stage, user_type, user_intent)
        
        # Filter and rank based on business goals and user context
        ranked_replies = self._rank_replies(replies, user_context, user_intent)
        
        # Return top N replies
        return ranked_replies[:max_replies]
    
    def _detect_conversation_stage(
        self, 
        conversation_history: List[Dict[str, Any]], 
        user_context: Dict[str, Any]
    ) -> ConversationStage:
        """Detect current conversation stage based on history and context."""
        
        if not conversation_history or len(conversation_history) <= 1:
            return ConversationStage.WELCOME
        
        # Analyze recent messages for stage indicators
        recent_messages = conversation_history[-3:]  # Last 3 messages
        
        for message in recent_messages:
            content = message.get('content', '').lower()
            
            # Support stage indicators
            if any(word in content for word in ['help', 'issue', 'problem', 'error', 'support']):
                return ConversationStage.SUPPORT
            
            # Pricing/qualification stage
            if any(word in content for word in ['price', 'cost', 'budget', 'plan']):
                return ConversationStage.QUALIFICATION
            
            # Demo/presentation stage
            if any(word in content for word in ['demo', 'show', 'features', 'how it works']):
                return ConversationStage.PRESENTATION
        
        # Default progression: Welcome -> Discovery -> Qualification -> Presentation
        message_count = len(conversation_history)
        if message_count <= 2:
            return ConversationStage.WELCOME
        elif message_count <= 4:
            return ConversationStage.DISCOVERY
        elif message_count <= 6:
            return ConversationStage.QUALIFICATION
        else:
            return ConversationStage.PRESENTATION
    
    def _detect_user_intent(self, conversation_history: List[Dict[str, Any]]) -> UserIntent:
        """Detect user intent from conversation history."""
        
        if not conversation_history:
            return UserIntent.UNKNOWN
        
        # Analyze recent user messages
        user_messages = [msg for msg in conversation_history if msg.get('sender') == 'user']
        if not user_messages:
            return UserIntent.UNKNOWN
        
        recent_content = ' '.join([msg.get('content', '') for msg in user_messages[-2:]]).lower()
        
        # Intent detection patterns
        if any(word in recent_content for word in ['price', 'cost', 'pricing', 'plan', 'expensive']):
            return UserIntent.PRICING_INQUIRY
        
        if any(word in recent_content for word in ['demo', 'show', 'try', 'test']):
            return UserIntent.DEMO_REQUEST
        
        if any(word in recent_content for word in ['sales', 'buy', 'purchase', 'contact']):
            return UserIntent.SALES_CONTACT
        
        if any(word in recent_content for word in ['help', 'support', 'issue', 'problem']):
            return UserIntent.TECHNICAL_SUPPORT
        
        if any(word in recent_content for word in ['features', 'how', 'what', 'learn']):
            return UserIntent.PRODUCT_INFO
        
        return UserIntent.UNKNOWN
    
    def _get_user_type(self, user_context: Dict[str, Any]) -> str:
        """Determine if user is new or returning."""
        
        # Check if user has previous conversations
        if user_context.get('previous_conversations', 0) > 0:
            return "returning_user"
        
        # Check if user has been identified (email captured)
        if user_context.get('email') or user_context.get('is_lead'):
            return "returning_user"
        
        return "new_visitor"
    
    def _get_stage_replies(
        self, 
        stage: ConversationStage, 
        user_type: str, 
        user_intent: UserIntent
    ) -> List[Dict[str, Any]]:
        """Get replies for specific stage and user type."""
        
        stage_templates = self.reply_templates.get(stage, {})
        
        # Try to get specific replies for user type
        if user_type in stage_templates:
            return stage_templates[user_type].copy()
        
        # Fall back to first available template for the stage
        if stage_templates:
            return list(stage_templates.values())[0].copy()
        
        # Default fallback replies
        return [
            {"text": "Tell me more", "payload": "tell_more", "intent": "product_info"},
            {"text": "Contact sales", "payload": "contact_sales", "intent": "sales_contact"},
            {"text": "Get help", "payload": "get_help", "intent": "technical_support"}
        ]
    
    def _rank_replies(
        self, 
        replies: List[Dict[str, Any]], 
        user_context: Dict[str, Any], 
        user_intent: UserIntent
    ) -> List[Dict[str, Any]]:
        """Rank replies based on business goals and user context."""
        
        for reply in replies:
            score = 0.0
            
            # Boost replies that match user intent
            if reply.get('intent') == user_intent.value:
                score += 0.5
            
            # Boost based on business goals
            reply_intent = reply.get('intent')
            if reply_intent == 'sales_contact':
                score += self.business_goals.get('sales_conversion', 0)
            elif reply_intent == 'pricing_inquiry':
                score += self.business_goals.get('lead_generation', 0)
            elif reply_intent == 'product_info':
                score += self.business_goals.get('product_education', 0)
            elif reply_intent == 'technical_support':
                score += self.business_goals.get('support_resolution', 0)
            
            # Boost for high-value users
            if user_context.get('is_enterprise', False):
                if reply_intent in ['sales_contact', 'demo_request']:
                    score += 0.3
            
            reply['_score'] = score
        
        # Sort by score (descending)
        return sorted(replies, key=lambda x: x.get('_score', 0), reverse=True)
    
    def get_welcome_replies(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get welcome message quick replies."""
        return self.generate_quick_replies(
            conversation_history=[],
            user_context=user_context,
            stage=ConversationStage.WELCOME
        )
    
    def process_quick_reply_click(
        self, 
        payload: str, 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process quick reply click and return next action."""
        
        # Map payloads to actions
        action_map = {
            'pricing_info': {
                'response': 'Here are our pricing plans tailored for your business:',
                'next_stage': ConversationStage.QUALIFICATION,
                'trigger_action': 'show_pricing_cards'
            },
            'request_demo': {
                'response': 'I\'d love to show you NETVEXA in action! Let me schedule a personalized demo.',
                'next_stage': ConversationStage.QUALIFICATION,
                'trigger_action': 'show_demo_booking'
            },
            'contact_sales': {
                'response': 'Perfect! Let me connect you with our sales team.',
                'next_stage': ConversationStage.QUALIFICATION,
                'trigger_action': 'capture_lead_info'
            },
            'product_info': {
                'response': 'NETVEXA is an AI-powered platform that helps businesses deploy intelligent chat agents in under 1 hour.',
                'next_stage': ConversationStage.DISCOVERY,
                'trigger_action': 'show_feature_overview'
            }
        }
        
        return action_map.get(payload, {
            'response': 'Thanks for your interest! How can I help you further?',
            'next_stage': ConversationStage.DISCOVERY,
            'trigger_action': None
        })


# Usage example:
if __name__ == "__main__":
    engine = QuickReplyEngine()
    
    # Test welcome replies for new user
    user_context = {"is_new_user": True, "source": "website"}
    replies = engine.get_welcome_replies(user_context)
    
    print("Welcome Quick Replies:")
    for reply in replies:
        print(f"- {reply['text']} (payload: {reply['payload']})")