from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import current_app
from werkzeug.exceptions import abort
import time
from flaskr.auth import login_required
from flaskr.db import get_db
from werkzeug.utils import secure_filename
from flaskr import ALLOWED_EXTENSIONS
import os

bp = Blueprint("blog", __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@bp.route("/", methods=("GET", "POST"))
def index():
    print("test")
    """Show all the posts, most recent first."""
    if request.method=='POST':
        print("test")
        search=request.form["search_input"]
        db = get_db()
        posts = db.execute(
            "SELECT p.id, title, body, created, likes,author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE title=?"
            " ORDER BY created DESC",(search,)
        ).fetchall()

        return render_template("blog/index.html", posts=posts)
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, likes,author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()

    return render_template("blog/index.html", posts=posts)
@bp.route("/<int:id>/likess", methods=("GET", "POST"))
@login_required
def likess(id):
    if request.method == "POST":
        db = get_db()
        likenumber=db.execute("SELECT likes"
                              " FROM post"
                              " WHERE id=?",(id,),).fetchall()

        likenum=likenumber[0]["likes"]
        if likenum==None:
            likenum=0
        likenum+=1
        db.execute(
            "UPDATE post SET likes=? WHERE id = ?", (likenum,id)
        )
        db.commit()
        return redirect("/")


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.


        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            print(filename)

            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)
@bp.route("/<int:id>/read", methods=("GET", "POST"))
def read(id):
    db = get_db()
    comments = db.execute(
        "SELECT user_id,post_id, comment, comment_time,username"
        " FROM comments c JOIN user u ON c.user_id = u.id"

    ).fetchall()
    post = get_post(id,False)
    return render_template("blog/read.html", post=post,comments=comments,id=id)

@bp.route("/<int:id>/comment", methods=("GET", "POST"))
@login_required
def comment(id):
    if request.method == "POST":
        user_id=g.user['id']
        post_id=id
        comment=request.form["comment_body"]
        comment_time=time.strftime("%Y-%m-%d",time.localtime())
        db=get_db()
        db.execute(
            "INSERT INTO comments (user_id,post_id,comment,comment_time) VALUES (?, ?,?,?)",
            (user_id,post_id,comment,comment_time),
        )
        db.commit()
    return redirect(url_for("blog.read",id=id))

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
