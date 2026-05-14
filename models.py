from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    RESIDENT = 'resident'
    ADMIN = 'admin'

class IssueStatus(Enum):
    SUBMITTED = 'Submitted'
    UNDER_REVIEW = 'Under Review'
    IN_PROGRESS = 'In Progress'
    RESOLVED = 'Resolved'
    REJECTED = 'Rejected'

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum('resident', 'admin', name='user_roles'), nullable=False, default='resident')

    def get_id(self):
        return str(self.user_id)

class Category(db.Model):
    __tablename__ = 'Categories'
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Issue(db.Model):
    __tablename__ = 'Issues'
    issue_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('Categories.category_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    location = db.Column(db.String(100))
    status = db.Column(db.Enum('Submitted', 'Under Review', 'In Progress', 'Resolved', 'Rejected', name='issue_statuses'), default='Submitted')
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='issues')
    category = db.relationship('Category', backref='issues')
    votes = db.relationship('Vote', backref='issue', lazy=True, cascade="all, delete-orphan")

class StatusUpdate(db.Model):
    __tablename__ = 'Status_Updates'
    update_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('Issues.issue_id', ondelete='CASCADE'))
    updated_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    note = db.Column(db.Text)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)

class Vote(db.Model):
    __tablename__ = 'Votes'
    vote_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete='CASCADE'))
    issue_id = db.Column(db.Integer, db.ForeignKey('Issues.issue_id', ondelete='CASCADE'))
    
    # Relationships
    user = db.relationship('User', backref='user_votes', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'issue_id', name='unique_vote'),)
