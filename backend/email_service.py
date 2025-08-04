"""
Email service for NETVEXA lead notifications and system emails.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from jinja2 import Template

from config import settings
from lead_models import Lead, HandoffRequest

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME
    
    def _create_smtp_connection(self):
        """Create SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.smtp_use_tls:
                server.starttls()
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {e}")
            raise
    
    def _send_email(self, to_emails: List[str], subject: str, html_content: str, text_content: Optional[str] = None):
        """Send email using SMTP"""
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email send")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(to_emails)
            
            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with self._create_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_lead_notification(self, lead: Lead, user_email: str):
        """Send new lead notification to user"""
        
        subject = f"New Lead Captured: {lead.email}"
        
        html_template = Template('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>New Lead Notification</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .lead-info { background: white; padding: 15px; border-radius: 5px; margin: 10px 0; }
                .label { font-weight: bold; color: #666; }
                .value { margin-left: 10px; }
                .cta { text-align: center; margin: 20px 0; }
                .cta a { 
                    background: #2563eb; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    display: inline-block;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 New Lead Captured!</h1>
                </div>
                <div class="content">
                    <p>Great news! A new lead has been captured through your NETVEXA agent.</p>
                    
                    <div class="lead-info">
                        <h3>Lead Details:</h3>
                        <p><span class="label">Email:</span><span class="value">{{ lead.email }}</span></p>
                        {% if lead.name %}
                        <p><span class="label">Name:</span><span class="value">{{ lead.name }}</span></p>
                        {% endif %}
                        {% if lead.company %}
                        <p><span class="label">Company:</span><span class="value">{{ lead.company }}</span></p>
                        {% endif %}
                        {% if lead.phone %}
                        <p><span class="label">Phone:</span><span class="value">{{ lead.phone }}</span></p>
                        {% endif %}
                        <p><span class="label">Source:</span><span class="value">{{ lead.source.value.replace('_', ' ').title() }}</span></p>
                        <p><span class="label">Lead Score:</span><span class="value">{{ lead.score }}/100</span></p>
                        <p><span class="label">Captured:</span><span class="value">{{ lead.created_at.strftime('%Y-%m-%d %H:%M UTC') }}</span></p>
                    </div>
                    
                    <div class="cta">
                        <a href="https://dashboard.netvexa.com/leads" target="_blank">
                            View Lead in Dashboard
                        </a>
                    </div>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        <li>Review the lead details in your dashboard</li>
                        <li>Follow up with the lead within 24 hours for best results</li>
                        <li>Update the lead status as you progress</li>
                    </ul>
                    
                    <p>Happy selling!<br>The NETVEXA Team</p>
                </div>
            </div>
        </body>
        </html>
        ''')
        
        text_content = f'''
        New Lead Captured!
        
        Lead Details:
        Email: {lead.email}
        Name: {lead.name or 'Not provided'}
        Company: {lead.company or 'Not provided'}
        Phone: {lead.phone or 'Not provided'}
        Source: {lead.source.value.replace('_', ' ').title()}
        Lead Score: {lead.score}/100
        Captured: {lead.created_at.strftime('%Y-%m-%d %H:%M UTC')}
        
        View this lead in your dashboard: https://dashboard.netvexa.com/leads
        
        Best regards,
        The NETVEXA Team
        '''
        
        html_content = html_template.render(lead=lead)
        
        return self._send_email([user_email], subject, html_content, text_content)
    
    def send_handoff_notification(self, handoff: HandoffRequest, user_email: str, lead: Lead):
        """Send human handoff notification to user"""
        
        subject = f"Human Handoff Request: {lead.email}"
        
        html_template = Template('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Human Handoff Request</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #f59e0b; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .handoff-info { background: white; padding: 15px; border-radius: 5px; margin: 10px 0; }
                .priority-high { border-left: 4px solid #ef4444; }
                .priority-normal { border-left: 4px solid #f59e0b; }
                .priority-low { border-left: 4px solid #10b981; }
                .label { font-weight: bold; color: #666; }
                .value { margin-left: 10px; }
                .cta { text-align: center; margin: 20px 0; }
                .cta a { 
                    background: #f59e0b; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    display: inline-block;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>👨‍💼 Human Handoff Request</h1>
                </div>
                <div class="content">
                    <p>A human handoff has been requested for one of your leads.</p>
                    
                    <div class="handoff-info priority-{{ handoff.priority }}">
                        <h3>Handoff Details:</h3>
                        <p><span class="label">Lead:</span><span class="value">{{ lead.name or lead.email }}</span></p>
                        <p><span class="label">Priority:</span><span class="value">{{ handoff.priority.title() }}</span></p>
                        {% if handoff.reason %}
                        <p><span class="label">Reason:</span><span class="value">{{ handoff.reason }}</span></p>
                        {% endif %}
                        <p><span class="label">Requested:</span><span class="value">{{ handoff.created_at.strftime('%Y-%m-%d %H:%M UTC') }}</span></p>
                    </div>
                    
                    <div class="handoff-info">
                        <h3>Lead Information:</h3>
                        <p><span class="label">Email:</span><span class="value">{{ lead.email }}</span></p>
                        {% if lead.company %}
                        <p><span class="label">Company:</span><span class="value">{{ lead.company }}</span></p>
                        {% endif %}
                        {% if lead.phone %}
                        <p><span class="label">Phone:</span><span class="value">{{ lead.phone }}</span></p>
                        {% endif %}
                        <p><span class="label">Lead Score:</span><span class="value">{{ lead.score }}/100</span></p>
                    </div>
                    
                    <div class="cta">
                        <a href="https://dashboard.netvexa.com/leads" target="_blank">
                            Handle Handoff Request
                        </a>
                    </div>
                    
                    <p><strong>Action Required:</strong></p>
                    <ul>
                        <li>Review the handoff request in your dashboard</li>
                        <li>Assign the request to a human agent</li>
                        <li>Contact the lead directly if needed</li>
                    </ul>
                    
                    <p>Best regards,<br>The NETVEXA Team</p>
                </div>
            </div>
        </body>
        </html>
        ''')
        
        text_content = f'''
        Human Handoff Request
        
        Handoff Details:
        Lead: {lead.name or lead.email}
        Priority: {handoff.priority.title()}
        Reason: {handoff.reason or 'Not specified'}
        Requested: {handoff.created_at.strftime('%Y-%m-%d %H:%M UTC')}
        
        Lead Information:
        Email: {lead.email}
        Company: {lead.company or 'Not provided'}
        Phone: {lead.phone or 'Not provided'}
        Lead Score: {lead.score}/100
        
        Handle this request in your dashboard: https://dashboard.netvexa.com/leads
        
        Best regards,
        The NETVEXA Team
        '''
        
        html_content = html_template.render(handoff=handoff, lead=lead)
        
        return self._send_email([user_email], subject, html_content, text_content)


# Global email service instance
email_service = EmailService()


# Helper functions for background tasks
async def send_lead_notification_email(lead: Lead, user_email: str):
    """Background task to send lead notification email"""
    try:
        email_service.send_lead_notification(lead, user_email)
    except Exception as e:
        logger.error(f"Failed to send lead notification email: {e}")


async def send_handoff_notification_email(handoff: HandoffRequest, user_email: str, lead: Lead):
    """Background task to send handoff notification email"""
    try:
        email_service.send_handoff_notification(handoff, user_email, lead)
    except Exception as e:
        logger.error(f"Failed to send handoff notification email: {e}")