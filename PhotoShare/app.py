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

UPLOAD_FOLDER = 'static/upload'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'even'
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

def getUserIdFrom(email):
    cursor = conn.cursor()
    cursor.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def getUserFname(email):
    cursor = conn.cursor()
    cursor.execute("SELECT fname  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

# Users control

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

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

#login method

@app.route('/Login', methods=['POST','GET'])
def Login():
    if request.method=='POST':
        # The request method is POST (page is recieving data)
        email = request.form['email']
        print (email)
        cursor = conn.cursor()
        # check if email is registered
        if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
            data = cursor.fetchone()
            print(data)
            pwd = str(data[0])
            if request.form['password'] == pwd:
                user = User()
                user.id = email
                flask_login.login_user(user)  # okay login in user
                cursor.execute("select uid from users where email='{0}'".format(email))
                id=cursor.fetchone()[0]
                return flask.redirect(flask.url_for('findu',uid=id))
                # protected is a function defined in this file
        # information did not match
        return render_template('Login.html',supress=False)

    elif request.method=='GET':
        return render_template('Login.html', supress=True)

#logout method
@app.route('/Logout')
def logout():
    flask_login.logout_user()
    return render_template('Hello.html', message='You are logged out', uname='')


# register method
@app.route("/register", methods=['POST','GET'])
def register():

    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        dob = request.values.get('dob')
        hometown = request.values.get('hometown')
        password = request.form['password']
        gender = request.values.get('gender')

        cursor = conn.cursor()
        test = isEmailUnique(email)
        if test:
            if hometown is None: hometown1='NULL'
            else: hometown1=hometown
            if gender is None: gender1='/'
            else: gender1=gender
            cursor.execute("INSERT INTO Users (fname,lname,email,dob,hometown,gender,password) "
                            "VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')"
                            .format(fname,lname,email,dob,hometown1,gender1,password))
            conn.commit()
            # log user in
            user = User()
            user.id = email
            flask_login.login_user(user)
            uid = getUserIdFrom(email)
            createDefaultAlbum(uid)
            return flask.redirect(flask.url_for('findu',uid=uid))

        else:
            print("register failed: email already used")
            return render_template('Register.html', supress='False', message="register failed: email already used")

    elif request.method == 'GET':
        return render_template('Register.html', supress='True', message="free to register!")




def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM photos WHERE uid = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getAlbumPhotos(aid):
    cursor = conn.cursor()
    cursor.execute("select * from photos WHERE aid='{0}'".format(aid))
    return cursor.fetchall()

def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True
#end login code

#profile page
@app.route('/profile/<uid>')
@flask_login.login_required
def findu(uid):
    cursor = conn.cursor()
    cursor.execute("select fname from users where uid='{0}'".format(uid))
    name = cursor.fetchone()[0]
    return render_template('Hello.html',name=name,message="Login success!",uname=name)

#album page
@app.route('/album/<aid>')
@flask_login.login_required
def finda(aid):
    return render_template('album.html', name=aid, message="this is the album")

#photo page
@app.route('/photo/<pid>')
@flask_login.login_required
def findp(pid):
    cursor=conn.cursor()
    cursor.execute("select count(*) from likephoto where pid='{0}'".format(pid))
    pl=cursor.fetchone()[0]
    return render_template('hello.html', name=pid, message="Here's photo",liken=pl)
'''
@app.route('/photo/<pid>',methods='post')
@flask_login.login_required
def getp(pid):
    return render_template('hello.html', name=pid, message="Here's photo")
'''

# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML



@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        aid=1  #todo
        imgtype=imgfile.mimetype.split("/")
        print (imgtype[1])

        if imgtype[0]=='image':
            cursor = conn.cursor()
            cursor.execute("INSERT INTO photos (path, aid, caption) VALUES (%s, %s, %s)",
                           ('path', aid, caption))
            cursor.execute("select pid from photos where path='path'")
            pid=cursor.fetchone()[0]
            cursor.execute("UPDATE photos set path=%s where pid=%s",
                           (str(pid)+'.'+imgtype[1],pid))
            conn.commit()
            print(str(pid)+'.'+imgtype[1])
            imgfile.save(os.path.join(app.config['UPLOAD_FOLDER'], str(pid)+'.'+imgtype[1]))
            return render_template('album.html', name=flask_login.current_user.id, album=getAlbumPhotos(aid),
                               photos=getAlbumPhotos(aid))
        else:
            print("not image")
            return render_template('Hello.html')
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('Upload.html')

# end photo uploading code

#bwen's query functions

def getUsersLike(uid,pid):
    cursor= conn.cursor()
    cursor.execute("SELECT pid from likePhoto where uid='{0}' and pid='{1}'".format(uid, pid))
    if cursor.fetchone()is None: # or NULL?
        return 0 # tuple exists (user likes the photo)
    else:
        return 1

#search function
@app.route("/search", methods=['GET', 'POST'])
def search(key,type):
#type T for tags, U for users, C for comments
    if request.method == 'POST':
        key = request.form.get('search')
        cursor=conn.cursor()
        if (type=="T"):
            cursor.execute("select DISTINCT pid from Tags")
            retPhotos = cursor.fetchall()
            tags = key.split(" ")
            for tag in tags:
                cursor.execute("select pid from Tags where tname='{0}'".format(tag))
                retPhotos = cursor.fetchall() and retPhotos #TODO result init to null??

            print(retPhotos)
            photolist = []
            for p in retPhotos:
                photolist += getPhotos(p)
            #return render_template('searchPhoto.html', photos=photolist, guest=anonymous, name=flask_login.current_user.id)
            return

        elif (type == "U"):
            cursor.execute("select * from comments where text like '{0}'".format('%'+key+'%'))
            retPhotos = cursor.fetchall()
            print(retPhotos)
            photolist = []
            for p in retPhotos:
                photolist += getPhotos(p)
            # return render_template('searchPhoto.html', photos=photolist, guest=anonymous, name=flask_login.current_user.id)
            return

        elif(type=="C"):
            cursor.execute("select * from users where fname='{0}'".format(key))
            retUsers = cursor.fetchall()
            userlist = []
            # return render_template('searchPhoto.html', photos=photolist, guest=anonymous, name=flask_login.current_user.id)
            return

#add tags
def addtags(pid,key):
    cursor=conn.cursor()
    tags = key.split(",")
    for tag in tags:
        cursor.execute("select * from Tags where tname='{0}'".format(tag))
        if cursor.fetchone() is None:
            cursor.execute("insert into Tags VALUES ('{0}','{1}')".format(pid,tag))
    return "success"

#add album
def addalbum(uid,aname):
    cursor=conn.cursor()
    cursor.execute("insert into albums(uid,aname) values ('{0}','{1}')".format(uid,aname))
    return "success"

#make comment

def addcomment(uid,comt,pid):
    cursor=conn.cursor()
    cursor.execute("insert into comments(uid,comt,pid) values('{0}','{1}','{2}')".format(uid,comt,pid))
    return "success"


#delete functions
def delalbum(aid,uid):
    cursor=conn.cursor()
    cursor.execute("select * from album where aid='{0}' and uid='{1}'".format(aid,uid))
    if cursor.fetchone()is not None:
        cursor.execute("delete from album where aid='{0}'".format(aid))
        return "deleted"
    else:
        return "not your album"

def delphoto(pid,uid):
    cursor=conn.cursor()
    cursor.execute("select * from photos where pid='{0}' "
                   "and aid in (select aid from album where uid='{1}')".format(pid,uid))
    if cursor.fetchone()is not None:
        cursor.execute("delete from photos where pid='{0}'".format(pid))
        return "deleted"
    else:
        return "not your photo"

def delcom(cid,uid):
    cursor=conn.cursor()
    cursor.execute("select * from comments where cid='{0}' and uid='{1}'".format(cid,uid))
    if cursor.fetchone()[0]is not None:
        cursor.execute("delete from comments where aid='{0}'".format(cid))
        return "deleted"
    else:
        return "not your comment"


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
    cursor.execute("select p1 from"
                   "(select pid as p1, count (pid) as cp1 from tags group by pid),"
                   "(select pid as p2, count (pid) as cp2 from tags,"
                   "(select DISTINCT c.tname as tagn from tags c,album b,photos a "
                   "where b.uid='{0}' and a.aid=b.aid and c.pid=a.pid)"
                   "where tags.tname in tagn"
                   "group by pid)"
                   "where p1=p2"
                   "order by p1,cp2/cp1 desc".format(uid))
    return cursor.fetchall()

#contribution function
def contribution():
    cursor=conn.cursor()
    cursor.execute("select up from"
                   "(select uid as up, count(pid) as cp from photos, users, albums "
                   "where albums.aid=photos.aid and users.uid=albums.uid "
                   "group by uid),"
                   "(select uid as uc, count(cid) as cc from comments "
                   "group by uid) "
                   "where uc=up "
                   "order by cc+cp desc")
    return cursor.fetchall()

'''
# Yiwen
def getFriendsList(uid):
    query = "SELECT u1.uid AS ID, u1.fname AS FirstName, u1.lname AS LastName " \
            "FROM Users AS u1" \
            "WHERE u1.uid IN (SELECT f.fuid FROM isFriend AS f WHERE f.uid = '{0}')" \
            "ORDER BY u1.fname, u1.lname"

    query2 = "SELECT u1.uid, u1.fname, u1.lname "\
            "FROM Users AS u1, isFriend AS f"\
            "WHERE u1.uid = f.fuid AND f.uid = '{0}'"\
            "ORDER BY u1.fname"
    print(query.format(uid))  # optional printing out in your terminal
    cursor = conn.cursor()
    cursor.execute(query.format(uid))
    return cursor.fetchall()
'''

#get photo by pidlist from cursor
def getPhotoFromList(list):
    plist=[]
    for pid in list:
        cursor=conn.cursor()
        cursor.execute("select * from photos where pid='{0}'".format(pid[0]))
        a=cursor.fetchone()
        plist.append(a)
    return plist

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
@app.route("/", methods=['GET','POST'])
def hello():
    print (flask_login.current_user.get_id())
    return render_template('Hello.html', message='Welcome to PhotoShare', uname='')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
