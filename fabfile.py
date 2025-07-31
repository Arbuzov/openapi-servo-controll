from fabric.api import env, run, put

env.hosts = ['root@192.168.99.15']

env.passwords = {
    'pi@192.168.99.15:22': 'int1144282'
}


def deploy():
    put('src/openapi_servo_control', '/usr/lib/python3/dist-packages')
    run('killall -9 sbc-web-manager || true')
