### Installing Prerequisites on Ubuntu/Debian

First, update your system and install the required tools:

```bash
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv unzip wget
```

## Step 1: Export Marzban Data

This tool exports **Admins**, **Users**, and **JWT keys** from Marzban.

### Setting Up the Export Tool

1. **Download the Export Tool**:
   ```bash
   cd /root
   wget -O old.zip https://github.com/erfjab/migration/archive/refs/heads/old.zip
   unzip -o old.zip
   mkdir -p /root/export
   cp -r migration-old/export/* /root/export/
   rm -rf migration-old old.zip
   ```

2. **Set Up the Python Environment**:
   ```bash
   cd /root/export
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Prepare the Database**:
   - **SQLite**: Ensure Marzban is stopped.
   - **MySQL**: Have your database credentials ready.

4. **Run the Export Script**:
   ```bash
   cd /root/export
   source venv/bin/activate
   python3 export.py
   ```

   This will generate a `marzban.json` file with the exported data. For the next step, upload this file to the `/root/import` directory.