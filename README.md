
````markdown
# Monitoring System

A lightweight monitoring solution that collects **system information** and **running processes** from multiple hosts using a Monitoring System agent. The data is posted to a **Django REST Framework (DRF)** API and displayed in a **FRONTEND dashboard**.

---

## Features
- Collect system information (CPU, RAM, OS, etc.) from each host.
- Collect process details from each host.
- Secure API communication with **DRF API keys**.
- Dashboard to view:
  - Hosts
  - System Info (expandable per host)
  - Process Info (expandable per host)
- Monitoring System agent can be converted to a `.exe` for Windows deployment.

---

## Requirements

### Backend
- Python 3.x
- Django
- Django REST Framework
- Django REST Framework API Key

### Monitoring System Agent
- Python 3.x
- `requests` library
- `psutil` library

### Frontend
- HTML, CSS, JavaScript

---

## Setup

### 0. Create Virtual Environment (Recommended)
```bash
python -m venv venv
# Activate the environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
````

### 1. Backend (DRF API)

```bash
cd api
pip install django djangorestframework djangorestframework-api-key
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

The API will start on `http://127.0.0.1:8000/`.

---

### 2. Generate API Key

Open Django shell:

```bash
python manage.py shell
```

Then run:

```python
from rest_framework_api_key.models import APIKey
api_key, key = APIKey.objects.create_key(name="monitoring-system")
print("API Key:", key)
```

Copy the API Key — you will need it in `monitoring_system.py`.

---

### 3. Monitoring System Agent

Edit `monitoring_system.py` and set:

```python
API_KEY = "your-generated-api-key"
API_URL = "http://127.0.0.1:8000/api/..."
```

Run the agent:

```bash
python monitoring_system.py
```

---

### 4. Convert Monitoring System to `.exe` (Windows)

Install **pyinstaller**:

```bash
pip install pyinstaller
```

Build `.exe`:

```bash
pyinstaller --onefile monitoring_system.py
```

The executable will be created in the `dist/` folder as:

```
monitoring_system.exe
```

Deploy this `.exe` on client machines to start sending monitoring data.

---

### 5. Frontend

Open `FRONTEND/index.html` in a browser.
It will fetch all hosts from the API and display:

* Hostname
* System Info (expandable row)
* Process Info (expandable row)

---

## Testing

1. Start Django API:

   ```bash
   python manage.py runserver
   ```
2. Run the Monitoring System agent on one or more machines:

   ```bash
   python monitoring_system.py
   ```
3. Open `index.html` in a browser.
4. Verify:

   * Hostnames appear in rows.
   * Clicking **System Info** shows system details.
   * Clicking **Process Info** shows running processes.

---

## Future Improvements

* Authentication per host
* Historical process logs
* Real-time WebSocket updates
* Notifications for high CPU/memory usage

---

## License

This project is for **educational and internal use**.


