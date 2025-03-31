# Monitoring and Logging Guide

This guide provides information about monitoring and logging in the DPRG Archive Agent project.

## Logging Configuration

### 1. Application Logging

1. Log format:
   ```python
   {
       "timestamp": "2024-01-01T12:00:00Z",
       "level": "INFO",
       "message": "Application started",
       "module": "src.api",
       "function": "startup",
       "line": 42
   }
   ```

2. Log levels:
   - DEBUG: Detailed information
   - INFO: General information
   - WARNING: Warning messages
   - ERROR: Error messages
   - CRITICAL: Critical errors

3. Log rotation:
   ```python
   from logging.handlers import RotatingFileHandler

   handler = RotatingFileHandler(
       'logs/app.log',
       maxBytes=10485760,  # 10MB
       backupCount=5
   )
   ```

### 2. Access Logging

1. Nginx access logs:
   ```nginx
   log_format json_combined escape=json
     '{'
     '"time_local":"$time_local",'
     '"remote_addr":"$remote_addr",'
     '"remote_user":"$remote_user",'
     '"request":"$request",'
     '"status": "$status",'
     '"body_bytes_sent":"$body_bytes_sent",'
     '"request_time":"$request_time",'
     '"http_referrer":"$http_referer",'
     '"http_user_agent":"$http_user_agent",'
     '"request_id":"$request_id"'
     '}';

   access_log /var/log/nginx/access.log json_combined;
   ```

2. Application access logs:
   ```python
   @app.middleware("http")
   async def log_requests(request, call_next):
       start_time = time.time()
       response = await call_next(request)
       duration = time.time() - start_time
       
       logger.info(
           "Request completed",
           extra={
               "method": request.method,
               "url": str(request.url),
               "status_code": response.status_code,
               "duration": duration
           }
       )
       return response
   ```

## Monitoring Setup

### 1. System Monitoring

1. CPU monitoring:
   ```python
   import psutil

   def get_cpu_metrics():
       return {
           "cpu_percent": psutil.cpu_percent(interval=1),
           "cpu_count": psutil.cpu_count(),
           "cpu_freq": psutil.cpu_freq()._asdict()
       }
   ```

2. Memory monitoring:
   ```python
   def get_memory_metrics():
       memory = psutil.virtual_memory()
       return {
           "total": memory.total,
           "available": memory.available,
           "percent": memory.percent,
           "used": memory.used,
           "free": memory.free
       }
   ```

3. Disk monitoring:
   ```python
   def get_disk_metrics():
       disk = psutil.disk_usage('/')
       return {
           "total": disk.total,
           "used": disk.used,
           "free": disk.free,
           "percent": disk.percent
       }
   ```

### 2. Application Monitoring

1. Request metrics:
   ```python
   from prometheus_client import Counter, Histogram

   request_count = Counter(
       'http_requests_total',
       'Total HTTP requests',
       ['method', 'endpoint', 'status']
   )

   request_duration = Histogram(
       'http_request_duration_seconds',
       'HTTP request duration',
       ['method', 'endpoint']
   )
   ```

2. Error tracking:
   ```python
   error_count = Counter(
       'application_errors_total',
       'Total application errors',
       ['type', 'module']
   )
   ```

3. Custom metrics:
   ```python
   search_count = Counter(
       'search_operations_total',
       'Total search operations',
       ['query_type']
   )

   cache_hits = Counter(
       'cache_hits_total',
       'Total cache hits',
       ['cache_type']
   )
   ```

## Alerting

### 1. Alert Rules

1. System alerts:
   ```yaml
   groups:
   - name: system
     rules:
     - alert: HighCPUUsage
       expr: cpu_percent > 80
       for: 5m
       labels:
         severity: warning
       annotations:
         summary: High CPU usage
         description: CPU usage is above 80% for 5 minutes

     - alert: HighMemoryUsage
       expr: memory_percent > 85
       for: 5m
       labels:
         severity: warning
       annotations:
         summary: High memory usage
         description: Memory usage is above 85% for 5 minutes
   ```

2. Application alerts:
   ```yaml
   groups:
   - name: application
     rules:
     - alert: HighErrorRate
       expr: rate(application_errors_total[5m]) > 0.1
       for: 5m
       labels:
         severity: critical
       annotations:
         summary: High error rate
         description: Error rate is above 0.1 per second

     - alert: HighLatency
       expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
       for: 5m
       labels:
         severity: warning
       annotations:
         summary: High latency
         description: 95th percentile latency is above 1 second
   ```

### 2. Notification Channels

1. Email notifications:
   ```yaml
   receivers:
   - name: email
     email_configs:
     - to: admin@example.com
       from: alerts@example.com
       smarthost: smtp.example.com:587
       auth_username: alerts
       auth_password: <secret>
   ```

2. Slack notifications:
   ```yaml
   receivers:
   - name: slack
     slack_configs:
     - channel: '#alerts'
       send_resolved: true
       title: '{{ template "slack.default.title" . }}'
       text: '{{ template "slack.default.text" . }}'
   ```

## Dashboard Setup

### 1. Grafana Dashboard

1. System metrics:
   ```json
   {
     "dashboard": {
       "panels": [
         {
           "title": "CPU Usage",
           "type": "graph",
           "datasource": "Prometheus",
           "targets": [
             {
               "expr": "cpu_percent",
               "legendFormat": "CPU %"
             }
           ]
         },
         {
           "title": "Memory Usage",
           "type": "graph",
           "datasource": "Prometheus",
           "targets": [
             {
               "expr": "memory_percent",
               "legendFormat": "Memory %"
             }
           ]
         }
       ]
     }
   }
   ```

2. Application metrics:
   ```json
   {
     "dashboard": {
       "panels": [
         {
           "title": "Request Rate",
           "type": "graph",
           "datasource": "Prometheus",
           "targets": [
             {
               "expr": "rate(http_requests_total[5m])",
               "legendFormat": "{{method}} {{endpoint}}"
             }
           ]
         },
         {
           "title": "Error Rate",
           "type": "graph",
           "datasource": "Prometheus",
           "targets": [
             {
               "expr": "rate(application_errors_total[5m])",
               "legendFormat": "{{type}}"
             }
           ]
         }
       ]
     }
   }
   ```

### 2. Custom Dashboards

1. Search metrics:
   ```json
   {
     "dashboard": {
       "panels": [
         {
           "title": "Search Operations",
           "type": "graph",
           "datasource": "Prometheus",
           "targets": [
             {
               "expr": "rate(search_operations_total[5m])",
               "legendFormat": "{{query_type}}"
             }
           ]
         },
         {
           "title": "Cache Performance",
           "type": "graph",
           "datasource": "Prometheus",
           "targets": [
             {
               "expr": "rate(cache_hits_total[5m])",
               "legendFormat": "{{cache_type}}"
             }
           ]
         }
       ]
     }
   }
   ```

## Log Analysis

### 1. Log Aggregation

1. ELK Stack setup:
   ```yaml
   version: '3.8'
   services:
     elasticsearch:
       image: docker.elastic.co/elasticsearch/elasticsearch:7.9.3
       environment:
         - discovery.type=single-node
         - ES_JAVA_OPTS=-Xms512m -Xmx512m
       ports:
         - "9200:9200"

     logstash:
       image: docker.elastic.co/logstash/logstash:7.9.3
       volumes:
         - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
       depends_on:
         - elasticsearch

     kibana:
       image: docker.elastic.co/kibana/kibana:7.9.3
       ports:
         - "5601:5601"
       depends_on:
         - elasticsearch
   ```

2. Logstash configuration:
   ```conf
   input {
     file {
       path => "/var/log/nginx/access.log"
       type => "nginx-access"
       codec => json
     }
     file {
       path => "/var/log/nginx/error.log"
       type => "nginx-error"
     }
   }

   filter {
     if [type] == "nginx-access" {
       date {
         match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
         target => "@timestamp"
       }
     }
   }

   output {
     elasticsearch {
       hosts => ["elasticsearch:9200"]
       index => "nginx-%{+YYYY.MM.dd}"
     }
   }
   ```

### 2. Log Analysis Tools

1. Log analysis scripts:
   ```python
   def analyze_logs(log_file):
       with open(log_file) as f:
           for line in f:
               log_entry = json.loads(line)
               # Analyze log entry
               process_log_entry(log_entry)
   ```

2. Log visualization:
   ```python
   def visualize_logs(log_data):
       # Create visualizations
       plt.figure(figsize=(10, 6))
       plt.plot(log_data['timestamp'], log_data['count'])
       plt.title('Log Entry Distribution')
       plt.xlabel('Time')
       plt.ylabel('Count')
       plt.savefig('log_distribution.png')
   ```

## Performance Monitoring

### 1. Application Performance

1. Response time tracking:
   ```python
   @app.middleware("http")
   async def track_response_time(request, call_next):
       start_time = time.time()
       response = await call_next(request)
       duration = time.time() - start_time
       
       # Record metrics
       request_duration.labels(
           method=request.method,
           endpoint=request.url.path
       ).observe(duration)
       
       return response
   ```

2. Resource usage tracking:
   ```python
   def track_resource_usage():
       while True:
           # Record CPU usage
           cpu_percent = psutil.cpu_percent()
           cpu_gauge.set(cpu_percent)
           
           # Record memory usage
           memory = psutil.virtual_memory()
           memory_gauge.set(memory.percent)
           
           time.sleep(60)
   ```

### 2. Database Performance

1. Query monitoring:
   ```python
   def monitor_queries():
       while True:
           # Get slow queries
           slow_queries = get_slow_queries()
           
           # Record metrics
           for query in slow_queries:
               slow_query_counter.labels(
                   query_type=query['type']
               ).inc()
           
           time.sleep(300)
   ```

2. Connection monitoring:
   ```python
   def monitor_connections():
       while True:
           # Get connection stats
           stats = get_connection_stats()
           
           # Record metrics
           active_connections_gauge.set(stats['active'])
           idle_connections_gauge.set(stats['idle'])
           
           time.sleep(60)
   ```

## Security Monitoring

### 1. Access Monitoring

1. Failed login tracking:
   ```python
   def track_failed_logins():
       failed_login_counter = Counter(
           'failed_logins_total',
           'Total failed login attempts',
           ['ip_address']
       )
       
       @app.middleware("http")
       async def track_login_attempts(request, call_next):
           if request.url.path == "/login":
               response = await call_next(request)
               if response.status_code == 401:
                   failed_login_counter.labels(
                       ip_address=request.client.host
                   ).inc()
               return response
           return await call_next(request)
   ```

2. API usage monitoring:
   ```python
   def monitor_api_usage():
       api_usage_counter = Counter(
           'api_usage_total',
           'Total API usage',
           ['endpoint', 'method']
       )
       
       @app.middleware("http")
       async def track_api_usage(request, call_next):
           api_usage_counter.labels(
               endpoint=request.url.path,
               method=request.method
           ).inc()
           return await call_next(request)
   ```

### 2. Security Alerts

1. Suspicious activity alerts:
   ```yaml
   groups:
   - name: security
     rules:
     - alert: MultipleFailedLogins
       expr: rate(failed_logins_total[5m]) > 5
       for: 5m
       labels:
         severity: critical
       annotations:
         summary: Multiple failed login attempts
         description: More than 5 failed login attempts in 5 minutes

     - alert: HighAPIUsage
       expr: rate(api_usage_total[5m]) > 100
       for: 5m
       labels:
         severity: warning
       annotations:
         summary: High API usage
         description: More than 100 API requests in 5 minutes
   ```

## Resources

### Documentation

- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [ELK Stack Documentation](https://www.elastic.co/guide/index.html)

### Tools

- Prometheus
- Grafana
- ELK Stack
- psutil
- logging 