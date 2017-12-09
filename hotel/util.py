import pymysql
import hotel.config as config
import names
import random as rand
import datetime
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

def buildCheckoutData(checkout):
    listInCheckout = []
    for x in checkout:
        hotelid = x["id"]
        roomNo = x["roomNo"]
        entry = x["entry"]
        depart = x["depart"]
        print(depart)
        discount = x["discount"]
        sql = "SELECT * FROM Room , Hotel WHERE Room.HotelId = %s and Room.RoomNo = %s"
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
