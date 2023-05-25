from flask import request, session, redirect, url_for, g, send_file, flash, abort, jsonify
from flask import render_template
from flask import current_app as app

from datetime import datetime
from werkzeug.utils import secure_filename
from io import BytesIO

from application.models import *
from application.myfunctions import *


@app.route("/", methods=["GET"])
def index():
    if 'user' in session:
        return redirect(url_for("home"))
    
    return render_template('index.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.pop('user', None)
        
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username = username).first()
        
        if user == None:
            flash("Incorrect username or username does not exist.", 'error')
            return redirect(url_for("login"))
        
        else:
            if user.password == password:
                session['user'] = request.form['username']
                session['fullname'] = user.name
                
                return redirect(url_for("home"))
            
            else:
                flash("Invalid Password. Please enter valid username and password to login", 'error')
                return render_template('index.html', formdata = request.form)
    else:
        if 'user' in session:
            return redirect(url_for("home"))
        
        return redirect(url_for("index"))


@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if request.method=="GET":
        # return render_template("register_user.html")
        return render_template('signup.html')

    elif request.method == "POST":
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mobile_number = request.form['mobile_number']

        created_date = getcurrentformatteddatetime()
        session['formdata'] = request.form

        user = User.query.filter_by(username = username).filter_by(email = email).filter_by(mobile_number = mobile_number).first()
        if user:
            flash('User already exists. Please to Login to your existing account','error')
            return render_template('signup.html')

        user = User.query.filter_by(username = username).first()
        if user:
            flash('username is already registered with another account. Please use another username to register new account.', 'error')
            return render_template('signup.html', formdata = session['formdata'])

        user = User.query.filter_by(mobile_number = mobile_number).first()
        if user:
            flash('Mobile Number is already registered with an account. Please use another mobile number to register new account.', 'error')
            return render_template('signup.html', formdata = session['formdata'])
        
        user = User.query.filter_by(email = email).first()
        if user:
            flash('Email is already registered with another account. Please use another E-mail to register new account.', 'error')
            return render_template('signup.html', formdata = session['formdata'])
    
        try:
            new_user = User(name = name, username = username, password = password, email = email, mobile_number = mobile_number, 
                                created_date = created_date, updated_date = created_date)
            db.session.add(new_user)
            db.session.commit()
        
        except Exception as e:
            flash('Sorry! Could not register the user. Please try again later.', 'error')
            return render_template('signup.html', formdata = session['formdata'])
            
        else:
            flash("User registered successfully.", 'success')
            session['user'] = username
            session['fullname'] = name
        
        return redirect(url_for("home"))

@app.route('/home', methods=["GET"])
def home():
    if not g.user:
        return redirect(url_for('session_expired'))
    
    username = session['user']
    user = User.query.filter_by(username = username).first()
    profilepic = ProfilePics.query.filter_by(user_id = user.user_id).first()
    if not profilepic:
        session['default_profilepic'] = True
    following_list = Following_List.query.filter_by(user_id = user.user_id).all()
    
    feed = []
    if following_list!=[]:

        following_ids = [user.user_id]
        for following in following_list:
            following_ids.append(following.following_id)
        
        
        posts = UserPosts.query.filter(UserPosts.user_id.in_(following_ids)).filter_by(isArchive = False).order_by(UserPosts.updated_date.desc()).all()
        feed = posts
        # for id in following_ids:
        #     posts = UserPosts.query.filter_by(user_id = id).order_by(UserPosts.created_date.desc()).all()
        #     posts = UserPosts.filter(UserPosts.user_id.in_(following_ids)).all()
        #     feed.append(posts)
    else:
        posts = UserPosts.query.filter_by(user_id = user.user_id).filter_by(isArchive = False).order_by(UserPosts.updated_date.desc()).all()
        feed = posts

    return render_template("home.html", username = username, name = session['fullname'], feed = feed)
    

@app.route('/view_profile/<temp_username>')
def view_profile(temp_username):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    if temp_username == session['user']:
        return redirect(url_for('profile', username = session['user']))
    
    user = User.query.filter_by(username = session['user']).first()
    temp_user = User.query.filter_by(username = temp_username).first()
    temp_profilepic = ProfilePics.query.filter_by(user_id = temp_user.user_id).first()
    temp_followers_list = Followers_List.query.filter_by(user_id = temp_user.user_id).all()
    temp_following_list = Following_List.query.filter_by(user_id = temp_user.user_id).all()
    temp_posts = UserPosts.query.filter_by(user_id = temp_user.user_id).filter_by(isArchive = False).all()

    if temp_profilepic:
            default_profilepic = False
    else:
            default_profilepic = True
    
    following = False
    for follower in temp_followers_list:
        if follower.follower_id == user.user_id:
            following = True
            break

    return render_template('view_profile.html', temp_user = temp_user, default_profilepic = default_profilepic, following = following,
                            temp_posts = temp_posts, temp_followers_count = len(temp_followers_list), 
                            temp_following_count = len(temp_following_list), username = session['user'], name = session['fullname'])

@app.route('/search', methods=["GET", "POST"])
def search():
    if not g.user:
        return redirect(url_for('session_expired'))
    
    if request.method == "GET":
        return render_template('search.html', name = session['fullname'], username = session['user'])
    
    elif request.method == "POST":
        search_word = request.form.get('query')

        if search_word == None:
            search_users, following = [], []
            
        else:
            search = "%{}%".format(search_word)
            search_users = User.query.filter(User.username.like(search)).all()
            
            user = User.query.filter_by(username = session['user']).first()
            following_list = Following_List.query.filter_by(user_id = user.user_id).all()
            
            following = [row.following_id for row in following_list]
    
        return jsonify({'htmlresponse': render_template('search_response.html', users = search_users, following = following)})


@app.route('/myprofile/<username>', methods=["GET"])
def profile(username):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    if request.method == "GET":
        user = User.query.filter_by(username = username).first()
        profilepic = ProfilePics.query.filter_by(user_id = user.user_id).first()
        posts = UserPosts.query.filter_by(user_id = user.user_id).filter_by(isArchive = False).all()
        followers_list = Followers_List.query.filter_by(user_id = user.user_id).all()
        following_list = Following_List.query.filter_by(user_id = user.user_id).all()

        if profilepic:
            default_profilepic = False
        else:
            default_profilepic = True

        return render_template('profile.html', username = username, default_profilepic = default_profilepic, posts = posts, 
                                followers_count = len(followers_list), following_count = len(following_list), name = session['fullname'])


@app.route('/<username>/addpost', methods = ['GET', 'POST'])
def addpost(username):
    if not g.user:
        return redirect(url_for('session_expired'))

    if request.method == "GET":
        return render_template("addpost.html", username = username, name = session['fullname'])
    
    elif request.method == "POST":
        postname = request.form['postname']
        postcaption = request.form['postcaption']
        postimage = request.files['postimage']

        if not postname:
            return 'No Post Name Entered', 400
        
        if not postimage:
            return 'No Pic uploaded', 400
        
        if not allowed_file(postimage.filename):
            flash("Invalid Image Type", 'danger')
            return redirect(url_for('addpost', username = username))
        
        img_filename = secure_filename(postimage.filename)
        mimetype = postimage.mimetype
        created_date = getcurrentformatteddatetime()

        user = User.query.filter_by(username = username).first()

        try:
            post = UserPosts(user_id = user.user_id, username = username, post_img = postimage.read(), img_filename = img_filename, 
                            post_name = postname, post_caption = postcaption, mimetype = mimetype, created_date = created_date, 
                            updated_date = created_date)

            db.session.add(post)
            db.session.commit()

        except Exception as e:
            db.session.commit()
            flash("Sorry! Couldn't Upload Post. Please try later.", "danger")

        else:
            flash("Post Uploaded Successfully...", 'success')
        
        return redirect(url_for('profile', username = username))


@app.route('/<username>/view_post/<post_id>', methods = ["GET"])
def view_post(username, post_id):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    # user = User.query.filter_by(username = username).first()
    post = UserPosts.query.filter_by(post_id = post_id).first()
    return render_template('view_post.html', username = username, name = session['fullname'], post = post)

@app.route('/<username>/edit_post/<post_id>', methods=["GET", "POST"])
def edit_post(username, post_id):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    if request.method == "GET":
        post = UserPosts.query.filter_by(post_id = post_id).first()

        return render_template('edit_post.html', username = username, name = session['fullname'], post = post)
    
    elif request.method == "POST":

        postname = request.form['postname']
        postcaption = request.form['postcaption']
        postimage = request.files['postimage']
        img_filename = secure_filename(postimage.filename)

        try:

            post = UserPosts.query.filter_by(post_id = post_id).first()

            if postname!="" and postname != post.post_name:
                post.post_name = postname
            
            if postcaption != post.post_caption:
                post.post_caption = postcaption
            
            if img_filename!='':
                post.post_img = postimage.read()
                post.img_filename = img_filename
                post.mimetype = postimage.mimetype
                post.updated_date = getcurrentformatteddatetime()
            
            db.session.commit()
        
        except Exception as e:
            db.session.commit()
            flash("Sorry! Couldn't update the post. Please try later...", 'danger')
        
        else:
            flash("Post updated successfully", 'success')

        return redirect(url_for('view_post', username = username, post_id = post_id))


@app.route('/<username>/delete_post/<post_id>')
def delete_post(username, post_id):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    try:
        post = UserPosts.query.filter_by(post_id = post_id).first()
        for comment in post.comments:
            db.session.delete(comment)
        db.session.delete(post)
        db.session.commit()
    
    except Exception as e:
        db.session.commit()
        flash("Sorry! Couldn't delete the post. Please try later...", 'danger')
    
    else:
        flash("Post deleted successfully.", 'success')
    
    return redirect(url_for('profile', username = username))

@app.route('/<username>/archive_post/<post_id>')
def archive_post(username, post_id):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    try:
        post = UserPosts.query.filter_by(post_id = post_id).first()
        post.isArchive = True
        db.session.commit()
    
    except Exception as e:
        db.session.commit()
        flash("Sorry! Couldn't archive the post. Please try later...", 'danger')
    
    else:
        flash("Post Archived successfully.", 'success')
    
    return redirect(url_for('profile', username = username))


@app.route('/<username>/unarchive_post/<post_id>')
def unarchive_post(username, post_id):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    try:
        post = UserPosts.query.filter_by(post_id = post_id).first()
        post.isArchive = False
        db.session.commit()
    
    except Exception as e:
        db.session.commit()
        flash("Sorry! Couldn't make the post public. Please try later...", 'danger')
    
    else:
        flash("Your post is now public. It is visible to all your followers.", 'success')
    
    return redirect(url_for('profile', username = username))

@app.route('/myarchivedposts')
def view_archived_posts():
    if not g.user:
        return redirect(url_for('session_expired'))
    username = session['user']
    user = User.query.filter_by(username = username).first()
    myarchivedposts = UserPosts.query.filter_by(user_id = user.user_id).filter_by(isArchive = True).order_by(UserPosts.updated_date.desc()).all()
    
    return render_template('archived_posts.html', username = username, name = session['fullname'], myarchivedposts = myarchivedposts)


@app.route('/followers/<username>', methods=["GET"])
def view_followers(username):
    if not g.user:
        return redirect(url_for('session_expired'))

    if request.method == "GET":
        user = User.query.filter_by(username = username).first()
        followers = Followers_List.query.filter_by(user_id = user.user_id).all()

        followers_list = []
        for follower in followers:
            user = User.query.filter_by(user_id = follower.follower_id).first()
            followers_list.append(user)
        
        return render_template('view_followers.html', username = username, followers_list = followers_list, name = session['fullname'])
    

@app.route('/following/<username>', methods=["GET"])
def view_following(username):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    if request.method == "GET":
        user = User.query.filter_by(username = username).first()
        following = Following_List.query.filter_by(user_id = user.user_id).all()

        following_list = []
        for follow in following:
            user = User.query.filter_by(user_id = follow.following_id).first()
            following_list.append(user)

        return render_template('view_following.html', username = username, name = session['fullname'], following_list = following_list)


@app.route('/remove_follower/<username>/<remove_id>')
def remove_follower(username, remove_id):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    if request.method == "GET":
        try:
            user = User.query.filter_by(username = username).first()
            follower = Followers_List.query.filter_by(user_id = user.user_id).filter_by(follower_id = remove_id).first()
            following = Following_List.query.filter_by(user_id = remove_id).filter_by(following_id = user.user_id).first()
            
            db.session.delete(follower)
            db.session.delete(following)
            db.session.commit()

        except Exception as e:
            db.session.commit()
            flash("Sorry! Couldn't remove user. Please try later.", 'danger')
        
        else:
            flash("User removed from followers successfully..", 'success')
    
    return redirect(url_for('view_followers', username = username))

@app.route('/unfollow_user/<username>/<unfollow_id>')
def unfollow_user(username, unfollow_id):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    if request.method == "GET":
        user2 = User.query.filter_by(user_id = unfollow_id).first()
        try:
            user = User.query.filter_by(username = username).first()
            following = Following_List.query.filter_by(user_id = user.user_id).filter_by(following_id = unfollow_id).first()
            follower = Followers_List.query.filter_by(user_id = unfollow_id).filter_by(follower_id = user.user_id).first()
            
            db.session.delete(following)
            db.session.delete(follower)
            db.session.commit()
        
        except Exception as e:
            db.session.commit()
            flash("Sorry! Couldn't unfollow user. Please try later.", 'danger')

        else:
            flash("Unfollowed user successfully...", 'success')

    return redirect(url_for('view_profile', temp_username = user2.username))
    # return redirect(url_for('view_following', username = username))


@app.route('/follow_user/<username>/<follow_id>')
def follow_user(username, follow_id):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    if request.method == "GET":
        user2 = User.query.filter_by(user_id = follow_id).first()
        try:
            user = User.query.filter_by(username = username).first()

            following = Following_List(user_id = user.user_id, following_id = follow_id)
            follower = Followers_List(user_id = follow_id, follower_id = user.user_id)

            db.session.add(following)
            db.session.add(follower)
            db.session.commit()
        
        except Exception as e:
            db.session.commit()
            flash("Sorry! Couln't follow user. Please try later.", 'danger')
        
        else:
            flash("Following the user successfully.", 'success')
        
    return redirect(url_for('view_profile', temp_username = user2.username))


@app.route('/renderimage/<int:image_id>')
def renderimage(image_id):
    post = UserPosts.query.filter_by(post_id = image_id).first()
    return send_file(
        BytesIO(post.post_img),
        mimetype = post.mimetype,
        download_name = post.img_filename
    )


@app.route('/edit_profile/<username>', methods=['GET', 'POST'])
def edit_profile(username):
    if not g.user:
        return redirect(url_for('session_expired'))

    if request.method == 'GET':
        user = User.query.filter_by(username = username).first()
        profilepic = ProfilePics.query.filter_by(user_id = user.user_id).first()
        if profilepic:
            default_profilepic = False
        else:
            default_profilepic = True
        return render_template('edit_profile.html', username = username, user = user, default_profilepic = default_profilepic, name = session['fullname'])
    
    elif request.method == 'POST':

        updated_name = request.form['name']
        # updated_username = request.form['username']
        updated_email = request.form['email']
        updated_mobile_number = request.form['mobile_number']

        duplicate_user = User.query.filter((User.email == updated_email) & (User.username != username)).first()
        if duplicate_user:
            flash("Couldn't update the Email. Email is already registered with another user.", "warning")
            return redirect(url_for('profile', username = username))
        
        duplicate_user = User.query.filter((User.mobile_number == updated_mobile_number) & (User.username != username)).first()
        if duplicate_user:
            flash("Couldn't update the Mobile number. Mobile number is already registered with another user.", "warning")
            return redirect(url_for('profile', username = username))

        try:
            user = User.query.filter_by(username=username).first()

            user.name = updated_name
            # user.username = updated_username
            user.email = updated_email
            user.mobile_number = updated_mobile_number
            user.updated_date = getcurrentformatteddatetime()
            db.session.commit()
            session.pop('fullname', None)
            session['fullname'] = updated_name

        except Exception as e:
            db.session.commit()
            flash("Sorry...Couldn't Update the details. Please try later..!", "danger")
        else:
            flash('Profile Updated successfully', "success")
        
        return redirect(url_for('profile', username = username))

@app.route('/renderprofilepic/<username>')
def renderprofilepic(username):
    user = User.query.filter_by(username = username).first()
    profilepic = ProfilePics.query.filter_by(user_id = user.user_id).first()
    if profilepic:
        return send_file(
            BytesIO(profilepic.profilepic_data),
            mimetype = profilepic.mimetype,
            download_name = profilepic.profilepic_name
        )

@app.route('/uploadprofilepic/<username>', methods=['POST'])
def uploadprofilepic(username):
    if not g.user:
        return redirect(url_for('session_expired'))

    if request.method == "POST":

        try:
            user = User.query.filter_by(username = username).first()

            uploadedprofilepic = request.files['uploadedprofilepic']

            profilepic_name = secure_filename(uploadedprofilepic.filename)
            mimetype = uploadedprofilepic.mimetype

            profilepic = ProfilePics(user_id = user.user_id, profilepic_name = profilepic_name, 
                                        profilepic_data = uploadedprofilepic.read(), mimetype = mimetype)
            db.session.add(profilepic)
            db.session.commit()

            session['default_profilepic'] = False

        except Exception as e:
            db.session.commit()
            flash("Sorry...Couldn't Update the profile pic.\nPlease try later..!", "danger")
        
        else:
            flash("Profile Pic Uploaded Successfully...", "success")
        
        return redirect(url_for('profile', username = username))


@app.route('/updateprofilepic/<username>', methods=["POST"])
def updateprofilepic(username):
    if not g.user:
        return redirect(url_for('session_expired'))

    if request.method == "POST":
        try:
            user = User.query.filter_by(username = username).first()
            profilepic = ProfilePics.query.filter_by(user_id = user.user_id).first()

            uploadedprofilepic = request.files['uploadedprofilepic']

            profilepic_name = secure_filename(uploadedprofilepic.filename)
            mimetype = uploadedprofilepic.mimetype

            profilepic.profilepic_name = profilepic_name
            profilepic.profilepic_data = uploadedprofilepic.read()
            profilepic.mimetype = mimetype

            db.session.add(profilepic)
            db.session.commit()

            session['default_profilepic'] = False
        except Exception as e:
            db.session.commit()
            flash("Sorry! Could not update profile pic ...", "danger")
        else:
            flash("Profile Pic Uploaded Successfully...", "success")
            return redirect(url_for('profile', username = username))


@app.route('/deleteprofilepic/<username>')
def deleteprofilepic(username):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    user = User.query.filter_by(username = username).first()
    profilepic = ProfilePics.query.filter_by(user_id = user.user_id).first()

    if profilepic:
        db.session.delete(profilepic)
        db.session.commit()
    
        flash("Profile Pic deleted successfully..!", "success")
        session['default_profilepic'] = True
    else:
        flash("Sorry! Couldn't delete profile pic. \nPlease try later..." ,"danger")
    
    return redirect(url_for('profile', username = username))


@app.route('/<username>/delete_profile')
def delete_profile(username):
    if not g.user:
        return redirect(url_for('session_expired'))
    
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

            for comment in user.comments:
                db.session.delete(comment)

            db.session.delete(user)
            db.session.commit()
        
        except Exception as e:
            flash("Sorry! Could not delete the profile. Please try later ...")
            return url_for('profile', username = username)
        
        else:
            flash("Profile deleted successfully", "success")
            session.pop('user', None)
            session.pop('fullname', None)
            session.pop('default_profilepic', None)
            return redirect(url_for('index'))


@app.route('/<username>/add_comment/<post_id>', methods=['POST'])
def add_comment(username, post_id):
    if not g.user:
        return redirect(url_for('session_expired'))
    
    comment = request.form['comment']

    if not comment:
        flash("Comment cannot be empty.", "warning")

    else:
        post = UserPosts.query.filter_by(post_id = post_id).first()
        if post:
            try:
                user = User.query.filter_by(username = username).first()
                comment = Comments(user_id = user.user_id, post_id = post.post_id , text = comment,  created_date = getcurrentformatteddatetime())
                db.session.add(comment)
                db.session.commit()

                flash("comment added successfully!", "success")

            except Exception as e:
                flash("Could not add comment.", "danger")
                return redirect(url_for('home'))

            else:
                return redirect(url_for('home'))
        else:
            flash("Post does not exist.", "danger")
    return redirect(url_for('home'))


@app.route('/<username>/delete_comment/<comment_id>', methods=['GET'])
def delete_comment():
    if not g.user:
        return redirect(url_for('session_expired'))
    
    pass

@app.route("/logout")
def logout():
    session.pop('user', None)
    session.pop('fullname', None)
    session.pop('default_profilepic', None)
    return redirect(url_for("session_expired")) 


@app.route("/session_expired")
def session_expired():
    return render_template("session_expired.html")

@app.route("/error")
def error():
    return render_template("error.html")

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, post-check=0, pre-check=0"
    return response

@app.route('/getsession')
def getsession():
    if 'user' in session:
        return session['user']+"--"+session['fullname']
    
    return 'Not logged in!'
 
@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    session.pop('fullname', None)
    session.pop('default_profilepic', None)
    return 'Dropped!'

# @app.route("/invalid_login")
# def invalid_login():
#     return render_template("invalid_login.html")