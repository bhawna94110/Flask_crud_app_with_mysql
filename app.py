from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_paginate import Pagination
import random
# from wtforms import validators
# from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import validates
import re


# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
# db = SQLAlchemy(app)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:[root]@localhost/uuid"
db = SQLAlchemy(app)


if __name__ == '__main__':
    app.run(debug=True)

class Employee(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(100), unique=False, nullable=False)
  last_name = db.Column(db.String(100), unique=False, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  mobile_no = db.Column(db.Integer)
  member_uuid = db.Column(db.Integer)

  def create(self):
    db.session.add(self)
    db.session.commit()
    return self

  def __repr__(self):
    return f'{self.id}'

with app.app_context():
  db.create_all()


#APIs
#Get single employee's information
@app.route('/user/<id>', methods=['GET'])
def get_item(id):
  item = Employee.query.get(id)
  del item.__dict__['_sa_instance_state']
  return jsonify(item.__dict__)


#Get all employee's information
@app.route('/users', methods=['GET'])
def get_items():
  page = request.args.get('page', 1, type=int)
  per_page = request.args.get('per_page', 1, type=int)
  items = Employee.query.paginate(page=page, per_page=per_page)
  data = []
  for i in items:
    data.append({
      'id': i.id,
      'first_name' : i.first_name,
      "last_name" : i.last_name,
      "email" : i.email,
      "mobile_no" : i.mobile_no,
      "member_uuid" : i.member_uuid
    })

  return jsonify({'data': data})


#Create employee with 6 digits random uuid 
@app.route('/user', methods=['POST'])
def create_item():
  body = request.get_json()
  if not re.match("[^@]+@[^@]+\.[^@]+", body['email']):
    return 'Provided email is not an email address'
  user_obj = Employee(
             first_name = body['first_name'],
             last_name = body['last_name'],
             email = body['email'],
             mobile_no = body['mobile_no'],
             member_uuid = random.randrange(111111, 999999, 6) 
  )
  db.session.add(user_obj)
  db.session.commit()
  return "item created"


#Update emolyee's detailes except email
@app.route('/user/<id>', methods=['PUT'])
def update_item(id):
  body = request.get_json()
  get_user = Employee.query.get(id)
  if body.get('first_name'):
    get_user.first_name = body['first_name']
  if body.get('last_name'):
    get_user.last_name = body['last_name']
  if body.get('mobile_no'):
    get_user.mobile_no = body['mobile_no']
  try:
    db.session.add(get_user)
    db.session.commit()
    return "item updated"
  except:
    return 'EMail can not be modified'


#Delete emloyee from database
@app.route('/user/<id>', methods=['DELETE'])
def delete_item(id):
  db.session.query(Employee).filter_by(id=id).delete()
  db.session.commit()
  return "item deleted"

# @app.errorhandler(HTTP_404_NOT_FOUND)
# def handle_404(e):
#   return jsonify({'error':'Page Not Found'}), HTTP_404_NOT_FOUND

# @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
# def handle_500(e):
#   return jsonify({'error':'Something went wrong.'}), HTTP_500_INTERNAL_SERVER_ERROR


  