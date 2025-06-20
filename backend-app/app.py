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

# # Create a new page
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

# #Get one page by ID
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

# #Update page
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

# #Delete a specific page
@app.route('/page/<int:pageId>', methods=["DELETE"])
def deletePageFunction(pageId: int):    
    page = pagesClass.query.get(pageId)

    db.session.delete(page)
    db.session.commit()

    return jsonify({
        "message": "Page deleted"
    }), 200

# #____________________________________________________________________________________________________

#Categories CRUD
#Get all categories
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

#Create a category
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


# #Get a specific category 
@app.route('/categories/<int:categoryId>', methods=["GET"])
def getCategoryByIdFunction(categoryId: int):
    category = categoriesClass.query.get_or_404(categoryId)

    category_data = {
        "category_id": category.categoryId,
        "category_name": category.categoryName
    }

    return jsonify(category_data), 200

# #____________________________________________________________________________________________________


# #Collaborators CRUD
#Get all collaborators users
@app.route('/collaborators', methods=["GET"])
def getCollaboratorsFunction():
    collaborators = collaboratorsClass.query.all()

    collaboratorsList = []
    for collaborator in collaborators:
        collaboratorsList.append({
            "collaborator_id": collaborator.collaboratorId,
            "collaborator_name": collaborator.collaboratorName,
            "collaborator_email": collaborator.collaboratorEmail,
            # "collaborator_categories": collaborator.collaboratorCategories
        })
    
    return jsonify(collaboratorsList), 200

#Get a specific collaborator 
@app.route('/collaborators/<int:collaboratorId>', methods=["GET"])
def getCollaboratorById(collaboratorId: int):
    collaborator = collaboratorsClass.query.get_or_404(collaboratorId)

    collaborator_data = {
        "collaborator_id": collaborator.collaboratorId,
        "collaborator_name": collaborator.collaboratorName,
        "collaborator_email": collaborator.collaboratorEmail,
    }

    return jsonify(collaborator_data), 200

#Create a new collaborator user
@app.route('/collaborators', methods=["POST"])
def addCollaborator():
    data = request.get_json()
    newCollaborator = collaboratorsClass(
        collaboratorName=data['collaborator_name'],
        collaboratorEmail=data['collaborator_email'],
    )
    db.session.add(newCollaborator)
    db.session.commit()

    return jsonify({
        "message": "Collaborator user added",
        "collaborator": {
            "collaborator_id": newCollaborator.collaboratorId,
            "collaborator_name": newCollaborator.collaboratorName,
            "collaborator_email": newCollaborator.collaboratorEmail,
        }
    }), 201


#Update collaborator
@app.route('/collaborators/<int:collaboratorId>', methods=["PUT"])
def updateCollaborator(collaboratorId: int):
    collaborator = collaboratorsClass.query.get(collaboratorId)
    data = request.get_json()

    collaborator.collaboratorId=data['collaborator_id']
    collaborator.collaboratorName=data['collaborator_name']
    collaborator.collaboratorEmail=data['collaborator_email']

    updatedCollaborator = collaboratorsClass(
        collaboratorId=data['collaborator_id'],
        collaboratorName=data['collaborator_name'],
        collaboratorEmail=data['collaborator_email'],
    )
    db.session.add(updatedCollaborator)
    db.session.commit()

    return jsonify({
        "message": "Collaborator updated",
        "collaborator": {
            "collaborator_id": collaborator.collaboratorId,
            "collaborator_name": collaborator.collaboratorName,
            "collaborator_email": collaborator.collaboratorEmail,
        }
    }), 201

#Delete collaborator
@app.route('/collaborators/<int:collaboratorId>', methods=["DELETE"])
def deleteCollaborator(collaboratorId):
    collaborator = collaboratorsClass.query.get(collaboratorId)
    db.session.delete(collaborator)
    db.session.commit()

    return jsonify ({
        "message": "User deleted"
    }), 200

#____________________________________________________________________________________________________










#____________________________________________________________________________________________________
# #Admin CRUD
# #Get all admins users
# @app.route('/admins', methods=["GET"])
# def getAllAdmins():
#     admins = adminsClass.query.all()
#     adminsList = []
#     for admin in admins:
#         adminsList.append({
#             "admin_id": admin.adminId,
#             "admin_name": admin.adminName,
#             "admin_email": admin.adminEmail,
#             # "admin_categories": admin.adminCategories
#         })
#     return jsonify(adminsList), 200 

# #Get a specific admin user
# @app.route('/admins/<int:adminId>', methods=["GET"])
# def getAdminById(adminId: int):
#     admin = adminsClass.query.get_or_404(adminId)
#     admin_data = {
#         "admin_id": admin.adminId,
#         "admin_name": admin.adminName,
#         "admin_email": admin.adminEmail,
#         # "admin_categories": admin.adminCategories
#     }

#     return jsonify(admin_data), 200

# #Crete a new admin user
# @app.route('/admins', methods=["POST"])
# def addAdmin():
#     data = request.get_json()
#     newAdmin = adminsClass(
#         adminName=data['admin_name'],
#         adminEmail=data['admin_email'],
#         # adminCategories=data['admin_categories']
#     )
#     db.session.add(newAdmin)
#     db.session.commit()

#     return jsonify({
#         "message": "Admin user added",
#         "Admin": {
#             "admin_id": newAdmin.adminId,
#             "admin_name": newAdmin.adminName,
#             "admin_email": newAdmin.adminEmail,
#             # "admin_categories": newAdmin.adminCategories
#         }
#     }), 201

# #Update a admin details
# @app.route('/admin/<int:admindId>', methods= ["PUT"])
# def updateAdmin(adminId: int):
#     admin = adminsClass.query(adminId)
#     data = request.get_json()
#     updatedAdmin = adminsClass(
#         adminId=data['admin_id'],
#         adminName=data['admin_name'],
#         adminEmail=data['admin_email'],
#         adminCategories=data['admin_categories']
#     )
#     db.session.add(updatedAdmin)
#     db.session.commit()

#     return jsonify({
#         "message": "Admin added",
#         "admin": {
#             "admin_id": updatedAdmin.adminId,
#             "admin_name": updatedAdmin.adminName,
#             "admin_email": updatedAdmin.adminEmail,
#             "admin_categories": updatedAdmin.adminCategories
#         }
#     }), 201

# #Delete a admin user
# @app.route('/admin/<int:admindId>', methods= ["DELETE"])
# def deleteAdmin(amindId: int):
#     admin = adminsClass.query.get(adminId)
#     db.session.delete(admin)
#     db.session.commit()

#     return jsonify({
#         "message": "Admin user deleted"
#     }), 200

# #____________________________________________________________________________________________________

# #Relationships routes
# #Pages and categories ESSE TRECO NAO TA FAZENDO NENHUM SENTIDO VSF
# #Get all pages from a specific category
# @app.route('/categories/<int:categoryId>/pages', methods=["GET"])
# def getPagesByCategory(categoryId: int):
#     category = categoriesClass.query.get(categoryId)
#     pages_data = []
#     for page in category.pages:
#         pages_data.append({
#             "page_id": page.pageId,
#             "page_name": page.pageName,
#             "page_collaborator": page.pageCollaborator
#         })

#     return jsonify(pages_data), 200

# #Assign a page to a specific category
# @app.route('/categories/<int:categoryId>/pages/<int:pageId>', methods=["POST"])
# def assignPageToCategory(categoryId: int, pageId: int):
#     category = categoriesClass.query.get(categoryId)
#     page = pagesClass.query.get(pageId)
#     category.pages.append(page) 
#     db.session.add(category)
#     db.session.coomit()

#     return jsonify({
#         "message": "Category updated"
#     }), 201

#Remove a page form a specific category
#@app.route('/categories/<int:categoryId>/pages/<int:pageId>', methods=["POST"])
#def assignPageToCategory(categoryId: int, pageId: int):
#    category = categoriesClass.query.get(categoryId)
#   page = pagesClass.query.get(pageId)
#   category.pages.append(page) 
#   db.session.add(category)
#   db.session.coomit()

#   return jsonify({
#       "message": "Category updated"
#   }), 200

    


##########


# def __init__(self, category_id, category_name):
#     self.categoryId = category_id
#     self.categoryName = category_name

# def __repr__(self):
#     return f"<Category {self.categoryName}>"

#____________________________________________________________________________________________________

if __name__ == '__main__':
    app.run(debug=True)