from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import uuid
from config import Config
from models import db, User, LoginHistory, Account, AccountMember, Invitation
from forms import RegistrationForm, LoginForm, InvitationForm, ProfileForm

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """Handle file size limit exceeded"""
    flash('Image Too Large - Maximum file size is 2MB', 'danger')
    return redirect(url_for('profile'))


@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Create a default account for the user
        account = Account(name=f"{user.username}'s Account", owner_id=user.id)
        db.session.add(account)
        db.session.commit()
        
        # Add user as admin member of their own account
        member = AccountMember(account_id=account.id, user_id=user.id, is_admin=True)
        db.session.add(member)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            # Record login event
            user.record_login()
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page if specified
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile editing"""
    form = ProfileForm()
    
    if form.validate_on_submit():
        # Update profile fields
        current_user.first_name = form.first_name.data.strip() or None
        current_user.last_name = form.last_name.data.strip() or None
        current_user.display_name = form.display_name.data.strip() or None
        current_user.city = form.city.data.strip() or None
        current_user.state = form.state.data.strip() or None
        current_user.country = form.country.data.strip() or None
        
        # Handle profile image upload
        if form.profile_image.data:
            file = form.profile_image.data
            
            # Check file size manually as additional validation
            file.seek(0, 2)  # Seek to end of file
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > app.config['MAX_CONTENT_LENGTH']:
                flash('Image Too Large - Maximum file size is 2MB', 'danger')
                return redirect(url_for('profile'))
            
            # Generate unique filename to avoid conflicts
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Delete old profile image if it exists
            if current_user.profile_image:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.profile_image)
                if os.path.exists(old_image_path):
                    try:
                        os.remove(old_image_path)
                    except Exception:
                        pass  # Ignore errors when deleting old image
            
            # Save new image
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            current_user.profile_image = unique_filename
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile. Please try again.', 'danger')
        return redirect(url_for('profile'))
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.display_name.data = current_user.display_name
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.country.data = current_user.country
    
    return render_template('profile.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard showing login statistics"""
    # Get recent login count (last 30 days)
    recent_login_count = current_user.get_recent_login_count(days=30)
    
    # Get recent login records
    recent_logins = current_user.get_recent_logins(limit=10)
    
    # Get user's accounts
    accounts = []
    # Add owned accounts
    for account in current_user.owned_accounts:
        accounts.append({
            'account': account,
            'is_owner': True,
            'is_admin': True
        })
    
    # Add accounts where user is a member
    for membership in current_user.memberships:
        if membership.account.owner_id != current_user.id:  # Don't duplicate owned accounts
            accounts.append({
                'account': membership.account,
                'is_owner': False,
                'is_admin': membership.is_admin
            })
    
    return render_template('dashboard.html', 
                           recent_login_count=recent_login_count,
                           recent_logins=recent_logins,
                           accounts=accounts)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/account/<int:account_id>')
@login_required
def view_account(account_id):
    """View account details"""
    account = Account.query.get_or_404(account_id)
    
    # Check if user has access to this account
    is_owner = account.owner_id == current_user.id
    membership = AccountMember.query.filter_by(account_id=account_id, user_id=current_user.id).first()
    
    if not is_owner and not membership:
        flash('You do not have access to this account.', 'danger')
        return redirect(url_for('dashboard'))
    
    is_admin = is_owner or (membership and membership.is_admin)
    
    # Get account members
    members = AccountMember.query.filter_by(account_id=account_id).all()
    
    # Get pending invitations (only if admin)
    pending_invitations = []
    if is_admin:
        pending_invitations = Invitation.query.filter_by(account_id=account_id, status='pending').all()
    
    return render_template('account.html', 
                           account=account,
                           is_owner=is_owner,
                           is_admin=is_admin,
                           members=members,
                           pending_invitations=pending_invitations)


@app.route('/account/<int:account_id>/invite', methods=['GET', 'POST'])
@login_required
def invite_user(account_id):
    """Invite a user to join an account"""
    account = Account.query.get_or_404(account_id)
    
    # Check if user has access to this account (any member can invite)
    is_owner = account.owner_id == current_user.id
    membership = AccountMember.query.filter_by(account_id=account_id, user_id=current_user.id).first()
    
    if not is_owner and not membership:
        flash('You do not have access to this account.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = InvitationForm()
    if form.validate_on_submit():
        email = form.email.data
        
        # Check if user is already a member
        invited_user = User.query.filter_by(email=email).first()
        if invited_user:
            existing_membership = AccountMember.query.filter_by(
                account_id=account_id, 
                user_id=invited_user.id
            ).first()
            if existing_membership:
                flash('This user is already a member of the account.', 'warning')
                return redirect(url_for('view_account', account_id=account_id))
        
        # Check if invitation already exists
        existing_invitation = Invitation.query.filter_by(
            account_id=account_id,
            invitee_email=email,
            status='pending'
        ).first()
        if existing_invitation:
            flash('An invitation has already been sent to this email.', 'warning')
            return redirect(url_for('view_account', account_id=account_id))
        
        # Create invitation
        invitation = Invitation(
            account_id=account_id,
            inviter_id=current_user.id,
            invitee_email=email
        )
        db.session.add(invitation)
        db.session.commit()
        
        flash(f'Invitation sent to {email}!', 'success')
        return redirect(url_for('view_account', account_id=account_id))
    
    return render_template('invite.html', form=form, account=account)


@app.route('/invitations')
@login_required
def view_invitations():
    """View pending invitations for current user"""
    invitations = Invitation.query.filter_by(
        invitee_email=current_user.email,
        status='pending'
    ).all()
    
    return render_template('invitations.html', invitations=invitations)


@app.route('/invitation/<int:invitation_id>/accept')
@login_required
def accept_invitation(invitation_id):
    """Accept an invitation"""
    invitation = Invitation.query.get_or_404(invitation_id)
    
    # Verify invitation is for current user
    if invitation.invitee_email != current_user.email:
        flash('This invitation is not for you.', 'danger')
        return redirect(url_for('dashboard'))
    
    if invitation.status != 'pending':
        flash('This invitation has already been processed.', 'warning')
        return redirect(url_for('view_invitations'))
    
    # Check if already a member
    existing_membership = AccountMember.query.filter_by(
        account_id=invitation.account_id,
        user_id=current_user.id
    ).first()
    
    if existing_membership:
        flash('You are already a member of this account.', 'warning')
        invitation.status = 'accepted'
        invitation.responded_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('view_invitations'))
    
    # Add user as member (non-admin)
    member = AccountMember(
        account_id=invitation.account_id,
        user_id=current_user.id,
        is_admin=False  # Invited users have no admin permissions
    )
    db.session.add(member)
    
    # Update invitation status
    invitation.status = 'accepted'
    invitation.responded_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'You have joined {invitation.account.name}!', 'success')
    return redirect(url_for('view_account', account_id=invitation.account_id))


@app.route('/invitation/<int:invitation_id>/decline')
@login_required
def decline_invitation(invitation_id):
    """Decline an invitation"""
    invitation = Invitation.query.get_or_404(invitation_id)
    
    # Verify invitation is for current user
    if invitation.invitee_email != current_user.email:
        flash('This invitation is not for you.', 'danger')
        return redirect(url_for('dashboard'))
    
    if invitation.status != 'pending':
        flash('This invitation has already been processed.', 'warning')
        return redirect(url_for('view_invitations'))
    
    # Update invitation status
    invitation.status = 'declined'
    invitation.responded_at = datetime.utcnow()
    db.session.commit()
    
    flash('Invitation declined.', 'info')
    return redirect(url_for('view_invitations'))


@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
