# Flask First

A simple Flask web application with login and logout functionality.

## Features

- User authentication (login/logout)
- Session management
- Flash messages for user feedback
- Responsive design with modern CSS
- Template inheritance using Jinja2
- Secure password hashing

## Project Structure

```
flask-first/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html      # Base template
│   ├── index.html     # Home page
│   └── login.html     # Login page
└── static/            # Static files
    └── style.css      # CSS styles
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/iamctodd/flask-first.git
cd flask-first
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Demo Credentials

- **Username:** admin
- **Password:** password

## Usage

1. Visit the home page at `http://localhost:5000`
2. Click "Login" in the navigation bar
3. Enter the demo credentials
4. After successful login, you'll be redirected to the home page
5. Click "Logout" to end your session

## Features Demonstrated

- **Routing:** Multiple routes for different pages
- **Session Management:** User sessions with Flask's session object
- **Template Rendering:** Dynamic HTML with Jinja2 templates
- **Form Handling:** POST request handling for login
- **Flash Messages:** User feedback with Flask's flash messages
- **Static Files:** CSS styling served from static directory
- **Security:** Password hashing with Werkzeug

## Deployment

For production deployment:

1. Set a secure secret key:
```bash
export SECRET_KEY='your-secure-random-key-here'
```

2. Disable debug mode by modifying `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

3. Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn app:app
```

## Note

This is a simple demonstration application. For production use:
- Use a proper database instead of in-memory user storage
- Implement proper user registration
- Add CSRF protection
- Use environment variables for configuration
- Add proper logging
- Implement rate limiting
