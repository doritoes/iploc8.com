from flask import Flask, jsonify, request, send_from_directory 
from flaskext.mysql import MySQL
import ipaddress
import time

app = Flask(__name__)
mysql = MySQL()

# Capture uptime
container_start_time = time.time()

# Configure MySQL database
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'your_password'
app.config['MYSQL_DATABASE_DB'] = 'mydatabase'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# Sample route
@app.route('/')
def hello_world():
    cursor = mysql.connect().cursor()
    user_count = cursor.execute("SELECT COUNT(*) FROM users")
    user_count_result = cursor.fetchone()[0]  # Fetch the count
    return jsonify({'message': 'Hello from Flask and MySQL!', 'user_count': user_count_result})

# Favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static','favicon.ico', mimetype='image/vnd.microsoft.icon')

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
    uptime_seconds = time.time() - container_start_time
    uptime_hours = uptime_seconds / 3600
    if uptime_hours > 12:
        return jsonify({'status': f'Container uptime exceeds threshold (uptime: {uptime_seconds} seconds)'}), 203
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
        cursor.execute("""
            SELECT Sanction FROM sanctions WHERE Country = %s
        """, (country,))
        sanction_result = cursor.fetchone()
        sanction = sanction_result[0] if sanction_result else None
    except Exception as e:
        print(f"Error encountered: {e}")
        return jsonify({'error': 'Database query failed'}), 500
    output_data = {  # Construct a dictionary for flexible modification
        'ip': ip_address,
        'country': country,
        'country_long': country_long,
        'isp': isp
    }
    if sanction:
        output_data['sanction'] = sanction
    return jsonify(output_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
