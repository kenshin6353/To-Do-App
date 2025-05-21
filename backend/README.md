# To-Do-Python-Backend
 
## How to run:
1. Create `.env` file on the parent directory and paste this value.

    ```env
    DATABASE_URL=sqlite:///./db.sqlite3
    JWT_SECRET_KEY=[PASTE_YOUR_JWT_SECRET_KEY]
    ```

2. Generate JWT token using this command:

    ```bash
    python3 - << 'EOF'
    import secrets; print(secrets.token_urlsafe(32))
    EOF
    ```

3. Copy the generated value, and paste into the `.env` file.

4. Run this command to install all necessary libraries.

    ```bash
    pip install -r requirements.txt
    ```

5. Run the app.

    ```bash
    python main.py
    ```