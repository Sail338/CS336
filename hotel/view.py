from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from hotel import app
from hotel.util import isNum, buildCheckoutData, InsertQuery, InsertQueryKV, SelectQuery, SelectQueryKV, buildQueryBreakfasts, buildQuerySerices, buildQueryServiceBreakfasts, ExecuteRaw
import hashlib
import json
import datetime, time
import random

@app.route('/')
def home():
    return render_template('index.html',incorrect=False,logoff=False)

@app.route('/authorize', methods=['POST'])
def authorize_credentials():
    m = hashlib.sha1()
    username = request.form['email']
    print(username)
    password = request.form['password']
    m.update(password.encode('utf-8'))
    user = SelectQueryKV(table="Account", columns="Cid", fields={"Email": email, "Password": m.hexdigest()}, fetch_one=True)
    info_correct = user != None
    #Check username and password in the database
    if info_correct:
        response = redirect(url_for("dashboard"))
        userid = user['Cid']
        response.set_cookie('Session', userid)
        return response
    else:
        print("Incorrect Information Given")
        return render_template('index.html',incorrect=True,logoff=False)

@app.route("/review", methods=['GET'])
def review():
    cid = request.cookies.get("Session")
    title = request.args.get('title')
    data = request.args.get('data').split('-')
    dtype = data[0]
    ext = data[1:]
    print(ext)
    hotelid = ext[1]
    extra = ext[-1]
    return render_template("review.html", title=title, type=dtype, hotelId=hotelid, extra_key=dtype.lower(), extra=extra, max_rating=5)

@app.route("/submitreview", methods=['POST'])
def submit_review():
    print(request.form)
    random.seed(int(time.time()))
    rid = random.randint(1000000, 9999999)
    review = {
        "Cid": request.cookies.get("Session")
        "HotelId": int(request.form['hotelId']),
        "ReviewId": rid,
        "TextComment": request.form['comment'],
        "Rating": int(request.form['rating'])
    }
    InsertQueryKV("Review", review)
    extra = request.form['extra'] if 'extra' in request.form else None
    sReview = {
        "ReviewId": rid,
        "HotelId": request.form['hotelId']
    }
    if request.form['type'] == 'room':
        del sReview['HotelId']
        sReview['RoomNo'] = int(extra)
        InsertQueryKV("RoomReview", sReview)
    elif request.form['type'] == 'hotel':
        pass
    elif request.form['type'] == 'service':
        sReview['SType'] = extra
        InsertQueryKV("ServiceReview", sReview)
    elif request.form['type'] == 'breakfast':
        sReview['BType'] = extra
        InsertQueryKV("BreakfastReview", sReview)
    return redirect('/dashboard', code=302)

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
class HotelR:
    def __init__(self, invoiceNo, hotelId, name, checkRes, rooms, services, breakfasts, total):
        self.name = name
        self.invoiceNo = invoiceNo
        self.hotelId = hotelId
        self.resDate = str(checkRes)
        self.services = services
        self.rooms = rooms
        self.breakfasts = breakfasts
        self.total = total

    def toDict(self):
        dictD = self.__dict__
        dictD['rooms'] = [r.toDict() for r in self.rooms]
        dictD['services'] = [s.toDict() for s in self.services]
        return dictD

class ServiceR:
    def __init__(self, stype, price):
        self.stype = stype
        self.price = price
    def toDict(self):
        return self.__dict__

class RoomR:
    def __init__(self, roomNo, price, checkIn, checkOut):
        self.roomNo = roomNo
        self.price = price
        self.checkIn = str(checkIn)
        self.checkOut = str(checkOut)
    def toDict(self):
        return self.__dict__

class BreakfastR:
    def __init__(self, btype, price, desc):
        self.btype = btype
        self.price = price
        self.desc = desc

@app.route("/login", methods=['GET'])
def login():
    return render_template("login.html")

@app.route("/dashboard", methods=['GET'])
def dashboard():
    cid = request.cookies.get('Session')
    customer = SelectQueryKV("Customer", columns='Name', fields={'Cid': cid}, fetch_one=True)
    reservations = SelectQueryKV("Reservation", fields={'Cid': cid})
    hotels = []
    for r in reservations:
        hotelId = r['HotelId']
        invoiceNo = r['InvoiceNo']
        resDate = r['ResDate']
        totalAmt = r['TotalAmt']
        hotel = SelectQueryKV("Hotel", fields={"HotelId": hotelId}, fetch_one=True)
        # fetches all rooms reserved in the reservation
        reserves = SelectQueryKV("Reserves", fields={"HotelId": hotelId, "InvoiceNo": invoiceNo})
        services = SelectQueryKV("Service", fields={"HotelId": hotelId})
        breakfasts = SelectQueryKV("Breakfast", fields={"HotelId": hotelId})
        rooms = [RoomR(res['RoomNo'],
                 SelectQueryKV("Room", columns="Price", fields={"RoomNo": res['RoomNo'], "HotelId": hotelId}, fetch_one=True)['Price'],
                 res['InDate'], res['OutDate']) for res in reserves]
        services = [ServiceR(s['SType'], s['SCost']) for s in services]
        breakfasts = [BreakfastR(b['BType'], b['BPrice'], b['Description']) for b in breakfasts]
        name = '%s, %s %s, %s %s' % (hotel['Street'], hotel['City'], hotel['State'], hotel['Country'], hotel['Zip'])
        hotels.append(HotelR(invoiceNo, hotelId, name, resDate, rooms, services, breakfasts, totalAmt))
    return render_template('dashboard.html', hotels=hotels)

'''
------------------------------------------------------------------------------------------
------------------------------------ SQL QUERIES USED ------------------------------------
------------------------------------------------------------------------------------------
(In order)

SELECT a.Email, a.Address, c.Name, c.PhoneNo from Account a INNER JOIN Customer c on a.Cid = c.Cid; (Personal)
Select * from CreditCards WHERE Cid = cid; (Credit Cards)
'''
@app.route("/profile", methods=['GET'])
def profile():
    cid = request.cookies.get("Session")
    personalQuery = "SELECT a.Email, a.Address, c.Name, c.PhoneNo from Account a INNER JOIN Customer c on a.Cid = %d and c.Cid = %d" % (cid,cid)
    personal = ExecuteRaw(personalQuery, fetch_one=True)
    personalKV = [(k, personal[k]) for k in ['Name', 'Email', 'Address', 'PhoneNo']]
    creditCards = SelectQueryKV("CreditCards", fields={"Cid": cid})
    creditCardsKV = [[((k,k, cc[k]) if isinstance(k, str) else (k[0], k[1], cc[k[1]])) for k in [('Credit Card Number', 'CNumber'), 'Name',
                                                                          ('Billing Address', 'BillingAddr'), ('CVV', 'SecCode'),
                                                                          'Type', ('Expires', 'ExpDate')]] for cc in creditCards]
    return render_template("profile.html", personal=personalKV, ccs=creditCardsKV)

@app.route('/profileedit', methods=['POST'])
def edit_profile():
    m = hashlib.sha1()
    cid = request.cookies.get("Session")
    updates = {
        "Name": request.form['Name'],
        "Address": request.form['Address'],
        "Email": request.form['Email'],
        "PhoneNo": request.form['PhoneNo']
    }

    security = {
        "Email": request.form["Email"],
        "Address": request.form['Address']
    }
    def toKV(d):
        keys = [k for k in d]
        vals = [d[k] for k in keys]
        return keys, vals
    keys, vals = toKV(updates)
    dataChange = ','.join(['%s="%s"' % (k,v) for k,v in zip(keys, vals)])
    updateStatement = "UPDATE Customer SET %s WHERE Cid=%d" % (dataChange, cid)
    ExecuteRaw(updateStatement)
    keys, vals = toKV(security)
    dataChange = ','.join(['%s="%s"' % (k,v) for k,v in zip(keys, vals)])
    updateStatement = "UPDATE Account SET %s WHERE Cid=%d" % (dataChange, cid)
    ExecuteRaw(updateStatement)
    # password = m.update(request.form['password'].encode('utf-8').hexdigest())
    credit_cards = request.form # perform set operation to figure out which cards to add, update, and delete
    billings = ['%s' % v for v in request.form.getlist("BillingAddr")]
    names = ['%s' % v for v in request.form.getlist("Name")]
    expires = ['%s' % v for v in request.form.getlist("ExpDate")]
    seccodes = ['%s' % v for v in request.form.getlist("SecCode")]
    types = ['%s' % v for v in request.form.getlist("Type")]
    creditNumbers = [str(v) for v in request.form.getlist("CNumber")]
    cids = [cid] * len(names)
    keys = ', '.join(["BillingAddr", "Name", "ExpDate", "SecCode", "Type", "CNumber", "Cid"]).strip()
    values = ', '.join([str((billings[i], names[i], expires[i], seccodes[i], types[i], creditNumbers[i], cids[i])) for i in range(len(billings))]).strip()

    deleteStatement = "DELETE FROM CreditCards WHERE Cid=%s" % cid
    print(deleteStatement)
    ExecuteRaw(deleteStatement)
    if values != None and values != "":
        insertStatement = "INSERT INTO CreditCards (%s) VALUES %s" % (keys, values)
        print(insertStatement)
        ExecuteRaw(insertStatement)
    return redirect(url_for("profile", code=302))

@app.route('/newUser', methods=['POST'])
def newUser():
    accCid = "SELECT MAX(Cid)+1 as nCid from Account"
    accCid = ExecuteRaw(accCid, fetch_one=True)['nCid']
    nCid = accCid
    userData = {
        "Email": form['email'],
        "PhoneNo": form['phoneno'],
        "Name": form['name'],
        "Address": form['address'],
        'Cid': nCid
    }

    m = hashlib.sha1()
    m.update(form['password'].encode("utf-8"))
    accountData = {
        "Email": form['email'],
        "Password": m.hexdigest(),
        "Address": form['address'],
        "Cid": nCid
    }

    # checks if email already in the database
    accEmail = 'SELECT Email as email from Account WHERE Email="%s"' % form['email']
    accEmail = ExecuteRaw(accEmail, fetch_one=True)
    if accEmail != None: # Email already exists
        return "Email already registered. Please go to the homepage and login."
    InsertQueryKV("Account", accountData)
    response = make_response("200")
    return "Registration Success! Please return to the homepage and login"

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
    if states == '' or countries == '':
        error.append("Please input a valid state or country")

    if entry == '' or depart == '':
        error.append("Please input a check in and checkout date")
    else:

        dtparsed = datetime.datetime.strptime(entry,'%Y-%m-%d')

        dtparsed2 = datetime.datetime.strptime(depart,'%Y-%m-%d')
        if dtparsed2 < dtparsed:
            error.append("Please make checkout date AFTER the entry date")
        if dtparsed < datetime.datetime.now():
            error.append("Please Input a time befroe today to checkin lol")
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

@app.route('/browse', methods=['GET'])
def browse():
    pass

@app.route('/hotel-page', methods=['POST'])
def hotel_page():
    val = json.loads(request.form['hotel'])
    #return (val['results']['country'])
    entry = val["results"]["entry"]
    depart = val["results"]["depart"]
    sqlst = "SELECT * FROM Room r1  WHERE r1.HotelId = %s AND r1.price >%s and r1.price <%s AND NOT EXISTS (SELECT * FROM Reserves res WHERE res.HotelID = r1.HotelID and res.RoomNo = r1.RoomNo and (%s between res.InDate and res.OutDate or %s between res.InDate and res.OutDate or (%s <= res.InDate and %s >= res.OutDate))) "
    results = SelectQuery(sqlst,(val["id"],val["results"]["min"],val["results"]["max"],entry,depart,entry,depart),one= False)
    sqlst = "SELECT *,o.Discount as dis FROM Room r1, Offerroom o WHERE r1.HotelId = %s and r1.price >%s and r1.price <%s AND NOT EXISTS (SELECT * FROM Reserves res WHERE res.HotelID = r1.HotelID and res.RoomNo = r1.RoomNo and (%s between res.InDate and res.OutDate or %s between res.InDate and res.OutDate or (%s <= res.InDate and %s >= res.OutDate))) and r1.HotelId = o.HotelId and r1.RoomNo = o.RoomNo  and %s between o.SDate and o.EDate and %s between o.SDate and o.EDate"
    results2 = SelectQuery(sqlst,(val["id"],val["results"]["min"],val["results"]["max"],entry,depart,entry,depart,entry,depart),one= False)
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


    sql = "SELECT BType, BPrice From Breakfast Where hotelId = %s"
    results = SelectQuery(sql,(hotelid),one=False)
    breakfastReviewList = []
    for x in range(len(results)):
        sql = "SELECT re.Rating as rate, re.TextComment as tc FROM Review re, BreakfastReview br WHERE re.ReviewId = br.ReviewId and br.HotelId = %s and br.BType = %s"
        re = SelectQuery(sql,(hotelid,results[x]["BType"]),one=False)
        breakfastReviewList.append((results[x]["BType"],results[x]['BPrice'],re))

    hotelInfo["breakfastReviews"] = breakfastReviewList
    sql = "SELECT SCost as s FROM Service WHERE Service.HotelId = %s"
    results = SelectQuery(sql,(hotelid), one=False)
    serviceList = []
    for x in range(len(val["results"]["services"])):
        serviceList.append({"SType":val["results"]["services"][x],"SCost":results[x]["s"]})
    #hotelInfo['service'] = val["results"]["services"]
    hotelInfo['service'] = serviceList


    sql = "SELECT SType, SCost From Service Where hotelId = %s"
    results = SelectQuery(sql,(hotelid),one=False)
    serviceReviewList = []
    for x in range(len(results)):
        sql = "SELECT re.Rating as rate, re.TextComment as tc FROM Review re, ServiceReview sr WHERE re.ReviewId = sr.ReviewId and sr.HotelId = %s and sr.SType = %s"
        re = SelectQuery(sql,(hotelid,results[x]["SType"]),one=False)
        serviceReviewList.append((results[x]["SType"],results[x]["SCost"],re))

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
    user_id = request.cookies.get("Session")
    checkout = request.cookies.get('Checkout')
    response = redirect(url_for("search_page"))
    #THIS IS FOR TESTING!! WHEN REGISTRATION IS DONE THIS WILL CHANGE
    if user_id:
        checkoutList = request.form.getlist('add_check')
        listOfRooms = []
        for x in checkoutList:
            listOfRooms.append(json.loads(x))
        if checkout:
            checkout = json.loads(checkout)
            if checkout[0]['id'] != listOfRooms[0]['id']:
                return render_template("search.html")
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
        #return the user to the registration html
        pass

@app.route('/checkout', methods=["GET","POST"])
def checkout():
    #user_id = request.cookies.get('Session')
    user_id = request.cookies.get("Session")
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
                    total += x['Price'] - (x['Price'] * (int(x['discount'])/100))
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

                return render_template("checkout.html",CL=listOfData,total=total,cc=cc,creditCards=creditCards,initial=False)


@app.route('/payment', methods=['POST'])
def payment():
    user_id = request.cookies.get("Session")
    checkout = json.loads(request.cookies.get('Checkout'))
    whatCard = request.form['card']
    if whatCard == "new":
        cNum = request.form['cn']
        bAddr = request.form['ba']
        sCode = request.form['sc']
        tCard = request.form['dc']
        if not(cNum and bAddr and sCode and tCard):
            return render_template("search.html")
        expDate = request.form['ed']
        #user_id = request.cookies.get('Session')
        name = SelectQuery("SELECT Name FROM Customer WHERE Customer.Cid = %s",(user_id))
        name = name['Name']
        try:
            InsertQuery("INSERT INTO CreditCards VALUES (%s,%s,%s,%s,%s,%s,%s)",(user_id,cNum,bAddr,name,sCode,tCard,expDate))
        except:
            return render_template("search.html")


    hotelId = checkout[0]['id']
    total = request.form['payment']
    invoiceNo = SelectQuery("Select MAX(InvoiceNo) as ino FROM Reservation")
    if invoiceNo['ino'] == None:
        invoiceNo = 0
    else:
        invoiceNo = int(invoiceNo['ino']) + 1
    #Fill In later
    now = datetime.datetime.now()
    InsertQuery("INSERT INTO Reservation VALUES (%s,%s,%s,%s,%s)",(invoiceNo,user_id,now,hotelId,total))
    for x in checkout:
        d1 = datetime.datetime.strptime(x['entry'], "%Y-%m-%d")
        d2 = datetime.datetime.strptime(x['depart'], "%Y-%m-%d")
        delta = (d2-d1).days
        InsertQuery("INSERT INTO Reserves VALUES (%s,%s,%s,%s,%s,%s)",(invoiceNo,x['depart'],x['entry'],x['roomNo'],delta,hotelId))

    response = make_response(render_template('search.html'))
    response.set_cookie('Checkout','',expires=0)
    return response
@app.route('/stats',methods =['GET','POST'])
def stastics():
    if request.method == 'POST':
        error = []
        print ("got here")
        to_date = request.form['todate1']
        form_date = request.form['fromdate1']
        queryval = request.form['query']
        query1 = ""
        #Highest rated room time for each hotel
        if queryval == 'hr':
            query1 = """SELECT dat.hotelid,dat.type,h.street,h.city,h.zip,h.country FROM
                    (SELECT rev.HotelId,max(rev.rating),room.type FROM Reservation res
                    INNER JOIN Reserves r on res.HotelId = r.HotelId and r.indate between %s and %s and r.outdate between %s and %s
                    INNER JOIN Review rev on res.Hotelid = rev.HotelId and r.HotelId = rev.Hotelid and rev.cid = res.cid
                    INNER JOIN RoomReview rreview on rreview.reviewid = rev.reviewid INNER JOIN
                    Room room on rev.HotelId = room.Hotelid AND rreview.roomno = room.roomno GROUP BY rev.hotelid) as dat INNER JOIN Hotel h on h.hotelid = dat.hotelid"""
        elif queryval == 'sr':
            query1 = """
                    SELECT dat.hotelid,dat.type,h.street,h.city,h.zip,h.country from
                            (SELECT rev.HotelId,max(rev.rating) as rate,s.Stype as type FROM Reservation res
                            INNER JOIN
                            Reserves r on res.HotelId = r.HotelId and r.indate between %s and %s AND  r.outdate between %s and %s
                            INNER JOIN
                            Review rev on res.Hotelid = rev.HotelId and r.HotelId = rev.Hotelid and rev.cid = res.cid
                            INNER JOIN ServiceReview rreview on rreview.reviewid = rev.reviewid INNER JOIN
                            Service s on rev.HotelId = s.Hotelid  GROUP BY rev.hotelid) as dat INNER JOIN Hotel h on h.hotelid = dat.hotelid """
        elif queryval == 'br':

            query1 = """
                    SELECT dat.hotelid,dat.type,h.city,h.zip,h.street,h.zip,h.country from
                            (SELECT rev.HotelId,max(rev.rating) as rate,b.BType as type FROM Reservation res
                            INNER JOIN
                            Reserves r on res.HotelId = r.HotelId and r.indate between %s and %s AND r.outdate between %s and %s
                            INNER JOIN
                            Review rev on res.Hotelid = rev.HotelId and r.HotelId = rev.Hotelid and rev.cid = res.cid
                            INNER JOIN BreakfastReview rreview on rreview.reviewid = rev.reviewid INNER JOIN
                            Breakfast  b on rev.HotelId = b.Hotelid  GROUP BY rev.hotelid) as dat INNER JOIN Hotel h on h.hotelid = dat.hotelid"""
        else:
            query1 = """
                        SELECT c.name,sum(r.totalamt) as x FROM Reservation r INNER JOIN Customer c on r.cid = c.cid INNER JOIN Reserves re on re.hotelid = r.hotelid
                        and re.indate between %s and %s and re.outdate between %s and %s GROUP BY r.cid ORDER BY x ASC
                    """



        restultsquery1 = SelectQuery(query1,(form_date,to_date,form_date,to_date),one = False)
        lis = []
        if queryval == "bestc":
            ctr = 1
            for i in restultsquery1:

                lis.append(i)
                if(ctr == 5):
                    break
                ctr +=1

        if to_date == '' or form_date == '':
            error.append("Please input dates")
        else:
            datetimefrom = datetime.datetime.strptime(form_date,"%Y-%m-%d")
            datetimeto = datetime.datetime.strptime(to_date,"%Y-%m-%d")
            if datetimeto < datetimefrom:
                error.append("Please make the to date after the from date")
        print(restultsquery1)
        if len(restultsquery1) ==0:
            error.append("The date had no results, please try inputting a different date range")
        if error:
            return render_template("statistics.html",error = error)
        return render_template("statistics.html",result = restultsquery1,error=error,bestc = lis)
    else:
        return render_template("statistics.html")
