from ..models import User,Role,Blog,Comment,Quote, Subscriber
from .forms import AddBlog, SubscriberForm, AddComment, UpdateProfile
from .. import db
from . import main
from flask import render_template, redirect, url_for,flash,request
from ..requests import get_quotes
from flask_login import login_required, current_user
from datetime import datetime
from ..email import mail_message
from sqlalchemy import desc

@main.route('/', methods = ['GET', 'POST'])
def index():
    title = "Bluebird"
    blogs = Blog.query.order_by(desc(Blog.id)).all()
    quotes = get_quotes()
    subscriber_form = SubscriberForm()
    if subscriber_form.validate_on_submit():
        subscriber_email = subscriber_form.email.data
        new_subscriber = Subscriber(email = subscriber_email)
        new_subscriber.save_subscriber()
        mail_message("Welcome to Blog", "email/welcome_user", new_subscriber.email)
        return redirect(url_for('main.index'))

    return render_template('index.html',title = title, blogs = blogs,quotes = quotes, subscriber_form = subscriber_form)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/user/<user_id>')
@login_required 
def profile(user_id):
    user = User.query.filter_by(id = user_id).first()
    blogs = Blog.query.filter_by(user_id = user.id).all()
    title = user.username.upper()
    return render_template('profile.html', user= user, blogs = blogs, title= title )



@main.route('/user/<user_id>/update', methods = ["GET", "POST"])
@login_required
def update_profile(user_id):
    title = "Edit Profile"
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        abort(404)
    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.profile', user_id = user.id))
    return render_template('update.html', form = form, title = title)

@main.route('/user/<user_id>/update/pic', methods = ['POST'])
@login_required
def update_pic(user_id):
    title = "Edit Profile"
    user = User.query.filter_by(id = user_id).first()
    
    if "profile_pic" in request.files:
        filename = photos.save(request.files["profile_pic"])
        file_path = "photos/{filename}"
        user.profile_pic = file_path
        db.session.commit()
    return redirect(url_for('main.profile', user_id = user_id))


@main.route('/blog/<blog_id>')
def blog(blog_id):
    title = "Blogs"
    blog = Blog.query.filter_by(id = blog_id).first()
    comments = Comment.query.filter_by(blog_id = blog_id).all()
    return render_template('blog.html', title = title,blog = blog, comments = comments)




@main.route('/blog/<user_id>/new', methods = ['GET', 'POST'])
@login_required
def add_blog(user_id):
    form = AddBlog()
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        abort(404)
    title = "Post new blog"
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        new_blog = Blog( title = title, description = description)
        new_blog.save_blog()
        subscribers = Subscriber.get_subscribers()
        for subscriber in subscribers: 
            mail_message("Welcome to Blog", "email/new_blog", subscriber.email)
        return redirect(url_for('main.index'))
    

        title = "New Blog"
        blogs = Blog.query.all()
        return redirect(url_for('main.blog', title = title, blog_id = new_blog.id))
    return render_template('new_blog.html', form = form, title =title)

@main.route('/blog/<blog_id>/update', methods =['GET', 'POST'] )
@login_required
def update_blog(blog_id):
    title = "Update Blog"
    form = AddBlog()
    blog = Blog.query.filter_by(id=blog_id).first()
    form.title.data = blog.title
    form.description.data = blog.description
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        blog.title = title
        blog.description = description
        db.session.commit()
        return redirect(url_for('main.blog', blog_id = blog_id))
    return render_template('new_blog.html',form = form, title =title )    

@main.route('/blog/<blog_id>/delete_blog')
@login_required
def delete_blog(blog_id):
    blog = Blog.query.filter_by(id = blog_id).first()
    db.session.delete(blog)
    db.session.commit()

    flash('Blog has been successfully deleted')
    return redirect(url_for('main.index'))



@main.route('/comments/<blog_id>',methods = ["GET", "POST"])
def comment(blog_id):
    blogs = Blog.query.filter_by(id = blog_id).first()
    comments = Comment.query.filter_by(id = blog_id).first()
    return redirect(url_for('main.blog',blogs = blogs, blog_id = blog_id, comments = comments))


@main.route('/comment/<blog_id>', methods = ['GET', 'POST'])
def add_comment(blog_id):
    title = "Add Comments"
    blog = Blog.query.filter_by(id = blog_id).first()
    form = AddComment()
    if form.validate_on_submit():
        content = form.text.data 
        new_comment = Comment(content= content, blog_id = blog_id)
        new_comment.save_comment()
        return redirect(url_for("main.comment", blog_id = blog.id))
    return render_template("new_comment.html",title = blog.title,form = form,blog = blog)
   




@main.route('/comment/<blog_id>/delete_comment')
@login_required
def delete_comment(blog_id):
    comment = Comment.query.filter_by(id = blog_id).first()
    db.session.delete(comment)
    db.session.commit()

    flash('Comment has been deleted')

    return redirect(url_for('main.blog',title = title,blogs = blogs))



     