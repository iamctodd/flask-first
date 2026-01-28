from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User account model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Profile information
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    display_name = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    profile_image = db.Column(db.String(200))
        
    # Relationships
    login_history = db.relationship('LoginHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    owned_accounts = db.relationship('Account', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    memberships = db.relationship('AccountMember', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_invitations = db.relationship('Invitation', foreign_keys='Invitation.inviter_id', backref='inviter', lazy='dynamic', cascade='all, delete-orphan')
    received_invitations = db.relationship('Invitation', foreign_keys='Invitation.invitee_email', primaryjoin='User.email==Invitation.invitee_email', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def record_login(self):
        """Record a login event"""
        login_entry = LoginHistory(user_id=self.id)
        db.session.add(login_entry)
        db.session.commit()
    
    def get_recent_login_count(self, days=30):
        """Get number of logins in the last X days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.login_history.filter(LoginHistory.login_time >= cutoff_date).count()
    
    def get_recent_logins(self, limit=10):
        """Get recent login records"""
        return self.login_history.order_by(LoginHistory.login_time.desc()).limit(limit).all()


class LoginHistory(db.Model):
    """Track user login events"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Account(db.Model):
    """Account that can have multiple members"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('AccountMember', backref='account', lazy='dynamic', cascade='all, delete-orphan')
    invitations = db.relationship('Invitation', backref='account', lazy='dynamic', cascade='all, delete-orphan')


class AccountMember(db.Model):
    """Membership of a user in an account"""
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('account_id', 'user_id', name='unique_account_member'),)


class Invitation(db.Model):
    """Invitation to join an account"""
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitee_email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, accepted, declined
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
