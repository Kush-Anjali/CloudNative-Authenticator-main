#!/bin/bash

# Check if the user exists
if id "csye6225" &>/dev/null; then
    echo "User csye6225 already exists."

    # Check if the user's login shell is already set to /usr/sbin/nologin
    if [ "$(getent passwd csye6225 | cut -d':' -f7)" == "/usr/sbin/nologin" ]; then
        echo "Login shell is already set to /usr/sbin/nologin."
    else
        # Change the user's login shell to /usr/sbin/nologin
        sudo usermod -s /usr/sbin/nologin csye6225
        echo "Login shell set to /usr/sbin/nologin."
    fi
else
    # Create the user
    sudo useradd -M -s /usr/sbin/nologin csye6225
    sudo chgrp csye6225 csye6225
    echo "User csye6225 created with login shell set to /usr/sbin/nologin."
fi
