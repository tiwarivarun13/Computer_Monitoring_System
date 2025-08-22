# monitor_agent.py
import psutil
import requests
import socket
import platform
import time
import shutil

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000/api/ingest/"   # Django ingest endpoint
API_KEY = "john@123"              # Must match ApiKey in Django
INTERVAL = 5                                   # seconds
# ----------------------------------------

def get_process_tree():
    """Return all processes in a parent-child hierarchy."""
    pid_map = {}

    # Build PID → info mapping
    for proc in psutil.process_iter(attrs=['pid', 'name', 'username', 'cpu_percent', 'memory_info', 'ppid']):
        try:
            info = proc.info
            pid_map[info['pid']] = {
                "pid": info['pid'],
                "name": info['name'],
                "user": info.get('username'),
                "cpu": info['cpu_percent'],
                "memory": info['memory_info'].rss / (1024*1024),  # MB
                "children": [],
                "ppid": info['ppid'],
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Attach children to parents
    root_processes = []
    for pid, proc in pid_map.items():
        parent_pid = proc["ppid"]
        if parent_pid in pid_map:
            pid_map[parent_pid]["children"].append(proc)
        else:
            root_processes.append(proc)

    return root_processes

def get_system_info():
    hostname = socket.gethostname()
    system = platform.system()
    processor = platform.processor()
    cpu_percent = psutil.cpu_percent(interval=1)
    virtual_mem = psutil.virtual_memory()
    ram_total = virtual_mem.total
    ram_used = virtual_mem.used
    ram_available = virtual_mem.available

    # Storage info (main disk)
    disk = shutil.disk_usage('/')
    storage_total = disk.total
    storage_used = disk.used
    storage_free = disk.free

    processes = get_process_tree()

    return {
        "hostname": hostname,
        "operating_system": system,
        "processor": processor,
        "num_cores": psutil.cpu_count(logical=False),
        "num_threads": psutil.cpu_count(logical=True),
        "cpu_usage": cpu_percent,
        "ram_total": ram_total,
        "ram_used": ram_used,
        "ram_available": ram_available,
        "storage_total": storage_total,
        "storage_used": storage_used,
        "storage_free": storage_free,
        "processes": processes
    }

def main():
    while True:
        data = get_system_info()
        try:
            headers = {"X-API-Key": API_KEY}
            response = requests.post(API_URL, json=data, headers=headers)
            print(f"Sent {len(data['processes'])} parent processes. Status: {response.status_code}")
        except Exception as e:
            print("Error sending data:", e)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
