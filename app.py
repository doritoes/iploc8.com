from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
import ipaddress

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
    cursor = mysql.connect().cursor()
    user_count = cursor.execute("SELECT COUNT(*) FROM users")
    user_count_result = cursor.fetchone()[0]  # Fetch the count
    return jsonify({'message': 'Hello from Flask and MySQL!', 'user_count': user_count_result})

# Healthcheck route
@app.route('/healthcheck')
def healthcheck():
    try:
        cursor = mysql.connect().cursor()
        user_count = cursor.execute("SELECT COUNT(*) FROM users")
        user_count_result = cursor.fetchone()[0]  # Fetch the count
    except Exception as e:
        print(f"Error encountered: {e}") # Log error
        return jsonify({'error': 'Database query failed'}), 500  # Return HTTP 500
    # Uptime check
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime_hours = uptime_seconds / 3600
    if uptime_hours > 12:
        return jsonify({'status': 'Container uptime exceeds threshold'}), 203
    else:
        return jsonify({'status': 'OK'})

# API Route (/api/v1/ip)
@app.route('/api/v1/ip')
def get_ip():
    ip_address = request.args.get('ip')
    if not ip_address:
        return jsonify({'error': 'Missing IP address'}), 400
    try:
        ip = ipaddress.ip_address(ip_address)
        ip_decimal = int(ip)
    except ValueError:
        return jsonify({'error': 'Invalid IP address'}), 400 
    try:
        cursor = mysql.connect().cursor()
        cursor.execute("""
            SELECT g.country, c.Name AS country_long
            FROM geo g
            LEFT JOIN countries c ON g.country = c.Code
            WHERE g.start <= %s AND g.end >= %s
        """, (ip_decimal, ip_decimal))
        result = cursor.fetchone()
        if result:
            country = result[0]
            country_long = result[1] if result[1] else "Unknown"  # Handle missing country_long
        else:
            country = "Unknown"
            country_long = "Unknown"
        cursor.execute("""
            SELECT description 
            FROM asn 
            WHERE start <= %s AND end >= %s
        """, (ip_decimal, ip_decimal))
        asn_result = cursor.fetchone()
        isp = asn_result[0] if asn_result else "Unknown" 

        isp = asn_result[0] if asn_result else "Unknown" 
    except Exception as e:
        print(f"Error encountered: {e}")
        return jsonify({'error': 'Database query failed'}), 500 
    return jsonify({
        'ip': ip_address,
        'decimal': ip_decimal,
        'country': country,
        'country_long': country_long,
        'isp': isp
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
