from app import app, db, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import relationship



@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))

class User(db.Model, UserMixin):
   id = db.Column(db.Integer, primary_key = True)
   first_name = db.Column(db.String(50), nullable = False)
   last_name = db.Column(db.String(50), nullable = False)
   email = db.Column(db.String(120), nullable = False, unique = True)
   phone_number = db.Column(db.String(20), nullable = False)
   password = db.Column(db.String(80), nullable = False)
   email_confirm = db.Column(db.Boolean, default = False, index=True)

   def __repr__(self):
      return f"User('{self.first_name}'),User('{self.last_name}'), User('{self.email}'),  User('{self.phone_number}')"

with app.app_context():
    db.create_all()
