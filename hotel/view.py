from flask import Flask, render_template, request, json, redirect, url_for, make_response,jsonify
from hotel import app
from hotel.util import InsertQuery, InsertQueryKV,SelectQuery,buildQueryBreakfasts,buildQuerySerices,buildQueryServiceBreakfasts
import hashlib
import json as js
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
            user = {"Name": "Sam Azouzi","Age":20}
            return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('home'))

@app.route("/search-page", methods=['GET'])
def search_page():
    return render_template('search.html')

@app.route("/search", methods=['POST'])
def search():
    #Need to sanitize this data
    #IF THERE ARE ANY ERRORS IN THE QUERY, ADD A STRING TO THE ERROR LIST DESCRIBING THE ERROR
    #e.g. "Incorrect Date Format"
    error = []
    countries = request.form['country']
    print(countries)
    states = request.form['state']
    states_arr = states.split(",")
    print(states)
    #entry and depart can be delimited by a -
    #NEED TO CHECK ACCURACY OF THIS, IF THE YEAR HAS MORE THAN 4 DIGITS -> Incorrect
    entry = request.form['entry']

    val = request.form.to_dict()
    print(entry)
    depart = request.form['depart']
    print(depart)
    minCost = request.form['min']
    if minCost == "" or minCost == None:
        minCost = 0
        val['min'] = 0   
    print(minCost)
    maxCost = request.form['max']
    if maxCost == "" or maxCost == None:
        maxCost = 999
        val['max'] = 0
    print(maxCost)
    services = request.form.getlist('service')
    for x in services:
        print(x)
    breakfasts = request.form.getlist('breakfast')
    for x in breakfasts:
        print(x)
    results = None

    val["services"] = services
    val["breakfasts"] = breakfasts
    sqlst = "SELECT * FROM Room r INNER JOIN Hotel h on h.HotelId = r.HotelId WHERE h.Country IN (%s) and h.state IN (%s) AND r.price >%s and r.price <%s GROUP BY h.Hotelid"
    if services !=  [] and breakfasts != []:
        sqlst = buildQueryServiceBreakfasts(services,breakfasts)
        print (sqlst)
        results = SelectQuery(sqlst,(countries,states,minCost,maxCost),one = False)



    elif services:

        sqlst = buildQuerySerices(services) 
        results = SelectQuery(sqlst,(countries,states,minCost,maxCost),one= False)
        
    elif breakfasts:
        sqlst = buildQueryBreakfasts(breakfasts)
        results = SelectQuery(sqlst,(countries,states,minCost,maxCost),one= False)
    else:
        results = SelectQuery(sqlst,(countries,states,minCost,maxCost),one= False)




    if error:
        return render_template('search.html',error=error,length=len(error))
    #Apply all these values into the query and rename query to be a list of dictionaries for all the info the hotel has in each dictionary
    return render_template('search.html',result=results,form_data= js.dumps(val))

@app.route("/account_settings", methods=['GET','POST'])
def account():
    if request.method == 'GET':
        #set variable info = the query that gives us the information of the user given session cookies
        user_id = request.cookies.get('Session')
        if request.form['submit'] != 'edit':
            if user_id:
                #info = user information
                info = {"name":"Sam Azouzi","email":"sazouzi21@gmail.com","phone":"1234567891234"}
                #credit_list will be a list of all this users credit cards
                credit_list = [
                {"cnumber":"12345617",
                 "expdate":"10/30/2017",
                 "type":"D",
                 "seccode":"123",
                 "name":"Sam Azouzi",
                 "addr":"78 Woodbridge Lane something something"},
                {"cnumber":"123412317",
                 "expdate":"10/31/2017",
                 "type":"C",
                 "seccode":"123",
                 "name":"Samd Azouzi",
                 "addr":"21 Woodbridge Lane something something"},
                {"cnumber":"321245617",
                 "expdate":"11/30/2017",
                 "type":"D",
                 "seccode":"113",
                 "name":"Sazouzi",
                 "addr":"98 Woodbridge Lane something something"}
                ]
                return render_template('account.html',info=info,credit_list=credit_list)
        else: # ??
            pass #Continue
    else:
        user_id = request.cookies.get('Session')
        if user_id:
            return

app.route('/registration', methods=['POST'])
def register_account():
    m = hashlib.sha1()
    try:
        args = {
            "Email": request.form['email'],
            "Password": m.update(request.form['password'].encode('utf-8')).hexdigest()
        }
        print(args)
        # InsertQueryKV("Account", args) # Insert into db
        return "200"
    except:
        return "Error: Bad values"
@app.route('/register', methods=['GET'])
def register_page():
    # return registration page
    pass

@app.route('/profile', methods=['GET'])
def get_profile():
    user = request.cookies.get('username')

@app.route('/profileedit', methods=['POST'])
def edit_profile():
    m = hashlib.sha1()
    try:
        password = m.update(request.form['password'].encode('utf-8').hexdigest())
        update_cards = request.form['cards'] # perform set operation to figure out which cards to add, update, and delete
        existing_cards = [] # getCreditCardsForUser(
        update_card_nos = set([card['card_no'] for card in existing_cards])
        existing_card_nos = set([card['card_no'] for card in update_card_nos])
        add_cards = update_card_nos - existing_card_nos # add these cards to db
        update_cards = update_card_nos & existing_card_nos # update these cards in db
        remove_cards = existing_card_nos - update_card_nos # remove these cards in db
        return "OK"
    except:
        return "ERROR"

@app.route('/browse', methods=['GET'])
def browse():
    pass

@app.route('/hotel-page', methods=['POST'])
def hotel_page():
    val = json.loads(request.form['hotel'])
    #return (val['results']['country'])
    hotelInfo = {}
    hotelid = val["id"]
    sql = "SELECT * FROM Hotel h WHERE h.HotelId=(%s)"
    results = SelectQuery(sql,(hotelid),one = False)

    return render_template('hotel-page', hotelInfo=hotelInfo)

@app.route('/reserve', methods=['POST'])
def reserve():
    pass

@app.route('/registerhotel', methods=['POST'])
def register_hotel():
    pass
