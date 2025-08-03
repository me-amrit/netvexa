#!/bin/bash
# NETVEXA API cURL Examples
# Common API operations using cURL

# Set your API key
API_KEY="your_api_key_here"
BASE_URL="https://api.netvexa.com/api"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}NETVEXA API Examples${NC}\n"

# 1. Create an Agent
echo -e "${GREEN}1. Creating an agent...${NC}"
AGENT_RESPONSE=$(curl -s -X POST "$BASE_URL/agents" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Support Bot",
    "description": "Customer support assistant",
    "model": "gpt-3.5-turbo",
    "welcome_message": "Hello! How can I help you today?",
    "suggested_questions": [
      "What are your business hours?",
      "How do I contact support?",
      "Where can I find documentation?"
    ],
    "collect_email": true,
    "brand_color": "#2563eb"
  }')

AGENT_ID=$(echo $AGENT_RESPONSE | jq -r '.id')
echo "Agent created with ID: $AGENT_ID"
echo

# 2. Upload a Document
echo -e "${GREEN}2. Uploading knowledge base document...${NC}"
# Note: Replace with actual file path
curl -s -X POST "$BASE_URL/knowledge/ingest/file" \
  -H "X-API-Key: $API_KEY" \
  -F "file=@/path/to/document.pdf" \
  -F "agent_id=$AGENT_ID" \
  -F "title=Product Documentation"
echo -e "\n"

# 3. Import from URL
echo -e "${GREEN}3. Importing content from URL...${NC}"
curl -s -X POST "$BASE_URL/knowledge/ingest/url" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"https://example.com/faq\",
    \"agent_id\": \"$AGENT_ID\",
    \"title\": \"FAQ Page\",
    \"max_depth\": 1
  }"
echo -e "\n"

# 4. Test the Agent
echo -e "${GREEN}4. Testing agent response...${NC}"
TEST_RESPONSE=$(curl -s -X POST "$BASE_URL/agents/$AGENT_ID/test-message?message=What%20are%20your%20business%20hours%3F" \
  -H "X-API-Key: $API_KEY")
echo "Response: $(echo $TEST_RESPONSE | jq -r '.response')"
echo

# 5. Deploy the Agent
echo -e "${GREEN}5. Deploying agent...${NC}"
DEPLOY_RESPONSE=$(curl -s -X POST "$BASE_URL/agents/$AGENT_ID/deploy" \
  -H "X-API-Key: $API_KEY")
echo "Embed code:"
echo $DEPLOY_RESPONSE | jq -r '.embed_code'
echo

# 6. Create a Webhook
echo -e "${GREEN}6. Setting up webhook...${NC}"
curl -s -X POST "$BASE_URL/webhooks" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhook",
    "events": ["conversation.started", "lead.captured", "conversation.resolved"],
    "secret": "webhook_secret_key",
    "active": true
  }'
echo -e "\n"

# 7. Get Analytics
echo -e "${GREEN}7. Fetching analytics...${NC}"
ANALYTICS=$(curl -s -X GET "$BASE_URL/agents/$AGENT_ID/analytics" \
  -H "X-API-Key: $API_KEY")
echo "Total conversations: $(echo $ANALYTICS | jq -r '.metrics.total_conversations')"
echo "Average response time: $(echo $ANALYTICS | jq -r '.metrics.avg_response_time_seconds')s"
echo

# 8. List Conversations
echo -e "${GREEN}8. Listing recent conversations...${NC}"
curl -s -X GET "$BASE_URL/agents/$AGENT_ID/conversations?limit=5&status=active" \
  -H "X-API-Key: $API_KEY" | jq '.conversations[] | {id: .id, email: .visitor_email, messages: .message_count}'
echo

# 9. Get Usage Stats
echo -e "${GREEN}9. Checking usage statistics...${NC}"
USAGE=$(curl -s -X GET "$BASE_URL/billing/usage" \
  -H "X-API-Key: $API_KEY")
echo "Messages used: $(echo $USAGE | jq -r '.usage.messages') / $(echo $USAGE | jq -r '.limits.messages')"
echo "API calls: $(echo $USAGE | jq -r '.usage.api_calls') / $(echo $USAGE | jq -r '.limits.api_calls')"
echo "Active agents: $(echo $USAGE | jq -r '.usage.agents') / $(echo $USAGE | jq -r '.limits.agents')"
echo

# 10. Pagination Example
echo -e "${GREEN}10. Pagination example (list all documents)...${NC}"
PAGE=1
while true; do
  RESPONSE=$(curl -s -X GET "$BASE_URL/knowledge/documents?agent_id=$AGENT_ID&page=$PAGE&limit=10" \
    -H "X-API-Key: $API_KEY")
  
  TOTAL=$(echo $RESPONSE | jq -r '.total')
  DOCS=$(echo $RESPONSE | jq -r '.documents | length')
  
  echo "Page $PAGE: Found $DOCS documents"
  
  if [ $DOCS -eq 0 ]; then
    break
  fi
  
  PAGE=$((PAGE + 1))
done
echo

# Error Handling Example
echo -e "${GREEN}11. Error handling example...${NC}"
ERROR_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/agents" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": ""}')  # Invalid: empty name

HTTP_CODE=$(echo "$ERROR_RESPONSE" | tail -n1)
BODY=$(echo "$ERROR_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "201" ]; then
  echo "Error $HTTP_CODE: $(echo $BODY | jq -r '.error')"
  echo "Details: $(echo $BODY | jq -r '.details')"
fi

echo -e "\n${BLUE}Examples completed!${NC}"