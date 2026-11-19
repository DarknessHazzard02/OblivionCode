# FreeCodeCamp Information Security with Python - Port Scanner
# Scans targeted IP addresses or hostnames across a specified port range and detects open services

import socket
import re

COMMON_PORTS = {
    20: "ftp-data",
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    143: "imap",
    443: "https",
    3306: "mysql",
    5432: "postgresql",
    8080: "http-alt"
}

def get_open_ports(target, port_range, verbose=False):
    # Validate target IP / hostname
    is_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target)
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        return "Error: Invalid IP address" if is_ip else "Error: Invalid hostname"

    try:
        host_name = socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        host_name = None

    open_ports = []

    for port in range(port_range[0], port_range[1] + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
        s.close()

    if not verbose:
        return open_ports

    # Format verbose table
    if host_name:
        header = f"Open ports for {host_name} ({ip})\nPORT     SERVICE"
    else:
        header = f"Open ports for {ip}\nPORT     SERVICE"

    lines = [header]
    for port in open_ports:
        service_name = COMMON_PORTS.get(port, "unknown")
        lines.append(f"{str(port):<9}{service_name}")

    return "\n".join(lines)

# Demonstration on localhost
if __name__ == "__main__":
    print("=== FreeCodeCamp Port Scanner Demo ===")
    print("Testing localhost scan on standard ports [78, 85]:")
    print(get_open_ports("127.0.0.1", [78, 85], verbose=True))
    print("\nScan completed successfully.")
