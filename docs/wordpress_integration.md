# WordPress Integration Guide for DprgArchiveAgent

This guide provides detailed instructions for integrating the DprgArchiveAgent into your WordPress website, including both the search functionality and the chat feature.

## Overview

The DprgArchiveAgent provides two main features that can be integrated into WordPress:
1. Advanced search capabilities with metadata filtering
2. Interactive chat interface for querying the DPRG archive

## API Integration

### 1. Backend Setup

First, ensure the DprgArchiveAgent is properly set up on your server:

```bash
# Clone the repository
git clone https://github.com/yourusername/DprgArchiveAgent.git
cd DprgArchiveAgent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 2. WordPress Plugin Development

Create a new WordPress plugin directory:

```bash
wp-content/plugins/dprg-archive-agent/
```

#### Plugin Structure

```
dprg-archive-agent/
├── admin/
│   ├── css/
│   ├── js/
│   └── class-admin.php
├── public/
│   ├── css/
│   ├── js/
│   └── class-public.php
├── includes/
│   └── class-api-client.php
├── dprg-archive-agent.php
└── readme.txt
```

#### Main Plugin File

```php
<?php
/**
 * Plugin Name: DPRG Archive Agent
 * Description: Integrates DprgArchiveAgent search and chat capabilities into WordPress
 * Version: 1.0.0
 * Author: Your Name
 */

if (!defined('ABSPATH')) exit;

class DPRG_Archive_Agent {
    private static $instance = null;

    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        $this->define_constants();
        $this->init_hooks();
    }

    private function define_constants() {
        define('DPRG_ARCHIVE_AGENT_VERSION', '1.0.0');
        define('DPRG_ARCHIVE_AGENT_PLUGIN_DIR', plugin_dir_path(__FILE__));
        define('DPRG_ARCHIVE_AGENT_PLUGIN_URL', plugin_dir_url(__FILE__));
    }

    private function init_hooks() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('rest_api_init', array($this, 'register_rest_routes'));
    }

    public function init() {
        // Initialize plugin components
        require_once DPRG_ARCHIVE_AGENT_PLUGIN_DIR . 'includes/class-api-client.php';
        require_once DPRG_ARCHIVE_AGENT_PLUGIN_DIR . 'public/class-public.php';
        require_once DPRG_ARCHIVE_AGENT_PLUGIN_DIR . 'admin/class-admin.php';
    }

    public function enqueue_scripts() {
        wp_enqueue_style(
            'dprg-archive-agent',
            DPRG_ARCHIVE_AGENT_PLUGIN_URL . 'public/css/style.css',
            array(),
            DPRG_ARCHIVE_AGENT_VERSION
        );

        wp_enqueue_script(
            'dprg-archive-agent',
            DPRG_ARCHIVE_AGENT_PLUGIN_URL . 'public/js/main.js',
            array('jquery'),
            DPRG_ARCHIVE_AGENT_VERSION,
            true
        );

        wp_localize_script('dprg-archive-agent', 'dprgArchiveAgent', array(
            'ajaxUrl' => rest_url('dprg-archive-agent/v1'),
            'nonce' => wp_create_nonce('wp_rest')
        ));
    }

    public function register_rest_routes() {
        register_rest_route('dprg-archive-agent/v1', '/search', array(
            'methods' => 'POST',
            'callback' => array($this, 'handle_search_request'),
            'permission_callback' => '__return_true'
        ));

        register_rest_route('dprg-archive-agent/v1', '/chat', array(
            'methods' => 'POST',
            'callback' => array($this, 'handle_chat_request'),
            'permission_callback' => '__return_true'
        ));
    }

    public function handle_search_request($request) {
        $api_client = new DPRG_Archive_Agent_API_Client();
        return $api_client->search($request->get_params());
    }

    public function handle_chat_request($request) {
        $api_client = new DPRG_Archive_Agent_API_Client();
        return $api_client->chat($request->get_params());
    }
}

// Initialize the plugin
function dprg_archive_agent() {
    return DPRG_Archive_Agent::get_instance();
}

dprg_archive_agent();
```

### 3. API Client Class

```php
<?php
class DPRG_Archive_Agent_API_Client {
    private $api_url;
    private $api_key;

    public function __construct() {
        $this->api_url = get_option('dprg_archive_agent_api_url');
        $this->api_key = get_option('dprg_archive_agent_api_key');
    }

    public function search($params) {
        $response = wp_remote_post($this->api_url . '/search', array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $this->api_key,
                'Content-Type' => 'application/json'
            ),
            'body' => json_encode($params)
        ));

        if (is_wp_error($response)) {
            return new WP_Error('api_error', $response->get_error_message());
        }

        return json_decode(wp_remote_retrieve_body($response), true);
    }

    public function chat($params) {
        $response = wp_remote_post($this->api_url . '/chat', array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $this->api_key,
                'Content-Type' => 'application/json'
            ),
            'body' => json_encode($params)
        ));

        if (is_wp_error($response)) {
            return new WP_Error('api_error', $response->get_error_message());
        }

        return json_decode(wp_remote_retrieve_body($response), true);
    }
}
```

## UI Integration

### 1. Search Interface

Create a shortcode for the search interface:

```php
// In class-public.php
public function register_shortcodes() {
    add_shortcode('dprg_archive_search', array($this, 'render_search_interface'));
}

public function render_search_interface() {
    ob_start();
    ?>
    <div class="dprg-archive-search">
        <form id="dprg-search-form" class="dprg-search-form">
            <div class="search-input-group">
                <input type="text" id="search-query" placeholder="Search the DPRG archive...">
                <button type="submit">Search</button>
            </div>
            
            <div class="search-filters">
                <div class="filter-group">
                    <label>Year:</label>
                    <select id="year-filter">
                        <option value="">All Years</option>
                        <?php for ($year = 1997; $year <= 2016; $year++): ?>
                            <option value="<?php echo $year; ?>"><?php echo $year; ?></option>
                        <?php endfor; ?>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Month:</label>
                    <select id="month-filter">
                        <option value="">All Months</option>
                        <?php
                        $months = array(
                            1 => 'January', 2 => 'February', 3 => 'March',
                            4 => 'April', 5 => 'May', 6 => 'June',
                            7 => 'July', 8 => 'August', 9 => 'September',
                            10 => 'October', 11 => 'November', 12 => 'December'
                        );
                        foreach ($months as $num => $name):
                        ?>
                            <option value="<?php echo $num; ?>"><?php echo $name; ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Search Type:</label>
                    <select id="search-type">
                        <option value="dense">Semantic Search</option>
                        <option value="sparse">Keyword Search</option>
                        <option value="hybrid">Hybrid Search</option>
                    </select>
                </div>
            </div>
        </form>
        
        <div id="search-results" class="search-results">
            <!-- Results will be populated here -->
        </div>
    </div>
    <?php
    return ob_get_clean();
}
```

### 2. Chat Interface

Create a shortcode for the chat interface:

```php
public function render_chat_interface() {
    ob_start();
    ?>
    <div class="dprg-archive-chat">
        <div id="chat-messages" class="chat-messages">
            <!-- Chat messages will appear here -->
        </div>
        
        <form id="chat-form" class="chat-form">
            <textarea id="chat-input" placeholder="Ask a question about the DPRG archive..."></textarea>
            <button type="submit">Send</button>
        </form>
    </div>
    <?php
    return ob_get_clean();
}
```

### 3. CSS Styling

```css
/* public/css/style.css */
.dprg-archive-search {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.dprg-search-form {
    margin-bottom: 20px;
}

.search-input-group {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.search-input-group input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.search-filters {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.filter-group select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.search-results {
    margin-top: 20px;
}

.result-item {
    padding: 15px;
    border: 1px solid #eee;
    margin-bottom: 10px;
    border-radius: 4px;
}

.result-item h3 {
    margin: 0 0 10px 0;
}

.result-meta {
    font-size: 0.9em;
    color: #666;
    margin-bottom: 10px;
}

.result-excerpt {
    color: #333;
}

/* Chat Interface */
.dprg-archive-chat {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.chat-messages {
    height: 400px;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 20px;
}

.chat-message {
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 4px;
}

.chat-message.user {
    background-color: #e3f2fd;
    margin-left: 20%;
}

.chat-message.assistant {
    background-color: #f5f5f5;
    margin-right: 20%;
}

.chat-form {
    display: flex;
    gap: 10px;
}

.chat-form textarea {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: vertical;
    min-height: 60px;
}

.chat-form button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.chat-form button:hover {
    background-color: #0056b3;
}
```

### 4. JavaScript Functionality

```javascript
// public/js/main.js
jQuery(document).ready(function($) {
    // Search functionality
    $('#dprg-search-form').on('submit', function(e) {
        e.preventDefault();
        
        const query = $('#search-query').val();
        const year = $('#year-filter').val();
        const month = $('#month-filter').val();
        const searchType = $('#search-type').val();
        
        $.ajax({
            url: dprgArchiveAgent.ajaxUrl + '/search',
            method: 'POST',
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-WP-Nonce', dprgArchiveAgent.nonce);
            },
            data: {
                query: query,
                year: year,
                month: month,
                type: searchType
            },
            success: function(response) {
                displaySearchResults(response);
            },
            error: function(xhr, status, error) {
                console.error('Search error:', error);
                $('#search-results').html('<p class="error">Error performing search. Please try again.</p>');
            }
        });
    });
    
    // Chat functionality
    $('#chat-form').on('submit', function(e) {
        e.preventDefault();
        
        const message = $('#chat-input').val();
        if (!message.trim()) return;
        
        // Add user message to chat
        addChatMessage(message, 'user');
        $('#chat-input').val('');
        
        $.ajax({
            url: dprgArchiveAgent.ajaxUrl + '/chat',
            method: 'POST',
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-WP-Nonce', dprgArchiveAgent.nonce);
            },
            data: {
                message: message
            },
            success: function(response) {
                addChatMessage(response.reply, 'assistant');
            },
            error: function(xhr, status, error) {
                console.error('Chat error:', error);
                addChatMessage('Sorry, there was an error processing your message. Please try again.', 'assistant');
            }
        });
    });
});

function displaySearchResults(results) {
    const $container = $('#search-results');
    $container.empty();
    
    if (!results.length) {
        $container.html('<p>No results found.</p>');
        return;
    }
    
    results.forEach(function(result) {
        const $result = $('<div class="result-item">');
        $result.append(`<h3>${result.title}</h3>`);
        $result.append(`<div class="result-meta">By ${result.author} on ${result.date}</div>`);
        $result.append(`<div class="result-excerpt">${result.excerpt}</div>`);
        $container.append($result);
    });
}

function addChatMessage(message, type) {
    const $message = $('<div class="chat-message ' + type + '">').text(message);
    $('#chat-messages').append($message);
    $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
}
```

## Usage

### 1. Install the Plugin

1. Upload the `dprg-archive-agent` folder to the `/wp-content/plugins/` directory
2. Activate the plugin through the 'Plugins' menu in WordPress
3. Configure the API settings in the WordPress admin panel

### 2. Add Search Interface

Add the search interface to any page or post using the shortcode:

```
[dprg_archive_search]
```

### 3. Add Chat Interface

Add the chat interface to any page or post using the shortcode:

```
[dprg_archive_chat]
```

## Security Considerations

1. Always use HTTPS for API communications
2. Implement rate limiting on the API endpoints (see [Rate Limiting Implementation](security_and_performance_examples.md#1-rate-limiting-implementation))
3. Validate and sanitize all user input (see [Input Validation and Sanitization](security_and_performance_examples.md#2-input-validation-and-sanitization))
4. Use nonces for form submissions (see [Nonce Implementation](security_and_performance_examples.md#3-nonce-implementation))
5. Implement proper error handling and logging (see [Error Handling and Logging](security_and_performance_examples.md#4-error-handling-and-logging))
6. Configure security headers (see [Additional Security Headers](security_and_performance_examples.md#additional-security-headers))

## Performance Optimization

1. Cache API responses when appropriate (see [Response Caching](security_and_performance_examples.md#1-response-caching))
2. Implement lazy loading for search results (see [Lazy Loading Implementation](security_and_performance_examples.md#2-lazy-loading-implementation))
3. Use pagination for large result sets
4. Optimize database queries (see [Database Query Optimization](security_and_performance_examples.md#4-database-query-optimization))
5. Minify and combine CSS/JS files (see [Asset Optimization](security_and_performance_examples.md#3-asset-optimization))
6. Monitor performance metrics (see [Performance Monitoring](security_and_performance_examples.md#performance-monitoring))

## Maintenance

1. Regularly update the plugin for security patches
2. Monitor API usage and performance
3. Keep dependencies up to date
4. Maintain proper error logging
5. Regular backups of configuration

## Troubleshooting

Common issues and solutions:

1. **API Connection Issues**
   - Verify API URL and credentials
   - Check server firewall settings
   - Ensure proper SSL certificates

2. **Search Not Working**
   - Verify search parameters
   - Check API response format
   - Validate JavaScript console for errors

3. **Chat Not Responding**
   - Check API endpoint availability
   - Verify message format
   - Monitor server logs for errors

## Support

For additional support or questions:
1. Check the plugin documentation
2. Review the API documentation
3. Contact the development team
4. Submit issues through the GitHub repository 