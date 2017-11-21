import pymysql
import config
def connect():
    """
        Connects to the databse

    """
    connection = pymysql.connect(host = config.host, user = config.username,password = config.password,db  = 'Hotels',cursorclass = pymysql.cursors.DictCursor)
    return connection
def SelectQuery(query:str,one:bool = True)->dict:
    """
        Returns a SELECT  query, default is fetchOne , but specify one = False to fetchAll 
    """
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(query)
        if one == True:
            return cursor.fetchone()
        else:
            return cursor.fetchall()
def InsertQuery(query:str):
    """
        Makes an INSERT Query
    """
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(query)
    con.commit()

