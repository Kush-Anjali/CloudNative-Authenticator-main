#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error: $1" >&2
    exit 1
}

# Function to update system packages
update_system() {
    echo "Updating System..."
    sudo yum update -y || handle_error "Failed to update system packages."
    sudo yum upgrade -y
}

# Function to install Python 3.9 and pip
install_python_and_pip() {
    echo "Installing Python 3.9..."
    sudo yum install -y python39 || handle_error "Failed to install Python 3.9."

    echo "Installing pip for Python 3.9..."
    sudo yum install -y python39-pip || handle_error "Failed to install pip for Python 3.9."

    echo "Upgrading pip..."
    python3.9 -m pip install --upgrade pip
}

# Function to install Python and MySQL development packages
install_dev_packages() {
    echo "Installing Python and MySQL development packages..."
    sudo yum install -y python39-devel mysql-devel || handle_error "Failed to install Python and MySQL development packages."
    sudo yum groupinstall -y "Development Tools" || handle_error "Failed to install development tools."
    python3.9 -m pip install mysqlclient || handle_error "Failed to install mysqlclient."
}

# Function to install project requirements
install_requirements() {
    echo "Installing requirements..."
    sudo /usr/bin/pip3.9 install -r /tmp/requirements.txt || handle_error "Failed to install requirements."
}

# Function to display installed packages
display_installed_packages() {
    echo "pip3.9 list..."
    pip3.9 list

    echo "python3.9 -m list output.."
    python3.9 -m pip list
}

# Main script execution
main() {
    update_system
    install_python_and_pip
    install_dev_packages
    install_requirements
    display_installed_packages

    echo "Installing unzip..."
    sudo yum install unzip -y || handle_error "Failed to install unzip."
}

# Execute the main function
main
