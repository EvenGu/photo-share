######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

UPLOAD_FOLDER = 'templates/upload'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0]) #why?
    print(data)
    user.is_authenticated = request.form['password'] == pwd
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
		    <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		    <a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route("/showPhotos", methods=['GET'])
def showPhotos():
    # get photopath from the database: SELECT path FROM PHOTOS WHERE uid = .....
    photopath = "upload/1.jpg"
    return render_template('testShowPhoto.html', photopath = photopath)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')


@app.route("/register", methods=['POST'])
def register_user():
    try:
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        dob = request.form.get('dob')
        hometown = request.form.get('hometown')
        gender = request.form.get('gender')
        password = request.form.get('password')
    except:
        print("register failed: couldn't find all tokens")
        # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (fname,lname,email,dob,hometown,gender,password) "
                             "VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".format(fname,lname,email,dob,hometown,gender,password)))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
<<<<<<< Updated upstream
        createDefaultAlbum(uid) # TODO
=======
        cursor.execute("INSERT INTO Albums(aname,)")
>>>>>>> Stashed changes
        return render_template('hello.html', name=fname, message='Account Created!')
    else:
        print("register failed: email already used")
        return flask.redirect(flask.url_for('register'))


def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM photos WHERE uid = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getAlbumPhotos(aid):
    cursor = conn.cursor()
    cursor.execute("select * from photos WHERE aid='{0}'".format(aid))
    return cursor.fetchall()

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True


# end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
<<<<<<< Updated upstream
        uid = getUserIdFromEmail(flask_login.current_user.id)
        aid = getAlbumIdFromUser(flask_login.current_user.id) # TODO
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        print(caption)
 #       photo_data = base64.standard_b64encode(imgfile.read())
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Photos (caption,path,aid) VALUES (%s, %s, %d)",# TODO
                       (caption, photopath, aid))
        conn.commit()
        imgfile.save(os.path.join(app.config['UPLOAD_FOLDER'], caption+".jpg"))
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotos(uid))
=======
    #    uid = getUserIdFromEmail(flask_login.current_user.id)
    #   aid = getAlbumIdFromUser(flask_login.current_user.id) # TO DO
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        aid=2


        imgtype=imgfile.mimetype.split("/")
        print (imgtype[1])
#       photo_data = base64.standard_b64encode(imgfile.read())
        if imgtype[0]=='image':
            cursor = conn.cursor()
            cursor.execute("INSERT INTO photos (path, aid, caption) VALUES (%s, %s, %s)",
                           ('path', aid, caption))
            cursor.execute("select pid from photos where path='path'")
            pid=cursor.fetchone()[0]
            cursor.execute("UPDATE photos set path=%s where pid=%s",
                           (str(pid)+'.'+imgtype[1],pid))
            conn.commit()
            print(pid)
            imgfile.save(os.path.join(app.config['UPLOAD_FOLDER'], str(pid)+'.'+imgtype[1]))
            return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getAlbumPhotos(aid))
        else:
            print("not image")
            return render_template('hello.html')
>>>>>>> Stashed changes
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')

    '''       
            print(caption)
    #       photo_data = base64.standard_b64encode(imgfile.read())
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Photos (caption,path,aid) VALUES (%s, %s, %d)",
                           (caption, path, aid))
            conn.commit()
            imgfile.save(os.path.join(app.config['UPLOAD_FOLDER'], caption+".jpg"))
            return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
    '''


# end photo uploading code


# bwen's query functions
def getUsersLike(uid,pid):
    cursor= conn.cursor()
    cursor.execute("SELECT * from likephoto where uid='{0}' and pid='{1}'".format(uid,pid))
    if cursor.fetchall()!='': # or NULL?
        return 1 # tuple exists (user likes the photo)
    else:
        return 0
'''
def search(key,type):
#type 1 for tags,2 for users,3 for albums
    cursor=conn.cursor()
    if (type==1):
        key.split(",")
    elif(type==2):
        key.split(",")
    elif(type==3):

        cursor
'''

def suggestFriends(uid):
    cursor=conn.cursor()
    cursor.execute("select u1 from "
                   "(select uid as u1,count(uid)as u1c1 from isfriend a,isfriend b"
                   "group by uid)"
                   "(select u2,count(u2)as u1c from isfriend a1, isfriend b1"
                   "(select c.fuid as u1 from isfriend a, isfriend b, isfriend c"
                   "where a.uid='{0}' and b.uid=a.fuid and b.fuid=c.uid and c.uid<>'{0}')"
                   "where a1.uid=u2 and b1.uid=a1.fuid and b1.fuid<>'{0}' group by u2)"  
                   "where u1=u2 order by u1c/u1c1 DESC ".format(uid))
    return cursor.fetchall()

def suggestPhotos(uid):
    cursor=conn.cursor()
    cursor.execute("select pid from"
                   "(select pid as p1, count (pid) as cp1 from tags group by pid),"
                   "(select pid as p2, count (pid) as cp2 from tags,"
                   "(select DISTINCT c.tname as tagn from tags c,album b,photos a "
                   "where b.uid='{0}' and a.aid=b.aid and c.pid=a.pid))"
                   "where tags.tname in tagn"
                   "group by pid".format(uid))
    return cursor.fetchall()


# Yiwen
def getFriendsList(uid):
    query = "SELECT u1.uid AS ID, u1.fname AS FirstName, u1.lname AS LastName " \
            "FROM Users AS u1" \
            "WHERE u1.uid = (SELECT f.fuid FROM isFriend AS f WHERE f.uid = '{0}')" \
            "ORDER BY u1.fname, u1.lname"
    print(query)  # optional printing out in your terminal
    cursor = conn.cursor()
    cursor.execute(query.format(uid))
    return cursor.fetchall()

'''
Alternatively, 

suggestFriends: RIGHT
SELECT u2.uid, u2.fname, u2.lname
FROM Users AS u2, isFriend f2
WHERE f2.uid IN (SELECT f1.fuid FROM isFriend AS f1 WHERE f1.uid = '{0}')
    AND u2.uid = f2.fuid
GROUP BY f2.fuid
ORDER BY COUNT(*) DESC

suggestPhotos: WRONG
SELECT p2.pid FROM Photos p2
WHERE p2.pid = pt2.pid AND
    pt2.hashtag IN (SELECT t.hashtag
                FROM Albums a, Photos p, photoTag pt, Tags t
                WHERE a.uid = '{0}' 
                AND a.aid = p.aid AND p.pid = pt.pid AND pt.hashtag = t.hashtag
                GROUP BY t.hashtag
                ORDER BY COUNT(*)
                LIMIT 5)
'''

def createDefaultAlbum(uid):
    query = "INSERT INTO Albums(aname, uid) VALUES ('default','{0}')"
    print(query.format(uid))  # optional printing out in your terminal
    cursor = conn.cursor()
    cursor.execute(query.format(uid))
    return

def createAlbum(uid, aname):
    query = "INSERT INTO Albums(aname, uid) VALUES ('{0}','{1}')"
    print(query.format(uid))  # optional printing out in your terminal
    cursor = conn.cursor()
    cursor.execute(query.format(aname,uid))
    return

# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
