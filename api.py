
import os

from flask import Flask, render_template, request
from netmiko import ConnectHandler

app = Flask(__name__)

# Demo Mode is enabled by default.
# Set DEMO_MODE=false only when a real router is available.
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

COMMAND_GROUPS = {
    "api.py": [
        "show running-config",
        "show ip interface brief",
        "show version",
    ],
    "lesson.py": [
        "show version",
        "show ip interface brief",
        "show running-config",
        "show ip route",
    ],
}

DEMO_OUTPUTS = {
    "show running-config": """Building configuration...

Current configuration:
!
hostname Router0
!
interface GigabitEthernet0/0
 ip address 192.168.10.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 no ip address
 shutdown
!
end""",

    "show ip interface brief": """Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.10.1    YES manual up                    up
GigabitEthernet0/1     unassigned      YES unset  administratively down down
Vlan1                  unassigned      YES unset  administratively down down""",

    "show version": """Cisco IOS Software, Version 15.2
Technical Support: http://www.cisco.com
Compiled for demonstration purposes

Router uptime is 2 hours, 15 minutes
System image file is "flash:c1900-universalk9-mz.SPA.bin"
Cisco 1941/K9 processor
1 Gigabit Ethernet interface
Configuration register is 0x2102""",

    "show ip route": """Codes: C - connected, S - static, R - RIP

Gateway of last resort is not set

C    192.168.10.0/24 is directly connected, GigabitEthernet0/0
L    192.168.10.1/32 is directly connected, GigabitEthernet0/0""",
}


@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    error = None

    router_host = os.getenv("ROUTER_HOST", "192.168.10.14")
    router_port = int(os.getenv("ROUTER_PORT", "32770"))

    if request.method == "POST":

        if DEMO_MODE:
            # Sample outputs for demonstration only.
            results = {
                script: {
                    command: DEMO_OUTPUTS[command]
                    for command in commands
                }
                for script, commands in COMMAND_GROUPS.items()
            }

        else:
            router_device = {
                "device_type": "cisco_ios_telnet",
                "ip": router_host,
                "port": router_port,
                "username": os.getenv("ROUTER_USERNAME", "admin"),
                "password": os.getenv("ROUTER_PASSWORD", "eve123"),
                "secret": os.getenv("ROUTER_SECRET", "eve123"),
                "conn_timeout": 5,
                "banner_timeout": 5,
                "auth_timeout": 5,
            }

            net_connect = None

            try:
                net_connect = ConnectHandler(**router_device)
                net_connect.enable()

                command_outputs = {}

                for commands in COMMAND_GROUPS.values():
                    for command in commands:
                        if command not in command_outputs:
                            command_outputs[command] = (
                                net_connect.send_command(command)
                            )

                results = {
                    script: {
                        command: command_outputs[command]
                        for command in commands
                    }
                    for script, commands in COMMAND_GROUPS.items()
                }

            except Exception as exc:
                error = (
                    f"Unable to reach router {router_host}:{router_port}. "
                    f"Details: {exc}"
                )

            finally:
                if net_connect is not None:
                    try:
                        net_connect.disconnect()
                    except Exception:
                        pass

    return render_template(
        "index.html",
        results=results,
        error=error,
        router_host=router_host,
        router_port=router_port,
        demo_mode=DEMO_MODE,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
