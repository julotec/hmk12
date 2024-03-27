# Secure Contact Management REST API with JWT Authentication

This repository extends the functionality of the previous homework assignment by implementing authentication and authorization mechanisms using JSON Web Tokens (JWT). Now, all operations on contacts are restricted to registered users only, ensuring data security and privacy.

## Features

- **User Registration:** Users can register with a unique email address and a securely hashed password. If a user attempts to register with an email address that already exists, the server returns an HTTP 409 Conflict error.
- **Token-based Authentication:** Authentication is handled using JWT tokens. Upon successful registration or login, the server issues an access_token and a refresh_token to the user.
- **Access Control:** Users can only access and modify their own contacts. Unauthorized access to other users' contacts is prohibited.
- **Token Refresh:** Users can refresh their access_token using the refresh_token without having to re-enter their credentials.
- **HTTP Status Codes:** The server returns appropriate HTTP status codes such as 201 Created for successful registration, 401 Unauthorized for invalid authentication attempts, and others as needed.

## Security Measures

- **Password Hashing:** User passwords are securely hashed and stored in the database. The server does not store passwords in plain text.
- **Token Encryption:** JWT tokens are encrypted to ensure data integrity and confidentiality during transmission.

## Technologies

- **FastAPI:** FastAPI is utilized for developing the REST API endpoints with Python.
- **JWT:** JSON Web Tokens are used for secure authentication and authorization.
- **SQLAlchemy ORM:** SQLAlchemy ORM facilitates interaction with the PostgreSQL database.
- **SQLite:** SQLite serves as the backend database for storing user and contact information.

## Getting Started

To get started with the project:

1. Install all the required dependencies from the `requirements.txt` file.
2. Configure the connection to the PostgreSQL database in the `.env` file.
3. Run the application using the command `uvicorn main:app --reload`.



