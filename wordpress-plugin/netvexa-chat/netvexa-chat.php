<?php
/**
 * Plugin Name: NETVEXA Chat - AI Business Agent
 * Plugin URI: https://netvexa.com
 * Description: Deploy an AI-powered business agent on your website in under 60 minutes. Qualify leads, answer questions, and convert visitors 24/7.
 * Version: 0.1.0
 * Author: NETVEXA
 * Author URI: https://netvexa.com
 * License: GPL v2 or later
 * Text Domain: netvexa-chat
 * Domain Path: /languages
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('NETVEXA_VERSION', '0.1.0');
define('NETVEXA_PLUGIN_URL', plugin_dir_url(__FILE__));
define('NETVEXA_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('NETVEXA_API_URL', 'https://api.netvexa.com'); // Will use localhost for MVP

// Include required files
require_once NETVEXA_PLUGIN_PATH . 'includes/class-netvexa-chat.php';
require_once NETVEXA_PLUGIN_PATH . 'includes/class-netvexa-admin.php';
require_once NETVEXA_PLUGIN_PATH . 'includes/class-netvexa-widget.php';
require_once NETVEXA_PLUGIN_PATH . 'includes/class-netvexa-shortcode.php';

// Initialize the plugin
function netvexa_chat_init() {
    $plugin = new Netvexa_Chat();
    $plugin->run();
}
add_action('plugins_loaded', 'netvexa_chat_init');

// Activation hook
register_activation_hook(__FILE__, 'netvexa_chat_activate');
function netvexa_chat_activate() {
    // Create default options
    add_option('netvexa_api_key', '');
    add_option('netvexa_agent_id', '');
    add_option('netvexa_widget_position', 'bottom-right');
    add_option('netvexa_widget_color', '#2563eb');
    add_option('netvexa_enable_chat', true);
    
    // Set activation redirect flag
    add_option('netvexa_activation_redirect', true);
}

// Deactivation hook
register_deactivation_hook(__FILE__, 'netvexa_chat_deactivate');
function netvexa_chat_deactivate() {
    // Clean up if needed
}

// Add settings link on plugin page
add_filter('plugin_action_links_' . plugin_basename(__FILE__), 'netvexa_add_settings_link');
function netvexa_add_settings_link($links) {
    $settings_link = '<a href="admin.php?page=netvexa-settings">' . __('Settings', 'netvexa-chat') . '</a>';
    array_unshift($links, $settings_link);
    return $links;
}