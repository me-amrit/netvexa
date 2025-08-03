<?php
/**
 * Admin functionality
 */
class Netvexa_Admin {
    
    public function add_admin_menu() {
        // Main menu
        add_menu_page(
            __('NETVEXA Chat', 'netvexa-chat'),
            __('NETVEXA Chat', 'netvexa-chat'),
            'manage_options',
            'netvexa-settings',
            array($this, 'settings_page'),
            'dashicons-format-chat',
            30
        );
        
        // Submenu items
        add_submenu_page(
            'netvexa-settings',
            __('Settings', 'netvexa-chat'),
            __('Settings', 'netvexa-chat'),
            'manage_options',
            'netvexa-settings',
            array($this, 'settings_page')
        );
        
        add_submenu_page(
            'netvexa-settings',
            __('Analytics', 'netvexa-chat'),
            __('Analytics', 'netvexa-chat'),
            'manage_options',
            'netvexa-analytics',
            array($this, 'analytics_page')
        );
    }
    
    public function register_settings() {
        // Register settings
        register_setting('netvexa_settings_group', 'netvexa_api_key');
        register_setting('netvexa_settings_group', 'netvexa_agent_id');
        register_setting('netvexa_settings_group', 'netvexa_widget_position');
        register_setting('netvexa_settings_group', 'netvexa_widget_color');
        register_setting('netvexa_settings_group', 'netvexa_enable_chat');
        register_setting('netvexa_settings_group', 'netvexa_api_endpoint');
    }
    
    public function enqueue_admin_scripts($hook) {
        if (strpos($hook, 'netvexa') === false) {
            return;
        }
        
        wp_enqueue_style(
            'netvexa-admin',
            NETVEXA_PLUGIN_URL . 'assets/admin.css',
            array(),
            NETVEXA_VERSION
        );
        
        wp_enqueue_script(
            'netvexa-admin',
            NETVEXA_PLUGIN_URL . 'assets/admin.js',
            array('jquery'),
            NETVEXA_VERSION,
            true
        );
        
        wp_localize_script('netvexa-admin', 'netvexa_admin', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('netvexa_admin_nonce')
        ));
    }
    
    public function settings_page() {
        ?>
        <div class="wrap">
            <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
            
            <?php if (isset($_GET['settings-updated'])) : ?>
                <div class="notice notice-success is-dismissible">
                    <p><?php _e('Settings saved successfully!', 'netvexa-chat'); ?></p>
                </div>
            <?php endif; ?>
            
            <div class="netvexa-admin-container">
                <div class="netvexa-main-content">
                    <form method="post" action="options.php">
                        <?php settings_fields('netvexa_settings_group'); ?>
                        
                        <div class="netvexa-card">
                            <h2><?php _e('Quick Setup', 'netvexa-chat'); ?></h2>
                            <p><?php _e('Get your AI business agent running in less than 60 minutes!', 'netvexa-chat'); ?></p>
                            
                            <table class="form-table">
                                <tr>
                                    <th scope="row">
                                        <label for="netvexa_api_key"><?php _e('API Key', 'netvexa-chat'); ?></label>
                                    </th>
                                    <td>
                                        <input type="password" 
                                               id="netvexa_api_key" 
                                               name="netvexa_api_key" 
                                               value="<?php echo esc_attr(get_option('netvexa_api_key')); ?>" 
                                               class="regular-text" />
                                        <p class="description">
                                            <?php _e('Don\'t have an API key?', 'netvexa-chat'); ?>
                                            <a href="https://app.netvexa.com/register" target="_blank"><?php _e('Get one here', 'netvexa-chat'); ?></a>
                                        </p>
                                    </td>
                                </tr>
                                
                                <tr>
                                    <th scope="row">
                                        <label for="netvexa_api_endpoint"><?php _e('API Endpoint', 'netvexa-chat'); ?></label>
                                    </th>
                                    <td>
                                        <input type="url" 
                                               id="netvexa_api_endpoint" 
                                               name="netvexa_api_endpoint" 
                                               value="<?php echo esc_attr(get_option('netvexa_api_endpoint', 'http://localhost:8000')); ?>" 
                                               class="regular-text" />
                                        <p class="description">
                                            <?php _e('For MVP testing, use http://localhost:8000', 'netvexa-chat'); ?>
                                        </p>
                                    </td>
                                </tr>
                                
                                <tr>
                                    <th scope="row">
                                        <label for="netvexa_agent_id"><?php _e('Agent ID', 'netvexa-chat'); ?></label>
                                    </th>
                                    <td>
                                        <input type="text" 
                                               id="netvexa_agent_id" 
                                               name="netvexa_agent_id" 
                                               value="<?php echo esc_attr(get_option('netvexa_agent_id', 'default_agent')); ?>" 
                                               class="regular-text" />
                                        <button type="button" class="button" id="test-connection">
                                            <?php _e('Test Connection', 'netvexa-chat'); ?>
                                        </button>
                                        <span id="connection-status"></span>
                                    </td>
                                </tr>
                            </table>
                        </div>
                        
                        <div class="netvexa-card">
                            <h2><?php _e('Widget Appearance', 'netvexa-chat'); ?></h2>
                            
                            <table class="form-table">
                                <tr>
                                    <th scope="row">
                                        <label for="netvexa_enable_chat"><?php _e('Enable Chat Widget', 'netvexa-chat'); ?></label>
                                    </th>
                                    <td>
                                        <label>
                                            <input type="checkbox" 
                                                   id="netvexa_enable_chat" 
                                                   name="netvexa_enable_chat" 
                                                   value="1" 
                                                   <?php checked(get_option('netvexa_enable_chat', true)); ?> />
                                            <?php _e('Show chat widget on your website', 'netvexa-chat'); ?>
                                        </label>
                                    </td>
                                </tr>
                                
                                <tr>
                                    <th scope="row">
                                        <label for="netvexa_widget_position"><?php _e('Widget Position', 'netvexa-chat'); ?></label>
                                    </th>
                                    <td>
                                        <select id="netvexa_widget_position" name="netvexa_widget_position">
                                            <option value="bottom-right" <?php selected(get_option('netvexa_widget_position'), 'bottom-right'); ?>>
                                                <?php _e('Bottom Right', 'netvexa-chat'); ?>
                                            </option>
                                            <option value="bottom-left" <?php selected(get_option('netvexa_widget_position'), 'bottom-left'); ?>>
                                                <?php _e('Bottom Left', 'netvexa-chat'); ?>
                                            </option>
                                        </select>
                                    </td>
                                </tr>
                                
                                <tr>
                                    <th scope="row">
                                        <label for="netvexa_widget_color"><?php _e('Primary Color', 'netvexa-chat'); ?></label>
                                    </th>
                                    <td>
                                        <input type="color" 
                                               id="netvexa_widget_color" 
                                               name="netvexa_widget_color" 
                                               value="<?php echo esc_attr(get_option('netvexa_widget_color', '#2563eb')); ?>" />
                                    </td>
                                </tr>
                            </table>
                        </div>
                        
                        <div class="netvexa-card">
                            <h2><?php _e('Shortcode Usage', 'netvexa-chat'); ?></h2>
                            <p><?php _e('Use this shortcode to embed the chat widget anywhere on your site:', 'netvexa-chat'); ?></p>
                            <code>[netvexa_chat]</code>
                            <p><?php _e('Or with custom settings:', 'netvexa-chat'); ?></p>
                            <code>[netvexa_chat position="bottom-left" color="#10b981"]</code>
                        </div>
                        
                        <?php submit_button(__('Save Settings', 'netvexa-chat')); ?>
                    </form>
                </div>
                
                <div class="netvexa-sidebar">
                    <div class="netvexa-card">
                        <h3><?php _e('Quick Stats', 'netvexa-chat'); ?></h3>
                        <div id="quick-stats">
                            <p><?php _e('Loading...', 'netvexa-chat'); ?></p>
                        </div>
                    </div>
                    
                    <div class="netvexa-card">
                        <h3><?php _e('Need Help?', 'netvexa-chat'); ?></h3>
                        <p><?php _e('Check out our resources:', 'netvexa-chat'); ?></p>
                        <ul>
                            <li><a href="https://docs.netvexa.com" target="_blank"><?php _e('Documentation', 'netvexa-chat'); ?></a></li>
                            <li><a href="https://netvexa.com/support" target="_blank"><?php _e('Support Center', 'netvexa-chat'); ?></a></li>
                            <li><a href="https://app.netvexa.com" target="_blank"><?php _e('Dashboard', 'netvexa-chat'); ?></a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        <?php
    }
    
    public function analytics_page() {
        ?>
        <div class="wrap">
            <h1><?php _e('Analytics', 'netvexa-chat'); ?></h1>
            
            <div class="netvexa-card">
                <h2><?php _e('Coming Soon', 'netvexa-chat'); ?></h2>
                <p><?php _e('Detailed analytics will be available in the next version. For now, visit your NETVEXA dashboard for full analytics.', 'netvexa-chat'); ?></p>
                <a href="https://app.netvexa.com" target="_blank" class="button button-primary">
                    <?php _e('View Full Analytics', 'netvexa-chat'); ?>
                </a>
            </div>
        </div>
        <?php
    }
    
    public function test_connection() {
        // Verify nonce for security
        if (!check_ajax_referer('netvexa_admin_nonce', 'nonce', false)) {
            wp_send_json_error(array('message' => __('Security check failed.', 'netvexa-chat')));
            return;
        }
        
        // Check user permissions
        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('Insufficient permissions.', 'netvexa-chat')));
            return;
        }
        
        $api_endpoint = sanitize_url(get_option('netvexa_api_endpoint', 'http://localhost:8000'));
        $agent_id = sanitize_text_field(get_option('netvexa_agent_id', ''));
        
        if (empty($agent_id)) {
            wp_send_json_error(array('message' => __('Please enter an Agent ID first.', 'netvexa-chat')));
            return;
        }
        
        // Validate API endpoint format
        if (!filter_var($api_endpoint, FILTER_VALIDATE_URL)) {
            wp_send_json_error(array('message' => __('Invalid API endpoint URL.', 'netvexa-chat')));
            return;
        }
        
        // Test connection to API with timeout and user agent
        $response = wp_remote_get($api_endpoint . '/api/agents/' . urlencode($agent_id) . '/config', array(
            'timeout' => 15,
            'user-agent' => 'NETVEXA-WordPress-Plugin/' . NETVEXA_VERSION,
            'headers' => array(
                'Accept' => 'application/json',
            )
        ));
        
        if (is_wp_error($response)) {
            wp_send_json_error(array(
                'message' => sprintf(
                    __('Connection failed: %s', 'netvexa-chat'),
                    $response->get_error_message()
                )
            ));
            return;
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        $response_body = wp_remote_retrieve_body($response);
        
        if ($status_code === 200) {
            // Store successful connection timestamp
            update_option('netvexa_last_connection_test', current_time('mysql'));
            
            // Try to parse agent info
            $agent_data = json_decode($response_body, true);
            $agent_name = isset($agent_data['name']) ? $agent_data['name'] : __('Unknown Agent', 'netvexa-chat');
            
            wp_send_json_success(array(
                'message' => sprintf(
                    __('Connection successful! Connected to agent: %s', 'netvexa-chat'),
                    esc_html($agent_name)
                )
            ));
        } else {
            wp_send_json_error(array(
                'message' => sprintf(
                    __('Connection failed. Status: %d. Please check your API endpoint and Agent ID.', 'netvexa-chat'),
                    $status_code
                )
            ));
        }
    }
    
    public function get_stats() {
        check_ajax_referer('netvexa_admin_nonce', 'nonce');
        
        // For MVP, return mock stats
        $stats = array(
            'total_conversations' => 0,
            'active_visitors' => 0,
            'leads_captured' => 0,
            'status' => get_option('netvexa_enable_chat') ? 'Active' : 'Inactive'
        );
        
        wp_send_json_success($stats);
    }
}