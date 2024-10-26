## Prerequisites

Ensure the following requirements are met before proceeding with installation:
- **Operating System**: Ubuntu
- **Permissions**: Root or sudo access

## Installation

To install the `migration-without_hashusername` bot, execute the following commands:

1. Download and set up the script:
   ```bash
   sudo bash -c "$(curl -sL https://raw.githubusercontent.com/MatinDehghanian/migration-without_hashusername/master/install.sh)" @ --install-script
   ```

2. Install the bot:
   ```bash
   migration-without_hashusername --install
   ```

3. Set up the system service:
   ```bash
   migration-without_hashusername --install-service
   ```

4. Set up the db:

   ```bash
   cd /opt/erfjab/migration 
    source venv/bin/activate
   ```

   ```bash
   python -m alembic upgrade head
   ```

5. Start the bot:
   ```bash
   migration-without_hashusername --start
   ```

### Installation Details

The above steps will:
1. **Check and Install Dependencies**: Ensure all necessary software is installed.
2. **Clone Repository**: Retrieve the `migration-without_hashusername` repository securely.
3. **Create Python Environment**: Set up an isolated environment for Python packages.
4. **Create and Enable Service**: Register `migration-without_hashusername` as a system service.
5. **Launch the Bot**: Start the bot, which will run continuously in the background.

## Usage

After installation, you can manage the `migration-without_hashusername` bot using the following commands:

```bash
migration-without_hashusername <command>
```

### Commands

- `--install`: Set up the bot, including dependencies and initial configuration.
- `--start`: Start the bot service.
- `--stop`: Stop the bot service.
- `--restart`: Restart the bot service.
- `--status`: Check the current status of the bot service.
- `--logs`: View the bot’s logs in real time.
- `--update`: Pull the latest changes from the repository and apply updates.
- `--uninstall`: Fully remove the bot and all related files.
- `--help`: Display a help message with all available commands.

## Directory Structure

- **Installation Directory**: `/opt/erfjab/migration`
- **Log File**: `/opt/erfjab/migration/migration.log`
- **Service File**: `/etc/systemd/system/migration.service`

## Uninstallation

To completely remove `migration-without_hashusername` and all associated files, execute:

```bash
sudo migration-without_hashusername --uninstall
```
