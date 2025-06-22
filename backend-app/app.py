import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import enum


app = Flask(__name__)

db_user = os.environ.get('DB_USER', 'postgres')
db_password = os.environ.get('DB_PASSWORD', 'qualquercoisa')
db_host = os.environ.get('DB_HOST', 'localhost')
db_port = os.environ.get('DB_PORT', '5432')
db_name = os.environ.get('DB_NAME', 'ad_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '1234')

# Initialize SQLAlchemy
db = SQLAlchemy(app)
CORS(app)


# --- Enums for Roles ---
class RoleEnum(enum.Enum):
    """Enumeration for collaborator roles."""
    WRITER = "writer"
    ADMIN = "admin"
    EDITOR = "editor"


# --- Database Models ---
class Role(db.Model):
     
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Role {self.name}>'


class Collaborator(db.Model):
  
    __tablename__ = 'collaborators'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    role = db.relationship('Role', backref=db.backref('collaborators', lazy=True))

    def set_password(self, password):
        """Hashes and sets the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Returns a dictionary representation of the collaborator."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.name
        }

    def __repr__(self):
        return f'<Collaborator {self.username}>'


class Category(db.Model):
   
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def to_dict(self):
        """Returns a dictionary representation of the category."""
        return {
            'id': self.id,
            'name': self.name,
            'pages': [page.to_dict_simple() for page in self.pages]
        }

    def __repr__(self):
        return f'<Category {self.name}>'


class Page(db.Model):
    
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    collaborator_id = db.Column(db.Integer, db.ForeignKey('collaborators.id'), nullable=False)

    category = db.relationship('Category', backref=db.backref('pages', lazy=True, cascade="all, delete-orphan"))
    author = db.relationship('Collaborator', backref=db.backref('pages', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category_id': self.category_id,
            'category_name': self.category.name,
            'author_id': self.collaborator_id,
            'author_username': self.author.username
        }

    def to_dict_simple(self):
        return {
            'id': self.id,
            'title': self.title
        }

    def __repr__(self):
        return f'<Page {self.title}>'

# --- API Endpoints (Routes) ---


# --- Collaborator Routes ---
@app.route('/api/collaborators', methods=['POST'])
def add_collaborator():
    data = request.get_json()
    if not data or not 'username' in data or not 'password' in data or not 'email' in data or not 'role_name' in data:
        return jsonify({'message': 'Missing required fields'}), 400

    role = Role.query.filter_by(name=data['role_name']).first()
    if not role:
        return jsonify({'message': f"Role '{data['role_name']}' not found."}), 404
        
    new_collaborator = Collaborator(
        username=data['username'],
        email=data['email'],
        role_id=role.id
    )
    new_collaborator.set_password(data['password'])
    db.session.add(new_collaborator)
    db.session.commit()
    return jsonify(new_collaborator.to_dict()), 201

@app.route('/api/collaborators', methods=['GET'])
def get_collaborators():
    collaborators = Collaborator.query.all()
    return jsonify([c.to_dict() for c in collaborators]), 200

# --- Category Routes ---
@app.route('/api/categories', methods=['POST'])
def add_category():
    data = request.get_json()
    if not data or not 'name' in data:
        return jsonify({'message': 'Category name is required'}), 400
    
    new_category = Category(name=data['name'])
    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.to_dict()), 201

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories]), 200

@app.route('/api/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify(category.to_dict()), 200
    
@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category and all its pages have been deleted.'}), 200

# --- Page Routes ---
@app.route('/api/pages', methods=['POST'])
def add_page():
    data = request.get_json()
    if not data or not 'title' in data or not 'content' in data or not 'category_id' in data or not 'collaborator_id' in data:
        return jsonify({'message': 'Missing required fields'}), 400

    # Verify category and collaborator exist
    Category.query.get_or_404(data['category_id'])
    Collaborator.query.get_or_404(data['collaborator_id'])
    
    new_page = Page(
        title=data['title'],
        content=data['content'],
        category_id=data['category_id'],
        collaborator_id=data['collaborator_id']
    )
    db.session.add(new_page)
    db.session.commit()
    return jsonify(new_page.to_dict()), 201

@app.route('/api/pages', methods=['GET'])
def get_pages():
    pages = Page.query.all()
    return jsonify([p.to_dict() for p in pages]), 200

@app.route('/api/pages/<int:page_id>', methods=['GET'])
def get_page(page_id):
    page = Page.query.get_or_404(page_id)
    return jsonify(page.to_dict()), 200

@app.route('/api/pages/<int:page_id>', methods=['PUT'])
def update_page(page_id):
    page = Page.query.get_or_404(page_id)
    data = request.get_json()
    
    page.title = data.get('title', page.title)
    page.content = data.get('content', page.content)
    if 'category_id' in data:
        Category.query.get_or_404(data['category_id'])
        page.category_id = data['category_id']
        
    db.session.commit()
    return jsonify(page.to_dict()), 200

@app.route('/api/pages/<int:page_id>', methods=['DELETE'])
def delete_page(page_id):
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return jsonify({'message': 'Page deleted successfully.'}), 200


# --- CLI Command to initialize the database ---
@app.cli.command('init-db')
def init_db_command():
    """Clears existing data and creates new tables."""
    db.drop_all()
    db.create_all()
    
    # --- Seed Initial Data ---
    # Create roles
    admin_role = Role(name=RoleEnum.ADMIN.value)
    writer_role = Role(name=RoleEnum.WRITER.value)
    editor_role = Role(name=RoleEnum.EDITOR.value)
    
    db.session.add_all([admin_role, writer_role, editor_role])
    db.session.commit()
    
    # Create a default admin user
    admin_user = Collaborator(username='admin', email='admin@example.com', role_id=admin_role.id)
    admin_user.set_password('supersecret')
    db.session.add(admin_user)
    
    # Create a default writer user
    writer_user = Collaborator(username='johndoe', email='john.doe@example.com', role_id=writer_role.id)
    writer_user.set_password('password123')
    db.session.add(writer_user)
    
    # Create some sample categories
    cat1 = Category(name='Our rhythms')
    cat2 = Category(name='Classes')
    db.session.add_all([cat1, cat2])
    db.session.commit()
    
    
    db.session.commit()
    print('Initialized and seeded the database.')


if __name__ == '__main__':
    app.run(debug=True)

    #    export FLASK_APP=main.py
    #    flask init-db
    #    flask run