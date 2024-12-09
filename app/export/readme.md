### Installing Prerequisites on Ubuntu/Debian

First, update your system and install the required tools:

```bash
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv unzip wget git
```

## Step 1: Export Marzban Data

This tool exports **Admins**, **Users**, and **JWT keys** from Marzban.

### Setting Up the Export Tool

1. **Install Uv**:

```bash
export PIP_BREAK_SYSTEM_PACKAGES=1
pip install uv
```

2. **Prepare the Database**:
   - **SQLite**: Ensure Marzban is stopped.
   - **MySQL**: Have your database credentials ready.

3. **Download and Run**:

```bash
cd && git clone https://github.com/erfjab/migration.git && cd migration && git checkout ref && uv sync &&  uv run app/export/export.py
```


This will generate a `marzban.json` file with the exported data. For the next step, upload this file to the `/root/import` directory.