from . import db

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    url = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.Text)
    rating = db.Column(db.Integer, db.CheckConstraint('rating >= 1 AND rating <= 5'), nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)
    access_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    last_accessed = db.Column(db.DateTime)

    # Define relationship to the tags
    tags = db.relationship('Tag', secondary='bookmarks_tags', back_populates='bookmarks')


class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)

    # Define relationship to bookmarks
    bookmarks = db.relationship('Bookmark', secondary='bookmarks_tags', back_populates='tags')


class BookmarkTag(db.Model):
    __tablename__ = 'bookmarks_tags'
    
    bookmark_id = db.Column(db.Integer, db.ForeignKey('bookmarks.id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)