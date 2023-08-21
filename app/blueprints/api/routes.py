from . import api
from app import db
from app.models import Contact, User
from flask import request
from .auth import basic_auth, token_auth


@api.route('/user')
def get_users():
    users = db.session.execute(db.select(User)).scalars().all()
    return [user.to_dict() for user in users]

@api.route('/user/<user_id>')
def get_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        return user.to_dict()
    else:
        {'error': f'User with an ID of {user_id} does not exist.'}, 404

@api.route('/user', methods=['POST'])
def create_user():
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json
    # Validate incoming data
    required_fields = ['first_name', 'last_name', 'email', 'username', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Get the data from the body
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    # Create a new User instance with the data
    new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
    # add to the database
    db.session.add(new_user)
    db.session.commit()

    return new_user.to_dict()


@api.route('/token')
@basic_auth.login_required
def get_token():
    auth_user = basic_auth.current_user()
    token = auth_user.get_token()
    return {
        'token': token,
        'token_expiration': auth_user.token_expiration
    }

@api.route('/contacts')
def get_contacts():
    contacts = db.session.execute(db.select(Contact)).scalars().all()
    return [contact.to_dict() for contact in contacts]

@api.route('/contacts/<contact_id>')
def get_contact(contact_id):
    contact = db.session.get(Contact, contact_id)
    if contact:
        return contact.to_dict()
    else:
        return {'error': f'Post with an ID of {contact_id} does not exist.'}, 404

@api.route('/contacts', methods=["POST"])
@token_auth.login_required
def create_contact():
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the data from the request body (Postman)
    data = request.json
    # Validate incoming data
    required_fields = ['first_name', 'last_name', 'phone_number', 'address']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Get the data from the body
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    address = data.get('address')

    # Make sure user is a authorized user
    current_user = token_auth.current_user()
    # Create a new post instance with the data
    new_contact = Contact(first_name=first_name, last_name=last_name, phone_number=phone_number, address=address, user_id=current_user.id)
    # add to the database
    db.session.add(new_contact)
    db.session.commit()

    return new_contact.to_dict(), 201

@api.route('/contacts/<contact_id>', methods=['PUT'])
@token_auth.login_required
def edit_contact(contact_id):
    # Check to make sure there is a JSON request body
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the post from the db
    contact = db.session.get(Contact, contact_id)
    if contact is None:
        return {'error': f"Contact with an ID of {contact_id} not found"}, 404
    # Make sure post authenticated user is the post author
    current_user = token_auth.current_user()
    if contact.author != current_user:
        return {'error': 'You do not have permission to edit this post'}, 403
    # Get the data from the request body (Postman)
    data = request.json
    # Update the post with changes
    for field in data:
        if field in {'first_name', 'last_name', 'phone_number', 'address'}:
            setattr(contact, field, data[field])
    db.session.commit()
    return contact.to_dict()

@api.route('/contacts/<contact_id>', methods=['DELETE'])
@token_auth.login_required
def delete_contact(contact_id):
    # Get the post from the db
    contact = db.session.get(Contact, contact_id)
    if contact is None:
        return {'error': f'Contact with an ID of {contact_id} does not exist!'}, 404
    # Make sure contact authenticated user is the contact author
    current_user = token_auth.current_user()
    if contact.author != current_user:
        return {'error': 'You do not have permission to delete this post'}, 403
    # Delete Post
    db.session.delete(contact)
    db.session.commit()
    return {'success': f"({contact.first_name} {contact.last_name}) has been deleted!"}

@api.route('/user/me')
@token_auth.login_required
def get_me():
    me = token_auth.current_user()
    return me.to_dict()