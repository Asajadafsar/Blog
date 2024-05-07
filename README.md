
```markdown
# Awesome Blog Project

Welcome to the Awesome Blog Project! This project is built with Django and provides a platform for users to create, manage, and share their blog posts.

## Features

### User Authentication
- User registration with username, email, and password.
- Login form with email/username and password.
- Logout functionality.

### Blog Post Management
- Create, update, delete, and view blog posts.
- Create blog posts with title, content, and optional image.
- View a list of all blog posts.
- View individual blog posts with full content.

### User Profile
- User profile page displaying user information (username, email, profile picture).
- List of blog posts authored by the user on their profile page.
- Option to edit user information (username, email, profile picture).

### Comment System
- Add comments to blog posts.
- Display comments under each blog post.
- Option to edit and delete own comments.

### Categories and Tags
- Create, assign, and filter blog posts by categories and tags.

### Search Functionality
- Search blog posts by title, content, or author.

### Drafts and Publishing
- Save blog posts as drafts.
- Publish drafts to make them publicly accessible.

## Tools and Technologies Used
- Django
- Figma (for UI/UX design)
- SQLite (as the database)
- UML (for diagramming)

## Project Structure

```
project-root/
│
├── sign/           # frontend this Django
│   ├── migrations/    # Database migrations
│   ├── templates/     # HTML templates
│   ├── static/        # Static files (CSS, JavaScript)
│   ├── models.py      # Database models (BlogPost, User, etc.)
│   ├── views.py       # Views for handling HTTP requests
│   └── ...
│
├── admin/           # Django app for react-admin
│   ├── migrations/    # Database migrations
│   ├── models.py      # Database models (CRUD)
│   ├── views.py       # Views for handling HTTP requests
│   └── ...
│
├── db.sqlite3         # SQLite database file
└── ...
```

## How to Run the Project

1. Clone the repository:

```bash
git clone https://github.com/Asajadafsar/Blog.git
```

2. Navigate to the project directory:

```bash
cd awesome-blog-project
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the Django development server:

```bash
python manage.py runserver
```

5. Open your web browser and go to `http://localhost:8000` to view the website.

## Contributing

Contributions are welcome! Feel free to submit bug reports, feature requests, or pull requests.
