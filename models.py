from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy instance
db = SQLAlchemy()


class BlogPost(db.Model):
    """
    Model for blog posts.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Slug is used for SEO-friendly URLs
    slug = db.Column(db.String(200), unique=True, nullable=False)


class Activity(db.Model):
    """
    Model for tracking various activities (learning days, projects, etc.).
    This powers the activity graph and stats on the homepage.
    """
    id = db.Column(db.Integer, primary_key=True)
    # Type can be 'project', 'blog_post', or 'learning_day'
    type = db.Column(db.String(20))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=True)
    # Hours spent on learning/project (optional)
    hours_spent = db.Column(db.Float, nullable=True)
    # Category of activity (e.g., 'ML', 'Web Dev')
    category = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        """
        Convert activity to dictionary format for API responses.
        """
        return {
            'id': self.id,
            'type': self.type,
            'date': self.date.strftime('%Y-%m-%d'),
            'title': self.title,
            'description': self.description,
            'hours_spent': self.hours_spent,
            'category': self.category
        }


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(200))  # For cards preview
    tech_stack = db.Column(db.String(200))  # Comma-separated technologies
    github_link = db.Column(db.String(200))
    demo_link = db.Column(db.String(200))
    image = db.Column(db.String(200))  # Image path
    status = db.Column(db.String(20))  # 'completed' or 'in-progress'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(200), unique=True, nullable=False)