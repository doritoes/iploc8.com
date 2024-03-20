from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from flaskext.mysql import MySQL
import ipaddress
import time
import os
from datetime import timedelta

# App Setup
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

# Configure JWT-Extended
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
jwt = JWTManager(app)  

# Sample route
@app.route('/')
def hello_world():
    cursor = mysql.connect().cursor()
    user_count = cursor.execute("SELECT COUNT(*) FROM users")
    user_count_result = cursor.fetchone()[0]  # Fetch the count
    return jsonify({'message': 'Hello from Flask and MySQL!', 'user_count': user_count_result})

# CORS setup
CORS(app, origins=["http://localhost:5000", "http://localhost:8080", "https://ipdice.com", "https://www.ipdice.com"]) 

# Favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static','favicon.ico', mimetype='image/vnd.microsoft.icon')

# robots.txt route
@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

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

# Test page route
@app.route('/test.html')
def test_page():
    return send_from_directory('static', 'test.html') 

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

@app.route("/api/v2/login", methods=["POST"])
def login():
    if not request.is_json or not "api_key" in request.json:
        return jsonify({"error": "Invalid request"}), 400
    api_key = request.json["api_key"]
    try:
        cursor = mysql.connect().cursor()
        query = "SELECT guuid FROM api_keys WHERE guuid = %s AND valid IS TRUE"
        cursor.execute(query, (api_key,))
        result = cursor.fetchone()
        if result and result[0] and result[0] == api_key:
            access_token = create_access_token(identity=api_key) 
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"error": "Invalid API key"}), 401 
    except Exception as e:
        print(f"Error encountered: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/v2/ip', methods=["GET", "POST"])
@jwt_required()
def ip_info():
    current_user = get_jwt_identity()  
    if request.method == "POST":
        if not request.is_json or not "ip" in request.json:
            return jsonify({"error": "Invalid request"}), 400 
        user_ip = request.json["ip"]
    elif request.method == "GET":
        if not request.args.get("ip"):
            return jsonify({"error": "Invalid request"}), 400
        user_ip = request.args.get("ip")
    else:
        return jsonify({"error": "Unsupported method"}), 405
    try:
        ip = ipaddress.ip_address(ip_address)
        ip_decimal = int(ip)
    except ValueError:
        return jsonify({'error': 'Invalid IP address'}), 400 
    try:
        cursor = mysql.connect().cursor()
        cursor.execute("""
            SELECT c.country_code, c.state1, c.state2, c.city, c.postcode, c.latitude, c.longitude, c.timezone)
            FROM city c
            WHERE c.start <= %c AND g.end >= %s
        """, (ip_decimal, ip_decimal))
        result = cursor.fetchone()
        if result:
            country = result[0] if result[0] else "Unknown"
            country_long = result[1] if result[1] else "Unknown"
            state1 = result[2] if result[2] else ""
            state2 = result[3] if result[3] else ""
            city = result[4] if result[4] else ""
            postcode = result[5] if result[5] else ""
            latitude = result[6] if result[6] else ""
            longitude = result [7] if result[7] else ""
            timezone = result[8] if result[8] else ""
        else:
            country = "Unidentified"
            country_long = "Unidentified"
            state1 = state2 = city = postcocde = latitude = longitude = timezone = ""
        isp = "disabled for testing"
    except Exception as e:
        print(f"Error encountered: {e}")
    ip_data = {
        "ip": user_ip,
        "city": city,
        "state": state1,
        "state2": state2,
        "country": country,
        "country_long": country_long,
        "postcode": postcode,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "isp": isp,
        "attribution": "db-ip.com",
        "link": "https://db-ip.com/"
    } 
    return jsonify(ip_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
