<?php
/**
 * Shortcode functionality
 */
class Netvexa_Shortcode {
    
    public function render_shortcode($atts) {
        $attributes = shortcode_atts(array(
            'position' => get_option('netvexa_widget_position', 'bottom-right'),
            'color' => get_option('netvexa_widget_color', '#2563eb'),
            'height' => '600px',
            'width' => '400px'
        ), $atts);
        
        $agent_id = get_option('netvexa_agent_id', 'default_agent');
        $api_endpoint = get_option('netvexa_api_endpoint', 'http://localhost:8000');
        
        if (!$agent_id) {
            return '<p>' . __('Please configure NETVEXA Chat in the admin settings.', 'netvexa-chat') . '</p>';
        }
        
        // Generate unique ID for this instance
        $widget_id = 'netvexa-inline-' . uniqid();
        
        ob_start();
        ?>
        <div id="<?php echo esc_attr($widget_id); ?>" class="netvexa-inline-chat" style="height: <?php echo esc_attr($attributes['height']); ?>; width: <?php echo esc_attr($attributes['width']); ?>; max-width: 100%;">
            <div class="netvexa-loading"><?php _e('Loading chat...', 'netvexa-chat'); ?></div>
        </div>
        
        <script>
        (function() {
            if (typeof netvexa_inline_init === 'undefined') {
                window.netvexa_inline_init = function(id, config) {
                    // Initialize inline chat widget
                    var container = document.getElementById(id);
                    if (!container) return;
                    
                    // Create iframe for inline chat
                    var iframe = document.createElement('iframe');
                    iframe.src = config.api_endpoint + '/static/index.html?agent=' + config.agent_id + '&inline=true';
                    iframe.style.width = '100%';
                    iframe.style.height = '100%';
                    iframe.style.border = 'none';
                    iframe.style.borderRadius = '8px';
                    iframe.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                    
                    container.innerHTML = '';
                    container.appendChild(iframe);
                };
            }
            
            // Initialize this instance
            document.addEventListener('DOMContentLoaded', function() {
                netvexa_inline_init('<?php echo esc_js($widget_id); ?>', {
                    api_endpoint: '<?php echo esc_js($api_endpoint); ?>',
                    agent_id: '<?php echo esc_js($agent_id); ?>',
                    color: '<?php echo esc_js($attributes['color']); ?>'
                });
            });
        })();
        </script>
        
        <style>
        .netvexa-inline-chat {
            position: relative;
            margin: 20px 0;
        }
        .netvexa-loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #666;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        </style>
        <?php
        return ob_get_clean();
    }
}