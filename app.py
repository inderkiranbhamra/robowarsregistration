from flask import Flask, request, jsonify
from flask_cors import CORS
import yagmail
import mysql.connector
import secrets
from urllib.parse import urlencode

app = Flask(__name__)
CORS(app)

app.secret_key = 'inderkiran@24'


# Email configuration
sender_email = 'hackoverflow@cumail.in'
app_password = 'lgde lflp hmgu krrd'

email_tokens = {}


def generate_token():
    return secrets.token_hex(16)


def generate_auth_link(token, data):
    auth_link = f'https://robowarsregistration.vercel.app/verify/{token}?'
    auth_link += urlencode(data)
    return auth_link

#
# def check_duplicate_email(data):
#     email_set = set()
#     emails = [data['leader_email'], data['p2_email'], data['p3_email'], data['p4_email']]
#     for email in emails:
#         if email in email_set:
#             print("Duplicate email detected:", email)
#             return True
#         else:
#             email_set.add(email)
#
#     for email in emails:
#         cursor.execute("SELECT * FROM UniqueEmails2 WHERE email = %s", (email,))
#         result = cursor.fetchone()
#         if result:
#             print("Duplicate email detected:", email)
#             return True
#
#     return False


# def check_duplicate_ign(data):
#     ign_set = set()
#     igns = [data['team_name'], data['leader_ign'], data['leader_game_id'], data['leader_id_no'], data['leader_contact'], data['leader_email'], data['p2_ign'], data['p2_game_id'], data['p2_id_no'], data['p2_contact'], data['p3_ign'], data['p3_game_id'], data['p3_id_no'], data['p3_contact'], data['p4_ign'], data['p4_game_id'], data['p4_id_no'], data['p4_contact']]
#     for ign in igns:
#         if ign in ign_set:
#             print("Duplicate IGN detected:", ign)
#             return True
#         else:
#             ign_set.add(ign)
#
#     for ign in igns:
#         cursor.execute("SELECT * FROM UniqueIGN WHERE ign = %s", (ign,))
#         result = cursor.fetchone()
#         if result:
#             print("Duplicate ign detected:", ign)
#             return True
#
#     return False

def check_duplicate_ign(data):
    # MySQL database configuration
    DB_HOST = '217.21.94.103'
    DB_NAME = 'u813060526_robowars'
    DB_USER = 'u813060526_robowars'
    DB_PASSWORD = '135@Hack'

    # Connect to the MySQL database
    conn = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    ign_set = set()
    igns = [data['team_name'], data['leader_contact'], data['leader_email'], data['robot_drive'], data['p2_contact'], data['p2_email'], data['p3_contact'], data['p3_email'], data['p4_contact'], data['p4_email'], data['p5_contact'], data['p5_email']]
    field_names = ['Team Name', 'Leader Contact', 'Leader Email', 'Robot Drive', 'P2 Contact', 'P2 Email', 'P3 Contact', 'P3 Email', 'P4 Contact', 'P4 Email', 'P5 Contact', 'P5 Email']
    duplicate_fields = []

    for i, ign in enumerate(igns):
        if ign in ign_set:
            print("Duplicate IGN detected at field", field_names[i], ":", ign)
            duplicate_fields.append(field_names[i])
        ign_set.add(ign)

    for ign in igns:
        cursor.execute("SELECT * FROM UniqueIGN WHERE ign = %s", (ign,))
        result = cursor.fetchone()
        if result:
            print("Duplicate IGN detected:", ign)
            return True, duplicate_fields, ign

    return False, [], ''


@app.route('/')
def index():
    return 'API is working'


@app.route('/submit', methods=['POST'])
def send_email():
    data = request.get_json()
    token = generate_token()

    # uniqueemails = [data['leader_email'], data['p2_email'], data['p3_email'], data['p4_email']]
    # uniqueigns = [data['leader_ign'], data['p2_ign'], data['p3_ign'], data['p4_ign']]

    # if check_duplicate_email(data):
    #     return jsonify({'message': 'Duplicate email detected.'}), 400

    result, duplicate_fields, duplicate_ign = check_duplicate_ign(data)
    if result:
        if duplicate_fields:
            return jsonify({'message': f'Duplicate data found at {duplicate_fields}: {duplicate_ign}.'}), 400
        else:
            return jsonify({'message': f'Duplicate data found: {duplicate_ign}.'}), 400


    email = data['leader_email']
    email_tokens[email] = token

    auth_link = generate_auth_link(token, data)
    subject = 'Authentication Email for ROBOWARS Registration'
    body = f'''
            <html>
            <head>
                <title>{subject}</title>
            </head>
            <body>
                <h2>Click on the link below to complete your registration:</h2>
                <h2><a href="{auth_link}" >Click Here</a><h2>
            </body>
            </html>
            '''

    yag = yagmail.SMTP(sender_email, app_password)
    yag.send(to=email, subject=subject, contents=body)

    return jsonify({'message': 'Email sent successfully.'})


@app.route('/verify/<token>', methods=['GET'])
def verify(token):
    # MySQL database configuration
    DB_HOST = '217.21.94.103'
    DB_NAME = 'u813060526_robowars'
    DB_USER = 'u813060526_robowars'
    DB_PASSWORD = '135@Hack'

    # Connect to the MySQL database
    conn = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    if token in email_tokens.values():
        emails = [key for key, value in email_tokens.items() if value == token][0]
        data = request.args.to_dict()
        # uniqueemails = [data['leader_email'], data['p2_email'], data['p3_email'], data['p4_email']]
        uniqueigns = [data['team_name'], data['leader_contact'], data['leader_email'], data['robot_drive'], data['p2_contact'], data['p2_email'], data['p3_contact'], data['p3_email'], data['p4_contact'], data['p4_email'], data['p5_contact'], data['p5_email']]

        try:
            for y in uniqueigns:
                cursor.execute("INSERT INTO UniqueIGN (ign) VALUES (%s)", (y,))
            conn.commit()

            # for x in uniqueemails:
            #     cursor.execute("INSERT INTO UniqueEmails2 (email) VALUES (%s)", (x,))
            # conn.commit()

            cursor.execute("INSERT INTO Robowarsregistrations (team_name, college_name, leader_name, leader_contact, leader_email, robot_drive, p2_name, p2_contact, p2_email, p3_name, p3_contact, p3_email, p4_name, p4_contact, p4_email, p5_name, p5_contact, p5_email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (data['team_name'], data['college_name'], data['leader_name'], data['leader_contact'], data['leader_email'], data['robot_drive'], data['p2_name'], data['p2_contact'], data['p2_email'], data['p3_name'], data['p3_contact'], data['p3_email'], data['p4_name'], data['p4_contact'], data['p4_email'], data['p5_name'], data['p5_contact'], data['p5_email']))
            conn.commit()

            del email_tokens[emails]
            return 'Authentication successful. You are now registered for ROBOWARS in gameathon.'
        except mysql.connector.Error as err:
            print("Error inserting data:", err)
            conn.rollback()
            error_message = f"Error inserting data into database: {err}"
            return jsonify({'message': error_message}), 500
    else:
        return jsonify({'message': 'Invalid or expired verification link.'}), 400

