### Installing Prerequisites on Ubuntu/Debian

1. **Prepare the Database**:
   - **SQLite**: Ensure Marzban is stopped.
   - **MySQL**: Have your database credentials ready.

2. **Run the Export Script**:
   ```bash
   sudo bash -c "$(curl -sL https://raw.githubusercontent.com/erfjab/migration/refactor/export.sh)"
   ```

   This will generate a `marzban.json` file with the exported data. For the next step, upload this file to the `/root/import` directory.