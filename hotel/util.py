import pymysql
import hotel.config as config
import names
import random as rand
import datetime
import sys

def connect():
    """
        Connects to the databse

    """
    connection = pymysql.connect(host = config.host, user = config.username,password = config.password,db  = 'Hotels',cursorclass = pymysql.cursors.DictCursor)
    return connection
def SelectQuery(query:str,x = None,one:bool = True)->dict:
    """
        Returns a SELECT  query, default is fetchOne , but specify one = False to fetchAll
    """
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(query,x)
        return cursor.fetchone() if one else cursor.fetchall()

def InsertQuery(query:str, x):
    """
        Makes an INSERT Query
    """
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(query,x)
    con.commit()

def InsertQueryKV(table, fields):
    keys, values = [k for k in fields], [v for k,v in fields.items()]
    insert = "INSERT INTO (%s) VALUES (%s)" % (table, ','.join(keys), ','.join(values))
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(insert)
    conn.commit()

def ExecuteRaw(query, fetch_one=False):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone() if fetch_one else cursor.fetchall()

def SelectQueryKV(table, columns="*", fields={}, fetch_one=False):
    query = "SELECT %s FROM %s" % (columns, table)
    print(query)
    if len(fields) > 0:
        where_query = ' AND '.join(['{} = {}'.format(k, v if isinstance(v, int) or isinstance(v, float)
                                                          else '"%s"' % v) for k,v in fields.items()])
        query = '%s WHERE %s' % (query, where_query)
    print("Q: ", query)
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(query)
    return cursor.fetchone() if fetch_one else cursor.fetchall()

def geneRandCustomers():
    for i in range(100):
         cid = i
         ph = str(rand.randint(1000000000000,9999999999999))
         name =  str(names.get_full_name())
         addr = str(rand.randint(10,99)) +  "   "  + names.get_first_name() + "way"
         email = name.replace(" ",".") + "@gmail.com"
         InsertQuery("INSERT INTO Customer VALUES (%s,%s,%s,%s,%s,%s)",(cid,None,email,addr,ph,name))

def genHotels():
    for i in range(100):
         hotelid = i
         addr = str(rand.randint(10,99)) + " " + names.get_first_name() +  "  Lane"
         city = names.get_first_name()
         statesarr = ['NJ','PA','CA','OH','MD','MN','TX','CO']
         countryarr = ['USA','India','China','Pakistan','Morrococo']
         country = countryarr[rand.randint(0,len(countryarr)-1)]
         state = statesarr[rand.randint(0,len(statesarr)-1)]
         zicode = str(rand.randint(00000,99999))
         ph = str(rand.randint(1000000000000,9999999999999))
         InsertQuery("INSERT INTO Hotel VALUES (%s,%s,%s,%s,%s,%s,%s)",(addr,state,city,zicode,country,ph,i))


def genBreakfasts():
    bfarr = ['Contential','English','Italian','American','French','Indian','Mexican']
    descarr = ['This is contiential','This is english','This is Italaitn','This is Murican','Fracais','this is indian','this is mexican']
    for i in range(100):
        pricesarr = []
        for j in range(7):
            pricesarr.append(rand.random() * 15)
        howmany = rand.randint(1,7)
        for x in range(0,howmany):
            InsertQuery("INSERT INTO Breakfast VALUES(%s,%s,%s,%s)",(bfarr[x],i,pricesarr[x],descarr[x]+str(i)))

def genServices():
    bfarr = ['Pool','Jaqcuuzi','Gym','Maid','Coference rooom','Casino','Track']
    for i in range(100):
        pricesarr = []
        for j in range(7):
            pricesarr.append(rand.random() * 100)
        howmany = rand.randint(1,7)
        for x in range(0,howmany):
            InsertQuery("INSERT INTO Service VALUES(%s,%s,%s)",(bfarr[x],i,pricesarr[x]))

def creditcards():
    ctype = ['C','D']
    for i in range(100):
        q = SelectQuery('SELECT name,Address From Customer where Cid = %s',i)
        name =q['name']
        addr = q['Address']
        howmanycc = rand.randint(1,6)
        for x in range(0,howmanycc):
            seccode = rand.randint(000,999)
            month = rand.randint(1,12)
            day = rand.randint(1,31)
            yr = rand.randint(10,39)

            ccnumber =  str(rand.randint(00000000,99999999))
            print(ccnumber)
            ctype_ = ctype[rand.randint(0,1)]
            InsertQuery("INSERT INTO CreditCards VALUES (%s,%s,%s,%s,%s,%s,%s)",(i,ccnumber,addr,name,seccode,ctype_,str(month) + "/" + str(day) + "/" + str(yr)))

def buildQueryBreakfasts(blist):
    base = "SELECT * FROM Room r INNER JOIN Hotel h1 on h1.HotelId = r.HotelId INNER JOIN Service s on h1.Hotelid = s.Hotelid INNER JOIN  Breakfast b on h1.hotelid = b.hotelid  WHERE h1.Country IN (%s) and h1.state IN (%s) AND r.price >%s and r.price <%s"

    for i in blist:
        base += " AND EXISTS (SELECT h1.hotelID FROM Room r , Breakfast s WHERE r.HotelId = h1.HotelId and h1.Hotelid = s.Hotelid AND '" + str(i)+ "' " +  " = s.Btype)"
    base += "GROUP BY h1.hotelid"
    return base


def buildQuerySerices(slist):
    base = "SELECT * FROM Room r INNER JOIN Hotel h1 on h1.HotelId = r.HotelId INNER JOIN Service s on h1.Hotelid = s.Hotelid INNER JOIN  Breakfast b on h1.hotelid = b.hotelid  WHERE h1.Country IN (%s) and h1.state IN (%s) AND r.price >%s and r.price <%s"

    for i in slist:
        base += " AND EXISTS (SELECT h1.hotelID FROM Room r , Service s WHERE r.HotelId = h1.HotelId and h1.Hotelid = s.Hotelid AND '" + str(i)+ "' " +  " = s.Stype)"
    base += "GROUP BY h1.hotelid"
    print (base)
    return base

def buildQueryServiceBreakfasts(slist,blist):

    base = "SELECT * FROM Room r INNER JOIN Hotel h1 on h1.HotelId = r.HotelId INNER JOIN Service s on h1.Hotelid = s.Hotelid INNER JOIN  Breakfast b on h1.hotelid = b.hotelid  WHERE h1.Country IN (%s) and h1.state IN (%s) AND r.price >%s and r.price <%s"


    for i in blist:
        base += " AND EXISTS (SELECT h1.hotelID FROM Room r , Breakfast s WHERE r.HotelId = h1.HotelId and h1.Hotelid = s.Hotelid AND '" + str(i)+ "' " +  " = s.Btype)"

    for i in slist:
        base += " AND EXISTS (SELECT h1.hotelID FROM Room r , Service s WHERE r.HotelId = h1.HotelId and h1.Hotelid = s.Hotelid AND '" + str(i)+ "' " +  " = s.Stype)"


    base += "GROUP BY h1.hotelid"
    return base




def genRandomReservaton():
    liyrs = [2019,2020,2018,2022]
    time = ' 10:00:00'
    taken = []
    for i in range (50):
        invoiceno = SelectQuery("SELECT max(invoiceno) as ino FROM Reservation")
        if invoiceno['ino'] == None:
            invoiceno = 0
        else:
            invoiceno = int(invoiceno['ino']) + 1
        day = rand.randint(1,29)
        month = rand.randint(1,12)
        yr = liyrs[rand.randint(0,len(liyrs)-1)]
        hotel = rand.randint(0,99)
        datetime = str(yr) + '-'+ str(month) + '-'+ str(day) + str(time)
        totalamt = rand.randint(1000,3000)
        InsertQuery("INSERT into Reservation VALUES (%s,%s,%s,%s,%s)",(invoiceno,i,datetime,hotel,totalamt))
        #pick 30 random rooms

        li = [k for k in range(1,61)]
        for j in range(rand.randint(10,30)):

            room = li[rand.randint(0,len(li)-1)]
            tup = (hotel,room)
            for l in taken:
                if l[0] == tup[0] and l[1] == tup[1]:
                    continue
            taken.append(tup)
            li.remove(room)
            inday = day + rand.randint(10,14)
            inmonth = month
            inyear = yr
            if inday > 28:
                inday = inday - 28
                inmonth += 1
                if inmonth > 12:
                    inmonth = 1
                    inyear += 1
            outdaynodays = rand.randint(10,14)
            outday = inday + outdaynodays

            outmonth = inmonth
            outyear = inyear
            if outday > 28:
                outday = outday - 28
                outmonth += 1
                if outmonth > 12:
                    outmonth = 1
                    outyear += 1
            indate = str(inyear) + '-' + str(inmonth) + '-' + str(inday) + time
            outdate = str(outyear) + '-' + str(outmonth) + '-' + str(outday) + time
            InsertQuery("INSERT Into Reserves VALUES (%s,%s,%s,%s,%s,%s)",(invoiceno,outdate,indate,room,outdaynodays,hotel))
            #now we generate roomreview
            comments = ['This was great','This was ok','Best service','Amazing beds','Gordon Ramsay should do a hotel hell','There were so many bed bugs wtf','Would not reccomend']
            gen_randomindex = rand.randint(0,len(comments)-1)
            rating = 0
            if gen_randomindex <=3:
                rating = rand.randint(3,5)
            else:
                rating = rand.randint(0,3)
            reviewid = SelectQuery("SELECT max(reviewid) as rev FROM Review")
            if reviewid['rev'] == None:
                reviewid = 0
            else:
                reviewid = int(reviewid['rev']) +1
                InsertQuery("INSERT INTO Review VALUES (%s,%s,%s,%s,%s)",(reviewid,hotel,i,comments[gen_randomindex],rating))
                InsertQuery("Insert into RoomReview VALUES (%s,%s)",(reviewid,room))
        bfarry = SelectQuery("SELECT * FROM Breakfast WHERE HotelId = %s",(hotel),one = False)
        servicesarray = SelectQuery("SELECT * From Service WHERE HotelId = %s",(hotel),one = False)
        commentsb = ['Great Food',"amazing","10/10 would go again","horrible","bland","raw!"]
        commentss = ["quality service","had lots of fun","kids enjoyed","generic","was not amused","I almost died"]
        randno = rand.randint(1,len(bfarry))

        for z in range(0,randno):
            gen_randomindexbf = rand.randint(0,len(commentsb)-1)
            ratingb = 0
            if gen_randomindexbf <=2:
                ratingb= rand.randint(3,5)
            else:
                ratingb = rand.randint(0,3)

            reviewid = SelectQuery("SELECT max(reviewid) as rev FROM Review")
            if reviewid['rev'] == None:
               reviewid = 0
            else:
               reviewid = int(reviewid['rev']) +1
            InsertQuery("INSERT INTO Review VALUES (%s,%s,%s,%s,%s)",(reviewid,hotel,i,commentsb[gen_randomindexbf],ratingb))
            InsertQuery("INSERT INTO BreakfastReview VALUES (%s,%s,%s)",(reviewid,bfarry[z]['BType'],hotel))
        randnoser  = rand.randint(1,len(servicesarray))
        for service in range(0,randnoser):

            gen_randomindexservice = rand.randint(0,len(commentss)-1)
            ratings = 0
            if gen_randomindexservice <=2:
                ratings= rand.randint(3,5)
            else:
                ratings = rand.randint(0,3)

            reviewid = SelectQuery("SELECT max(reviewid) as rev FROM Review")
            if reviewid['rev'] == None:
               reviewid = 0
            else:
               reviewid = int(reviewid['rev']) +1
            InsertQuery("INSERT INTO Review VALUES (%s,%s,%s,%s,%s)",(reviewid,hotel,i,commentss[gen_randomindexservice],ratings))
            InsertQuery ("INSERT INTO ServiceReview VALUES (%s,%s,%s)",(reviewid,servicesarray[service]['SType'],hotel))














def genServices():
    bfarr = ['Pool','Jaqcuuzi','Gym','Maid','Coference rooom','Casino','Track']
    for i in range(100):
        pricesarr = []
        for j in range(7):
            pricesarr.append(rand.random() * 100)
        howmany = rand.randint(1,7)
        for x in range(0,howmany):
            InsertQuery("INSERT INTO Service VALUES(%s,%s,%s)",(bfarr[x],i,pricesarr[x]))

def creditcards():
    ctype = ['C','D']
    for i in range(100):
        q = SelectQuery('SELECT name,Address From Customer where Cid = %s',i)
        name =q['name']
        addr = q['Address']
        howmanycc = rand.randint(1,6)
        for x in range(0,howmanycc):
            seccode = rand.randint(000,999)
            month = rand.randint(1,12)
            day = rand.randint(1,31)
            yr = rand.randint(10,39)

            ccnumber =  str(rand.randint(00000000,99999999))
            print(ccnumber)
            ctype_ = ctype[rand.randint(0,1)]
            InsertQuery("INSERT INTO CreditCards VALUES (%s,%s,%s,%s,%s,%s,%s)",(i,ccnumber,addr,name,seccode,ctype_,str(month) + "/" + str(day) + "/" + str(yr)))

def buildQueryBreakfasts(blist):
    base = "SELECT * FROM Room r INNER JOIN Hotel h1 on h1.HotelId = r.HotelId INNER JOIN Service s on h1.Hotelid = s.Hotelid INNER JOIN  Breakfast b on h1.hotelid = b.hotelid  WHERE h1.Country IN (%s) and h1.state IN (%s) AND r.price >%s and r.price <%s"

    for i in blist:
        base += " AND EXISTS (SELECT h1.hotelID FROM Room r , Breakfast s WHERE r.HotelId = h1.HotelId and h1.Hotelid = s.Hotelid AND '" + str(i)+ "' " +  " = s.Btype)"
    base += "GROUP BY h1.hotelid"
    return base


def buildQuerySerices(slist):
    base = "SELECT * FROM Room r INNER JOIN Hotel h1 on h1.HotelId = r.HotelId INNER JOIN Service s on h1.Hotelid = s.Hotelid INNER JOIN  Breakfast b on h1.hotelid = b.hotelid  WHERE h1.Country IN (%s) and h1.state IN (%s) AND r.price >%s and r.price <%s"

    for i in slist:
        base += " AND EXISTS (SELECT h1.hotelID FROM Room r , Service s WHERE r.HotelId = h1.HotelId and h1.Hotelid = s.Hotelid AND '" + str(i)+ "' " +  " = s.Stype)"
    base += "GROUP BY h1.hotelid"
    print (base)
    return base

def buildQueryServiceBreakfasts(slist,blist):

    base = "SELECT * FROM Room r INNER JOIN Hotel h1 on h1.HotelId = r.HotelId INNER JOIN Service s on h1.Hotelid = s.Hotelid INNER JOIN  Breakfast b on h1.hotelid = b.hotelid  WHERE h1.Country IN (%s) and h1.state IN (%s) AND r.price >%s and r.price <%s"


    for i in blist:
        base += " AND EXISTS (SELECT h1.hotelID FROM Room r , Breakfast s WHERE r.HotelId = h1.HotelId and h1.Hotelid = s.Hotelid AND '" + str(i)+ "' " +  " = s.Btype)"

    for i in slist:
        base += " AND EXISTS (SELECT h1.hotelID FROM Room r , Service s WHERE r.HotelId = h1.HotelId and h1.Hotelid = s.Hotelid AND '" + str(i)+ "' " +  " = s.Stype)"


    base += "GROUP BY h1.hotelid"
    return base


def buildCheckoutData(checkout):
    listInCheckout = []
    for x in checkout:
        hotelid = x["id"]
        roomNo = x["roomNo"]
        entry = x["entry"]
        depart = x["depart"]
        discount = x["discount"]
        sql = "SELECT * FROM Room INNER JOIN Hotel ON Room.HotelId = Hotel.HotelId WHERE Room.HotelId = %s and Room.RoomNo = %s"
        results = SelectQuery(sql,(hotelid,roomNo),one=True)
        results["discount"] = results['Price'] * (discount/100)
        results["entry"] = entry
        results["depart"] = depart
        listOfB = []
        sql = "SELECT BType, BPrice FROM Breakfast WHERE Breakfast.HotelId = %s"
        re = SelectQuery(sql,(hotelid),one=False)
        results["breakfasts"] = re
        listOfS = []
        sql = "SELECT SType, SCost FROM Service WHERE Service.HotelId = %s"
        re = SelectQuery(sql,(hotelid),one=False)
        results["services"] = re
        listInCheckout.append(results)
    return listInCheckout






def isNum(x):
    try:
        val = int(x)
        return True
    except ValueError:
        return False
