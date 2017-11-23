import pymysql
import config
import names
import random as rand
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
        if one == True:
            return cursor.fetchone()
        else:
            return cursor.fetchall()
def InsertQuery(query:str,x):
    """
        Makes an INSERT Query
    """
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(query,x)
    con.commit()

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
            


