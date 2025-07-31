import os
import shutil
import importlib.resources as pkg_resources


def install_file(resource, dest):
    with pkg_resources.path(
        'openapi_servo_control.data', resource
    ) as src_path:
        print(f'Installing {resource} to {dest}')
        shutil.copy(src_path, dest)


def main():
    os.makedirs('/etc/openapi_servo_control', exist_ok=True)
    install_file('api.yaml', '/etc/openapi_servo_control/api.yaml')
    install_file(
        'servo-control.service',
        '/etc/systemd/system/servo-control.service',
    )
    print("✅ Installation completed.")
