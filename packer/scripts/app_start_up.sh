#!/bin/bash


# Function to handle errors
handle_error() {
    echo "Error: $1" >&2
    exit 1
}

# Function to create log directory with appropriate permissions
create_log_dir() {
    # Create log directory if it doesn't exist
    if [ ! -d "$LOG_DIR" ]; then
        sudo mkdir -p "$LOG_DIR" || handle_error "Failed to create log directory: $LOG_DIR"
        echo "Created log directory: $LOG_DIR"

        # Set appropriate permissions
        sudo chown -R csye6225:csye6225 "$LOG_DIR" || handle_error "Failed to set ownership for log directory: $LOG_DIR"
        sudo chmod 750 "$LOG_DIR" || handle_error "Failed to set permissions for log directory: $LOG_DIR"
        echo "Set permissions for log directory: $LOG_DIR"
    else
        echo "Log directory already exists: $LOG_DIR"
    fi
}

# Function to remove unnecessary files
remove_unnecessary_files() {
    rm -rf /home/csye6225/webapp* __MACOSX
    rm -rf /home/csye6225/cloud/__MACOSX
    rm -rf "$PROJECT_LOC"/app_artifact
    rm -f "$PROJECT_LOC"/*.json
    cd /home/csye6225 || handle_error "Failed to change directory to /home/csye6225"
    sudo rm -rf app_artifact/ config/ gha-creds* LICENSE manage.py myapp/ packer/ README.md requirements/ setup.sh utils/ || handle_error "Failed to remove unnecessary files"
    cd - || handle_error "Failed to change directory back"
}

# Main script execution
main() {
    # Setup web application
    echo "Setting up web application..."
    mkdir -p "$PROJECT_LOC" || handle_error "Failed to create project directory: $PROJECT_LOC"
    unzip webapp.zip -d "$PROJECT_LOC" || handle_error "Failed to unzip webapp.zip to $PROJECT_LOC"
    chmod +x "$PROJECT_LOC/setup.sh" || handle_error "Failed to make setup.sh executable"
    sudo mv /tmp/webapp.service /etc/systemd/system/webapp.service || handle_error "Failed to move webapp.service to /etc/systemd/system/"

    create_log_dir
    remove_unnecessary_files

    sudo chown csye6225:csye6225 "$PROJECT_LOC"/setup.sh || handle_error "Failed to set ownership for setup.sh"
    sudo chown -R csye6225:csye6225 "$PROJECT_LOC" || handle_error "Failed to set ownership for project directory: $PROJECT_LOC"
    sudo chmod -R 755 "$PROJECT_LOC" || handle_error "Failed to set permissions for project directory: $PROJECT_LOC"
    chmod +x "$PROJECT_LOC"/setup.sh || handle_error "Failed to make setup.sh executable"

    sudo setenforce 0 || handle_service_status_error "Failed to set SELinux to Permissive mode"
    sudo systemctl daemon-reload || handle_error "Failed to reload systemd."
    sudo systemctl enable webapp.service || handle_error "Failed to enable webapp.service."
}

# Execute the main function
main
