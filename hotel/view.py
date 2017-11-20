from flask import Flask, render_template, request, json
from hotel import app
@app.route('/')
def home():
    return render_template('index.html')


#@app.route('/registration')

#@app.route('/register')

#@app.route('/profile')

#@app.route('/profile-edit')

#@app.route('/browse')

#@app.route('/reserve')

#@app.route('/registerHotel')
