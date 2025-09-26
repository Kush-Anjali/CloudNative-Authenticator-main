#!/bin/bash

set -e

# Set project location
project_loc="$1"

# Source environment variables
source "$project_loc"/config/.env || {
  echo "Error: Unable to load environment variables from config.env"
  exit 1
}

# Change directory to project path
cd "$PROJECT_PATH"

# Apply migrations if necessary
if python3.9 manage.py showmigrations --plan | grep -q "\[ \]"; then
    echo "Pending migrations found. Applying migrations..."
    python3.9 manage.py migrate
    echo "Migrations applied successfully."
else
    echo "No pending migrations found."
fi

# Check for pending migrations
if python3.9 manage.py makemigrations myapp --check | grep -q "No changes detected"; then
    echo "No pending migrations found."
else
#      python3.9 manage.py flush --no-input
      python3.9 manage.py makemigrations myapp
      python3.9 manage.py migrate
      echo "Migration done for myapp"
fi
