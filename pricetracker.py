# Install required packages
!pip install flask requests beautifulsoup4 pyngrok

import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template_string
from pyngrok import ngrok
import re
import smtplib
from email.mime.text import MIMEText

# Configure ngrok with your authtoken
!ngrok authtoken 2oQXS0hePEGwf50s0Vg3kYFszQu_4KLzypHTtQon4J8h5ozRh

app = Flask(__name__)

def get_price(url):
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        })

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try multiple selectors for the price element
        price_selectors = [
            '.a-price-whole', '#priceblock_ourprice', '#priceblock_dealprice', '#price_inside_buybox'
        ]

        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.text.strip()
                price_number = re.findall(r'[\d,]+', price_text)
                if price_number:
                    return float(price_number[0].replace(',', ''))
        return None
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def send_email(subject, body, to_email):
    from_email = "lakshmanvirijala34@gmail.com"
    from_password = "rmoq fglv gpxw derv"
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/')
def index():
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Price Tracker</title>
        <style>
            /* Styling */
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; }
            h1 { text-align: center; margin-top: 50px; color: #4CAF50; }
            .container { max-width: 600px; margin: auto; padding: 20px; background-color: #fff; }
            form { display: flex; flex-direction: column; gap: 15px; }
            input, button { padding: 10px; font-size: 16px; border-radius: 5px; }
            button { background-color: #4CAF50; color: white; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Price Tracker</h1>
        <div class="container">
            <form id="priceForm">
                <input type="text" id="url" placeholder="Enter product URL" required>
                <input type="number" id="target_price" placeholder="Enter target price" required>
                <input type="email" id="email" placeholder="Enter your email" required>
                <button type="submit">Track Price</button>
            </form>
            <div id="response"></div>
        </div>
        <script>
            document.getElementById('priceForm').onsubmit = async function(event) {
                event.preventDefault();
                const url = document.getElementById('url').value;
                const targetPrice = document.getElementById('target_price').value;
                const email = document.getElementById('email').value;
                const response = await fetch('/track', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, target_price: targetPrice, email })
                });
                const result = await response.json();
                document.getElementById('response').innerText = result.message;
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/track', methods=['POST'])
def track_price():
    data = request.get_json()
    url = data['url']
    target_price = float(data['target_price'])
    email = data['email']

    current_price = get_price(url)
    if current_price is not None:
        if current_price <= target_price:
            send_email("Price Drop Alert", f"The price dropped to ₹{current_price}!\nCheck the product here: {url}", email)
            return jsonify({"message": f"Email sent! Current price: ₹{current_price}"}), 200
        else:
            return jsonify({"message": f"Current price: ₹{current_price}. Price has not dropped."}), 200
    return jsonify({"message": "Unable to fetch the price. Please try again later."}), 500

if __name__ == "__main__":
    # Start ngrok
    public_url = ngrok.connect(5000)
    print(" * ngrok tunnel:", public_url)
    app.run(port=5000)

