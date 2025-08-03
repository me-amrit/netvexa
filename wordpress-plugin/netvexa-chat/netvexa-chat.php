<?php
/**
 * Plugin Name: NETVEXA Chat - AI Business Agent
 * Plugin URI: https://netvexa.com
 * Description: Deploy an AI-powered business agent on your website in under 60 minutes. Qualify leads, answer questions, and convert visitors 24/7.
 * Version: 1.0.0
 * Author: NETVEXA
 * Author URI: https://netvexa.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: netvexa-chat
 * Domain Path: /languages
 * Requires at least: 5.0
 * Tested up to: 6.4
 * Requires PHP: 7.4
 * Network: false
 * Update URI: https://updates.netvexa.com/wp-plugin/
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('NETVEXA_VERSION', '1.0.0');
define('NETVEXA_PLUGIN_URL', plugin_dir_url(__FILE__));
define('NETVEXA_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('NETVEXA_API_URL', 'https://api.netvexa.com');
define('NETVEXA_UPDATE_CHECK_URL', 'https://updates.netvexa.com/wp-plugin/check/');
define('NETVEXA_MIN_WP_VERSION', '5.0');
define('NETVEXA_MIN_PHP_VERSION', '7.4');

// Check system requirements
function netvexa_check_requirements() {
    $errors = array();
    
    // Check WordPress version
    if (version_compare(get_bloginfo('version'), NETVEXA_MIN_WP_VERSION, '<')) {
        $errors[] = sprintf(
            __('NETVEXA Chat requires WordPress %s or higher. You are running version %s.', 'netvexa-chat'),
            NETVEXA_MIN_WP_VERSION,
            get_bloginfo('version')
        );
    }
    
    // Check PHP version
    if (version_compare(PHP_VERSION, NETVEXA_MIN_PHP_VERSION, '<')) {
        $errors[] = sprintf(
            __('NETVEXA Chat requires PHP %s or higher. You are running version %s.', 'netvexa-chat'),
            NETVEXA_MIN_PHP_VERSION,
            PHP_VERSION
        );
    }
    
    // Check required PHP extensions
    $required_extensions = array('curl', 'json');
    foreach ($required_extensions as $extension) {
        if (!extension_loaded($extension)) {
            $errors[] = sprintf(
                __('NETVEXA Chat requires the PHP %s extension to be installed.', 'netvexa-chat'),
                $extension
            );
        }
    }
    
    return $errors;
}

// Include required files
require_once NETVEXA_PLUGIN_PATH . 'includes/class-netvexa-chat.php';
require_once NETVEXA_PLUGIN_PATH . 'includes/class-netvexa-admin.php';
require_once NETVEXA_PLUGIN_PATH . 'includes/class-netvexa-widget.php';
require_once NETVEXA_PLUGIN_PATH . 'includes/class-netvexa-shortcode.php';

// Initialize the plugin
function netvexa_chat_init() {
    // Check requirements first
    $errors = netvexa_check_requirements();
    if (!empty($errors)) {
        add_action('admin_notices', function() use ($errors) {
            foreach ($errors as $error) {
                echo '<div class="notice notice-error"><p>' . esc_html($error) . '</p></div>';
            }
        });
        return;
    }
    
    $plugin = new Netvexa_Chat();
    $plugin->run();
}
add_action('plugins_loaded', 'netvexa_chat_init');

// Activation hook
register_activation_hook(__FILE__, 'netvexa_chat_activate');
function netvexa_chat_activate() {
    // Check requirements before activation
    $errors = netvexa_check_requirements();
    if (!empty($errors)) {
        wp_die(
            implode('<br>', array_map('esc_html', $errors)) . 
            '<br><br><a href="' . admin_url('plugins.php') . '">' . __('Back to Plugins', 'netvexa-chat') . '</a>',
            __('Plugin Activation Error', 'netvexa-chat'),
            array('back_link' => true)
        );
    }
    
    // Create default options with better defaults
    $default_options = array(
        'netvexa_api_key' => '',
        'netvexa_agent_id' => '',
        'netvexa_api_endpoint' => 'http://localhost:8000', // Default for MVP
        'netvexa_widget_position' => 'bottom-right',
        'netvexa_widget_color' => '#2563eb',
        'netvexa_enable_chat' => false, // Disabled by default until configured
        'netvexa_version' => NETVEXA_VERSION,
        'netvexa_first_install' => current_time('mysql'),
        'netvexa_activation_redirect' => true
    );
    
    foreach ($default_options as $option => $value) {
        add_option($option, $value);
    }
    
    // Create custom database table for analytics (if needed)
    netvexa_create_analytics_table();
    
    // Schedule update check
    if (!wp_next_scheduled('netvexa_update_check')) {
        wp_schedule_event(time(), 'daily', 'netvexa_update_check');
    }
}

// Create analytics table
function netvexa_create_analytics_table() {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'netvexa_analytics';
    
    $charset_collate = $wpdb->get_charset_collate();
    
    $sql = "CREATE TABLE $table_name (
        id mediumint(9) NOT NULL AUTO_INCREMENT,
        event_type varchar(50) NOT NULL,
        event_data longtext,
        ip_address varchar(45),
        user_agent text,
        created_at datetime DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        KEY event_type (event_type),
        KEY created_at (created_at)
    ) $charset_collate;";
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
}

// Deactivation hook
register_deactivation_hook(__FILE__, 'netvexa_chat_deactivate');
function netvexa_chat_deactivate() {
    // Clear scheduled events
    wp_clear_scheduled_hook('netvexa_update_check');
    
    // Clear transients
    delete_transient('netvexa_update_check');
    delete_transient('netvexa_api_status');
}

// Uninstall hook - only remove data if user chooses to
register_uninstall_hook(__FILE__, 'netvexa_chat_uninstall');
function netvexa_chat_uninstall() {
    // Only remove data if user has enabled complete removal
    if (get_option('netvexa_remove_data_on_uninstall', false)) {
        global $wpdb;
        
        // Remove options
        $options_to_remove = array(
            'netvexa_api_key',
            'netvexa_agent_id',
            'netvexa_api_endpoint',
            'netvexa_widget_position',
            'netvexa_widget_color',
            'netvexa_enable_chat',
            'netvexa_version',
            'netvexa_first_install',
            'netvexa_remove_data_on_uninstall'
        );
        
        foreach ($options_to_remove as $option) {
            delete_option($option);
        }
        
        // Remove analytics table
        $table_name = $wpdb->prefix . 'netvexa_analytics';
        $wpdb->query("DROP TABLE IF EXISTS $table_name");
        
        // Clear scheduled events
        wp_clear_scheduled_hook('netvexa_update_check');
    }
}

// Auto-update functionality
add_action('netvexa_update_check', 'netvexa_check_for_updates');
function netvexa_check_for_updates() {
    $current_version = NETVEXA_VERSION;
    $plugin_slug = plugin_basename(__FILE__);
    
    $remote_version = wp_remote_get(NETVEXA_UPDATE_CHECK_URL . '?plugin=' . $plugin_slug . '&version=' . $current_version);
    
    if (!is_wp_error($remote_version)) {
        $version_info = json_decode(wp_remote_retrieve_body($remote_version), true);
        
        if (isset($version_info['new_version']) && version_compare($current_version, $version_info['new_version'], '<')) {
            set_transient('netvexa_update_available', $version_info, DAY_IN_SECONDS);
        }
    }
}

// Add update notification
add_action('admin_notices', 'netvexa_update_notice');
function netvexa_update_notice() {
    $update_info = get_transient('netvexa_update_available');
    if ($update_info && current_user_can('update_plugins')) {
        echo '<div class="notice notice-info">';
        echo '<p><strong>' . __('NETVEXA Chat Update Available!', 'netvexa-chat') . '</strong></p>';
        echo '<p>' . sprintf(
            __('Version %s is available. <a href="%s">Update now</a> or <a href="%s" target="_blank">view details</a>.', 'netvexa-chat'),
            esc_html($update_info['new_version']),
            wp_nonce_url(self_admin_url('update.php?action=upgrade-plugin&plugin=' . plugin_basename(__FILE__)), 'upgrade-plugin_' . plugin_basename(__FILE__)),
            esc_url($update_info['details_url'])
        ) . '</p>';
        echo '</div>';
    }
}

// Add settings link on plugin page
add_filter('plugin_action_links_' . plugin_basename(__FILE__), 'netvexa_add_settings_link');
function netvexa_add_settings_link($links) {
    $settings_link = '<a href="admin.php?page=netvexa-settings">' . __('Settings', 'netvexa-chat') . '</a>';
    array_unshift($links, $settings_link);
    return $links;
}