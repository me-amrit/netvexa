#!/usr/bin/env node
/**
 * NETVEXA API JavaScript Example
 * Demonstrates common API operations
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class NetvexaClient {
  constructor(apiKey, baseUrl = 'https://api.netvexa.com/api') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json'
      }
    });
  }

  async createAgent(data) {
    const response = await this.client.post('/agents', {
      name: data.name,
      description: data.description,
      model: data.model || 'gpt-3.5-turbo',
      welcome_message: data.welcomeMessage || 'Hello! How can I help you today?',
      collect_email: data.collectEmail !== false,
      suggested_questions: data.suggestedQuestions || []
    });
    return response.data;
  }

  async uploadDocument(agentId, filePath, title) {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    formData.append('agent_id', agentId);
    if (title) {
      formData.append('title', title);
    }

    const response = await axios.post(
      `${this.baseUrl}/knowledge/ingest/file`,
      formData,
      {
        headers: {
          'X-API-Key': this.apiKey,
          ...formData.getHeaders()
        }
      }
    );
    return response.data;
  }

  async testAgent(agentId, message) {
    const response = await this.client.post(
      `/agents/${agentId}/test-message`,
      {},
      { params: { message } }
    );
    return response.data;
  }

  async deployAgent(agentId) {
    const response = await this.client.post(`/agents/${agentId}/deploy`);
    return response.data;
  }

  async getAnalytics(agentId, options = {}) {
    const response = await this.client.get(`/agents/${agentId}/analytics`, {
      params: options
    });
    return response.data;
  }

  async listConversations(agentId, options = {}) {
    const response = await this.client.get(`/agents/${agentId}/conversations`, {
      params: options
    });
    return response.data;
  }

  async createWebhook(url, events) {
    const response = await this.client.post('/webhooks', {
      url,
      events,
      active: true
    });
    return response.data;
  }
}

async function main() {
  // Initialize client
  const apiKey = process.env.NETVEXA_API_KEY;
  if (!apiKey) {
    console.error('Please set NETVEXA_API_KEY environment variable');
    process.exit(1);
  }

  const client = new NetvexaClient(apiKey);

  try {
    // 1. Create an agent
    console.log('Creating agent...');
    const agent = await client.createAgent({
      name: 'Customer Service Assistant',
      description: 'Helps customers with inquiries and support',
      model: 'gpt-3.5-turbo',
      welcomeMessage: 'Welcome! I\'m here to help. What can I do for you today?',
      suggestedQuestions: [
        'What are your business hours?',
        'How do I track my order?',
        'What is your return policy?'
      ]
    });
    console.log(`✓ Agent created: ${agent.id}`);

    // 2. Upload knowledge base (if file exists)
    /*
    console.log('\nUploading knowledge base...');
    const document = await client.uploadDocument(
      agent.id,
      './knowledge/faq.pdf',
      'Frequently Asked Questions'
    );
    console.log(`✓ Document uploaded: ${document.id}`);
    */

    // 3. Test the agent
    console.log('\nTesting agent...');
    const testResponse = await client.testAgent(
      agent.id,
      'What products do you offer?'
    );
    console.log(`✓ Test response: ${testResponse.response}`);

    // 4. Deploy the agent
    console.log('\nDeploying agent...');
    const deployment = await client.deployAgent(agent.id);
    console.log('✓ Agent deployed!');
    console.log('Embed code:');
    console.log(deployment.embed_code);

    // 5. Set up webhook
    console.log('\nSetting up webhook...');
    const webhook = await client.createWebhook(
      'https://your-app.com/netvexa-webhook',
      ['conversation.started', 'lead.captured']
    );
    console.log(`✓ Webhook created: ${webhook.id}`);

    // 6. Get analytics
    console.log('\nFetching analytics...');
    const analytics = await client.getAnalytics(agent.id);
    console.log('Analytics summary:');
    console.log(`- Total conversations: ${analytics.metrics.total_conversations}`);
    console.log(`- Unique visitors: ${analytics.metrics.unique_visitors}`);
    console.log(`- Average response time: ${analytics.metrics.avg_response_time_seconds}s`);

    // 7. List conversations
    console.log('\nListing conversations...');
    const conversations = await client.listConversations(agent.id, {
      status: 'active',
      limit: 5
    });
    console.log(`✓ Found ${conversations.total} conversations`);
    conversations.conversations.forEach(conv => {
      console.log(`  - ${conv.id}: ${conv.visitor_email || 'Anonymous'} (${conv.message_count} messages)`);
    });

  } catch (error) {
    console.error('API Error:', error.message);
    if (error.response?.data) {
      console.error('Details:', error.response.data);
    }
  }
}

// Run the example
main();