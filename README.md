# Support++ Backend

## Installation
Follow these steps to set up the Backend on your local machine:

1. Clone the repository:
   ```
   git clone https://github.com/17sTomy/backend-support.git
   ```
2. Set up the Django backend. Create a virtual environment and activate it:
    ```
   python -m venv .venv
   .venv/scripts/activate
   ``` 
3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Apply migrations to set up the database:
   ```
   cd backend
   python manage.py migrate
   ```
6. Run the development server:
   ```
   python manage.py runserver
   ```