# Flask Security Application with Docker

This README file provides detailed instructions on how to set up and run a Flask application with user authentication and role management using Flask-Security, Flask-SQLAlchemy, and Docker.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Docker Configuration](#docker-configuration)
4. [Running the Application](#running-the-application)
5. [API Endpoints](#api-endpoints)
6. [Environment Variables](#environment-variables)
7. [Running Tests](#running-tests)

## Prerequisites

- Docker and Docker Compose installed on your machine
- Python 3.8+
- PostgreSQL

## Project Setup

1. **Clone the repository:**
    
    ```cmd
   git clone git@github.com:pinballtec/Flask-Security.git
   cd yourproject

2. Create a .env file in the root directory:

    ```cmd
   DATABASE_URI=postgresql://user:password@db:5432/mydatabase
   SECRET_KEY=your_secret_key
   SECURITY_PASSWORD_SALT=your_security_password_salt

## Running the Application

1. Build and start the Docker containers:

   docker-compose up --build

2. Apply database migrations:

    ```cmd
   docker-compose run web /bin/bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade

## Docker Configuration

The project includes a docker-compose.yml file that defines the following services:

    1) db: PostgreSQL database
    2) web: Flask application
    3) pgadmin: pgAdmin for database management
    4) tests: Service to run tests


## API Endpoints

1) Registration

    Endpoint: /register

    Method: POST

Payload:
```cmd
{
    "email": "user@example.com",
    "password": "userpassword",
    "first_name": "Normal",
    "last_name": "User",
    "phone": "1231231234"
}
```
2) Login

    Endpoint: /signin

    Method: POST

Payload:
```cmd
{
    "email": "user@example.com",
    "password": "userpassword"
}
```

3) Reset Password

    Endpoint: /reset_password

    Method: POST


В
```cmd
{
    "email": "user@example.com",
    "old_password": "oldpassword",
    "new_password": "newpassword"
}
```

4) Deactivate User

    Endpoint: /admin/deactivate/<int:user_id>

    Method: POST


5) Change User Role

   Endpoint: /admin/change_role/<int:user_id>/<role_name>

   Method: POST


6) Delete User

   Endpoint: /admin/delete_user/<int:user_id>

   Method: DELETE


7) Get Users

   Endpoint: /admin/users

   Method: GET

Payload:
```cmd
[
    {
        "id": 1,
        "email": "user@example.com",
        "first_name": "First",
        "last_name": "Last",
        "phone": "1234567890",
        "active": true,
        "roles": ["user"]
    },
    ...
]
```

Environment Variables

The application requires the following environment variables to be set:

    Endpoint: /reset_password

Running Tests

    To run the tests, use the following command:

```cmd
docker-compose run tests
```

Linting with flake8

    To ensure code quality and consistency, flake8 is used. 
    
    You can run flake8 with the following command:
```cmd
flake8 .
```

## Additional Notes
Ensure that the PostgreSQL service is running before starting the Flask application.

The pgAdmin service is optional and can be used to manage the PostgreSQL database via a web interface available at :

http://localhost:5050.