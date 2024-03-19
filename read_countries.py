import csv
import mysql.connector  # You'll need to install this

# Database connection details
config = {
    'user': 'your_database_user',
    'password': 'your_database_password',
    'host': 'your_database_host', 
    'database': 'your_database_name'
}

# CSV file path
csv_file_path = 'countries.csv'

# SQL Insert query
insert_query = """
    INSERT INTO countries (Name, Code)
    VALUES (%s, %s)
"""

try:
    # Connect to the database
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    # Open and read the CSV
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip header row (if you have one)

        # Iterate through rows and insert
        for row in reader:
            cursor.execute(insert_query, row)

    # Commit changes
    db.commit()

except mysql.connector.Error as error:
    print("Database error: {}".format(error))

finally:
    # Close database resources
    if db.is_connected():
        cursor.close()
        db.close()
