# WebApp

WebApp is a simple web application designed for cloud environments.

For additional infrastructure resources related to this project, refer to the following repositories:
1. [tf-gcp-infra](https://github.com/DeathOrg/tf-gcp-infra) - Infrastructure setup for Google Cloud Platform.
2. [serverless](https://github.com/DeathOrg/serverless) - Repository for serverless architecture.
   
## Introduction

WebApp is a lightweight web application built to demonstrate cloud-based development practices. It provides a platform for users to perform various tasks, including user management and authentication.

## Features

- **User Management**: Create, update user profiles.
- **Authentication**: Secure authentication using token-based basic authentication.
- **Password Hashing**: User passwords are securely hashed using the BCrypt algorithm.
- **User Information Retrieval**: Retrieve user account information.
- **API Endpoints**: Provides endpoints for creating, updating, and retrieving user accounts.

## Installation

To install and set up the WebApp locally, follow these steps:

1. Clone the repository:

    ```bash
    git clone git@github.com:Sourabh-Kumar7/webapp.git
    ```

2. Navigate to the project directory:

    ```bash
    cd webapp
    ```

3. Set up the virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Set up environment variables:

    Create a `.env` file in the root directory and define the following variables:

    ```plaintext
    SECRET_KEY=your_secret_key
    DEBUG=True
    DATABASE_NAME=your_database_name
    DATABASE_USER=your_database_user
    DATABASE_PASSWORD=your_database_password
    DATABASE_HOST=your_database_host
    DATABASE_PORT=your_database_port
    ```

6. Migrate the database:

    ```bash
    python manage.py migrate
    ```

## Usage

To run the WebApp locally, use the following command:

```bash
python manage.py runserver
```
or

```bash
#This will handle migration and run app
./setup.sh
```

Access the application in your web browser at `http://localhost:8000`.

- **Commands to set venv:**

  ```bash
    ```bash
      python -m venv venv
      source venv/bin/activate
      deactivate
   

- **Commands to set up git remotes:**

  ```bash
    git remote | xargs -n 1 git remote remove (To remove all remotes)
    git remote remove origin (To remove specific remote, in this case origin)
    git remote add sourabh git@github.com:Sourabh-Kumar7/webapp.git
    git remote add upstream git@github.com:DeathOrg/webapp.git
    git remote set-url --push upstream no_push

## Contributing

We welcome contributions from the community. If you'd like to contribute to the project, please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with clear and descriptive messages.
4. Push your changes to your fork.
5. Submit a pull request to the main repository.

## License

This project is licensed under the [MIT License](LICENSE).
