from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from sqlalchemy import ForeignKey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:qualquercoisa@localhost:5432/ad_db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#____________________________________________________________________________________________________

# Creating classes
class categoriesClass(db.Model):
    __tablename__ = 'categories'

    categoryId = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(), nullable=False)
    pages = db.relationship('pagesClass', back_populates='category')


class pagesClass(db.Model):
    __tablename__ = 'pages'

    pageId = db.Column(db.Integer, primary_key=True)
    pageName = db.Column(db.String(50), nullable=False)
    categoryId = db.Column(db.Integer, ForeignKey('categories.categoryId'))
    category = db.relationship('categoriesClass', back_populates='pages')
    collaboratorId = db.Column(db.Integer, ForeignKey('collaborator.collaboratorId'))
    collaborator = db.relationship('collaboratorsClass', back_populates='pages')

class rolesClass(db.Model):
    __tablename__ = 'roles'

    roleId = db.Column(db.Integer, primary_key=True)
    roleName = db.Column(db.String(50), nullable=False)
    collaborators = db.relationship('collaboratorsClass', back_populates='role')


class collaboratorsClass(db.Model):
    __tablename__ = 'collaborator'

    collaboratorId = db.Column(db.Integer, primary_key=True)
    collaboratorName = db.Column(db.String(50), nullable=False)
    collaboratorEmail = db.Column(db.String(50), nullable=False)
    pages = db.relationship('pagesClass', back_populates='collaborator')
    roleId = db.Column(db.Integer, ForeignKey('roles.roleId'))
    role = db.relationship('rolesClass', back_populates='collaborators')
    

#____________________________________________________________________________________________________

@app.route('/')
def hello():
    return {"hello":"socorro"}
#____________________________________________________________________________________________________

#Categories CRUD
# Get all categories
@app.route('/categories', methods=["GET"])
def getCategoriesFunction():
    categories = categoriesClass.query.all()

    categoriesList = []
    for category in categories:
        categoriesList.append({
            "category_id": category.categoryId,
            "category_name": category.categoryName
            })
    return jsonify(categoriesList), 200

# Create a category
@app.route('/categories', methods=["POST"])
def addNewCategoryFunction():
    data = request.get_json()
    newCategory = categoriesClass(
        categoryName=data['category_name']
    )

    db.session.add(newCategory)
    db.session.commit()

    newCategory_data = {
        "category_id": newCategory.categoryId,
        "category_name": newCategory.categoryName
    }

    return jsonify(newCategory_data), 200


# Get a specific category 
@app.route('/categories/<int:categoryId>', methods=["GET"])
def getCategoryByIdFunction(categoryId: int):
    category = categoriesClass.query.get_or_404(categoryId)

    category_data = {
        "category_id": category.categoryId,
        "category_name": category.categoryName
    }

    return jsonify(category_data), 200

# "Category" doesn't have a "delete" option
#____________________________________________________________________________________________________

#Pages CRUD
# Get all pages
@app.route('/pages', methods=["GET"])
def getPagesFunction():
    pages = pagesClass.query.all()

    pagesList = []
    for page in pages:
        pagesList.append({
            "page_id": page.pageId,
            "page_name": page.pageName,
            "page_category": {
                "category_id": page.category.categoryId,
                "category_name": page.category.categoryName
            },
            "page_collaborator": {
                "collaborator_id": page.collaborator.collaboratorId,
                "collaborator_name": page.collaborator.collaboratorName,
                "collaborator_email": page.collaborator.collaboratorEmail
            }
        })
    return jsonify(pagesList), 200

# Create a new page
@app.route('/pages/', methods=["POST"])
def addPageFunction():
    data = request.get_json()
    newPage = pagesClass(
        pageName=data['page_name'],
        categoryId=data['category_id'],
        collaboratorId=data['collaborator_id']
        )
    db.session.add(newPage)
    db.session.commit()

    return jsonify({
        "message": "Page added",
        "page":{
            "page_id": newPage.pageId,
            "page_name": newPage.pageName,
           "page_category": {
                "category_id": newPage.category.categoryId,
                "category_name": newPage.category.categoryName
            },
            "page_collaborator": {
                "collaborator_id": newPage.collaborator.collaboratorId,
                "collaborator_name": newPage.collaborator.collaboratorName,
                "collaborator_email": newPage.collaborator.collaboratorEmail
            }
        }
    }), 201

# Get one page by ID
@app.route('/pages/<int:pageId>', methods=["GET"])
def getPageByIdFunction(pageId: int):
    page = pagesClass.query.get_or_404(pageId)

    page_data = {
            "page_id": page.pageId,
            "page_name": page.pageName,
            "page_category": {
                "category_id": page.category.categoryId,
                "category_name": page.category.categoryName
            },
            "page_collaborator": {
                "collaborator_id": page.collaborator.collaboratorId,
                "collaborator_name": page.collaborator.collaboratorName,
                "collaborator_email": page.collaborator.collaboratorEmail
            }
        }

    return jsonify(page_data), 200

# Update page
@app.route('/pages/<int:pageId>', methods=["PUT"])
def updatePageFunction(pageId: int):
    page = pagesClass.query.get(pageId)
    data = request.get_json()

    page.pageName = data['page_name']
    page.categoryId = data['category_id']
    page.collaboratorId = data['collaborator_id']

    db.session.commit()

    return jsonify({
        "message": "Page updated",
        "page": {
            "page_id": page.pageId,
            "page_name": page.pageName,
             "page_category": {
                "category_id": page.category.categoryId,
                "category_name": page.category.categoryName
            },
            "page_collaborator": {
                "collaborator_id": page.collaborator.collaboratorId,
                "collaborator_name": page.collaborator.collaboratorName,
                "collaborator_email": page.collaborator.collaboratorEmail
            }
        }
    }), 201

# Delete a specific page
@app.route('/page/<int:pageId>', methods=["DELETE"])
def deletePageFunction(pageId: int):    
    page = pagesClass.query.get(pageId)

    db.session.delete(page)
    db.session.commit()

    return jsonify({
        "message": "Page deleted"
    }), 200
#____________________________________________________________________________________________________

#Roles CRUD
# Get all roles
@app.route('/roles', methods=["GET"])
def getRolesFunction():
    roles = rolesClass.query.all()

    rolesList=[]
    for role in roles:
        rolesList.append({
            "role_id": role.roleId,
            "role_name": role.roleName,
            "collaborators_list": role.collaborators
        })
    return jsonify(rolesList),200

# Create a new role
@app.route('/roles/', methods=["POST"])
def addNewRoleFunction():
    data = request.get_json()
    newRole = rolesClass(
        roleName=data['role_name'],
    )
    db.session.add(newRole)
    db.session.commit()

    return jsonify({
        "message": "Role added",
        "role": {
            "role_id": newRole.roleId,
            "role_name": newRole.roleName
        }
    }), 201

# Get one role by ID
@app.route('/roles/<int:roleId>', methods=["GET"])
def getRoleByIdFunction(roleId: int):
    role = rolesClass.query.get_or_404(roleId)

    role_data = {
        "role_id": role.roleId,
        "role_name": role.roleName,
        "collaborators_list": role.collaborators
    }
    return jsonify(role_data), 200

# Update role
@app.route('/roles/<int:roleId>', methods=["PUT"])
def updateRoleFunction(roleId: int):
    role = rolesClass.query.get(roleId)
    data = request.get_json()

    role.roleName = data['role_name']
    role.roleId = data['role_id']
    role.collaborators = data['collaborators']

    db.session.commit()

    return jsonify({
        "message": "Role updated",
        "role":{
            "role_id": role.roleId,
            "role_name": role.rolename,
            "collaborators": role.collaborators
        }
    }), 201

# Delete a specific role
@app.route('/role/<int:roleId>', methods=["DELETE"])
def deleteRoleFunction(roleId: int):
    role = rolesClass.query.get(roleId)

    db.session.delete(role)
    db.session.commit()

    return jsonify({
        "message": "Role deleted"
    }), 200
#____________________________________________________________________________________________________

#Collaborators CRUD
# Get all collaborators users
@app.route('/collaborators', methods=["GET"])
def getCollaboratorsFunction():
    collaborators = collaboratorsClass.query.all()

    collaboratorsList = []
    for collaborator in collaborators:
        collaboratorsList.append({
            "collaborator_id": collaborator.collaboratorId,
            "collaborator_name": collaborator.collaboratorName,
            "collaborator_email": collaborator.collaboratorEmail,
            "collaborator_pages": collaborator.pages,
            "collaborator_role_id": collaborator.roleId,
            "collaborator_role": collaborator.role
        })
    
    return jsonify(collaboratorsList), 200

# Get a specific collaborator 
@app.route('/collaborators/<int:collaboratorId>', methods=["GET"])
def getCollaboratorById(collaboratorId: int):
    collaborator = collaboratorsClass.query.get_or_404(collaboratorId)

    collaborator_data = {
        "collaborator_id": collaborator.collaboratorId,
        "collaborator_name": collaborator.collaboratorName,
        "collaborator_email": collaborator.collaboratorEmail,
        "collaborator_role": {
            "collaborator_role_id": collaborator.role.roleId,
            "collaborator_role_name": collaborator.role.roleName
        }
    }

    return jsonify(collaborator_data), 200

# Create a new collaborator user
@app.route('/collaborators', methods=["POST"])
def addCollaborator():
    data = request.get_json()
    newCollaborator = collaboratorsClass(
        collaboratorName=data['collaborator_name'],
        collaboratorEmail=data['collaborator_email'],
        roleId=data['collaborator_role_id']
    )
    db.session.add(newCollaborator)
    db.session.commit()

    return jsonify({
        "message": "Collaborator user added",
        "collaborator": {
            "collaborator_id": newCollaborator.collaboratorId,
            "collaborator_name": newCollaborator.collaboratorName,
            "collaborator_email": newCollaborator.collaboratorEmail,
            "collaborator_role": {
                "collaborator_role_id": newCollaborator.role.roleId,
                "collaborator_role_name": newCollaborator.role.roleName
            }
        }
    }), 201


# Update collaborator
@app.route('/collaborators/<int:collaboratorId>', methods=["PUT"])
def updateCollaborator(collaboratorId: int):
    collaborator = collaboratorsClass.query.get(collaboratorId)
    data = request.get_json()

    collaborator.collaboratorId=data['collaborator_id']
    collaborator.collaboratorName=data['collaborator_name']
    collaborator.collaboratorEmail=data['collaborator_email']
    collaborator.roleId=data['collaborator_role_id']

    db.session.commit()

    return jsonify({
        "message": "Collaborator updated",
        "collaborator": {
            "collaborator_id": collaborator.collaboratorId,
            "collaborator_name": collaborator.collaboratorName,
            "collaborator_email": collaborator.collaboratorEmail,
            "collaborator_role": {
                "collaborator_role_id": collaborator.roleId,
                "collaborator_role_name": collaborator.role
            }
        }
    }), 201

# Delete collaborator
@app.route('/collaborators/<int:collaboratorId>', methods=["DELETE"])
def deleteCollaborator(collaboratorId):
    collaborator = collaboratorsClass.query.get(collaboratorId)
    db.session.delete(collaborator)
    db.session.commit()

    return jsonify ({
        "message": "User deleted"
    }), 200
#____________________________________________________________________________________________________

#Relationships routes
# Pages and categories 

#  Get all pages from a specific category
@app.route('/categories/<int:categoryId>/pages', methods=["GET"])
def getPagesByCategory(categoryId: int):
    category = categoriesClass.query.get(categoryId)
    pages_data = []
    for page in category.pages:
        pages_data.append({
            "page_id": page.pageId,
            "page_name": page.pageName,
            "page_collaborator": {
                "collaborator_id": page.collaborator.collaboratorId,
                "collaborator_name": page.collaborator.collaboratorName,
                "collaborator_email": page.collaborator.collaboratorEmail
            }
        })

    return jsonify(pages_data), 200

#____________________________________________________________________________________________________

if __name__ == '__main__':
    app.run(debug=True)