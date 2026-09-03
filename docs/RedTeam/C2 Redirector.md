# Conf AdaptixC2
URIs:
- **\[GET\]** ``/api/status`` -> **\[POST\]** `/api/v1/status` 
- **\[GET\]** ``/api/updates`` -> **\[POST\]** `/updates/check.php` 
- **\[GET\] ``/index.html`` -> \[POST\]** `/content.html` 

User-Agents:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Teams/1.6.00.26474 Chrome/114.0.5735.289 Electron/25.8.4 Safari/537.36
```

Heartbeat Header : `X-Request-Token`

![](img/Pasted%20image%2020260903161905.png)
# Conf Nginx

```
sudo apt update
sudo apt -y install nginx
```

```
sudo vim /etc/nginx/sites-enabled/default
```

```nginx
server {
    listen 80;
    server_name _;

    # !~ : ne correspond pas à la regex (sensible à la casse)
    # !~* : ne correspond pas à la regex (insensible à la casse)

    location /api/status {
        if ($request_method !~* GET) { return 404; }
        if ($http_user_agent !~ "Teams/1\.6\.00\.26474") { return 404; }
        if ($http_x_request_token = "") { return 404; }
        proxy_pass http://127.0.0.1:8888;
        include proxy_params;
    }

    location /api/updates {
        if ($request_method !~* GET) { return 404; }
        if ($http_user_agent !~ "Teams/1\.6\.00\.26474") { return 404; }
        if ($http_x_request_token = "") { return 404; }
        proxy_pass http://127.0.0.1:8888;
        include proxy_params;
    }

    location /index.html {
        if ($request_method !~* GET) { return 404; }
        if ($http_user_agent !~ "Teams/1\.6\.00\.26474") { return 404; }
        if ($http_x_request_token = "") { return 404; }
        proxy_pass http://127.0.0.1:8888;
        include proxy_params;
    }

    location / {
        return 404;
    }
}
```

```
sudo systemctl restart nginx
```

```bash
tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```

# SSL

```nginx
server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # !~ : ne correspond pas à la regex (sensible à la casse)
    # !~* : ne correspond pas à la regex (insensible à la casse)

    location /api/status {
        if ($request_method !~* GET) { return 404; }
        if ($http_user_agent !~ "Teams/1\.6\.00\.26474") { return 404; }
        if ($http_x_request_token = "") { return 404; }
        proxy_pass https://127.0.0.1:8888;
        proxy_ssl_verify off;
        include proxy_params;
    }

    location /api/updates {
        if ($request_method !~* GET) { return 404; }
        if ($http_user_agent !~ "Teams/1\.6\.00\.26474") { return 404; }
        if ($http_x_request_token = "") { return 404; }
        proxy_pass https://127.0.0.1:8888;
        proxy_ssl_verify off;
        include proxy_params;
    }

    location /index.html {
        if ($request_method !~* GET) { return 404; }
        if ($http_user_agent !~ "Teams/1\.6\.00\.26474") { return 404; }
        if ($http_x_request_token = "") { return 404; }
        proxy_pass https://127.0.0.1:8888;
        proxy_ssl_verify off;
        include proxy_params;
    }

    location / {
        return 404;
    }
}
```