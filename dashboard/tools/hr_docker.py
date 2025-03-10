import yaml
from django.conf import settings
import docker
import subprocess, json

HR_MANAGEMENT_SYSTEM_SRC_PATH = settings.HR_MANAGEMENT_SYSTEM_SRC_PATH
compose_path = f'{HR_MANAGEMENT_SYSTEM_SRC_PATH}/docker-compose.yaml'

REMOTE_DOCKER_HOST = "tcp://77.37.122.10:2375"

client = docker.DockerClient(base_url=REMOTE_DOCKER_HOST)

# Define the new data to append
app_conf = {
        "image": "hr",
        "container_name": "app",
        "build": {
            "context": ".",
            "dockerfile": "Dockerfile",
        },
        "ports": ["8000:8000"],
        "restart": "unless-stopped",
        "environment": {
            "DATABASE_URL": "postgres://postgres:postgres@db:5432/app",
        },
        "command": "./entrypoint.sh",
        "volumes": [
            "./horilla:/app/horilla"
            "/var/www/horilla/app/staticfiles:/app/staticfiles",
            "/var/www/horilla/app/media:/app/media"
            ],
        "depends_on": {
            "db": {
                "condition": "service_healthy",
            }
        }
    }

def add_hr_service(app_name, app_port):
    # Load the existing YAML file
    with open(compose_path, "r") as file:
        data = yaml.safe_load(file) or {}

    app_conf['ports'] = [f"{app_port}:8000"]
    app_conf['container_name'] = app_name
    app_conf['environment']['DATABASE_URL'] = f"postgres://postgres:postgres@db:5432/{app_name}"
    app_conf['volumes'] = [
                f"./horilla:/app/horilla",
                # f"/var/www/horilla/{app_name}/staticfiles:/{app_name}/staticfiles",
                # f"/var/www/horilla/{app_name}/media:/{app_name}/media",
            ]
    # Merge the new data
    data['services'][app_name] = app_conf

    # Write back to the YAML file
    with open(compose_path, "w") as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False)

def remove_hr_service(app_name):
    with open(compose_path, "r") as file:
        data = yaml.safe_load(file) or {}
    data['services'].pop(app_name)

    # Write back to the YAML file
    with open(compose_path, "w") as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False)




def remove_container(app_name):
    try:
        container = client.containers.get(app_name)  # Get the container by name
        container.remove(force=True)  # Remove the container (force stops it first)
        print(f"Container '{app_name}' removed successfully.")
        return True
    except docker.errors.NotFound:
        print(f"Error: Container '{app_name}' not found.")
        return False
    except docker.errors.APIError as e:
        print(f"Error: {str(e)}")
        return False



def run_container(app_name, app_port):

    # Run the container
    container = client.containers.run(
        "hr",  # Image name
        name=app_name,
        detach=True,  # Run in detached mode
        ports={f"8000/tcp": app_port},  # Map port 8000 on host to 8000 in container
        environment={
            "DATABASE_URL": f"postgres://postgres:postgres@db:5432/{app_name}",
            "ANOTHER_ENV": "value"
        },
        volumes={"./horilla": {"bind": "/app/horilla", "mode": "rw"}},  # Mount volume
        restart_policy={"Name": "unless-stopped"}  # Restart policy
    )



def compose_up(app_name):
    try:
        # Make sure the --no-deps option is placed correctly
        result = subprocess.run(
            ["docker", "--context", "remote", "compose", "up", "-d", "--no-deps", app_name],  # Correct order
            cwd=HR_MANAGEMENT_SYSTEM_SRC_PATH,  # Ensure the path is correct
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE  # Capture the output and error
        )

        if result.returncode == 0:
            print(result.stdout.decode())  # Print the stdout
            return True  # Success
        else:
            print(f"Error: {result.stderr.decode()}")
            return False  # Failure
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")
        return False  # ❌ Failed execution


def exec_command_on_container(app_name, command):
    # الاتصال بـ Docker
    # تنفيذ الأمر داخل الحاوية باستخدام اسم الخدمة
    result = client.containers.get(app_name).exec_run(command)
    # عرض النتيجة
    print(result.output.decode())
    return result

def add_user(app_name, first_name, last_name, username, password, email, phone):
    command = f'python3 manage.py createhorillauser --first_name {first_name} --last_name {last_name} --username {username} --password {password} --email {email} --phone {phone}'
    r = exec_command_on_container(app_name, command)
    response_data = r.output.decode()
    if r.exit_code == 0:
        response_data = json.loads(r.output.decode())
    return response_data, r.exit_code

def add_subscription(app_name, plan_scope, subscription_model):
    number_of_days_user = 30 if plan_scope == '1' else 365

    command = f"""python manage.py add_subscription \
"{subscription_model.title}" \
"{subscription_model.subtitle}" \
"{subscription_model.Theem}" \
"{subscription_model.plan_type}" \
{subscription_model.number_of_days} \
{subscription_model.price_monthly} \
{subscription_model.discont_monthly} \
{subscription_model.price_yearly} \
{subscription_model.discont_yearly} \
"{subscription_model.currency}" \
{subscription_model.number_of_employees} \
{subscription_model.number_of_managers} \
{subscription_model.manage_employee} \
{subscription_model.manage_recruitment} \
{subscription_model.manage_onboarding} \
{subscription_model.manage_attendance} \
{subscription_model.payroll_management} \
{subscription_model.leave_management} \
{subscription_model.manage_assets} \
{subscription_model.pms_management} \
{subscription_model.manage_Offboarding} \
{subscription_model.manage_helpdesk} \
{subscription_model.employee_attendance_report} \
{subscription_model.employee_salary_report} \
{subscription_model.employee_leave_report} \
{subscription_model.performance_review_report} \
{subscription_model.send_email_notifications} \
{subscription_model.live_chat_with_support} \
{subscription_model.is_enabled} \
"{plan_scope}" \
{number_of_days_user} \
"""
    print(command)
    exec_command_on_container(app_name, command)


def change_user_password(app_name, user_id, pwd):
    command = f"python manage.py change_user_password {user_id} {pwd}"
    r = exec_command_on_container(app_name, command)
    response_data = r.output.decode()

    return response_data, r.exit_code

def get_system_info(app_name, user_id):
    command = f"python manage.py get_system_info {user_id}"
    r = exec_command_on_container(app_name, command)
    response_data = r.output.decode()
    if r.exit_code == 0:
        response_data = json.loads(r.output.decode())
    return response_data, r.exit_code

def check_migrations(app_name):
    command = 'python manage.py check_migrations'
    r = exec_command_on_container(app_name, command)
    if r.exit_code == 0:
        return True  # Success
    else:
        return False  # Failure