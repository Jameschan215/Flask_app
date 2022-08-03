import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    comments = db.relationship('Comment', backref='post')

    def __repr__(self):
        return f'[Post "{self.title}"]'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    # Remember it
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return f'[Comment "{self.content[:20]}..."]'


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('Content can not be empty!')
            return redirect(url_for('post', post_id=post.id))
        comment = Comment(content=content, post=post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))

    return render_template('post.html', post=post)


@app.route('/comments/')
def comments():
    comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template('comments.html', comments=comments)


@app.route('/comments/<int:comment_id>/delete', methods=['GET', 'POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for('post', post_id=post_id))