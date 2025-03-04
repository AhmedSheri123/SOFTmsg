import os
from pathlib import Path

def run_command(command):
    print(f"Running: {command}")
    os.system(command)

def create_gunicorn_service(working_directory, env_directory, wsgi_module, service_name, subdomain):
    working_directory = Path(working_directory).resolve()
    env_directory = Path(env_directory).resolve()

    service_content = f"""[Unit]
Description=gunicorn daemon for {subdomain} project
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory={working_directory}
ExecStart={env_directory}/bin/gunicorn --workers 3 --bind unix:{working_directory}/{subdomain}.sock {wsgi_module}:application

[Install]
WantedBy=multi-user.target
"""
    service_path = f"/etc/systemd/system/{service_name}.service"
    with open(service_path, "w") as f:
        f.write(service_content)

    run_command("sudo systemctl daemon-reload")
    run_command(f"sudo systemctl enable {service_name}")
    run_command(f"sudo systemctl start {service_name}")

def set_permissions(working_directory):
    working_directory = Path(working_directory).resolve()
    run_command(f"sudo chown -R www-data:www-data {working_directory}")
    run_command(f"sudo chmod -R 755 {working_directory}")

def create_nginx_config(working_directory, static_folder_name, subdomain, domain, port=80):
    working_directory = Path(working_directory).resolve()
    nginx_config = f"""server {{
    listen {port};
    server_name {subdomain}.{domain};

    location /static/ {{
        alias {working_directory}/{static_folder_name}/;
    }}

    location / {{
        proxy_pass http://unix:{working_directory}/{subdomain}.sock;
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

def check_service_status(service_name):
    status = os.system(f"systemctl is-active --quiet {service_name}")
    if status != 0:
        print(f"❌ تحذير: الخدمة {service_name} لم تبدأ بشكل صحيح!")
    else:
        print(f"✅ الخدمة {service_name} تعمل بنجاح.")
        
def restart_services(service_name):
    run_command(f"sudo systemctl restart {service_name}")
    check_service_status(service_name)
    run_command("sudo nginx -s reload")

def deploy(subdomain, working_directory, env_directory, wsgi_module, static_folder_name, domain, port=80):
    """
    wsgi_module example = horilla.wsgi
    working_directory example =  /var/www/hr
    env_directory example =  /var/www/hr/env
    static_folder_name example =  static
    domain example = example.softmsg.com
    """
    gunicorn_service_name = f'gunicorn_{subdomain}'
    set_permissions(working_directory)
    create_gunicorn_service(working_directory, env_directory, wsgi_module, gunicorn_service_name, subdomain)
    create_nginx_config(working_directory, static_folder_name, subdomain, domain, port)
    restart_services(gunicorn_service_name)
    return True

# if __name__ == "__main__":
#     # استبدل هذه القيم بالقيم الحقيقية الخاصة بك
#     deploy(
#         project_name="horilla",
#         working_directory="/var/www/hr",
#         env_directory="/var/www/hr/env",
#         static_folder_name="staticfiles",
#         domain="softmsg.com",
#         port=8003
#     )
