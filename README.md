# FaceLocking

## How to run

This project can run in an isolated **Python 3.11** virtual environment so it **does not affect** your latest Python installation (e.g. 3.14).

### 1) Create a Python 3.11 virtual environment in `env/`
On Windows (PowerShell), use your installed Python 3.11 executable (example path below):

```powershell
& "C:\Users\TitanRiftYT\AppData\Local\Programs\Python\Python311\python.exe" -m venv env
```

### 2) Install dependencies into `env/`
```powershell
.\env\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\env\Scripts\python.exe -m pip install -r .\requirements.txt
```

### 3) Enroll a face (creates the local DB)
You can enroll either interactively (it will ask for the person name), or pass `--name`.

```powershell
.\env\Scripts\python.exe -m src.enroll --name your_name
```

### 4) Run FaceLocking (lock by name)
This keeps the old command working:

```powershell
.\env\Scripts\python.exe .\face_lock.py --lock-name your_name
```

### Notes
- If you don't want to type `.\env\Scripts\python.exe ...` every time, **activate the venv once** and then you can just use `python` / `pip` normally:

```powershell
.\env\Scripts\Activate.ps1
python --version
python -m pip install -r .\requirements.txt
python -m src.enroll --name your_name
python .\face_lock.py --lock-name your_name
```

- When the venv is activated, `python` points to the **env Python 3.11**, not your system Python.
- MediaPipe `0.10.x` uses the **Tasks** API. On first run the app will try to download `models/face_landmarker.task` automatically. If download fails, manually download it from:
  - `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task`
  and save it as `models\face_landmarker.task`.
- This does not uninstall or replace any other Python versions on your PC.
