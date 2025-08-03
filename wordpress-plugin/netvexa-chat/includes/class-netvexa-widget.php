<?php
/**
 * Frontend widget functionality
 */
class Netvexa_Widget {
    
    public function enqueue_scripts() {
        if (!get_option('netvexa_enable_chat', true)) {
            return;
        }
        
        wp_enqueue_script(
            'netvexa-widget',
            NETVEXA_PLUGIN_URL . 'assets/widget.js',
            array(),
            NETVEXA_VERSION,
            true
        );
        
        wp_localize_script('netvexa-widget', 'netvexa_config', array(
            'api_endpoint' => get_option('netvexa_api_endpoint', 'http://localhost:8000'),
            'agent_id' => get_option('netvexa_agent_id', 'default_agent'),
            'position' => get_option('netvexa_widget_position', 'bottom-right'),
            'color' => get_option('netvexa_widget_color', '#2563eb'),
            'site_url' => home_url(),
            'page_title' => get_the_title(),
            'page_url' => get_permalink()
        ));
    }
    
    public function render_widget() {
        if (!get_option('netvexa_enable_chat', true)) {
            return;
        }
        
        if (!get_option('netvexa_agent_id')) {
            return;
        }
        
        ?>
        <!-- NETVEXA Chat Widget Container -->
        <div id="netvexa-chat-widget"></div>
        <?php
    }
}