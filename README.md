# BlogApp_API


### Environment setup

It is higly recommended to run every single python project in a virtual environment but here is what the Flask recommends [here](https://flask.palletsprojects.com/en/1.1.x/installation/#virtual-environments)

To install all the requirements

```
pip install -r requirements.txt
```

### Development

```
flask run
```

### API Routes: 
- POST `/api/register` - Register a new user
- POST `/api/login` - Login for an existing user
- POST `/api/posts` - Create a new post

Only a logged in `User` can use this blogging website API, with the exception of the login and register routes.


## Database

### Setup

**Note: No database setup should be required to get started with running the project.**

This project uses SQLite, which stores your tables inside a file. It uses [SQLAlchemy](https://www.sqlalchemy.org/) as an ORM layer.

### Seed Data

We've included sample data that the application has been configured to use. If you want to re-seed the database, you can run `python seed.py`. [seed.py](./seed.py) can be referenced to see what the sample data is. Viewing the database file itself is not required to complete your tasks, but if you would like to, an application like [DB Browser for SQLite](https://sqlitebrowser.org/) can be used.

## Testing

You can use cURL or a tool like [Postman](https://www.postman.com/) to test the API.

### Example Curl Commands

You can log in as one of the seeded users with the following curl command:

```bash
curl --location --request POST 'localhost:5000/api/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "thomas",
    "password": "123456"
}'
```

Then you can use the token that comes back from the /login request to make an authenticated request to create a new blog post

```bash
curl --location --request POST 'localhost:5000/api/posts' \
--header 'x-access-token: your-token-here' \
--header 'Content-Type: application/json' \
--data-raw '{
    "text": "This is some text for the blog post...",
    "tags": ["travel", "hotel"]
}'
```
