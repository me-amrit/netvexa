# WordPress Test Environment for NETVEXA Plugin

This Docker setup provides a complete WordPress testing environment for developing and testing the NETVEXA Chat plugin.

## Quick Start

### Start the WordPress Test Environment
```bash
cd wordpress-test
docker-compose up -d
```

### Access the Services
- **WordPress Site**: http://localhost:8080
- **WordPress Admin**: http://localhost:8080/wp-admin
- **Database Admin (phpMyAdmin)**: http://localhost:8081

### First-Time Setup
1. Visit http://localhost:8080 to complete WordPress installation
2. Create admin user (e.g., admin/password123)
3. Login to wp-admin and activate the NETVEXA Chat plugin
4. Configure the plugin with your API settings

### Plugin Development Workflow
1. Make changes to plugin files in `../wordpress-plugin/netvexa-chat/`
2. Changes are automatically reflected in the WordPress container
3. Test plugin functionality in the WordPress admin and frontend
4. Use browser dev tools to debug JavaScript and styles

### Database Access
- **Host**: localhost:3306 (from host machine) or wordpress-db:3306 (from containers)
- **Username**: wordpress
- **Password**: wordpress
- **Database**: wordpress
- **Root Password**: rootpassword

### Useful Commands

#### View Container Logs
```bash
docker-compose logs -f wordpress
docker-compose logs -f wordpress-db
```

#### Reset Environment (Clean Start)
```bash
docker-compose down -v  # Remove containers and volumes
docker-compose up -d    # Start fresh
```

#### Access WordPress Container Shell
```bash
docker exec -it netvexa-wordpress bash
```

#### Stop Environment
```bash
docker-compose down
```

## Plugin Testing Checklist

### Basic Functionality
- [ ] Plugin activates without errors
- [ ] Admin menu appears in WordPress admin
- [ ] Settings page loads and saves correctly
- [ ] Connection test works with NETVEXA API
- [ ] Chat widget appears on frontend
- [ ] Widget positioning works (bottom-left/bottom-right)
- [ ] Color customization works

### Integration Testing
- [ ] Widget loads without JavaScript errors
- [ ] Chat messages send to NETVEXA API
- [ ] Responses display correctly in widget
- [ ] Shortcode works: `[netvexa_chat]`
- [ ] Multiple widgets don't conflict

### WordPress Compatibility
- [ ] Works with default WordPress themes
- [ ] No conflicts with common plugins
- [ ] Proper WordPress coding standards
- [ ] Security best practices followed
- [ ] Translation ready

## Development Notes

### Plugin File Structure
```
netvexa-chat/
├── netvexa-chat.php          # Main plugin file
├── readme.txt                # WordPress plugin repository readme
├── assets/                   # CSS, JS, images
│   ├── admin.css
│   ├── admin.js
│   └── widget.js
├── includes/                 # PHP classes
│   ├── class-netvexa-chat.php
│   ├── class-netvexa-admin.php
│   ├── class-netvexa-widget.php
│   └── class-netvexa-shortcode.php
└── languages/               # Translation files
```

### API Integration
The plugin communicates with the NETVEXA API at:
- **Production**: https://api.netvexa.com
- **Development**: http://localhost:8000

### Security Considerations
- All user inputs are sanitized
- AJAX requests use WordPress nonces
- API keys are stored securely
- No direct file access allowed