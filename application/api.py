from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request

from application.models import *
from application.validation import *
from application.myfunctions import getcurrentformatteddatetime, validPassword

user_output = {
    "user_id" : fields.Integer,
    "username" : fields.String,
    "fullname": fields.String(attribute="name"),
    "email" : fields.String,
    "mobile_number" : fields.Integer,
    "no_of_posts" : fields.Integer,
    "followers" : fields.Integer,
    "following" : fields.Integer
}

update_user_output = {
    "user_id" : fields.Integer,
    "username" : fields.String,
    "fullname": fields.String(attribute="name"),
    "email" : fields.String,
    "mobile_number" : fields.Integer
}

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument("email")
create_user_parser.add_argument("mobile_number")
create_user_parser.add_argument("full_name")
create_user_parser.add_argument("username")
create_user_parser.add_argument("password")

update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument("email")
update_user_parser.add_argument("mobile_number")
update_user_parser.add_argument("full_name")

blog_output = {
    "user_id" : fields.Integer,
    "username" : fields.String,
    "blog_id" : fields.Integer(attribute="post_id"),
    "blog_name" : fields.String(attribute="post_name"),
    "blog_caption" : fields.String(attribute="post_caption"),
    "is_archive": fields.Boolean(attribute="isArchive")
}

create_blog_parser = reqparse.RequestParser()
create_blog_parser.add_argument("blog_name")
create_blog_parser.add_argument("blog_caption")
create_blog_parser.add_argument("blog_image")

update_blog_parser = reqparse.RequestParser()
update_blog_parser.add_argument("blog_name")
update_blog_parser.add_argument("blog_caption")

class User_Data():
    def __init__(self, user_id, username, name, email, mobile_number, no_of_posts, followers, following):
        self.user_id = user_id
        self.username = username
        self.name = name
        self.email = email
        self.mobile_number = mobile_number
        self.no_of_posts = no_of_posts
        self.followers = followers
        self.following = following

class UserAPI(Resource):
    @marshal_with(user_output)
    def get(self):
        args = request.args
        username = args['username']
        password = args['password']
        
        user = User.query.filter_by(username = username).first()
        if user:
            if user.password == password:
                posts_count = UserPosts.query.filter_by(user_id = user.user_id).count()
                follower_count = Followers_List.query.filter_by(user_id = user.user_id).count()
                following_count = Following_List.query.filter_by(user_id = user.user_id).count()

                user_data = User_Data(user.user_id, user.username, user.name, user.email, user.mobile_number, 
                                posts_count, follower_count, following_count)

                return user_data
            else:
                raise InvalidCredentials(status_code=410)
                
        else:
            raise NotFoundError(status_code=404)

        
    @marshal_with(update_user_output)
    def put(self, username):

        args = update_user_parser.parse_args()
        email = args.get("email", None)
        mobile_number = args.get("mobile_number", None)
        full_name = args.get("full_name", None)

        # email = request.form.get('email')
        # mobile_number = request.form.get('mobile_number')
        # full_name = request.form.get('full_name')

        user = User.query.filter_by(username = username).first()
        if user is None:
            raise NotFoundError(status_code=404)

        if email is None or email == "":
            raise BusinessValidationError(status_code=400, error_code = "BE1001", error_message = "Email is required")
        
        if mobile_number is None or mobile_number == "":
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="Mobile Number is required")
        
        if full_name is None or full_name == "":
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="Full Name is required")

        if ('@' not in email) or (email[-4:] != ".com" and email[-6:]!=".co.in"):
            raise BusinessValidationError(status_code=400, error_code="BE1006", error_message="Invalid Email")
        
        if len(str(mobile_number))!=10:
            raise BusinessValidationError(status_code=400, error_code="BE1007", error_message="Invalid Mobile Number")

        duplicate_user  = User.query.filter_by(email = email).first()
        if duplicate_user!=None and duplicate_user.username != username:
            raise BusinessValidationError(status_code=400, error_code="BE1010", error_message="Duplicate Email")
        
        duplicate_user  = User.query.filter_by(mobile_number = mobile_number).first()
        if duplicate_user!=None and duplicate_user.username != username:
            raise BusinessValidationError(status_code=400, error_code="BE1011", error_message="Duplicate Mobile Number")

        try:
            user = User.query.filter_by(username = username).first()
            if user is None:
                raise NotFoundError(status_code=404)
            
            user.email = email
            user.mobile_number = mobile_number
            user.name = full_name
            user.updated_date = getcurrentformatteddatetime()

            db.session.commit()

            return user 

        except Exception as e:
            return "Oops! There's an error. Could not update the user.", 500 
        

    def delete(self, username):
        user = User.query.filter_by(username = username).first()
        if user:
            try:
                profile_pic = ProfilePics.query.filter_by(user_id = user.user_id).first()
                if profile_pic:
                    db.session.delete(profile_pic)
                
                following_list = Following_List.query.filter((Following_List.user_id == user.user_id)|(Following_List.following_id == user.user_id)).all()
                if len(following_list)>0:
                    for following in following_list:
                        db.session.delete(following)
                
                followers_list = Followers_List.query.filter((Followers_List.user_id == user.user_id)|(Followers_List.follower_id == user.user_id)).all()
                if len(followers_list) > 0:
                    for follower in followers_list:
                        db.session.delete(follower)
                
                posts = UserPosts.query.filter_by(user_id = user.user_id).all()
                if len(posts) > 0:
                    for post in posts:
                        db.session.delete(post)

                db.session.delete(user)
                db.session.commit()
                
                return 'Successfully deleted user and user data.', 200
            except Exception as e:
                return "Oops! There's an error. Could not delete the user.", 500
        else:
            raise NotFoundError(status_code=404)


    def post(self):
        # args = create_user_parser.parse_args()
        # email = args.get("email", None)
        # mobile_number = args.get("mobile_number", None)
        # full_name = args.get("full_name", None)
        # username = args.get("username", None)
        # password = args.get("password", None)

        email = request.form.get('email')
        mobile_number = request.form.get('mobile_number')
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')



        if email is None or email == "":
            raise BusinessValidationError(status_code=400, error_code = "BE1001", error_message = "Email is required")
        
        if mobile_number is None or mobile_number == "":
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="Mobile Number is required")
        
        if full_name is None or full_name == "":
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="Full Name is required")
        
        if username is None or username == "":
            raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="Username is required")
        
        if password is None or password == "":
            raise BusinessValidationError(status_code=400, error_code="BE1005", error_message="Password is required")
        
        if ('@' not in email) or (email[-4:] != ".com" and email[-6:]!=".co.in"):
            raise BusinessValidationError(status_code=400, error_code="BE1006", error_message="Invalid Email")
        
        if len(str(mobile_number))!=10:
            raise BusinessValidationError(status_code=400, error_code="BE1007", error_message="Invalid Mobile Number")
        
        if not validPassword(password):
            raise BusinessValidationError(status_code=400, error_code="BE1008", error_message="Password must have 8-16 characters, a capital letter, small letter, number & special character[!@#$%_]")
        
        duplicate_user = User.query.filter((User.email == email) | (User.mobile_number == mobile_number) | (User.username == username)).first()
        if duplicate_user:
            raise BusinessValidationError(status_code=400, error_code="BE1009", error_message="User already exists.")
        
        try:
            created_date = getcurrentformatteddatetime()
            new_user = User(email = email, mobile_number = mobile_number, name = full_name, username = username, 
                            password = password, created_date = created_date, updated_date = created_date)
            db.session.add(new_user)
            db.session.commit()

        except Exception as e:
            return "Oops! There's an error. Could not register the user.", 500
        else:
            return "User registered successfully", 200

class BlogAPI(Resource):

    @marshal_with(blog_output)
    def get(self, post_id):

        userblog = db.session.query(UserPosts).join(User).filter((UserPosts.post_id == post_id) & (User.user_id == UserPosts.user_id)).first()

        if userblog:
            return userblog

        else:
            raise BlogNotFoundError(status_code=404) 
        
    @marshal_with(blog_output)
    def put(self, post_id):
        
        blog = UserPosts.query.filter_by(post_id = post_id).first()

        if blog is None:
            raise BlogNotFoundError(status_code=404)
        
        try:
            args = update_blog_parser.parse_args()
            blog_name = args.get("blog_name", None)
            blog_caption = args.get("blog_caption", None)

            if blog_name:
                blog.post_name = blog_name
            
            if blog_caption:
                blog.post_caption = blog_caption
            
            
            blog.updated_date = getcurrentformatteddatetime()

            db.session.commit()

            return blog

        except Exception as e:
            print(e)
            return "Oops! There's an error. Could not update the blog.", 500


    def delete(self, post_id):
        
        blog = UserPosts.query.filter_by(post_id = post_id).first()

        if blog is None:
            raise BlogNotFoundError(status_code=404)

        try:
            db.session.delete(blog)
            db.session.commit()
        
        except Exception as e:
            return "Oops! There's an error. Could not delete the blog.", 500 

        else:
            return "Blog deleted successfully...", 200

    def post(self, username):
        try:
            args = create_blog_parser.parse_args()
            blog_name = args.get("blog_name", None)
            blog_caption = args.get("blog_caption", None)

            return {"username": username,
                    "blog_name": blog_name,
                    "blog_caption": blog_caption
                    }, 200
        except Exception as e:
            pass

class UserBlogAPI(Resource):
    @marshal_with(blog_output)
    def get(self, username):
        user = User.query.filter_by(username = username).first()

        if user is None:
            raise NotFoundError(status_code=404)
        
        blogs = UserPosts.query.filter_by(user_id = user.user_id).all()
        if len(blogs) == 0:
            raise NoBlogsForUser(status_code=400)
        else:
            return blogs