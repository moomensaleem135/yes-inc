This project is designed to match leads from HubSpot to a user's Google Sheet. If a lead (based on company name) matches, it will be saved in the database. Below is a step-by-step guide on how to set up and run the application.

1. **Basic Python Setup:**
    - First, ensure that you have Python 3.11+ installed on your system.
    - Create a virtual environment for the project to isolate dependencies.

    **For Mac/Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

    **For Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

2. **Install Dependencies:**
    - Once your virtual environment is activated, install the required packages.

    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables:**
    - Create a `.env` file in the root of the project and add the necessary environment variables:
    
    ```
    HUBSPOT_API_KEY=<your_hubspot_api_key>
    CLIENT_ID=<your_client_id>
    CLIENT_SECRET=<your_client_secret>
    REDIRECT_URI=<your_redirect_uri>
    GOOGLE_SHEETS_API_KEY=<your_google_sheets_api_key>
    SPREADSHEET_ID=<your_spreadsheet_id>
    SPREADSHEET_SHEET_NAME=<your_sheet_name>
    SCOPE=<your_scope>
    USER_ID=<your_user_id>
    SECRET_KEY=<your_secret_key>
    SQLALCHEMY_DATABASE_URI=<your_database_uri>
    SQLALCHEMY_TRACK_MODIFICATIONS=False
   SECRET_KEY
    ```

    - Make sure to replace the placeholders `<...>` with your actual values.

4. **Set Up the Database:**
    - Run the database migrations to set up your database schema.

    ```bash
    flask db upgrade
    ```

5. **Run the Flask Project Locally:**
    - Ensure the Flask application is running locally. In your terminal, run:

    ```bash
    flask run
    ```

6. **Set Up Ngrok for Public Access:**
    - To make your local Flask app publicly accessible, use Ngrok. You can download Ngrok from [here](https://ngrok.com/).
    - After installing Ngrok, run it from the terminal:

    ```bash
    ngrok http 5000
    ```

    - This will generate a public URL that you can use for testing. For example:
    ```
    http://6374-221-120-236-55.ngrok-free.app
    ```

7. **Configure HubSpot Webhook:**
    - Join your Ngrok link to the `/webhook` endpoint. The full URL should look like:
    ```
    http://6374-221-120-236-55.ngrok-free.app/webhook
    ```

    - Add this URL as a webhook in your HubSpot app under the "Webhooks" section.

    1. Go to [HubSpot Developer Webhooks](https://app.hubspot.com/developer/application/webhooks).
    2. Create a new webhook subscription for **Contact Creation** and use your Ngrok URL as the webhook URL.

8. **Authenticate HubSpot API:**
    - Visit the following URL to authenticate and save the access token in the database:
    ```
    http://localhost:5000/hubspot/auth
    ```

9. **Create a New Company and Lead in HubSpot:**
    - Go to [HubSpot CRM](https://app.hubspot.com/contacts/).
    - Create a new company and add the **company domain** carefully.
    - After creating the company, create a new contact (lead). Make sure the email follows the format:
    ```
    your-email@your-company-domain
    ```

10. **Google Sheets Integration:**
    - The application will now automatically match the created lead with the data in your Google Sheet (by company name). If a match is found, the lead will be saved in the system's database.

11. **Checking the Database:**
    - You can verify that the matched lead has been saved in your database by checking the records.

That's it! You've successfully set up the system to match leads from HubSpot to Google Sheets and save them in the database when a match is found.
