# app/routes.py

from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, login_manager
from app.forms import RegistrationForm, LoginForm, TicketForm, ProjectForm, AssignUserForm, EmptyForm
from app.models import User, Ticket, Project
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# Handle unauthorized access
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Please log in to access this page.', 'info')
    return redirect(url_for('login', next=request.endpoint))

@app.route('/')
@app.route('/home')
@login_required
def home():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects)

# Registration route
# In app/routes.py, within the register route

# app/routes.py

@app.route('/register', methods=['GET', 'POST'])
# app/routes.py

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='pbkdf2:sha256'
        )
        user = User(
            username=form.username.data,
            password=hashed_password,
            role='regular'  # Enforce regular role
        )
        db.session.add(user)
        db.session.commit()
        flash('The account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You have been logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/login_as/<string:username>')
def login_as(username):
    if current_user.is_authenticated:
        logout_user()
    user = User.query.filter_by(username=username).first()
    if user:
        login_user(user)
        flash(f'Logged in as {username}', 'success')
        return redirect(url_for('home'))
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

@app.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        abort(403)  # Forbidden access
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='pbkdf2:sha256'
        )
        role = 'admin' if form.is_admin.data else 'regular'
        user = User(
            username=form.username.data,
            password=hashed_password,
            role=role
        )
        db.session.add(user)
        db.session.commit()
        flash(f"User '{user.username}' has been created successfully!", 'success')
        return redirect(url_for('home'))
    return render_template('create_user.html', title='Create User', form=form)

# Logout route
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Modify the new_ticket route
@app.route('/project/<int:project_id>/ticket/new', methods=['GET', 'POST'])
@login_required
def new_ticket(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user not in project.users and current_user.role != 'admin':
        abort(403)
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(
            subject=form.subject.data,
            description=form.description.data,
            status=form.status.data,
            author=current_user,
            project=project
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Your ticket has been created!', 'success')
        return redirect(url_for('project', project_id=project.id))
    return render_template(
        'create_ticket.html',
        form=form,
        legend='New Ticket',
        back_to_project_url=url_for('project', project_id=project.id)
    )

# Route to view a single ticket (requires login)
@app.route('/ticket/<int:ticket_id>')
@login_required
def ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    delete_ticket_form = EmptyForm()
    return render_template('ticket.html', ticket=ticket, delete_ticket_form=delete_ticket_form)

# app/routes.py

# Update the update_ticket route
@app.route('/ticket/<int:ticket_id>/update', methods=['GET', 'POST'])
@login_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    project = ticket.project
    if current_user not in project.users and current_user.role != 'admin':
        abort(403)
    form = TicketForm()
    if form.validate_on_submit():
        ticket.subject = form.subject.data
        ticket.description = form.description.data
        ticket.status = form.status.data
        db.session.commit()
        flash('Your ticket has been updated!', 'success')
        return redirect(url_for('ticket', ticket_id=ticket.id))
    elif request.method == 'GET':
        form.subject.data = ticket.subject
        form.description.data = ticket.description
        form.status.data = ticket.status
    return render_template('create_ticket.html', title='Update Ticket', form=form, legend='Update Ticket', project=project)

# Update the delete_ticket route
# app/routes.py

@app.route('/ticket/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    delete_ticket_form = EmptyForm()
    if delete_ticket_form.validate_on_submit():
        if current_user.role != 'admin' and ticket.author != current_user:
            abort(403)
        db.session.delete(ticket)
        db.session.commit()
        flash('The ticket has been deleted.', 'success')
        return redirect(url_for('project', project_id=ticket.project_id))
    else:
        abort(400)


# Route to create a new project (admin only)
@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def create_project():
    if current_user.role != 'admin':
        abort(403)
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(name=form.name.data, description=form.description.data)
        db.session.add(project)
        db.session.commit()
        flash('New project has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_project.html', form=form, legend='Create New Project')

# Route to view a single project and its tickets
@app.route('/project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def project(project_id):
    project = Project.query.get_or_404(project_id)
    tickets = Ticket.query.filter_by(project_id=project.id).all()
    assign_user_form = AssignUserForm()
    form = EmptyForm()
    delete_project_form = EmptyForm()

    if assign_user_form.validate_on_submit():
        if current_user.role != 'admin':
            abort(403)
        username = assign_user_form.username.data.strip()
        user = User.query.filter_by(username=username).first()
        if user:
            if user in project.users:
                flash(f'User {username} is already assigned to this project.', 'info')
            else:
                project.users.append(user)
                db.session.commit()
                flash(f'User {username} has been assigned to the project.', 'success')
        else:
            flash(f'User {username} does not exist.', 'danger')
        return redirect(url_for('project', project_id=project.id))

    return render_template(
        'project.html',
        project=project,
        tickets=tickets,
        assign_user_form=assign_user_form,
        form=form,
        delete_project_form=delete_project_form
    )

@app.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    delete_project_form = EmptyForm()
    if delete_project_form.validate_on_submit():
        if current_user.role != 'admin':
            abort(403)
        db.session.delete(project)
        db.session.commit()
        flash('The project has been deleted.', 'success')
        return redirect(url_for('home'))
    else:
        abort(400)

@app.route('/project/<int:project_id>/remove_user/<int:user_id>', methods=['POST'])
@login_required
def remove_user(project_id, user_id):
    project = Project.query.get_or_404(project_id)
    if current_user.role != 'admin':
        abort(403)
    user = User.query.get_or_404(user_id)
    if user in project.users:
        project.users.remove(user)
        db.session.commit()
        flash(f'User {user.username} has been removed from the project.', 'success')
    else:
        flash(f'User {user.username} is not assigned to this project.', 'info')
    return redirect(url_for('project', project_id=project.id))


# Error handler for 403 Forbidden
@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

