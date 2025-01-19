# Import necessary modules
from flask import Flask, render_template, jsonify
from models import db, BlogPost, Activity, Project
from datetime import datetime, timedelta
from config import Config


# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


def get_activity_stats():
    """
    Calculates statistics for the activity graph and stats display.
    Returns both general stats (total days, projects, posts) and 
    daily activity data for the graph.
    """
    # Get date range for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # Calculate totals for stats display
    total_days = Activity.query.filter_by(type='learning_day').count()
    total_projects = Activity.query.filter_by(type='project').count()
    total_posts = BlogPost.query.count()

    # Get all activities within the last year
    activities = Activity.query.filter(
        Activity.date.between(start_date, end_date)
    ).all()

    # Create a dictionary of date -> activity count
    activity_data = {}
    for activity in activities:
        date_key = activity.date.strftime('%Y-%m-%d')
        # Increment count for each day (or initialize to 1)
        activity_data[date_key] = activity_data.get(date_key, 0) + 1

    return {
        'stats': {
            'days': total_days,
            'projects': total_projects,
            'posts': total_posts
        },
        'activity_data': activity_data
    }


@app.route('/')
def home():
    """
    Home page route - displays profile, stats, activity graph, and recent posts.
    """
    try:
        recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(5).all()
    except Exception as e:
        # Handle potential errors (e.g., database connection issues)
        print(f"Error fetching recent posts: {e}")
        recent_posts = []

    # Get activity statistics and graph data
    activity_info = get_activity_stats()

    return render_template('home.html',
                           recent_posts=recent_posts,
                           stats=activity_info['stats'],
                           activity_data=activity_info['activity_data'])


@app.route('/blog')
def blog():
    """Blog listing page - shows all posts in reverse chronological order."""
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/projects')
@app.route('/projects')
def projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=projects)

@app.route('/project/<slug>')
def project(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    return render_template('project.html', project=project)


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@app.route('/api/activity-data')
def activity_data():
    """
    API endpoint that returns activity data in JSON format.
    Used by the JavaScript to populate the activity graph.
    """
    activity_info = get_activity_stats()
    return jsonify(activity_info)


# Run the application
if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)