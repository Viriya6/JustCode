<div align="center">
  <img width="500" height="282" alt="github-removebg-preview" src="https://github.com/user-attachments/assets/0695fc65-4835-452e-b570-b4933dfd3701" />
  <br>
  <code>MUCH MUCH MUCH SIMPLER JUDGE</code>
</div>

## ❓ What Is JustCode?
JustCode is a simple online judge for people who wants to host private coding contests or teach students competitive programming to sharpen their problem-solving skills.

JustCode is inspired by [Codeforces](codeforces.com) and [TLX Online Judge](tlx.toki.id) to simplify how to deliver competitive programming.

## Quick Start ❗
If you using Windows make a new 'start.bat' file:
```bat
@echo off
SET VENV_DIR=venv

echo [1/3] Inspecting Virtual Environment...
IF NOT EXISTS %VENV_DIR% (
    echo Creating new Virtual Environment...
    python -m venv %VENV_DIR%
) ELSE (
    echo Virtual Environment already exist.
)

echo [2/3] Activating Venv and Install/Update Library...
call %VENV_DIR%\Scripts\activate
pip install -r requirements.txt

echo [3/3] Running Flask...
echo Application running at http://127.0.0.1:5000
python app.py

pause
```

But if you using linux add 'start.sh' file:
```bash
#!/bin/bash
VENV_DIR="venv"

echo "[1/3] Inspecting Virtual Environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating new Virtual Environment..."
    python -m venv $VENV_DIR
else
    echo "Virtual Environment already exist."
fi

echo "[2/3] Activating Venv and Install/Update Library..."
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    source $VENV_DIR/Scripts/activate
else
    source $VENV_DIR/bin/activate
fi

pip install -r requirements.txt

echo "[3/3] Running Flask..."
echo "Application running at http://127.0.0.1:5000"
python app.py

echo "Press enter to close..."
read
```

OR if you dont wanna do that just type
```python
pip install -r requirements.txt
```

## Requirements 🔧
Require Modules:
```txt
Flask
Flask-SQLAlchemy
python-dotenv
Werkzeug
```

## How To 📜

> Login

Login using admin account (username:admin, password:admin123)
<div>
  <img weight="600" heigth="auto" src="https://github.com/user-attachments/assets/3254cbaa-fbd6-49c4-86fe-7c9c25a892f0">
</div>

> Add User

Adding user using admin acocunt.
<div>
  <img weight="600" heigth="auto" src="https://github.com/user-attachments/assets/ece1d57c-b7ae-4080-a81a-14a3aa52b8af">
</div>

> Create A Problem

To create a problem you need to make a folder inside ```./problems``` folder
```
problems/
└── problem1
    └── info.json
    └── testcases/
        └── sample1.in
        └── sample1.out
```
