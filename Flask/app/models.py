class DiscussionForum(db.Model):
    __tablename__ = 'DiscussionForum'

    forum_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Foreign key relationship
    course = db.relationship('Course', backref='discussions', lazy=True)
