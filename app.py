from flask import Flask, request, jsonify, redirect, url_for, send_file
from flask_cors import CORS
import yagmail
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import secrets
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for your Flask app

# Set the secret key for the session
app.secret_key = 'inderkiran@24'

# Email configuration
sender_email = 'inderkiran20233@gmail.com'  # replace with your email
app_password = 'krhu cexv lyue dmnz'  # replace with your generated app password

# Google Sheets configuration
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('bgmi-registration-e1d0ccd3b338.json', scope)
gc = gspread.authorize(credentials)
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1Y02mNph9lvPE-LmoJ2Ks6BZ4T84_HPF-O1toDIqYe3w/edit#gid=0'
sh = gc.open_by_url(spreadsheet_url)
worksheet = sh.get_worksheet(1)  # Accessing the second sheet (index 1)

# Dictionary to store email verification tokens
email_tokens = {}


# Function to generate a random token
def generate_token():
    return secrets.token_hex(16)


# Function to generate an authentication link with token
def generate_auth_link(token, team_name, college_name, leader_name, leader_contact, leader_email, robot_drive,
                       member_details):
    # Replace spaces with underscores in each parameter
    team_name = team_name.replace(' ', '_')
    college_name = college_name.replace(' ', '_')
    leader_name = leader_name.replace(' ', '_')
    leader_contact = leader_contact.replace(' ', '_')  # Added space
    leader_email = leader_email.replace(' ', '_')  # Added space
    robot_drive = robot_drive.replace(' ', '_')  # Added space

    # Construct the authentication link with modified parameters
    auth_link = f'https://robowarsregistration.vercel.app/verify/{token}?team_name={team_name}&college_name={college_name}&leader_name={leader_name}&leader_contact={leader_contact}&leader_email={leader_email}&robot_drive={robot_drive}'

    # Append member details to the authentication link
    for i, member in enumerate(member_details, start=1):
        name = member['name'].replace(' ', '_')
        contact = member['contact'].replace(' ', '_')
        email = member['email'].replace(' ', '_')
        auth_link += f'&member{i}_name={name}&member{i}_contact={contact}&member{i}_email={email}'

    return auth_link


# Route to handle form submission and send authentication email
@app.route('/submit', methods=['POST'])
def send_email():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        college_name = request.form.get('college_name')
        leader_name = request.form.get('leader_name')
        leader_contact = request.form.get('leader_contact')
        leader_email = request.form.get('leader_email')
        robot_drive = request.form.get('robot_drive')

        # Extract details of other members
        member_details = []
        for i in range(1, 5):  # Assuming there are up to 4 team members
            member_name = request.form.get(f'member{i}_name')
            member_contact = request.form.get(f'member{i}_contact')
            member_email = request.form.get(f'member{i}_email')
            if member_name and member_contact and member_email:
                member_details.append({
                    'name': member_name,
                    'contact': member_contact,
                    'email': member_email
                })

        token = generate_token()
        email = leader_email  # Assuming leader's email is used for verification
        email_tokens[email] = token

        # Construct authentication link with all required parameters
        auth_link = generate_auth_link(token, team_name, college_name, leader_name, leader_contact, leader_email,
                                       robot_drive, member_details)
        subject = 'Authentication Link'
        body = f'''
                <html>
                <head>
                    <title>{subject}</title>
                </head>
                <body>
                    <h2>{subject}</h2>
                    <p>Click the button below to authenticate:</p>
                    <a href="{auth_link}" >Authenticate</a>
                </body>
                </html>
                '''

        # Create yagmail SMTP client
        yag = yagmail.SMTP(sender_email, app_password)

        # Send the email
        yag.send(to=email, subject=subject, contents=body)

        return redirect(url_for('email_sent'))


# Route to inform user that email has been sent
@app.route('/email_sent')
def email_sent():
    return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'email_sent.html'))


# Route to handle verification
@app.route('/verify/<token>', methods=['GET'])
def verify(token):
    if token:
        # Check if the token exists in email_tokens
        if token in email_tokens.values():
            # Get the email associated with the token
            email = [key for key, value in email_tokens.items() if value == token][0]

            # Retrieve data from the query parameters
            team_name = request.args.get('team_name')
            college_name = request.args.get('college_name')
            leader_name = request.args.get('leader_name')
            leader_contact = request.args.get('leader_contact')
            leader_email = request.args.get('leader_email')
            robot_drive = request.args.get('robot_drive')

            # Check if all required parameters are present
            if team_name and college_name and leader_name and leader_contact and leader_email and robot_drive:
                # Append new data to Google Sheets
                new_row = [team_name, college_name, leader_name, leader_contact, leader_email, robot_drive]

                # Extract member details
                for i in range(1, 5):  # Assuming there are up to 4 team members
                    member_name = request.args.get(f'member{i}_name')
                    member_contact = request.args.get(f'member{i}_contact')
                    member_email = request.args.get(f'member{i}_email')
                    if member_name and member_contact and member_email:
                        new_row.extend([member_name, member_contact, member_email])
                    else:
                        new_row.extend(['', '', ''])  # Append empty strings if data is missing

                # Append the row to the worksheet
                worksheet.append_row(new_row)

                # Remove token from dictionary after verification
                del email_tokens[email]

                return jsonify({'message': 'Authentication successful. Data stored into Google Sheets.'})
            else:
                return jsonify({'message': 'Missing parameters in the verification link.'}), 400
        else:
            return jsonify({'message': 'Invalid or expired verification link.'}), 400
    else:
        return jsonify({'message': 'No token provided.'}), 400