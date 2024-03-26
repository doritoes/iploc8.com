from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flaskext.mysql import MySQL
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
import ipaddress
import datetime
import requests
import logging
import base64
import random
import socket
import time
import os
from datetime import timedelta

def get_reverse_dns(ip_address, timeout=5):
    try:
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return hostname
    except socket.timeout:
        return None
    except socket.herror:
        return None

# App Setup
app = Flask(__name__)
mysql = MySQL()

# Capture uptime
container_start_time = time.time()

# ip-api key
apikey = base64.b64decode('bVNOZTlhazVYaGRwVkJY').decode()

# back off timer
back_off = None

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

# CORS setup
CORS(app, origins=[
    "http://localhost:5000",
    "http://localhost:8080",
    "https://iploc8.com",
    "https://www.iploc8.com",
    "https://ipdice.com",
    "https://www.ipdice.com"
]) 

# Initial Database healthcheck
healthy = True
try:
    cursor = mysql.connect().cursor()
    geo_count = cursor.execute("SELECT COUNT(*) FROM geo")
    geo_count_result = cursor.fetchone()[0]  # Fetch the count
    if geo_count_result == 0:
        healthy = False
        logging.warning("table geo empty")
except Exception as e:
    healthy = False
    logging.warning("table geo failed sql call")

try:
    cursor = mysql.connect().cursor()
    asn_count = cursor.execute("SELECT COUNT(*) FROM asn")
    asn_count_result = cursor.fetchone()[0]  # Fetch the count
    if asn_count_result == 0:
        healthy = False
        logging.warning("table asn empty")
except Exception as e:
    healthy = False
    logging.warning("table asn failed sql call")

try:
    cursor = mysql.connect().cursor()
    isp_count = cursor.execute("SELECT COUNT(*) FROM isp")
    isp_count_result = cursor.fetchone()[0]  # Fetch the count
    if isp_count_result == 0:
        healthy = False
        logging.warning("table isp empty")
except Exception as e:
    healthy = False
    logging.warning("table isp failed sql call")

try:
    cursor = mysql.connect().cursor()
    corporate_count = cursor.execute("SELECT COUNT(*) FROM corporate")
    corporate_count_result = cursor.fetchone()[0]  # Fetch the count
    if corporate_count_result == 0:
        healthy = False
        logging.warning("table corporate empty")
except Exception as e:
    healthy = False
    logging.warning("table corporate failed sql call")

try:
    cursor = mysql.connect().cursor()
    city_count = cursor.execute("SELECT COUNT(*) FROM city")
    city_count_result = cursor.fetchone()[0]  # Fetch the count
    if city_count_result == 0:
        healthy = False
        logging.warning("table city empty")
except Exception as e:
    healthy = False
    logging.warning("table city failed sql call")

# Home page
@app.route('/')
def welcome_home():
    return send_from_directory('static', 'index.html') 
    
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
    if not healthy:
        return jsonify({'error': 'Database health check failed'}), 500  # Return HTTP 500
    # Database health check
    try:
        cursor = mysql.connect().cursor()
        countries_count = cursor.execute("SELECT COUNT(*) FROM countries")
        countries_count_result = cursor.fetchone()[0]  # Fetch the count
    except Exception as e:
        print(f"Error encountered: {e}") # Log error
        return jsonify({'error': 'Database query failed'}), 500  # Return HTTP 500
    if countries_count_result == 0:
        return jsonify({'error': 'Empty table countries'}), 500  # Return HTTP 500

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
            SELECT vendor, type 
            FROM corporate 
            WHERE start <= %s AND end >= %s
        """, (ip_decimal, ip_decimal))
        corporate_result = cursor.fetchone()
        corporate_proxy = corporate_result[1] if corporate_result else None
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
    if corporate_proxy:
        output_data['corporate_proxy'] = corporate_proxy
    return jsonify(output_data)

# API Route (/api/v2/login)
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

# API Route (/api/v2/ip)
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
        ip = ipaddress.ip_address(user_ip)
        ip_decimal = int(ip)
    except ValueError:
        return jsonify({'error': 'Invalid IP address'}), 400
    try:
        cursor = mysql.connect().cursor()
        cursor.execute("""
            SELECT c.country_code, g.Name AS country_long, c.state1, c.state2, c.city, c.postcode, c.latitude, c.longitude, c.timezone
            FROM city c
            LEFT JOIN countries g on c.country_code = g.Code
            WHERE start <= %s AND end >= %s
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
        cursor.execute("""
            SELECT description 
            FROM isp 
            WHERE start <= %s AND end >= %s
        """, (ip_decimal, ip_decimal))
        isp_result = cursor.fetchone()
        isp = isp_result[0] if isp_result else "Unidentified"
        cursor.execute("""
            SELECT vendor, type 
            FROM corporate 
            WHERE start <= %s AND end >= %s
        """, (ip_decimal, ip_decimal))
        corporate_result = cursor.fetchone()
        corporate_proxy = corporate_result[1] if corporate_result else None
        cursor.execute("""
            SELECT Sanction FROM sanctions WHERE Country = %s
        """, (country,))
        sanction_result = cursor.fetchone()
        sanction = sanction_result[0] if sanction_result else None
    except Exception as e:
        print(f"Error encountered: {e}")
    finally:
        if cursor:
            cursor.close()  # Ensure cursor is closed
    reverse = get_reverse_dns(user_ip, 4)
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
        "reverse": reverse,
        "attribution": [
            {"name": "db-ip.com", "link": "https://db-ip.com/"},
            {"name": "RouteViews", "link": "https://www.routeviews.org/routeviews/"}
        ]
    }
    if corporate_proxy:
        ip_data['corporate_proxy'] = corporate_proxy
    if sanction:
        output_data['sanction'] = sanction
    return jsonify(ip_data), 200

# API Route (/api/v3/ip)
@app.route('/api/v3/ip/<ip_address>', methods=["GET"])
def get_ip_info(ip_address):
    global back_off
    if back_off and back_off > datetime.datetime.now():
        return jsonify({"error": "Too many requests. Please try again later."}), 429  
    try:
        ip = ipaddress.ip_address(ip_address)
        ip_decimal = int(ip)
    except ValueError:
        return jsonify({'error': 'Invalid IP address'}), 400
    api_url = f"http://ip-api.com/json/{ip_address}?fields=status,message,city,regionName,country,countryCode,zip,isp,org,reverse,mobile,proxy,hosting"
    if back_off:
        time.sleep(0.5 + random.random())
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception if request failed
        data = response.json()
        if data.get('status') == 'fail':
            # Return an error response
            return jsonify({"error": data.get('message', "IP lookup failed")}), 400
        # Process the successful response data
        result = {
            "city": data.get("city"),
            "state": data.get("regionName"),
            "country": data.get("country"),
            "country_code": data.get("countryCode"),
            "zipCode": data.get("zip"),
            "isp": data.get("isp"),
            "organization": data.get("org"),
            "reverseLookup": data.get("reverse"),
            "isMobile": data.get("mobile"),
            "isProxy": data.get("proxy"),
            "isHosting": data.get("hosting"),
            "attribution": [
                {"name": "ip-api.com", "link": "https://www.ip-api.com/"}
            ]
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            # Handle 429: Implement back-off strategy
            if back_off:
                back_off = datetime.datetime.now() + datetime.timedelta(seconds=100)
            else:
                back_off = datetime.datetime.now() + datetime.timedelta(seconds=10)
            return jsonify({"error": "Too many requests. Please try again later."}), 429  
        else:
            # Handle other HTTP errors
            return jsonify({"error": "Error fetching IP data"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error fetching IP data"}), 500
    try:
        cursor = mysql.connect().cursor()
        cursor.execute("""
            SELECT vendor, type 
            FROM corporate 
            WHERE start <= %s AND end >= %s
        """, (ip_decimal, ip_decimal))
        corporate_result = cursor.fetchone()
        corporate_proxy = corporate_result[1] if corporate_result else None
        cursor.execute("""
            SELECT Sanction FROM sanctions WHERE Country = %s
        """, (country_code,))
        sanction_result = cursor.fetchone()
        sanction = sanction_result[0] if sanction_result else None
    except Exception as e:
        print(f"Error encountered: {e}")
        sanction = None
        corporate_proxy = None
    finally:
        if cursor:
            cursor.close()  # Ensure cursor is closed
    if corporate_proxy:
        result['corporate_proxy'] = corporate_proxy
    if sanction:
        result['sanction'] = sanction
    back_off = None
    return jsonify(result), 200  # Return the processed data

# API Route (/api/v4/ip)
@app.route('/api/v4/ip/<ip_address>', methods=["GET"])
def get_ip_info_v4(ip_address):
    try:
        ip = ipaddress.ip_address(ip_address)
        ip_decimal = int(ip)
    except ValueError:
        return jsonify({'error': 'Invalid IP address'}), 400
    api_url = f"https://pro.ip-api.com/json/{ip_address}?fields=status,message,city,regionName,country,countryCode,zip,isp,org,reverse,mobile,proxy,hosting&key={apikey}"    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception if request failed
        data = response.json()
        if data.get('status') == 'fail':
            # Return an error response
            return jsonify({"error": data.get('message', "IP lookup failed")}), 400
        # Process the successful response data
        result = {
            "city": data.get("city"),
            "state": data.get("regionName"),
            "country": data.get("country"),
            "country_code": data.get("countryCode"),
            "zipCode": data.get("zip"),
            "isp": data.get("isp"),
            "organization": data.get("org"),
            "reverseLookup": data.get("reverse"),
            "isMobile": data.get("mobile"),
            "isProxy": data.get("proxy"),
            "isHosting": data.get("hosting"),
            "attribution": [
                {"name": "ip-api.com", "link": "https://www.ip-api.com/"}
            ]
        }
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error fetching IP data"}), 500
    try:
        cursor = mysql.connect().cursor()
        cursor.execute("""
            SELECT vendor, type 
            FROM corporate 
            WHERE start <= %s AND end >= %s
        """, (ip_decimal, ip_decimal))
        corporate_result = cursor.fetchone()
        corporate_proxy = corporate_result[1] if corporate_result else None
        cursor.execute("""
            SELECT Sanction FROM sanctions WHERE Country = %s
        """, (country_code,))
        sanction_result = cursor.fetchone()
        sanction = sanction_result[0] if sanction_result else None
    except Exception as e:
        print(f"Error encountered: {e}")
        sanction = None
        corporate_proxy = None
    finally:
        if cursor:
            cursor.close()  # Ensure cursor is closed
    if corporate_proxy:
        result['corporate_proxy'] = corporate_proxy
    if sanction:
        result['sanction'] = sanction
    return jsonify(result), 200  # Return the processed data

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
