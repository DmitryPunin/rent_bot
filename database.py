import sqlite3
class database:

    def insert_rent(self,type,city,price,street,contact):
        con = sqlite3.connect(r'D:\PythonProject\rent_housing.db')
        cursor = con.cursor()
        cursor.execute('INSERT INTO rent_housing(type, city, price, street, contact) VALUES (?, ?, ?, ?, ?);',(type,city,price,street,contact))
        con.commit()
        con.close()
    def select_rent(self,type,city,from_price,to_price,street):
        con = sqlite3.connect(r'D:\PythonProject\rent_housing.db')
        cursor = con.cursor()
        if street:
            cursor.execute(
                'SELECT type, city, price, street, contact FROM rent_housing WHERE type=? AND city=? AND price BETWEEN ? AND ? AND street LIKE ?;',
                (type, city, from_price, to_price, f'%{street}%'))
        else:
            cursor.execute(
                'SELECT type, city, price, street, contact FROM rent_housing WHERE type=? AND city=? AND price BETWEEN ? AND ?;',
                (type, city, from_price, to_price))

        res = cursor.fetchall()
        con.close()
        return res
db = database()
