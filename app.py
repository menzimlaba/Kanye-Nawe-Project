import os
import re
from flask import Flask, jsonify, render_template, request, g, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Define the path to the SQLite database
DATABASE = os.path.join(app.root_path, 'data', 'kanye.db')

# Function to get the SQLite database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Teardown function to close the database connection at the end of each request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
@app.route('/pricing', methods=['POST'])
def show_pricing():
  return render_template('pricing.html')
# Route to display the home page
@app.route('/', methods=['GET'])
def show_home():
    return render_template('index.html')

# Route to process the payment form submission
@app.route('/process_payment', methods=['POST'])
def process_payment():
    id_number = request.form['idNumber']
    card_number = request.form['cardNumber']
    expiration_month = request.form['expirationMonth']
    expiration_year = request.form['expirationYear']
    cvv = request.form['cvv']

    # Validate form data
    errors = []
    if not re.match(r"^\d{13}$", id_number):
        errors.append("ID Number must be 13 digits.")
    if not re.match(r"^\d{16}$", card_number.replace(" ", "")):
        errors.append("Card Number must be 16 digits.")
    if not (1 <= int(expiration_month) <= 12):
        errors.append("Invalid Expiration Month.")
    if int(expiration_year) < 2024:
        errors.append("Invalid Expiration Year.")
    if not re.match(r"^\d{3}$", cvv):
        errors.append("CVV must be 3 digits.")

    if errors:
        for error in errors:
            flash(error)
        return redirect(url_for('show_payment'))

    # Get database connection
    db = get_db()
    c = db.cursor()

    # Insert payment data into the payments table
    try:
        c.execute("INSERT INTO payments (id_number, card_number, expiration_month, expiration_year, cvv) VALUES (?, ?, ?, ?, ?)",
                  (id_number, card_number, expiration_month, expiration_year, cvv))
        db.commit()
    except Exception as e:
        db.rollback()
        flash("An error occurred while processing your payment. Please try again.")
        return redirect(url_for('show_payment'))

    # Redirect to a thank you page
    return jsonify(success=True)

# Route to display the thank you page
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# Route to display the payment page
@app.route('/pric', methods=['GET'])
def show_payment():
    return render_template('payment.html')

if __name__ == '__main__':
    app.run(debug=True)
