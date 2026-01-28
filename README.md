# flask-first
A Flask application with user authentication, login tracking, and account invitation system.

## Features

- **User Authentication**: Register and login with secure password hashing
- **Login Dashboard**: View your login statistics and recent login history
- **Login Tracking**: Automatically tracks and displays how many times you've logged in over the last 30 days
- **Account Management**: Create and manage accounts with multiple members
- **User Invitations**: Invite other users to join your accounts via email
- **Permission System**: Invited users have member access (no admin permissions)

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

The application will be available at `http://localhost:5000`

## Usage

1. **Register**: Create a new account at `/register`
2. **Login**: Access your account at `/login`
3. **Dashboard**: View your login statistics and accounts
4. **Invite Users**: From any account page, click "Invite User" to send an invitation
5. **Accept Invitations**: Check your invitations at `/invitations` and accept/decline them

## Database

The application uses SQLite by default. The database file (`app.db`) will be created automatically when you first run the application.

## Models

- **User**: User accounts with authentication
- **LoginHistory**: Tracks each login event
- **Account**: Accounts that can have multiple members
- **AccountMember**: Membership relation between users and accounts
- **Invitation**: Pending invitations to join accounts
