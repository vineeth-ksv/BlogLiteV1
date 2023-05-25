from .database import db

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True)
    name = db.Column(db.String, nullable = False)
    username = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False, unique = True)
    mobile_number = db.Column(db.Integer, nullable = False, unique = True)
    created_date = db.Column(db.String, nullable = False)
    updated_date = db.Column(db.String, nullable = False)
    userposts = db.relationship('UserPosts', backref = 'user', lazy = True)
    profilepics = db.relationship('ProfilePics', backref = 'user', lazy = True)
    followers_list = db.relationship('Followers_List', backref = 'user', lazy = True)
    following_list = db.relationship('Following_List', backref = 'user', lazy = True)
    comments = db.relationship('Comments', backref='user', lazy = True)

class UserPosts(db.Model):
    __tablename__ = 'userposts'
    post_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable = False)
    username = db.Column(db.Text, nullable = False)
    post_img = db.Column(db.Text, nullable = False)
    img_filename = db.Column(db.Text, nullable = False)
    post_name = db.Column(db.Text, nullable = False)
    post_caption = db.Column(db.Text)
    mimetype = db.Column(db.Text, nullable = False)
    created_date = db.Column(db.Text, nullable = False)
    updated_date = db.Column(db.Text, nullable = False)
    isArchive = db.Column(db.Boolean, nullable = False, default = False)
    comments = db.relationship('Comments', backref='userposts', lazy = True)

class Comments(db.Model):
    __tablename__ = 'comments'
    comment_id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey("userposts.post_id"), nullable = False)
    text = db.Column(db.String, nullable = False)
    created_date = db.Column(db.String, nullable = False)

class ProfilePics(db.Model):
    __tablename__ = 'profilepics'
    profilepic_id = db.Column(db.Integer, primary_key=True, autoincrement = True, unique = True, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable = False)
    profilepic_name = db.Column(db.Text, nullable=False)
    profilepic_data = db.Column(db.LargeBinary, nullable=False)
    mimetype = db.Column(db.String, nullable=False)

class Followers_List(db.Model):
    __tablename__ = 'followers_list'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable = False)
    follower_id = db.Column(db.Integer, nullable = False)

class Following_List(db.Model):
    __tablename__ = 'following_list'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable = False)
    following_id = db.Column(db.Integer, nullable = False)
