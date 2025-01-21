# Import necessary modules
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify
from models import db, BlogPost, Activity, Project
from datetime import datetime, timedelta
from config import Config
import requests
import os

load_dotenv()
# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


@app.route('/')
def home():
    """Home page route - displays profile, stats, activity graph, and recent posts/projects."""
    try:
        recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(3).all()
        recent_projects = Project.query.order_by(Project.created_at.desc()).limit(3).all()
    except Exception as e:
        print(f"Error fetching recent content: {e}")
        recent_posts = []
        recent_projects = []

    # Get stats from database
    stats = {
        'days': Activity.query.filter_by(type='learning_day').count() or 0,
        'projects': Activity.query.filter_by(type='project').count() or 0,
        'posts': BlogPost.query.count() or 0
    }

    return render_template('home.html',
                         recent_posts=recent_posts,
                         recent_projects=recent_projects,
                         stats=stats,
                         activity_data={})
@app.route('/blog')
def blog():
    """Blog listing page - shows all posts in reverse chronological order."""
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', posts=posts)


@app.route('/post/<slug>')
def post(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    return render_template('post.html', post=post)


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


def get_github_contributions():
    """
    Fetch GitHub contributions data using GraphQL API starting from 2025
    """
    query = """
    query {
        viewer {
            contributionsCollection(from: "2025-01-01T00:00:00Z") {
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            contributionCount
                            date
                        }
                    }
                }
            }
        }
    }
    """

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("No GitHub token found in environment!")
        return None

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    try:
        print("Making request to GitHub API...")
        response = requests.post(
            'https://api.github.com/graphql',
            json={'query': query},
            headers=headers
        )

        print(f"GitHub API Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"GitHub API returned errors: {data['errors']}")
                return None
            print(f"Successful response: {data}")
            return data
        else:
            print(f"GitHub API Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error fetching GitHub data: {str(e)}")
        return None

@app.route('/test-token')
def test_token():
    """Test endpoint to verify token is loaded"""
    token = os.getenv("GITHUB_TOKEN")
    return jsonify({
        'token_exists': bool(token),
        'token_length': len(token) if token else 0,
        'token_preview': f"{token[:4]}...{token[-4:]}" if token else None
    })


@app.route('/api/activity-data')
def activity_data():
    """
    API endpoint that returns activity data in JSON format.
    """
    try:
        print("Fetching GitHub contributions...")
        github_data = get_github_contributions()
        print(f"GitHub data received: {github_data}")

        if (github_data and 'data' in github_data and
                github_data['data']['viewer'] and
                github_data['data']['viewer']['contributionsCollection']):

            print("Valid GitHub data found")
            stats = {
                'days': Activity.query.filter_by(type='learning_day').count() or 0,
                'projects': Activity.query.filter_by(type='project').count() or 0,
                'posts': BlogPost.query.count() or 0
            }

            # Get the contribution calendar from the correct path
            contribution_calendar = github_data['data']['viewer']['contributionsCollection']['contributionCalendar']

            return jsonify({
                'data': contribution_calendar,
                'stats': stats
            })
        else:
            print("No valid GitHub data received")
            return jsonify({
                'error': 'GitHub data not available',
                'data': None,
                'stats': {
                    'days': 0,
                    'projects': 0,
                    'posts': 0
                }
            })

    except Exception as e:
        print(f"Error in activity_data: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'data': None,
            'stats': {
                'days': 0,
                'projects': 0,
                'posts': 0
            }
        })

# Run the application
if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)