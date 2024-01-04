from flask import Flask, render_template, request, redirect, url_for,session,flash
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, random
import bcrypt
import smtplib
app = Flask(__name__)
otp=random.randint(1111,9999)
def get_country():
    try:
        response = requests.get("http://ip-api.com/json/")
        js=response.json()
        lat = js['lat']
        lon = js['lon']
        #print(lat,lon)
        yorn=fence(lat,lon)
        return yorn
    except Exception as e:
        return "Unknown"
app.config['SECRET_KEY'] = 'MajrProj'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logdb.db'
app.config['SQLALCHEMY_BINDS'] = {'usr':'sqlite:///users.db'}
def pointstatus(lowerx,higherx,lowery,highery,x,y,la,lo):
    if(x > lowerx and x < higherx and y > lowery
    and y < highery):
        return 'A'
    else:
        s=len(la)
        for i in range(0,s):
            if((la[i]==x)and(lo[i]==y)):
                return 'B'
        return 'C'
def fence(lat,lon):
    '''n = int(input('Enter the number of vertices set in polygon :'))
    la=[]
    lo=[]
    print('Enter the x-coordinates of polygon : ')
    for i in range(n):
        lat =float(input())
        la.append(lat)
    print('Enter the y-coordinates of polygon : ')
    for i in range(n):
        lon = float(input())
        lo.append(lon)'''
    n=4
    la=[0,200,200,0]
    lo=[0,0,200,200]
    lowerx=min(la)
    higherx=max(la)
    lowery=min(lo)
    highery=max(lo)
    #print('X coordinate to search:')
    x=lat
    # print('Y coordinate to search:')
    y=lon
    if (pointstatus(lowerx,higherx,lowery,highery,x,y,la,lo)=='A'):
        return 0 #('Inside the geofence')
    elif(pointstatus(lowerx,higherx,lowery,highery,x,y,la,lo)=='B'):
        return 1 #print('On the geofence')
    else:
        return 2 #print('Outside the geofence')

db= SQLAlchemy(app)  
class Users(db.Model):
    __bind_key__ = 'usr'
    id=db.Column(db.Integer, primary_key=True, nullable = False)
    u_name= db.Column(db.String(100), nullable=False)
    passwrd = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phno=db.Column(db.String(20),nullable=False)
    ro=db.Column(db.String(20))
    def __repr__(self):
        return 'users' + str(self.id)        
class Logdbase(db.Model):
    i=db.Column(db.Integer,primary_key=True) 
    empid=db.Column(db.Integer, nullable = False)
    emp_mail= db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), default=datetime.now().strftime("%m/%d/%y at %H:%M:%S"))
    notify = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return 'employees' + str(self.empid)
db.create_all()
@app.route('/')
def funa():
    return render_template('index.html')
@app.route('/si')
def fun12():
    return render_template('signin.html')
@app.route("/postsignup",methods=["POST"])
def signuu():
    email=request.form['uname']
    #session['otpu']=request.form['uname']
    #session['otpp']=request.form['psw']
    password=request.form['psw']
    name=request.form['name']
    r=request.form.get('abcd')
    #print(r)
    ph=request.form['ph']
    ch=password.encode('utf-8')
    hashed=bcrypt.hashpw(ch,bcrypt.gensalt())
    #print(hashed)
    new_post = Users(u_name=email, passwrd=hashed, name=name,phno=ph, ro=r)
    db.session.add(new_post)
    db.session.commit()
    '''s=smtplib.SMTP('smtp.gmail.com',587)
    s.starttls()
    s.login(request.form['uname'],password)
    msg="OTP generated is "+str(otp)+".Please use this otp to verify successful sign up"
    s.sendmail(request.form['uname'],request.form['uname'],msg)
    s.quit()'''
    print(otp)
    return render_template("otppage.html")
@app.route("/postOTP",methods=["POST"])
def otppost():
    if request.form['otp1']==str(otp):
        return render_template('signin.html')
    else:
        flash("Invalid OTP")
        return render_template('signin.html')
@app.route("/postsignin",methods=['POST','GET'])
def success():
    em=request.form['uname']
    ps=request.form['psw']
    try:
        u = Users.query.filter_by(u_name=em).first_or_404()
        #print(u)
        roo=request.form.get('abcd')
        if u:
            psw1=u.passwrd
            if bcrypt.checkpw(ps.encode('utf-8'),psw1):
                session['idu']=u.id
                session['m']=u.u_name
                if roo==u.ro:
                    if roo=="c": 
                        return render_template('consentmng.html')
                    elif roo=="d":
                        return render_template('consentemp.html')
                    else:
                        return render_template('consentemp.html')
                else:
                    flash("Invalid Role")
                    return render_template('signin.html')
            else:
                flash("Invalid Password")
                return render_template('signin.html')
    except Exception as ex:
        flash("Invalid UserID...Try to signup first")
        return render_template('index.html') 

@app.route('/consentyes',methods=['POST','GET'])
def yesconsent():
    country = get_country()
    print(country)
    if country==0:
        new_post = Logdbase(empid=session['idu'], emp_mail=session['m'], notify="Inside the fence")
        db.session.add(new_post) 
        db.session.commit()
    elif country==1:
        new_post = Logdbase(empid=session['idu'], emp_mail=session['m'], notify="On the fence")
        db.session.add(new_post) 
        db.session.commit() 
    else:
        new_post = Logdbase(empid=session['idu'], emp_mail=session['m'], notify="Outside the fence")
        db.session.add(new_post) 
        db.session.commit()  
    return render_template('th.html')     
@app.route('/consentno',methods=['POST','GET'])
def noconsent():
    new_post = Logdbase(empid=session['idu'], emp_mail=session['m'], notify="Consent not given")
    db.session.add(new_post) 
    db.session.commit()  
    return render_template('th.html')
@app.route("/out",methods=['GET'])
def out1():
    session['us']=False
    session['idu']=None
    return render_template('index.html')
@app.route("/myattm",methods=['GET','POST'])
def myat():
    all_posts = Logdbase.query.filter_by(empid =session['idu']).all()
    return render_template('tablemng.html',posts=all_posts)
@app.route("/myempm",methods=['GET','POST'])
def myat1():
    all_posts = Logdbase.query.filter(Logdbase.empid !=session['idu']).all()
    print("came here")
    return render_template('tablemng.html',posts = all_posts)
@app.route("/postattm",methods=['GET','POST'])
def myat2():
    return render_template('mngcon.html')
@app.route("/myatte",methods=['GET','POST'])
def myat3():
    all_posts = Logdbase.query.filter_by(empid=session['idu']).all()
    return render_template('tableemp.html',posts=all_posts)
@app.route('/postatte',methods=['GET','POST'])
def myat4():
    return render_template('empcon.html')
@app.route("/consentmng",methods=['GET','POST'])
def myat5():
    return render_template('consentmng.html')
@app.route("/consentemp",methods=['GET','POST'])
def myat6():
    return render_template('consentemp.html')
if __name__ == "__main__":
    app.run(debug=True)