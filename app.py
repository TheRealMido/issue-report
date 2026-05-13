import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from models import db, User, Category, Issue, StatusUpdate, Vote
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'premium_super_secret_key_2026')

# Setup Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Decorator to restrict admin access
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access Denied. You must be an admin to view this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# MySQL Configuration
# Format: mysql+pymysql://DB_USER:DB_PASSWORD@DB_HOST/DB_NAME
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'issue_reporter')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    # Seed data if empty
    seed_db()
    
    issues = Issue.query.all()
    # Sort primarily by number of votes, then by date submitted
    issues.sort(key=lambda x: (len(x.votes), x.date_submitted), reverse=True)
    
    categories = Category.query.all()
    return render_template('index.html', issues=issues, categories=categories)

@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_issue():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        location = request.form.get('location')
        
        # Now we use the exactly logged in user!
        user = current_user
        
        new_issue = Issue(
            title=title,
            description=description,
            category_id=category_id,
            location=location,
            user_id=user.user_id if user else None
        )
        
        db.session.add(new_issue)
        db.session.commit()
        flash('Issue reported successfully!', 'success')
        return redirect(url_for('index'))
        
    categories = Category.query.all()
    return render_template('submit_issue.html', categories=categories)

@app.route('/vote/<int:issue_id>', methods=['POST'])
def vote(issue_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized', 'redirect': url_for('login')}), 401
        
    issue = Issue.query.get_or_404(issue_id)
    existing_vote = Vote.query.filter_by(user_id=current_user.user_id, issue_id=issue_id).first()
    
    if existing_vote:
        db.session.delete(existing_vote)
        db.session.commit()
    else:
        new_vote = Vote(user_id=current_user.user_id, issue_id=issue_id)
        db.session.add(new_vote)
        db.session.commit()
        
    return jsonify({'new_vote_count': len(issue.votes)})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email not found. Please register.', 'warning')
            
    return render_template('auth.html', form_type='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered! Try logging in.', 'danger')
            return redirect(url_for('login'))
            
        new_user = User(name=name, email=email, role='resident')
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('index'))
        
    return render_template('auth.html', form_type='register')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    user_issues = Issue.query.filter_by(user_id=current_user.user_id).order_by(Issue.date_submitted.desc()).all()
    return render_template('profile.html', issues=user_issues)

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    issues = Issue.query.order_by(Issue.date_submitted.desc()).all()
    # List of valid enum statuses
    statuses = ['Submitted', 'Under Review', 'In Progress', 'Resolved', 'Rejected']
    return render_template('admin.html', issues=issues, statuses=statuses)

@app.route('/admin/update_status/<int:issue_id>', methods=['POST'])
@login_required
@admin_required
def update_status(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    new_status = request.form.get('status')
    note = request.form.get('note', 'No note provided.')
    old_status = issue.status
    
    if new_status in ['Submitted', 'Under Review', 'In Progress', 'Resolved', 'Rejected']:
        # Update the issue status
        issue.status = new_status
        
        # Log the status update with the note
        status_log = StatusUpdate(
            issue_id=issue_id,
            updated_by=current_user.user_id,
            old_status=old_status,
            new_status=new_status,
            note=note
        )
        db.session.add(status_log)
        db.session.commit()
        flash(f'Status for issue #{issue_id} updated to {new_status}', 'success')
        
    return redirect(url_for('admin_dashboard'))

def seed_db():
    # Only seed if categories are empty
    if Category.query.first() is None:
        cats = ['Pothole', 'Street Light', 'Waste', 'Graffiti', 'Water/Sewage', 'Other']
        for cat_name in cats:
            db.session.add(Category(name=cat_name))
        
        # Create a default user if none exists
        if User.query.first() is None:
            default_user = User(name='Test Resident', email='resident@example.com', role='resident')
            db.session.add(default_user)
            
        db.session.commit()
        print("Database seeded with default values.")

if __name__ == '__main__':
    # Use a try-except block to handle connection errors gracefully
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            # Check if we can connect
            db.engine.connect()
            print("Successfully connected to the database!")
        except Exception as e:
            print(f"Warning: Could not connect to database. Make sure your credentials in .env are correct. Error: {e}")
            
    app.run(debug=True, port=5000)
