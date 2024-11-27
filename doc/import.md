### Installing Prerequisites on Ubuntu/Debian

First, update your system and install the required tools:

```bash
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv unzip wget
```

## Step 2: Import Marzban Data

### Setup & Run

Ensure prerequisites are installed as in Step 1.

1. **Download the Import Tool**:
   ```bash
   cd /root
   wget -O old.zip https://github.com/erfjab/migration/archive/refs/heads/old.zip
   unzip -o old.zip
   mkdir -p /root/import
   cp -r migration-old/import/* /root/import/
   rm -rf migration-old old.zip
   ```

### Configure Marzneshin

Edit the Marzneshin Docker configuration to include these volumes:

```
nano /etc/opt/marzneshin/docker-compose.yml
```

**for v0.6.0:**

```yaml
    volumes:
      - /var/lib/marzneshin:/var/lib/marzneshin
      - /root/import/docker/v0_6_0/models/user.py:/app/app/models/user.py
      - /root/import/docker/v0_6_0/db/crud.py:/app/app/db/crud.py
```

Restart Marzneshin to apply changes:

```bash
marzneshin restart
```

### Configure Import

1. **Edit the Environment File**:
   ```bash
   cd /root/import
   nano .env
   ```

   Add environment details for the import, creating a new sudo admin account. Ensure this username is unique:

   ```
   MARZNESHIN_USERNAME="sudo_user"
   MARZNESHIN_PASSWORD="sudo_pass"
   MARZNESHIN_ADDRESS="https://sub.domain.com:port"
   MARZBAN_USERS_DATA="marzban.json"
   ```

2. **Set Up Python Environment**:
   ```bash
   cd /root/import
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Run Import

Start the import process:

```bash
cd /root/import
source venv/bin/activate
python3 main.py
```

> **Important:** After the import is complete, delete the Docker map files in volume.