from flask import Flask, render_template, request, json, redirect, url_for, make_response
from hotel import app
@app.route('/')
def home():
    return render_template('index.html',incorrect=False,logoff=False)

@app.route('/authorize', methods=['POST'])
def authorize_credentials():
    username = request.form['username']
    print(username)
    password = request.form['password']
    print(password)
    info_correct = True
    #Check username and password in the database
    if info_correct:
        response = redirect(url_for("dashboard"))
        #This cookie will be used to check if the person is signed in
        #The way to check if a person is already signed in is to simply do the following
        #username = request.cookies.get('Session')
        #if username
        #So if there is a Session cookie then we can assume that the user already logged in
        #Otherwise they did not
        response.set_cookie('Session', username)
        return response
    else:
        print("Incorrect Information Given")
        return render_template('index.html',incorrect=True,logoff=False)


@app.route('/logoff', methods=['GET'])
def logoff():
    user_id = request.cookies.get('Session')
    if user_id:
        response = make_response(render_template('index.html',incorrect=False,logoff=True))
        response.set_cookie('Session','',expires=0)
        return response


@app.route("/dashboard")
def dashboard():
    user_id = request.cookies.get('Session')
    if user_id:
        #The if statement below would check if the cookie containeed is in the database,
        #if it is you can directory take the user to the dashboard instead of having them login again
        if True:
            #user = {}
            #user will a dictionary that contains all the information from the user
            #that the html will use to display the corresponding data
            user = {"Name": "Sam Azouzi","Age":19}
            return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('home'))

@app.route("/search-page")
def search_page():
    return render_template('search.html')

@app.route("/search", methods=['POST'])
def search():
    #Need to sanitize this data
    query = request.form['search']
    print(query)
    minCost = request.form['min']
    print(minCost)
    maxCost = request.form['max']
    print(maxCost)
    services = request.form.getlist('service')
    for x in services:
        print(x)
    #Apply all these values into the query and rename query to be a list of dictionaries for all the info the hotel has in each dictionary
    hotels = []
    return render_template('search.html',results=resuult)







#@app.route('/registration')

#@app.route('/register')

#@app.route('/profile')

#@app.route('/profile-edit')

#@app.route('/browse')

#@app.route('/reserve')

#@app.route('/registerHotel')
