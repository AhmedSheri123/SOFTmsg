import os
from pathlib import Path

def run_command(command):
    print(f"Running: {command}")
    os.system(command)

def create_nginx_config(static_folder_name, subdomain, proxy_port, domain, port=80):
    nginx_config = f"""server {{
    listen {port};
    server_name {subdomain}.{domain};

    location /static/ {{
        alias /var/www/hr-original/{static_folder_name}/;
    }}

    # location /media/ {{
    #     alias /var/www/horilla/{subdomain}/media/;
    # }}

    location / {{
        proxy_pass http://127.0.0.1:{proxy_port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    error_log /var/log/nginx/{subdomain}_error.log;
    access_log /var/log/nginx/{subdomain}_access.log;
}}"""
    nginx_config_path = f"/etc/nginx/sites-enabled/{subdomain}.conf"
    with open(nginx_config_path, "w") as f:
        f.write(nginx_config)

def restart_services():
    run_command("sudo nginx -s reload")

