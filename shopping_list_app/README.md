# Shopping List Web Application

A simple web application for managing household shopping lists, built with Flask.

## Prerequisites

- Python 3 (3.7+ recommended)
- pip (Python package installer)
- virtualenv (recommended for creating isolated Python environments)

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd shopping_list_app
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # For Windows:
    # venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables:**
    ```bash
    export FLASK_APP=wsgi.py  # On Linux/macOS
    # For Windows:
    # set FLASK_APP=wsgi.py
    ```
    (Note: `wsgi.py` is the main application file.)

5.  **Initialize/Upgrade the Database:**
    The application uses Flask-Migrate to manage database schemas.
    ```bash
    flask db upgrade
    ```
    This command applies any pending database migrations and creates the `instance/app.db` SQLite database file if it doesn't exist. The first time you run this, it will create all tables.

## Running the Development Server

1.  **Ensure your virtual environment is activated and `FLASK_APP` is set.**

2.  **Run the Application:**
    ```bash
    flask run
    ```

3.  Open your web browser and navigate to:
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

You should now be able to register new users, create households, manage shopping lists, and add items.
