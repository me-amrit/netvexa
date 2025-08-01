<?php
/**
 * Main plugin class
 */
class Netvexa_Chat {
    
    protected $admin;
    protected $widget;
    protected $shortcode;
    
    public function __construct() {
        $this->load_dependencies();
    }
    
    private function load_dependencies() {
        $this->admin = new Netvexa_Admin();
        $this->widget = new Netvexa_Widget();
        $this->shortcode = new Netvexa_Shortcode();
    }
    
    public function run() {
        // Admin hooks
        add_action('admin_menu', array($this->admin, 'add_admin_menu'));
        add_action('admin_init', array($this->admin, 'register_settings'));
        add_action('admin_enqueue_scripts', array($this->admin, 'enqueue_admin_scripts'));
        
        // Frontend hooks
        add_action('wp_enqueue_scripts', array($this->widget, 'enqueue_scripts'));
        add_action('wp_footer', array($this->widget, 'render_widget'));
        
        // Shortcode
        add_shortcode('netvexa_chat', array($this->shortcode, 'render_shortcode'));
        
        // Activation redirect
        add_action('admin_init', array($this, 'activation_redirect'));
        
        // AJAX handlers
        add_action('wp_ajax_netvexa_test_connection', array($this->admin, 'test_connection'));
        add_action('wp_ajax_netvexa_get_stats', array($this->admin, 'get_stats'));
    }
    
    public function activation_redirect() {
        if (get_option('netvexa_activation_redirect', false)) {
            delete_option('netvexa_activation_redirect');
            if (!isset($_GET['activate-multi'])) {
                wp_redirect(admin_url('admin.php?page=netvexa-settings'));
                exit;
            }
        }
    }
}