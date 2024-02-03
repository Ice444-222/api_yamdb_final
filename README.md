# YaMDb Django
## Description:
Implemented an API for this project using Django REST framework. The YaMDb project collects user reviews on various works. The works themselves are not stored in YaMDb; you cannot watch a movie or listen to music here. Works are divided into categories, such as "Books," "Movies," and "Music."

## Technology Stack:
```
Python 3.9.10
Django 3.2.16
djoser 2.1.0
```

### API Resources in YaMDb
- Auth Resource: Authentication.
- Users Resource: Users.
- Titles Resource: Works for which reviews are written (a specific movie, book, or song).
- Categories Resource: Categories (types) of works ("Movies," "Books," "Music"). One work can be associated with only one category.
- Genres Resource: Genres of works. One work can be associated with multiple genres.
- Reviews Resource: Reviews on works. A review is linked to a specific work.
- Comments Resource: Comments on reviews. A comment is linked to a specific review.
- Each resource is described in the documentation, specifying endpoints (addresses for making requests), allowed types of requests, access rights, and additional parameters when necessary.
### User Roles and Access Rights
- Anonymous: Can view descriptions of works, read reviews and comments.
- Authenticated User (user): Can read everything, like Anonymous; can post reviews and rate works (movies/books/songs), comment on reviews; can edit and delete their own reviews and comments, edit their ratings of works. This role is assigned by default to every new user.
- Moderator (moderator): Same rights as an Authenticated User, plus the right to delete and edit any reviews and comments.
- Administrator (admin): Full rights to manage all project content. Can create and delete works, categories, and genres. Can assign roles to users.
- Django Superuser must always have administrator rights, a user with admin rights. Even if you change the user role to a superuser, it will not deprive them of administrator rights. A Superuser is always an administrator, but an administrator is not necessarily a superuser.
### Independent Registration of New Users
A user sends a POST request with the parameters email and username to the /api/v1/auth/signup/ endpoint.
The YaMDB service sends an email with a confirmation code (confirmation_code) to the specified email address.
The user sends a POST request with the parameters username and confirmation_code to the /api/v1/auth/token/ endpoint.
In response to the request, the user receives a token (JWT token). As a result, the user receives a
token and can work with the project's API by sending this token with each request. After registration
and receiving the token, the user can send a PATCH request to the /api/v1/users/me/ endpoint and
fill in the fields in their profile (description of fields is in the documentation).

## How to Run the Project:

Clone the repository and navigate to it in the command line:

```
git clone https://github.com/rerolll/api_yamdb
```

```
cd api_api_yamdb
```

Create and activate a virtual environment:

```
python3 -m venv env
```

```
source venv/scripts/activate
```

Install dependencies from the requirements.txt file:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Execute migrations:

```
python3 manage.py migrate
```

Run the project:

```
python3 manage.py runserver
```
