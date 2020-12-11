# Purpose
This python script monitors the size of the ***/src/server/log/server.log*** file.
If the file grows to 50MB, the script will empty the contents of the log

## Install
Ansible is used to deploy the src files. In addition, there is a ***.service*** file deployed that will make this script run on startup
