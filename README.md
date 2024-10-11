A web-based Helpdesk system built with Flask that allows organizations to efficiently manage support tickets within various projects. The application features user authentication with role-based access, project management, and ticket tracking functionalities.

Table of Contents
Features
Technologies Used
Prerequisites
Installation
Configuration
Database Setup
Running the Application
Deployment on AWS Lightsail
Usage
Contributing
License
Contact
Features
User Authentication:

Secure login system with role-based access (Admin and Regular User).
Predefined admin and user accounts accessible via navbar buttons.
Project Management:

Admins can create, view, and manage projects.
Users can view projects they are assigned to.
Ticket Management:

Create, view, edit, and delete support tickets within projects.
Users assigned to a project can manage tickets within that project.
Navigation:

Intuitive navigation buttons to move between tickets, projects, and the project list.
Responsive Design:

User-friendly interface built with Bootstrap for compatibility across devices.
Technologies Used
Backend:

Python 3.x
Flask
Flask-Login
Flask-WTF
SQLAlchemy
Gunicorn
Frontend:

HTML5
CSS3 (Bootstrap)
Database:

SQLite (for development)


