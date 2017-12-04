from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from hotel import app
from hotel.util import isNum, buildCheckoutData, InsertQuery, InsertQueryKV, SelectQuery, buildQueryBreakfasts, buildQuerySerices, buildQueryServiceBreakfasts
import hashlib
import json
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
        #This will contain checkout information as well
        response.set_cookie('Session', userid)
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

'''
------------------------------------------------------------------------------------------
------------------------------------ SQL QUERIES USED ------------------------------------
------------------------------------------------------------------------------------------
(In order)

SELECT Name From Customer WHERE Email = email;
SELECT * FROM Reservation WHERE Cid IN (SELECT Cid FROM Customer WHERE Email = email); (Reservation)
SELECT * FROM Reserves WHERE InvoiceNo IN (Reservation.InvoiceNo);
SELECT * FROM Service WHERE HotelId IN (Reservation.HotelId);
SELECT * FROM Hotel WHERE HotelId IN (Reservation.HotelID);
'''
@app.route("/dashboard", methods=['GET'])
def dashboard():
    email = request.args.get('email')
    return render_template('dashboard.html', user=user)
    '''
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
        return redirect(url_for('home'))'''

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
        val['max'] = 999
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
    return render_template('search.html',result=results,form_data= json.dumps(val))

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
    entry = val["results"]["entry"]
    depart = val["results"]["depart"]
    sqlst = "SELECT * FROM Room r1  WHERE r1.HotelId = %s AND r1.price >%s and r1.price <%s AND NOT EXISTS (SELECT * FROM Reserves res WHERE res.HotelID = r1.HotelID and res.RoomNo = r1.RoomNo and %s between res.InDate and res.OutDate and %s between res.InDate and res.OutDate) "
    results = SelectQuery(sqlst,(val["id"],val["results"]["min"],val["results"]["max"],entry,depart),one= False)
    sqlst = "SELECT *,o.Discount as dis FROM Room r1, Offerroom o WHERE r1.HotelId = %s and r1.price >%s and r1.price <%s AND NOT EXISTS (SELECT * FROM Reserves res WHERE res.HotelID = r1.HotelID and res.RoomNo = r1.RoomNo and %s between res.InDate and res.OutDate and %s between res.InDate and res.OutDate) and r1.HotelId = o.HotelId and r1.RoomNo = o.RoomNo  and %s between o.SDate and o.EDate and %s between o.SDate and o.EDate"
    results2 = SelectQuery(sqlst,(val["id"],val["results"]["min"],val["results"]["max"],entry,depart,entry,depart),one= False)
    if len(results2) == 0:
        for i in range(0,len(results)):
            results[i]["Discount"] = 0
    else:
        for i in range(0,len(results)):
            results[i]["Discount"] = 0
            for y in range(0,len(results2)):
                if results[i]["RoomNo"] == results2[y]["RoomNo"]:
                    print(results2[y]["dis"])
                    print(i)
                    results[i]["Discount"] = results2[y]["dis"] * 100
                    break
                else:
                    results[i]["Discount"] = 0



    hotelInfo = {}
    for x in range(len(results)):
        sql = "SELECT re.Rating as rate, re.TextComment as tc FROM Review re, RoomReview ro WHERE ro.ReviewId = re.ReviewId and ro.RoomNo = %s and re.HotelId = %s"
        re = SelectQuery(sql,(results[x]["RoomNo"],val["id"]),one=False)
        results[x]["Reviews"] = re;
    hotelInfo["rooms"] = results
    hotelid = val["id"]
    sql = "SELECT BPrice as b FROM Breakfast WHERE Breakfast.HotelId = %s"
    results = SelectQuery(sql,(hotelid),one=False)
    breakfastList = []
    for x in range(len(val["results"]["breakfasts"])):
        breakfastList.append({"BType":val["results"]["breakfasts"][x],"BPrice":results[x]["b"]})
    #hotelInfo['breakfast'] = val["results"]["breakfasts"]
    hotelInfo['breakfast'] = breakfastList


    sql = "SELECT BType From Breakfast Where hotelId = %s"
    results = SelectQuery(sql,(hotelid),one=False)
    breakfastReviewList = []
    for x in range(len(results)):
        sql = "SELECT re.Rating as rate, re.TextComment as tc FROM Review re, BreakfastReview br WHERE re.ReviewId = br.ReviewId and br.HotelId = %s and br.BType = %s"
        re = SelectQuery(sql,(hotelid,results[x]["BType"]),one=False)
        breakfastReviewList.append((results[x]["BType"],re))

    hotelInfo["breakfastReviews"] = breakfastReviewList
    sql = "SELECT SCost as s FROM Service WHERE Service.HotelId = %s"
    results = SelectQuery(sql,(hotelid), one=False)
    serviceList = []
    for x in range(len(val["results"]["services"])):
        serviceList.append({"SType":val["results"]["services"][x],"SCost":results[x]["s"]})
    #hotelInfo['service'] = val["results"]["services"]
    hotelInfo['service'] = serviceList


    sql = "SELECT SType From Service Where hotelId = %s"
    results = SelectQuery(sql,(hotelid),one=False)
    serviceReviewList = []
    for x in range(len(results)):
        sql = "SELECT re.Rating as rate, re.TextComment as tc FROM Review re, ServiceReview sr WHERE re.ReviewId = sr.ReviewId and sr.HotelId = %s and sr.SType = %s"
        re = SelectQuery(sql,(hotelid,results[x]["SType"]),one=False)
        serviceReviewList.append((results[x]["SType"],re))

    hotelInfo["serviceReviews"] = serviceReviewList


    minVal = int(val["results"]["min"])
    maxVal = int(val["results"]["max"])
    sql = "SELECT * FROM Hotel h WHERE h.HotelId=(%s)"
    results = SelectQuery(sql,(hotelid))
    hotelInfo['address'] = results["Street"] +" "+results["State"] +" "+ results["City"] +" "+ str(results["Zip"]) +" "+ results["Country"]
    hotelInfo["phone"] = results["PhoneNo"]
    hotelInfo["min"] = minVal
    hotelInfo["max"] = maxVal
    hotelInfo["entry"] = entry
    hotelInfo["depart"] = depart
    hotelInfo["id"] = hotelid
    return render_template('hotel-page.html', hotelInfo=hotelInfo)

@app.route('/add_checkout', methods=['POST'])
def add_to_checkout():
    #check to see if person is logged in:
    #user_id = request.cookies.get('Session')
    user_id = 2
    checkout = request.cookies.get('Checkout')
    response = redirect(url_for("search_page"))
    #THIS IS FOR TESTING!! WHEN REGISTRATION IS DONE THIS WILL CHANGE
    if user_id:
        checkoutList = request.form.getlist('add_check')
        listOfRooms = []
        for x in checkoutList:
            print(x)
            listOfRooms.append(json.loads(x))
        if checkout:
            checkout = json.loads(checkout)
            for y in listOfRooms:
                if y in checkout:
                    continue
                checkout.append(y)

            response.set_cookie('Checkout', json.dumps(checkout))
        else:
            listOfRooms = json.dumps(listOfRooms)
            response.set_cookie('Checkout', listOfRooms)
        return response
    else:
        #return registration htmls
        pass

@app.route('/checkout', methods=["GET","POST"])
def checkout():
    #user_id = request.cookies.get('Session')
    user_id = 2
    checkout = json.loads(request.cookies.get('Checkout'))
    if request.method == 'GET':
        if user_id:
            listInCheckout = buildCheckoutData(checkout)

            return render_template("checkout.html",CL=listInCheckout,initial="True")
        else:
            #reroute to register
            pass
    elif request.method == 'POST':
        #user_id = request.cookies.get('Session')
        user_id = 2
        checkout = json.loads(request.cookies.get('Checkout'))
        try:
            remove = request.form["remove"]
        except:
            remove = None
        if user_id:
            if remove:
                response = redirect(url_for("checkout"))
                remove = json.loads(remove)
                for x in checkout:
                    if remove["id"] == x["id"] and remove["roomNo"] == x["roomNo"]:
                        checkout.remove(x)
                        break
                response.set_cookie('Checkout',json.dumps(checkout))
                return response
            else:
                listOfData = buildCheckoutData(checkout)
                #First Check Capacity
                try:
                    cap = request.form["cap"]
                    cap = int(cap)
                except ValueError:
                    return render_template("checkout.html",CL=listOfData,initial=True,capError1=True)
                total = 0
                trueCap = 0
                for x in listOfData:
                    total += x['Price'] - (x['Price'] * x['discount'])
                    trueCap += x['Capacity']
                if cap > trueCap:
                    return render_template("checkout.html",CL=listOfData,initial=True,capError2=True)


                allB = request.form.getlist("bnum")
                if "" in allB:
                    return render_template("checkout.html",CL=listOfData,initial=True,valError=True)
                countB = 0
                for x in allB:
                    if not isNum(x):
                        return render_template("checkout.html",CL=listOfData,initial=True,valError=True)

                for x in listOfData:
                    for y in x['breakfasts']:
                        y['mult'] = []

                for x in listOfData:
                    for y in x['breakfasts']:
                        total += (y['BPrice'] * int(allB[countB]))
                        y['mult'].append(allB[countB])
                        countB+=1




                re = request.form.getlist("sChoose")
                allS = []

                for x in re:
                    allS.append(json.loads(x))
                listToAdd = []
                x = 0
                y = 0
                for x in range(len(listOfData)):
                    for y in range(len(listOfData[x]['services'])):
                        for z in allS:
                            if listOfData[x]['HotelId'] == z['HotelId'] and listOfData[x]['RoomNo'] == z['RoomNo']:
                                if listOfData[x]['services'][y]['SType'] == z['SType'] and listOfData[x]['services'][y] not in listToAdd:
                                    listToAdd.append(listOfData[x]['services'][y])
                    listOfData[x]['services'] = listToAdd
                    listToAdd = []



                for x in listOfData:
                    for y in x['services']:
                        total += y['SCost']


                sql = "SELECT * FROM CreditCards WHERE CreditCards.Cid = %s"
                creditCards = SelectQuery(sql,(user_id),one=False)
                cc=True
                if len(creditCards) == 0:
                    cc=False

                #NEED TO ADD TO RESERVATION WHEN THEY MAKE PAYMENT, ADD ALL THE ROOM TO ROOM RESERVES!!!!!

                return render_template("checkout.html",CL=listOfData,total=total,cc=cc,creditCards=creditCards,initial=False)







@app.route('/registerhotel', methods=['POST'])
def register_hotel():
    pass
