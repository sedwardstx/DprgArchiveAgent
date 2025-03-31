# Security and Performance Implementation Examples

This document provides practical examples and implementation details for the security and performance recommendations outlined in the WordPress integration guide.

## Security Implementation Examples

### 1. Rate Limiting Implementation

```php
// In class-api-client.php
class DPRG_Archive_Agent_API_Client {
    private $rate_limit_key = 'dprg_api_rate_limit_';
    private $rate_limit_period = 3600; // 1 hour
    private $max_requests = 100; // Maximum requests per hour

    public function check_rate_limit($user_id) {
        $key = $this->rate_limit_key . $user_id;
        $current_count = get_transient($key);
        
        if ($current_count === false) {
            set_transient($key, 1, $this->rate_limit_period);
            return true;
        }
        
        if ($current_count >= $this->max_requests) {
            return false;
        }
        
        set_transient($key, $current_count + 1, $this->rate_limit_period);
        return true;
    }

    public function search($params) {
        $user_id = get_current_user_id();
        
        if (!$this->check_rate_limit($user_id)) {
            return new WP_Error(
                'rate_limit_exceeded',
                'Rate limit exceeded. Please try again later.',
                array('status' => 429)
            );
        }
        
        // Existing search implementation...
    }
}
```

### 2. Input Validation and Sanitization

```php
// In class-public.php
class DPRG_Archive_Agent_Public {
    public function validate_search_params($params) {
        $validated = array();
        
        // Validate and sanitize query
        if (isset($params['query'])) {
            $validated['query'] = sanitize_text_field($params['query']);
        }
        
        // Validate year
        if (isset($params['year'])) {
            $year = intval($params['year']);
            if ($year >= 1997 && $year <= 2016) {
                $validated['year'] = $year;
            }
        }
        
        // Validate month
        if (isset($params['month'])) {
            $month = intval($params['month']);
            if ($month >= 1 && $month <= 12) {
                $validated['month'] = $month;
            }
        }
        
        // Validate search type
        if (isset($params['type'])) {
            $valid_types = array('dense', 'sparse', 'hybrid');
            if (in_array($params['type'], $valid_types)) {
                $validated['type'] = $params['type'];
            }
        }
        
        return $validated;
    }
}
```

### 3. Nonce Implementation

```php
// In class-public.php
class DPRG_Archive_Agent_Public {
    public function render_search_interface() {
        $nonce = wp_create_nonce('dprg_search_nonce');
        
        ob_start();
        ?>
        <div class="dprg-archive-search">
            <form id="dprg-search-form" class="dprg-search-form">
                <?php wp_nonce_field('dprg_search_nonce', 'dprg_search_nonce'); ?>
                <!-- Existing form fields... -->
            </form>
        </div>
        <?php
        return ob_get_clean();
    }
}

// In JavaScript
jQuery(document).ready(function($) {
    $('#dprg-search-form').on('submit', function(e) {
        e.preventDefault();
        
        const nonce = $('#dprg_search_nonce').val();
        
        $.ajax({
            url: dprgArchiveAgent.ajaxUrl + '/search',
            method: 'POST',
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-WP-Nonce', nonce);
            },
            data: {
                query: $('#search-query').val(),
                year: $('#year-filter').val(),
                month: $('#month-filter').val(),
                type: $('#search-type').val(),
                nonce: nonce
            },
            success: function(response) {
                displaySearchResults(response);
            },
            error: function(xhr, status, error) {
                handleAjaxError(xhr, status, error);
            }
        });
    });
});
```

### 4. Error Handling and Logging

```php
// In class-api-client.php
class DPRG_Archive_Agent_API_Client {
    private function log_error($message, $context = array()) {
        if (defined('WP_DEBUG') && WP_DEBUG) {
            error_log(sprintf(
                '[DPRG Archive Agent] %s | Context: %s',
                $message,
                json_encode($context)
            ));
        }
    }

    public function search($params) {
        try {
            // Validate parameters
            $validated_params = $this->validate_search_params($params);
            
            // Make API request
            $response = wp_remote_post($this->api_url . '/search', array(
                'headers' => array(
                    'Authorization' => 'Bearer ' . $this->api_key,
                    'Content-Type' => 'application/json'
                ),
                'body' => json_encode($validated_params)
            ));
            
            if (is_wp_error($response)) {
                $this->log_error('API request failed', array(
                    'error' => $response->get_error_message(),
                    'params' => $validated_params
                ));
                return new WP_Error('api_error', $response->get_error_message());
            }
            
            return json_decode(wp_remote_retrieve_body($response), true);
            
        } catch (Exception $e) {
            $this->log_error('Unexpected error', array(
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ));
            return new WP_Error('unexpected_error', 'An unexpected error occurred');
        }
    }
}
```

## Performance Implementation Examples

### 1. Response Caching

```php
// In class-api-client.php
class DPRG_Archive_Agent_API_Client {
    private $cache_group = 'dprg_archive_agent';
    private $cache_expiration = 3600; // 1 hour

    public function search($params) {
        // Generate cache key from parameters
        $cache_key = md5(json_encode($params));
        
        // Try to get cached results
        $cached_results = wp_cache_get($cache_key, $this->cache_group);
        if ($cached_results !== false) {
            return $cached_results;
        }
        
        // Make API request if no cache
        $response = $this->make_api_request($params);
        
        // Cache the results
        if (!is_wp_error($response)) {
            wp_cache_set($cache_key, $response, $this->cache_group, $this->cache_expiration);
        }
        
        return $response;
    }
}
```

### 2. Lazy Loading Implementation

```javascript
// In public/js/main.js
class LazyLoader {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            pageSize: options.pageSize || 10,
            loadingThreshold: options.loadingThreshold || 200,
            ...options
        };
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMore = true;
        
        this.init();
    }
    
    init() {
        this.observer = new IntersectionObserver(
            (entries) => this.handleIntersection(entries),
            { threshold: 0.1 }
        );
        
        this.loadingElement = document.createElement('div');
        this.loadingElement.className = 'loading-spinner';
        this.loadingElement.style.display = 'none';
        this.container.appendChild(this.loadingElement);
        
        this.observer.observe(this.loadingElement);
    }
    
    async handleIntersection(entries) {
        if (entries[0].isIntersecting && !this.isLoading && this.hasMore) {
            await this.loadMore();
        }
    }
    
    async loadMore() {
        this.isLoading = true;
        this.loadingElement.style.display = 'block';
        
        try {
            const response = await this.fetchPage(this.currentPage + 1);
            this.appendResults(response.results);
            this.hasMore = response.hasMore;
            this.currentPage++;
        } catch (error) {
            console.error('Error loading more results:', error);
        } finally {
            this.isLoading = false;
            this.loadingElement.style.display = 'none';
        }
    }
    
    appendResults(results) {
        results.forEach(result => {
            const element = this.createResultElement(result);
            this.container.insertBefore(element, this.loadingElement);
        });
    }
}

// Usage
const searchResults = document.getElementById('search-results');
const lazyLoader = new LazyLoader(searchResults, {
    pageSize: 10,
    loadingThreshold: 200
});
```

### 3. Asset Optimization

```php
// In class-public.php
class DPRG_Archive_Agent_Public {
    public function enqueue_scripts() {
        // Enqueue minified CSS
        wp_enqueue_style(
            'dprg-archive-agent',
            DPRG_ARCHIVE_AGENT_PLUGIN_URL . 'public/css/style.min.css',
            array(),
            DPRG_ARCHIVE_AGENT_VERSION
        );
        
        // Enqueue minified JavaScript
        wp_enqueue_script(
            'dprg-archive-agent',
            DPRG_ARCHIVE_AGENT_PLUGIN_URL . 'public/js/main.min.js',
            array('jquery'),
            DPRG_ARCHIVE_AGENT_VERSION,
            true
        );
        
        // Add preload for critical assets
        add_action('wp_head', function() {
            ?>
            <link rel="preload" href="<?php echo DPRG_ARCHIVE_AGENT_PLUGIN_URL; ?>public/css/style.min.css" as="style">
            <link rel="preload" href="<?php echo DPRG_ARCHIVE_AGENT_PLUGIN_URL; ?>public/js/main.min.js" as="script">
            <?php
        });
    }
}
```

### 4. Database Query Optimization

```php
// In class-api-client.php
class DPRG_Archive_Agent_API_Client {
    private function get_cached_search_stats() {
        global $wpdb;
        
        // Use WordPress transients for caching
        $stats = get_transient('dprg_search_stats');
        if ($stats !== false) {
            return $stats;
        }
        
        // Optimize query with proper indexing
        $stats = $wpdb->get_row("
            SELECT 
                COUNT(*) as total_searches,
                COUNT(DISTINCT user_id) as unique_users,
                AVG(response_time) as avg_response_time
            FROM {$wpdb->prefix}dprg_search_logs
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        ");
        
        // Cache for 1 hour
        set_transient('dprg_search_stats', $stats, 3600);
        
        return $stats;
    }
}
```

## Additional Security Headers

Add these headers to your `.htaccess` file or server configuration:

```apache
# Security Headers
<IfModule mod_headers.c>
    # Prevent clickjacking
    Header set X-Frame-Options "SAMEORIGIN"
    
    # Enable XSS protection
    Header set X-XSS-Protection "1; mode=block"
    
    # Prevent MIME type sniffing
    Header set X-Content-Type-Options "nosniff"
    
    # Referrer policy
    Header set Referrer-Policy "strict-origin-when-cross-origin"
    
    # Content Security Policy
    Header set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
</IfModule>
```

## Performance Monitoring

Add this code to monitor and log performance metrics:

```php
// In class-api-client.php
class DPRG_Archive_Agent_API_Client {
    private function log_performance_metrics($operation, $duration) {
        global $wpdb;
        
        $wpdb->insert(
            $wpdb->prefix . 'dprg_performance_logs',
            array(
                'operation' => $operation,
                'duration' => $duration,
                'created_at' => current_time('mysql')
            ),
            array('%s', '%f', '%s')
        );
    }
    
    public function search($params) {
        $start_time = microtime(true);
        
        try {
            $response = $this->make_api_request($params);
            
            $duration = microtime(true) - $start_time;
            $this->log_performance_metrics('search', $duration);
            
            return $response;
        } catch (Exception $e) {
            $duration = microtime(true) - $start_time;
            $this->log_performance_metrics('search_error', $duration);
            throw $e;
        }
    }
}
```

These examples provide practical implementations of the security and performance recommendations. Remember to:

1. Test thoroughly in a development environment
2. Monitor performance metrics
3. Regularly update security measures
4. Keep dependencies up to date
5. Follow WordPress coding standards
6. Document any custom implementations 