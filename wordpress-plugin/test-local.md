# Testing NETVEXA WordPress Plugin Locally

## Quick Start

### 1. Start Backend API
```bash
cd /Users/amrit/Repo/netvexa/backend
./run_mvp.sh
```

### 2. Verify API is Running
- Open http://localhost:8000
- Test chat at http://localhost:8000/static/index.html

### 3. Install Plugin in WordPress
```bash
# Copy to your WordPress plugins directory
cp -r /Users/amrit/Repo/netvexa/wordpress-plugin/netvexa-chat /path/to/wordpress/wp-content/plugins/
```

### 4. Activate & Configure
1. WordPress Admin → Plugins → Activate "NETVEXA Chat"
2. Go to NETVEXA Chat settings
3. Configure:
   - API Endpoint: `http://localhost:8000`
   - API Key: `test-api-key`
   - Agent ID: `test-agent-001`

### 5. Test Features
- ✅ Connection test button
- ✅ Chat widget on frontend
- ✅ Send messages through widget
- ✅ Shortcode `[netvexa_chat]`

## Troubleshooting

### Widget Not Showing?
1. Check browser console for errors
2. Verify API is running
3. Check CORS settings

### Connection Failed?
1. Ensure backend is running on port 8000
2. Check firewall settings
3. Try `127.0.0.1` instead of `localhost`

### Chat Not Working?
1. Check WebSocket connection in browser console
2. Verify agent ID matches backend configuration
3. Check for JavaScript errors