jQuery(document).ready(function($) {
    // Test connection button
    $('#test-connection').on('click', function() {
        var button = $(this);
        var statusElement = $('#connection-status');
        
        button.prop('disabled', true);
        statusElement.text('Testing...').removeClass('success error');
        
        $.ajax({
            url: netvexa_admin.ajax_url,
            type: 'POST',
            data: {
                action: 'netvexa_test_connection',
                nonce: netvexa_admin.nonce
            },
            success: function(response) {
                if (response.success) {
                    statusElement.text(response.data.message).addClass('success');
                } else {
                    statusElement.text(response.data.message).addClass('error');
                }
            },
            error: function() {
                statusElement.text('Connection test failed').addClass('error');
            },
            complete: function() {
                button.prop('disabled', false);
            }
        });
    });
    
    // Load quick stats
    function loadQuickStats() {
        $.ajax({
            url: netvexa_admin.ajax_url,
            type: 'POST',
            data: {
                action: 'netvexa_get_stats',
                nonce: netvexa_admin.nonce
            },
            success: function(response) {
                if (response.success) {
                    var stats = response.data;
                    var html = '';
                    
                    html += '<div class="stat-item">';
                    html += '<span class="stat-label">Total Conversations</span>';
                    html += '<span class="stat-value">' + stats.total_conversations + '</span>';
                    html += '</div>';
                    
                    html += '<div class="stat-item">';
                    html += '<span class="stat-label">Active Visitors</span>';
                    html += '<span class="stat-value">' + stats.active_visitors + '</span>';
                    html += '</div>';
                    
                    html += '<div class="stat-item">';
                    html += '<span class="stat-label">Leads Captured</span>';
                    html += '<span class="stat-value">' + stats.leads_captured + '</span>';
                    html += '</div>';
                    
                    html += '<div class="stat-item">';
                    html += '<span class="stat-label">Status</span>';
                    html += '<span class="stat-value">';
                    html += '<span class="status-badge ' + (stats.status === 'Active' ? 'active' : 'inactive') + '">';
                    html += stats.status;
                    html += '</span>';
                    html += '</span>';
                    html += '</div>';
                    
                    $('#quick-stats').html(html);
                }
            }
        });
    }
    
    // Load stats on page load
    if ($('#quick-stats').length) {
        loadQuickStats();
        
        // Refresh stats every 30 seconds
        setInterval(loadQuickStats, 30000);
    }
});