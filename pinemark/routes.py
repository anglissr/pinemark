from flask import current_app as app, render_template
from .models import Bookmark, Tag, BookmarkTag


@app.route('/')
def home():
    bookmarks = Bookmark.query.all()  # Fetch all bookmarks
    return render_template('index.html', bookmarks=bookmarks)