import os

from netmiko import ConnectHandler


router_device = {
    'device_type': 'cisco_ios_telnet',
    'host': os.getenv('ROUTER_HOST', '192.168.10.14'),
    'port': int(os.getenv('ROUTER_PORT', '32770')),
    'username': os.getenv('ROUTER_USERNAME', 'admin'),
    'password': os.getenv('ROUTER_PASSWORD', 'eve123'),
    'secret': os.getenv('ROUTER_SECRET', 'eve123'),
    'conn_timeout': 5,
    'banner_timeout': 5,
    'auth_timeout': 5,
}

try:
    print('Connecting to router...')
    net_connect = ConnectHandler(**router_device)
    net_connect.enable()

    commands_to_run = [
        'show version',
        'show ip interface brief',
        'show running-config',
        'show ip route',
    ]

    for command in commands_to_run:
        print(f'\n--- Output for: {command} ---')
        print(net_connect.send_command(command))

    net_connect.disconnect()
    print('\nDisconnected successfully.')
except Exception as exc:
    print(f'Connection failed: {exc}')
