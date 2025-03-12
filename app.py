from flask import Flask, render_template, request
import random
import string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html'), 200

@app.route('/create_password', methods=['POST'])
def create_password():
    # Default to an empty password if something fails
    password = ''

    # Safely parse user input for length
    try:
        length = int(request.form.get('length', 8))
    except ValueError:
        length = 8

    # Build the character set based on checkboxes
    selected_chars = ""

    if request.form.get('use_upper'):
        selected_chars += string.ascii_uppercase  # A-Z
    if request.form.get('use_lower'):
        selected_chars += string.ascii_lowercase  # a-z
    if request.form.get('use_digits'):
        selected_chars += string.digits           # 0-9
    if request.form.get('use_punct'):
        selected_chars += string.punctuation      # !"#$%&'()

    # If user didn't select any option, fall back to something
    if not selected_chars:
        selected_chars = string.ascii_letters + string.digits

    # Generate the password
    password_list = random.choices(selected_chars, k=length)
    password = ''.join(password_list)

    return render_template('index.html', generated_password=password)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
