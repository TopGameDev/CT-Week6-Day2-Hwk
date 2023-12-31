from app import app, db
from flask import render_template, redirect, url_for, flash
from app.forms import AddInfoForm, SignUpForm, LoginForm
from app.models import Contact, User
from flask_login import login_user, logout_user, login_required, current_user



# Add a route
@app.route('/')
def index():
    images = ['https://www.hollywoodreporter.com/wp-content/uploads/2015/10/mcdwiwo_ec022_h.jpg?w=2000&h=1126&crop=1', 'https://cdn.vox-cdn.com/thumbor/r5QXLu7kIMTjzCCxruHGeKCQTgg=/0x0:1440x900/920x0/filters:focal(0x0:1440x900):format(webp):no_upscale()/cdn.vox-cdn.com/uploads/chorus_asset/file/6194665/toothsome3.0.jpg']
    return render_template('index.html', images=images)

@app.route('/contacts')
@login_required
def contacts():
    contacts = db.session.execute(db.select(Contact).where(Contact.user_id==current_user.id).order_by(Contact.date_time.desc())).scalars().all()
    return render_template('contacts.html', contacts=contacts)

# Make a route that takes in the ID of the post
@app.route('/contacts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    # Query the database to find the single post by its ID
    contact = db.session.execute(db.select(Contact).where(Contact.id==id)).scalar()
    # Create an instance of the AddInfoForm so we can make changes through the form
    form = AddInfoForm()
    # Check if user has pressed submit
    if form.validate_on_submit():
        # Update the content in the database with the data I input in each form field
        contact.first_name = form.first_name.data
        contact.last_name = form.last_name.data
        contact.phone_number = form.phone_number.data
        contact.address = form.address.data
        # Add to Database
        db.session.add(contact)
        # Update Database
        db.session.commit()
        # Send Flash Message
        flash("Contact has been updated", 'success')
        # Redirect back to contacts page.
        return redirect(url_for('contacts', id=contact.id))
    # Pre-Fillout Form Fields with unchanged data from the database
    form.first_name.data = contact.first_name
    form.last_name.data = contact.last_name
    form.phone_number.data = contact.phone_number
    form.address.data = contact.address
    return render_template('contact.html', form=form)

@app.route('/contacts/delete/<int:id>', methods=['GET', 'DELETE'])
@login_required
def delete_contact(id):
    # Query the database to find the Contact by its ID
    contact = db.session.execute(db.select(Contact).where(Contact.id==id)).scalar()
    # Delete the contact by ID from the database
    db.session.delete(contact)
    # Update Database
    db.session.commit()
    # Send Flash Message
    flash(f'{contact.first_name} {contact.last_name} has been deleted!', 'success')
    # Redirect back to Contacts page
    return redirect(url_for('contacts'))

@app.route('/signup', methods=['GET', "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        # Get the data from the form
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data

        #Check user table to see if there are any users with username or email
        check_user = db.session.execute(db.select(User).where((User.username==username) | (User.email==email))).scalar()
        if check_user:
            flash('A user with that username and/or email already exists', 'warning')
            return redirect(url_for('signup'))
        
        # Create a new instance of the User class with the data from form
        new_user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password)

        # Add the new_user objects to the database
        db.session.add(new_user)
        db.session.commit()
        flash(f"{new_user.username} has been created", 'success')

        # log the user in
        login_user(new_user)

        # Redirect to the homepage
        return redirect(url_for('index'))
    elif form.is_submitted():
        flash("Your Passwords do not match", 'warning')
        return redirect(url_for('signup'))
    
    return render_template('signup.html', form=form)
            


@app.route('/phoneform', methods=['GET', "POST"])
@login_required
def phone():
    form = AddInfoForm()
    if form.validate_on_submit():
        # Get the data from the form
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone_number = form.phone_number.data
        address = form.address.data
        
        # Create a new instance of the User class with the data from form
        new_contact = Contact(first_name=first_name, last_name=last_name, phone_number=phone_number, address=address, user_id=current_user.id)

        # Add the new_user objects to the database
        db.session.add(new_contact)
        db.session.commit()
        flash(f"{new_contact.first_name} has been added to your contacts! ", 'success')
        flash(f"Another ticket has been added to your total SWEEPSTAKES tickets!! ", 'success')

        # Redirect to the homepage
        return redirect(url_for('index'))

    return render_template('phoneform.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have successfully logged out", 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Query the User Table for a user with that username
        user = db.session.execute(db.select(User).where(User.username==username)).scalar()
        # If we have a user AND the password is correct for that user
        if user is not None and user.check_password(password):
            # log the user in via login_user function
            login_user(user)
            flash("You have successfully logged in", 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid Username and/or Password', 'danger')
            return redirect(url_for('login'))
        
    return render_template('login.html', form=form)