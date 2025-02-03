from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
    session,
    flash
)
from models import db, BlogPost, Activity, Project
from datetime import datetime, timedelta
from config import Config
from slugify import slugify
from functools import wraps
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)




# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if (request.form['username'] == app.config['ADMIN_USERNAME'] and
            request.form['password'] == app.config['ADMIN_PASSWORD']):
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('admin/login.html')

# Admin logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# Admin dashboard
@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = {
        'total_posts': BlogPost.query.count(),
        'total_projects': Project.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/posts')
@admin_required
def admin_posts():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts)

@app.route('/admin/post/new', methods=['GET', 'POST'])
@admin_required
def admin_new_post():
    if request.method == 'POST':
        post = BlogPost(
            title=request.form['title'],
            content=request.form['content'],
            slug=request.form['slug']
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!')
        return redirect(url_for('admin_posts'))
    return render_template('admin/post_form.html')

@app.route('/admin/post/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_post(id):
    post = BlogPost.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.slug = request.form['slug']
        db.session.commit()
        flash('Post updated successfully!')
        return redirect(url_for('admin_posts'))
    return render_template('admin/post_form.html', post=post)

@app.route('/admin/post/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_post(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!')
    return redirect(url_for('admin_posts'))

@app.route('/admin/projects')
@admin_required
def admin_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=projects)


def create_slug(title):
    # remove any special chars, convert spaces to hyphens, make lowercase
    slug = ''.join(e for e in title if e.isalnum() or e.isspace())
    return slug.lower().replace(' ', '-')
@app.route('/admin/project/new', methods=['GET', 'POST'])
@admin_required
def admin_new_project():
    if request.method == 'POST':
        project = Project(
            title=request.form['title'],
            description=request.form['description'],
            tech_stack=request.form['tech_stack'],
            github_link=request.form['github_link'] or None,
            demo_link=request.form['demo_link'] or None,
            status=request.form['status'],
            slug=create_slug(request.form['title'])
        )
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!')
        return redirect(url_for('admin_projects'))
    return render_template('admin/project_form.html')


@app.route('/admin/project/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_project(id):
    project = Project.query.get_or_404(id)

    if request.method == 'POST':
        try:
            print("Form data received:", {
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'tech_stack': request.form.get('tech_stack'),
                'github_link': request.form.get('github_link'),
                'demo_link': request.form.get('demo_link'),
                'status': request.form.get('status')
            })

            project.title = request.form.get('title')
            project.description = request.form.get('description')
            project.tech_stack = request.form.get('tech_stack')

            # Handle empty or 'None' string links
            github_link = request.form.get('github_link')
            demo_link = request.form.get('demo_link')
            project.github_link = None if github_link in ['None', ''] else github_link
            project.demo_link = None if demo_link in ['None', ''] else demo_link

            project.status = request.form.get('status')
            # Use create_slug instead of slugify
            project.slug = create_slug(request.form.get('title'))

            db.session.commit()
            flash('Project updated successfully!')
            return redirect(url_for('admin_projects'))

        except Exception as e:
            db.session.rollback()
            import traceback
            print("Error details:")
            print(traceback.format_exc())
            flash(f'Error updating project: {str(e)}')

    return render_template('admin/project_form.html', project=project)
@app.route('/admin/project/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!')
    return redirect(url_for('admin_projects'))

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


@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.get_json()

        # Create email content
        msg = MIMEMultipart()
        msg['From'] = data['email']
        msg['To'] = 'nawafkm01@gmail.com'
        msg['Subject'] = f"New contact from {data['name']}"

        body = f"""
        Name: {data['name']}
        Email: {data['email']}

        Message:
        {data['message']}
        """

        msg.attach(MIMEText(body, 'plain'))

        # Setup email server (Gmail example)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # You'll need to set up an app password for Gmail
        email_password = os.getenv('EMAIL_PASSWORD')
        server.login('nawafkm01@gmail.com', email_password)

        # Send email
        server.send_message(msg)
        server.quit()

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
    """Test endpoint to make sure token is loaded"""
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
    app.run(debug=True, host='0.0.0.0', port=8080)