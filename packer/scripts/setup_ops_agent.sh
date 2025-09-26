#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error: $1" >&2
    exit 1
}

# Function to add Google Cloud Ops Agent repository and install the agent
install_ops_agent() {
    echo "Downloading Google Cloud Ops Agent repository script..."
    curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh || handle_error "Failed to download Google Cloud Ops Agent repository script."

    echo "Running Google Cloud Ops Agent repository script..."
    sudo bash add-google-cloud-ops-agent-repo.sh --also-install || handle_error "Failed to add Google Cloud Ops Agent repository or install the agent."

    echo "Removing Google Cloud Ops Agent repository script..."
    sudo rm add-google-cloud-ops-agent-repo.sh || handle_error "Failed to remove Google Cloud Ops Agent repository script."
}

# Function to configure Ops Agent with custom config file
configure_ops_agent() {
    echo "Copying custom config file to Ops Agent directory..."
    sudo cp /tmp/config.yaml /etc/google-cloud-ops-agent/config.yaml || handle_error "Failed to copy custom config file to Ops Agent directory."
}

# Function to restart Ops Agent service
restart_ops_agent() {
    echo "Restarting Google Cloud Ops Agent service..."
    sudo systemctl restart google-cloud-ops-agent || handle_error "Failed to restart Google Cloud Ops Agent service."
}

# Main script execution
main() {
    install_ops_agent
    configure_ops_agent
    restart_ops_agent

    echo "Google Cloud Ops Agent installation and configuration completed successfully."
}

# Execute the main function
main
