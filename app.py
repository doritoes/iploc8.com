from flask import Flask, jsonify
#from flask_mysql import MySQL
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL database
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DATABASE_DB'] = 'mydatabase'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql = MySQL(app) 

# Sample Model (You can keep your existing User model if you have one)
class User(object):  
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

# Sample route
@app.route('/')
def hello_world():
    cursor = mysql.get_db().cursor()  # Get a cursor
    user_count = cursor.execute("SELECT COUNT(*) FROM users")
    user_count_result = cursor.fetchone()[0]  # Fetch the count

    return jsonify({'message': 'Hello from Flask and MySQL!', 'user_count': user_count_result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
