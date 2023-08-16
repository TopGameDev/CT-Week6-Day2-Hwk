from app import app, db
from flask import render_template, redirect, url_for
from app.forms import AddInfoForm
from app.models import User



# Add a route

@app.route('/')
def index():
    images = ['https://www.hollywoodreporter.com/wp-content/uploads/2015/10/mcdwiwo_ec022_h.jpg?w=2000&h=1126&crop=1', 'https://cdn.vox-cdn.com/thumbor/r5QXLu7kIMTjzCCxruHGeKCQTgg=/0x0:1440x900/920x0/filters:focal(0x0:1440x900):format(webp):no_upscale()/cdn.vox-cdn.com/uploads/chorus_asset/file/6194665/toothsome3.0.jpg']
    return render_template('index.html', images=images)

@app.route('/phoneform', methods=['GET', "POST"])
def phone():
    form = AddInfoForm()
    if form.validate_on_submit():
        # Get the data from the form
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone_number = form.phone_number.data
        address = form.address.data

        #Check user table to see if there are any users with username or email
        check_user = db.session.execute(db.select(User).where((User.phone_number==phone_number) | (User.address==address))).scalar()
        if check_user:
            print('A user with that Phone number or Address already exists')
            return redirect((url_for('phone')))
        
        # Create a new instance of the User class with the data from form
        new_user = User(first_name=first_name, last_name=last_name, phone_number=phone_number, address=address)

        # Add the new_user objects to the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the homepage
        return redirect(url_for('index'))

    return render_template('phoneform.html', form=form)