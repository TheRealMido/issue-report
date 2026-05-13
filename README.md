# Issue Reporter

A modern web application for residents to report and track local issues like potholes, street light failures, and more.

## Features
- **User Authentication**: Secure login and registration.
- **Issue Submission**: Report issues with category and location.
- **Voting System**: Upvote important issues to increase visibility.
- **Admin Dashboard**: Manage and update issue status with notes.
- **User Profile**: Track your reported issues and their status.

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: MySQL (SQLAlchemy)
- **Frontend**: HTML5, CSS3, JavaScript

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- MySQL Server

### 2. Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/TheRealMido/issue-report.git
   cd issue-report
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Database Setup
1. Create a MySQL database named `issue_reporter`.
2. Create a `.env` file in the root directory (use `.env.example` as a template):
   ```env
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_NAME=issue_reporter
   ```

### 4. Running the App
```bash
python app.py
```
The application will be available at `http://127.0.0.1:5000`.

## License
MIT
