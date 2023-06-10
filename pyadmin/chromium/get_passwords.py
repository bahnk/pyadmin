
import sqlite3
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

path = "passwords.db"
db = sqlite3.connect(path)
cursor = db.cursor()
	
cursor.execute(
        "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins "
        "order by date_last_used")

def clean(x): 
    return x[:-x[-1]].decode('utf8')
	
for row in cursor.fetchall():
    main_url = row[0]
    login_page_url = row[1]
    user_name = row[2]
    #decrypted_password = password_decryption(row[3], key)
    date_of_creation = row[4]
    last_usuage = row[5]
    salt = b'saltysalt'
    iv = b' ' * 16
    length = 16
    iterations = 1
    pb_pass = "peanuts".encode('utf8')
    key = PBKDF2(pb_pass, salt, length, iterations)
    cipher = AES.new(key, AES.MODE_CBC, IV=iv)
    #print(row[3])
    #print(row[3][3:])
    decrypted = cipher.decrypt(row[3][3:])
    print(row[1], decrypted)
    #print(type(decrypted))
    #print(len(decrypted))
    ##return x[:-x[-1]].decode('utf8')
    ##print(decrypted.decode("utf-8"))
    ##print(clean(decrypted))


#import sqlite3
#from Crypto.Cipher import AES
#from Crypto.Protocol.KDF import PBKDF2
#
#
#def get_encrypted_data(db_path):
#    # choose a database
#    conn = sqlite3.connect(db_path)
#    cursor = conn.cursor()
#    # connect and egt exncypted data
#    data = cursor.execute('SELECT action_url, username_value, password_value FROM logins')
#    return data
#
#
## to get rid of padding
#def clean(x): 
#    return x[:-x[-1]].decode('utf8')
#
#
#def get_decrypted_data(encrypted_password):
#
#    print("Decrypting the string: {}".format(encrypted_password))
#
#    # trim off the 'v10' that Chrome/ium prepends
#    encrypted_password = encrypted_password[3:]
#
#    # making the key
#    salt = b'saltysalt'
#    iv = b' ' * 16
#    length = 16
#    iterations = 1
#    pb_pass = "peanuts".encode('utf8')
#
#    key = PBKDF2(pb_pass, salt, length, iterations)
#    cipher = AES.new(key, AES.MODE_CBC, IV=iv)
#    
#    decrypted = cipher.decrypt(encrypted_password)
#    print(decrypted)
#    print(clean(decrypted))
#
#
#if __name__ == "__main__":
#    
#    #db_path = '/tmp/data-chrome-test-1/Default/Login Data'
#    db_path = "passwords.db"
#    for url, user, encrypted_password in get_encrypted_data(db_path):
#        print(url)
#        get_decrypted_data(encrypted_password)

