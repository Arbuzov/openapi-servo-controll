from setuptools import setup, find_packages

setup(
    name="openapi_servo",
    version='0.1.0',
    maintainer='Serge Arbuzov',
    author_email='info@whitediver.com',
    maintainer_email='info@whitediver.com',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,
    package_data={
        'openapi_servo_control': ['data/*.yaml', 'data/*.service']
    },
    install_requires=[
        'aiohttp',
        'aiohttp_swagger',
        'aiohttp_cors',
        'Adafruit_PCA9685'
    ],
    entry_points={
        'console_scripts': [
            "openapi-servo-control=openapi_servo_control:main",
            (
                "install-openapi-servo-configs="
                "openapi_servo_control.installer:main"
            ),
        ]
    },
    python_requires='>=3.5.1'
)
