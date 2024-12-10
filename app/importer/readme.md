### Installing Prerequisites on Ubuntu/Debian

First, update your system and install the required tools:

```bash
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv unzip wget git
```

## Step 2: Import Marzban Data

### Setup & Run

Ensure prerequisites are installed as in Step 1.


2. **Install Uv**:

```bash
export PIP_BREAK_SYSTEM_PACKAGES=1
pip install uv
```

3. **Download the Import Tool**:

```bash
cd && git clone https://github.com/erfjab/migration.git && cd migration
```

### Configure Marzneshin

Edit the Marzneshin Docker configuration to include these volumes:

```
nano /etc/opt/marzneshin/docker-compose.yml
```

**for v0.6.0 to v0.6.2:**

```yaml
    volumes:
      - /var/lib/marzneshin:/var/lib/marzneshin
      - /root/migration/app/importer/docker/v062/user.py:/app/app/models/user.py
      - /root/migration/app/importer/docker/v062/crud.py:/app/app/db/crud.py
```


**for v0.6.3:**

```yaml
    volumes:
      - /var/lib/marzneshin:/var/lib/marzneshin
      - /root/migration/app/importer/docker/v063/user.py:/app/app/models/user.py
      - /root/migration/app/importer/docker/v063/crud.py:/app/app/db/crud.py
```

Restart Marzneshin to apply changes:

```bash
marzneshin restart
```

### Configure Import

1. **Edit the Environment File**:

```bash
cd /root/migration && nano .env
```

Add environment details for the import, creating a new sudo admin account. Ensure this username is unique:

```
MARZNESHIN_USERNAME="sudo_user"
MARZNESHIN_PASSWORD="sudo_pass"
MARZNESHIN_ADDRESS="https://sub.domain.com:port"
MARZBAN_USERS_DATA="marzban.json"
```

2. **Run Project**
```bash
cd /root/migration && uv sync &&  uv run import.py
```

3. **Save exceptions.json file to your pc**

4. **Delete docker map files**
   
   After the import is complete, delete the Docker map files in volume. and `marzneshin restart` 


5. **Delete script Files**

```bash
rm -rf /root/migration
```