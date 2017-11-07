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

def getUserFname():
    cursor = conn.cursor()
    email=flask_login.current_user.get_id()
    print(email)
    if email is None:
        return ''
    cursor.execute("SELECT fname  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def getCurrentUserId():
    cursor=conn.cursor()
    email=flask_login.current_user.get_id()
    if email is None: return -1
    else:
        print(email)
        cursor.execute("select uid from users where email='{0}'".format(email))
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
    print(request.form['password'] == pwd)
    '''if request.form['password'] == pwd:
        user.is_authenticated = True
    else :
        user.is_authenticated = False'''
    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

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
            temp=flask.request.form['password']
            if temp == pwd:
                user = User()
                cursor.execute("SELECT uid FROM Users WHERE email = '{0}'".format(email))
                user.id = email
                flask_login.login_user(user)  # okay login in user
                return flask.redirect(flask.url_for('findu',uid=cursor.fetchone()[0]))
                # protected is a function defined in this file
        # information did not match
        return render_template('Login.html',supress=False)

    elif request.method=='GET':
        return render_template('Login.html', supress=True)

#logout method
@app.route('/Logout')
def logout():
    flask_login.logout_user()
    return render_template('Hello.html', message='You are logged out',uid=getCurrentUserId(), uname='guest')

# register method
@app.route("/register", methods=['POST','GET'])
def register():

    if request.method == 'POST':
        fname = request.form['fname']
        print("f",fname)
        lname = request.form['lname']
        print("l",lname)
        email = request.form['email']
        print("e",email)
        dob = request.values.get('dob')
        print("d",dob)
        hometown = request.values.get('hometown')
        print("h",hometown)
        password = request.form['password']
        print("p",password)
        gender = request.values.get('gender')
        print("g",gender)

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
            cursor.execute("SELECT uid FROM Users WHERE email = '{0}'".format(email))
            uid = cursor.fetchone()[0]
            user = User()
            user.id=email

            flask_login.login_user(user)

            cursor.execute("INSERT INTO Albums(aname, uid) VALUES ('default','{0}')".format(uid))
            conn.commit()


            return flask.redirect(flask.url_for('findu',uid=uid))
        else:
            print("register failed: email already used")
            return render_template('Register.html', supress='False')
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


#profile page
@app.route('/profile/<uid>')
def findu(uid):
    cursor = conn.cursor()
    cursor.execute("select fname from users where uid='{0}'".format(uid))
    profname = cursor.fetchone()[0]
    cursor.execute("select * from albums where uid='{0}'".format(uid))
    albums=cursor.fetchall()
    profid = int(uid)
    uid = int(getCurrentUserId())
    friends=getUsersFriend(uid,profid)
    cursor.execute("select u.* from users u,isfriend i where u.uid=i.fuid and i.uid='{0}'".format(profid))
    users=cursor.fetchall()
    recfriends=getPeopleFromList(suggestFriends(uid))
    recphotos=getPhotoFromList(suggestPhotos(uid))
    print(suggestFriends(uid))
    print(users)
    return render_template('MyProfile.html', uname=getUserFname(),uid=uid,albums=albums,
                           profname=profname, profid=profid,friends=friends,users=users,
                           recphotos=recphotos, recfriends=recfriends)

#album page
@app.route('/album/<aid>',methods=['GET','POST'])
def album(aid):
    if request.method=='GET':
        ucurrent=getCurrentUserId()
        cursor=conn.cursor()
        print(aid,ucurrent)
        cursor.execute("select * from albums where aid='{0}' and uid='{1}'".format(aid,ucurrent))
        a=cursor.fetchone()
        if a == None:
            auth=False
        else:
            auth=True
        cursor.execute("select * from photos where aid='{0}'".format(aid))
        photos=cursor.fetchall()
        cursor.execute("select fname,aname,albums.uid from albums, users where users.uid=albums.uid and aid='{0}'".format(aid))
        name=cursor.fetchone()
        fname=name[0]
        aname=name[1]
        oid=int(name[2])
        cursor.execute("select count(pid) from photos where aid='{0}' GROUP BY aid".format(aid))
        pnum=cursor.fetchone()
        if pnum is None: pnum=0
        else : pnum=pnum[0]
        return render_template('Album.html',name=aid,auth=auth,photos=photos,oid=oid,
                               aname=aname,uname=fname,uid=int(ucurrent),pnum=pnum,cname=getUserFname())
#photo page
@app.route('/photo/<pid>', methods=['GET','POST'])
def photo(pid):
    if request.method=='GET':
        cursor=conn.cursor()
        cursor.execute("select count(*) from likephoto where pid='{0}'".format(pid))
        pl=cursor.fetchone()[0]
        if pl is None: pl=0#could be none
        cursor.execute("select c.*,u.fname from comments c,users u where c.pid='{0}' and u.uid=c.uid".format(pid))
        comm=cursor.fetchall() #could be none
        cursor.execute("select * from tags where pid='{0}'".format(pid))
        tags = cursor.fetchall() #could be none
        ucurrent=getCurrentUserId()
        uname=getUserFname()
        cursor.execute("select * from photos where pid='{0}'".format(pid))
        photo=cursor.fetchone()
        cursor.execute("select aname from Albums a,photos p where p.pid='{0}' and a.aid=p.aid".format(pid))
        aname=cursor.fetchone()[0]
        cursor.execute("select u.fname,u.uid from users u,photos p,albums a "
                       "where p.pid='{0}' and u.uid=a.uid and a.aid=p.aid".format(pid))
        owner=cursor.fetchone()
        oid=owner[1]
        oname=owner[0]
        print(photo)
        cursor.execute("select uid from likephoto where pid='{0}'".format(pid))
        likeu=getPeopleFromList(cursor.fetchall())
        print(likeu)
        return render_template('Photo.html', name=pid, message="Here's photo",photo=photo,aname=aname,
                               liken=pl,like=getUsersLike(ucurrent,pid),comments=comm,uid=int(getCurrentUserId())
                               ,uname=uname,oname=oname,tags=tags,oid=int(oid),likeu=likeu)

# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
@app.route('/upload/<aid>', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file(aid):
    uname = getUserFname()
    uid = getUserIdFrom(flask_login.current_user.id)
    if request.method == 'POST':
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        imgtype=imgfile.mimetype.split("/")
        tags=request.values.get('tags')
        print (imgtype[1])
        if imgtype[0]=='image':
            cursor = conn.cursor()
            cursor.execute("INSERT INTO photos (path, aid, caption) VALUES (%s, %s, %s)",
                           ('path', aid, caption))

            cursor.execute("select pid from photos where path='path'")
            pid = cursor.fetchone()[0]

            if tags is not None:
                tagss=tags.split(",")
                print(tagss)
                for tag in tagss:
                    cursor.execute("INSERT INTO Tags(pid,tname) VALUES ('{0}','{1}')".format(pid,tag))

            cursor.execute("UPDATE photos set path=%s where pid=%s",
                           (str(pid)+'.'+imgtype[1],pid))
            conn.commit()
            print(str(pid)+'.'+imgtype[1])
            imgfile.save(os.path.join(app.config['UPLOAD_FOLDER'], str(pid)+'.'+imgtype[1]))
            return flask.redirect(flask.url_for('album',aid=aid))

        else:
            print("not image")
            return render_template('upload.html',uname=uname,uid=uid,message="Upload Failed: not an image",name=aid)

    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('Upload.html', uname=uname, uid=uid,message="Please upload your photo",name=aid)
# end photo uploading code

#bwen's query functions

def getUsersLike(uid,pid):
    cursor= conn.cursor()
    cursor.execute("SELECT pid from likePhoto where uid='{0}' and pid='{1}'".format(uid, pid))
    if cursor.fetchone()is None: # or NULL?
        return False # tuple does not exist (this user does not like the photo)
    else:
        return True

def getUsersFriend(uid, fuid):
    cursor = conn.cursor()
    cursor.execute("SELECT * from isfriend where uid='{0}' and fuid='{1}'".format(uid, fuid))
    if cursor.fetchone() is None:  # or NULL?
        return False  # tuple does not exist (they are not friends)
    else:
        return True

#search function
@app.route("/search", methods=['POST'])
def search():
#type T for tags, U for users, C for comments
    if request.method == 'POST':
        key = request.values.get('key')
        type = request.form['Type']
        print(key, type)
        cursor=conn.cursor()
        print(request.values.get('mine'))

        if (request.values.get('mine') is None):
            print('?')
            if (type=="T"):
                type="tags";
                retPhotos=[]
                print("k",key)
                if key is not None :
                    tags = key.split(" ")
                    for tag in tags:
                        print('t',tag)
                        cursor.execute("select distinct pid from Tags where tname='{0}'".format(tag))
                        retPhotos = tuple(set(cursor.fetchall()).intersection(set(retPhotos)))
                        print(retPhotos)
                elif key=='':
                    print('test')
                    cursor.execute("select pid from photos")
                    retPhotos=cursor.fetchall()
                    print(retPhotos)
                photolist=getPhotoFromList(retPhotos)
                return render_template('searchPhoto.html', photos=photolist,uid=getCurrentUserId()
                                       ,uname=getUserFname(),type=type,key='"'+key+'"',message="Here is your search result")

            elif (type == "C"):
                type="comments";
                cursor.execute("select distinct pid from comments where text like '{0}'".format('%'+key+'%'))
                retPhotos = cursor.fetchall()
                print(retPhotos)
                photolist=getPhotoFromList(retPhotos)
                return render_template('searchPhoto.html', photos=photolist, uid=getCurrentUserId(),
                                       uname=getUserFname(),type=type,key='"'+key+'"',message="Here is your search result")


            elif(type=="U"):
                type = "users";
                cursor.execute("select * from users where uid<>-1 and (fname like '{0}' OR lname like '{0}')".format('%'+key+'%'))
                retUsers = cursor.fetchall()
                print(retUsers)
                return render_template('searchUser.html', users=retUsers, uname=getUserFname(),
                                       uid=getCurrentUserId(),key='"'+key+'"',type=type,message="Here is your search result")
        else:
            if (type == "T"):
                type = "tags";
                retPhotos = []
                if key is not None:
                    tags = key.split(" ")
                    for tag in tags:
                        print(tag)
                        cursor.execute("select distinct p.pid from Tags t,photos p,albums a"
                                       " where tname='{0}' and t.pid=p.pid and p.aid=a.aid and a.uid='{1}'"
                                       .format(tag, getCurrentUserId()))
                        retPhotos = tuple(set(cursor.fetchall()).union(set(retPhotos)))
                        print(retPhotos)
                photolist = getPhotoFromList(retPhotos)
                return render_template('searchPhoto.html', photos=photolist, uid=getCurrentUserId(), type=type,
                                       key='"' + key + '"',uname=getUserFname(),message="Here is your search result")

            elif (type == "C"):
                type = "comments";
                cursor.execute("select distinct c.pid from comments c,photos p,albums a "
                               "where text like '{0}' "
                               "and c.pid=p.pid and p.aid=a.aid and a.uid='{1}'".format('%' + key + '%',
                                                                                        getCurrentUserId()))
                retPhotos = cursor.fetchall()
                print(retPhotos)
                photolist = getPhotoFromList(retPhotos)
                return render_template('searchPhoto.html', photos=photolist, uid=getCurrentUserId(), type=type,
                                       key='"' + key + '"',uname=getUserFname(),message="Here is your search result")

            elif (type == "U"):
                return render_template('searchPhoto.html',message='search invalid',
                                       key='"' + key + '"',uname=getUserFname(),uid=getCurrentUserId(),type='users')

# search by click tag
@app.route("/searcht/<tag>", methods=['POST'])
def searchTag(tag):
    cursor.execute("select distinct pid from Tags where tname='{0}'".format(tag))
    a=cursor.fetchall()
    print (a)
    photolist=getPhotoFromList(a)
    return render_template('searchPhoto.html', photos=photolist,uid=getCurrentUserId(),type="tags",key='"'+tag+'"')

#add tags
@app.route("/Ctag/<pid>",methods=['POST'])
def AddTags(pid):
    cursor=conn.cursor()
    key=request.form['crtTag']
    tags = key.split(" ")
    for tag in tags:
        cursor.execute("select * from Tags where tname='{0}'".format(tag))
        if cursor.fetchone() is None:
            cursor.execute("insert into Tags VALUES ('{0}','{1}')".format(pid,tag))
            conn.commit()
    return flask.redirect(flask.url_for('photo', pid=pid))

#add album
@app.route("/createalbum/<uid>",methods=['POST'])
def AddAlbum(uid):
    an=request.values.get('createalbum')
    if an=='': aname="untitled"
    else: aname=an
    cursor=conn.cursor()
    cursor.execute("insert into albums(uid,aname) values ('{0}','{1}')".format(uid,aname))
    conn.commit()
    return flask.redirect(flask.url_for('findu',uid=uid))

#make comment
@app.route('/comment/<pid>',methods=['POST'])
def AddComment(pid):
    uid=getCurrentUserId()
    comt=request.values.get('addComment')
    cursor=conn.cursor()
    cursor.execute("insert into comments(uid,text,pid) values('{0}','{1}','{2}')".format(uid,comt,pid))
    conn.commit()

    return flask.redirect(flask.url_for('photo', pid=pid))

@app.route('/friend/<uid>',methods=['GET'])
@flask_login.login_required
def MakeFriends(uid):
    cursor=conn.cursor()
    ucurrent=getCurrentUserId()
    if getUsersFriend(uid, ucurrent):
        cursor.execute("delete from isfriend where uid='{0}' and fuid='{1}'".format(uid, ucurrent))
        cursor.execute("delete from isfriend where uid='{0}' and fuid='{1}'".format(ucurrent, uid))
        conn.commit()
    else:
        cursor.execute("insert into isfriend(uid,fuid) values('{0}','{1}'),('{1}','{0}')".format(uid, ucurrent))
    conn.commit()
    return flask.redirect(flask.url_for('findu',uid=uid))

#delete functions
@app.route('/deletea/<aid>',methods=['GET'])
@flask_login.login_required
def delalbum(aid):
    cursor=conn.cursor()
    uid=getCurrentUserId()
    cursor.execute("select * from albums where aid='{0}' and uid='{1}'".format(aid,uid))
    c=cursor.fetchone()
    if c is not None:
        cursor.execute("delete from albums where aid='{0}'".format(aid))
        conn.commit()
        return flask.redirect(flask.url_for('findu',uid=uid))
    else:
        return "not your album"

@app.route('/deletep/<pid>',methods=['GET'])
@flask_login.login_required
def delphoto(pid):
    cursor=conn.cursor()
    uid = getCurrentUserId()
    cursor.execute("select * from photos where pid='{0}' "
                   "and aid in (select aid from albums where uid='{1}')".format(pid,uid))
    if cursor.fetchone()is not None:
        cursor.execute("select aid from photos where pid='{0}'".format(pid))
        aid=cursor.fetchone()[0]
        cursor.execute("delete from photos where pid='{0}'".format(pid))
        conn.commit()
        return flask.redirect(flask.url_for('album', aid=aid))
    else:
        return "not your photo"

@app.route('/deletec/<cid>',methods=['GET'])
@flask_login.login_required
def delcom(cid):
    cursor=conn.cursor()
    uid = getCurrentUserId()
    cursor.execute("select * from comments where cid='{0}' and uid='{1}'".format(cid,uid))
    a=cursor.fetchone()is not None
    print(a)
    cursor.execute("select * from comments c,photos p where c.cid='{0}' and c.pid=p.pid "
                   "and p.aid in (select aid from albums where uid='{1}')".format(cid, uid))
    b=cursor.fetchone()is not None
    print(b)
    if a|b:
        cursor.execute("select pid from comments where cid='{0}'".format(cid))
        pid=cursor.fetchone()[0]
        cursor.execute("delete from comments where cid='{0}'".format(cid))
        conn.commit()
        return flask.redirect(flask.url_for('photo', pid=pid))
    else:
        return "not your comment or photo"

@app.route('/like/<pid>',methods=['GET'])
@flask_login.login_required
def likechange(pid):
    cursor=conn.cursor()
    uid=getCurrentUserId()
    if not getUsersLike(uid,pid):
        cursor.execute("insert into likephoto(uid,pid) VALUES ('{0}','{1}')".format(uid,pid))
        conn.commit()
    else:
        cursor.execute("delete from likephoto where uid='{0}' and '{1}'".format(uid,pid))
        conn.commit()
    return flask.redirect(flask.url_for('photo', pid=pid))

def suggestFriends(uid):
    cursor=conn.cursor()
    cursor.execute("select c1.u1 from"
                   "(select uid as u1,count(uid)as u1c1 from isfriend group by uid) c1,"
                   "(select find3.u2,count(find3.u2)as u1c from isfriend a1, isfriend b1,"
                   "(select c.uid as u2 from isfriend a, isfriend b, isfriend c "
                   "where a.uid='{0}' and b.uid=a.fuid and b.fuid=c.uid and c.uid<>'{0}') find3 "
                   "where a1.uid=find3.u2 and b1.uid=a1.fuid and b1.fuid='{0}' group by find3.u2) c2 "
                   "where c1.u1=c2.u2 and not exists (select * from isfriend where uid='{0}' and fuid=c1.u1)"
                   " order by c2.u1c/c1.u1c1 DESC".format(uid))
    return cursor.fetchall()

def suggestPhotos(uid):
    cursor=conn.cursor()
    cursor.execute("select p1 from"
                   "(select pid as p1, count(pid) as cp1 from tags group by pid) t1,"
                   "(select pid as p2, count(pid) as cp2 from tags,"
                   "(select DISTINCT c.tname as tagn from tags c,albums b,photos a "
                   "where b.uid='{0}' and a.aid=b.aid and c.pid=a.pid) tn "
                   "where tags.tname in (tagn) "
                   "group by pid) t2 "
                   "where t1.p1=t2.p2 and "
                   "not exists( select * from photos p,albums al where p.pid=p1 and p.aid=al.aid and al.uid='{0}')"
                   "order by p1,cp2/cp1 desc".format(uid))
    return cursor.fetchall()


@app.route('/global')
def popular():
    cursor=conn.cursor()
    cursor.execute("select * from contribution")
    popularu =cursor.fetchall()
    print ('a',popularu)
    cursor.execute("select * from tagcount")
    populart=cursor.fetchall()
    return render_template("Global.html",uid=getCurrentUserId(),uname=getUserFname(),actusers=popularu,tags=populart)


def getFriendsList(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT u1.uid AS ID, u1.fname AS FirstName, u1.lname AS LastName " 
                    "FROM Users AS u1 " 
                    "WHERE u1.uid IN (SELECT f.fuid FROM isFriend AS f WHERE f.uid = '{0}')" 
                    "ORDER BY u1.fname, u1.lname".format(uid))
    return cursor.fetchall()


#get photo by pidlist from cursor
def getPhotoFromList(list):
    plist=[]
    for pid in list:
        cursor=conn.cursor()
        cursor.execute("select * from photos where pid='{0}'".format(pid[0]))
        a=cursor.fetchone()
        plist.append(a)
    return plist

#get people by pidlist from cursor
def getPeopleFromList(list):
    plist=[]
    for uid in list:
        cursor=conn.cursor()
        cursor.execute("select * from users where uid='{0}'".format(uid[0]))
        a=cursor.fetchone()
        plist.append(a)
    return plist

# default page
@app.route("/", methods=['GET','POST'])
def hello():
    id=getCurrentUserId()
    return render_template('Hello.html', message='Welcome to PhotoShare',
                           uid=id,uname=getUserFname())


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
#    contribution()
    app.run(port=5000, debug=True)
