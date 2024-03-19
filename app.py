from flask import Flask, jsonify
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

# Configure MySQL database
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'your_password'
app.config['MYSQL_DATABASE_DB'] = 'mydatabase'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# Sample Model (You can keep your existing User model if you have one)
class User(object):  
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

# Sample route
@app.route('/')
def hello_world():
    # cursor = mysql.get_db().cursor()  # Get a cursor
    cursor = mysql.connect().cursor()
    user_count = cursor.execute("SELECT COUNT(*) FROM users")
    user_count_result = cursor.fetchone()[0]  # Fetch the count
    # return jsonify({'message': 'Hello from Flask and MySQL!'})
    return jsonify({'message': 'Hello from Flask and MySQL!', 'user_count': user_count_result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
