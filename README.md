# flask-first
A Flask web application with user authentication and profile management

## Features

- **User Authentication**: Complete registration and login system with secure password hashing
- **Profile Management**: Logged-in users can edit their profile information including:
  - First Name
  - Last Name
  - Display Name
  - Location (City, State, Country)
  - Profile Picture/Avatar Upload
- **Profile Picture Upload**: Upload and display custom profile pictures with:
  - File size limit (2MB maximum)
  - Supported formats: PNG, JPG, JPEG, GIF
  - Circular avatar display with blue border
  - Automatic placeholder with user's initial
- **Session Management**: Flask-Login integration for secure session handling
- **Responsive UI**: Clean, modern interface with proper navigation and flash messages
- **Security**: Protection against open redirect vulnerabilities, secure password storage, and configurable debug mode

## Installation

1. Clone the repository:
```bash
git clone https://github.com/iamctodd/flask-first.git
cd flask-first
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000/`

## Usage

1. **Register**: Create a new account with username, email, and password
2. **Login**: Log in with your credentials
3. **Edit Profile**: Navigate to the Profile page to update your personal information
4. **Logout**: Log out from the navigation menu

## Testing

Run the test suite:
```bash
pytest test_app.py -v
```

## Configuration

Set environment variables for production:
- `SECRET_KEY`: Flask secret key (required for production)
- `FLASK_DEBUG`: Set to 'true' to enable debug mode (disabled by default)

## Project Structure

```
flask-first/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── test_app.py        # Test suite
└── templates/         # HTML templates
    ├── base.html      # Base template with navigation
    ├── index.html     # Home page
    ├── login.html     # Login page
    ├── register.html  # Registration page
    └── profile.html   # Profile editing page
```
