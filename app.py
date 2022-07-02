import sqlite3
import cv2
import os
import time
import imutils
import numpy as np
from sklearn.metrics import pairwise
import time
import tensorflow as tf
from keras.datasets import mnist
from keras.models import Sequential
from keras.models import model_from_json
from keras.models import load_model
from keras.layers import Dense
from keras.layers import Dropout
from keras.utils import np_utils
import glob

from flask import *

global loadedModel
loadedModel = load_model('full_model.h5')
path = "/static/Plain"
size = 300

app = Flask(__name__)
# resize the frame to required dimensions and predict
def predict_pothole(currentFrame):
    currentFrame = cv2.resize(currentFrame, (size, size))
    currentFrame = currentFrame.reshape(1, size, size, 1).astype('float')
    currentFrame = currentFrame / 255
    prob = loadedModel.predict(currentFrame)
    classes_x = np.argmax(prob, axis=1)
    print(classes_x[0])
    if classes_x[0] == 1:
        print("Pothole Detected")

    else:
        print("Road is Plane")
    max_prob = classes_x[0]
    if (max_prob > .90):
        return (loadedModel.predict(currentFrame) > 0.5).astype("int32"), max_prob
        #return loadedModel.predict_classes(currentFrame), max_prob
    return "none", 0

@app.route('/')
def index():
    return redirect(url_for('home'))
@app.route('/log')
def log():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/sign_up',methods=['POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form['name']
        mob = request.form['mob']
        mail = request.form['mail']
        psw = request.form['psw']
        conn = sqlite3.connect('data.db')
        conn.execute("INSERT INTO accounts(name,mob,mail,psw) VALUES(?,?,?,?)",(name,mob,mail,psw))
        conn.commit()
        msg = "Registered Successfully"
        return render_template("register.html",msg=msg)
@app.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
        mail = request.form['user']
        psw = request.form['psw']
        conn = sqlite3.connect('data.db')
        cur = conn.execute("SELECT * FROM accounts WHERE mail=? AND psw=?",(mail,psw))
        rows = cur.fetchone()
        if rows == None:
            msg = "Invalid Id & Password"
            return render_template('login.html',msg=msg)
        else:
            return render_template('home.html')
@app.route('/logout')
def logout():
    return render_template('login.html')
@app.route('/predict',methods=['POST'])
def predict():
    if request.method == "POST":
        sname=request.form['sname']
        file= request.files['file']
        f=file.filename
        if not os.path.isdir('static/'+str(sname)):
            os.mkdir('static/'+sname)




        camera = cv2.VideoCapture(f)

        show_pred = False
        n1=n2=n3=0

        # loop until interrupted
        while (True):

            (grabbed, frame) = camera.read()
            if grabbed == True:
                frame = imutils.resize(frame, width=700)
                # frame = cv2.flip(frame, 0)

                clone = frame.copy()

                (height, width) = frame.shape[:2]

                grayClone = cv2.cvtColor(clone, cv2.COLOR_BGR2GRAY)

                pothole, prob = predict_pothole(grayClone)
                n1 = n1 + 1
                print(pothole, prob, n1)

                if prob > 0:
                    n2 = n2 + 1
                    if n2>n3+40:
                        n3=n2
                        cv2.imwrite(os.path.join('static/'+str(sname),str(n2)+'.jpg'),frame)
                if(n1==100 or n1==200 or n1==300 or n1==400):
                    cv2.imwrite(os.path.join('static/' + str(sname), str(n1) + '.jpg'), frame)

                keypress_toshow = cv2.waitKey(1)

                if (keypress_toshow == ord("e")):
                    show_pred = not show_pred

                if True:
                    cv2.putText(clone, "Pothole" + ' ' + str(prob * 100) + '%', (30, 30), cv2.FONT_HERSHEY_DUPLEX, 1,
                                (0, 255, 0), 2)

                cv2.imshow("GrayClone", grayClone)

                cv2.imshow("Video Feed", clone)

            else:
                damage = (n2 / n1) * 100
                damage=round(damage, 2)
                break
        camera.release()

        cv2.destroyAllWindows()
        conn = sqlite3.connect("data.db")
        cur = conn.execute("SELECT * FROM s_road WHERE s_name=?",(sname,))
        row=cur.fetchone()
        if row==None:
            conn.execute("INSERT INTO s_road(s_name,accuracy)VALUES(?,?)",(sname,damage))
            conn.commit()
            conn = sqlite3.connect("data.db")
            rows = conn.execute("SELECT * FROM s_road")
            return render_template("result.html",rows=rows)
        else:
            conn.execute("UPDATE s_road SET accuracy=? WHERE s_name=?",(damage,sname))
            conn.commit()
            conn = sqlite3.connect("data.db")
            rows = conn.execute("SELECT * FROM s_road")
            return render_template("result.html",rows=rows)

@app.route('/view/<a>')
def view(a):
    folder='static/'+str(a)
    rows=[]
    for count, filename in enumerate(os.listdir(folder)):
        rows.append(filename)
    return render_template("view.html",rows=rows,a=a)
@app.route('/home')
def home():
    conn = sqlite3.connect("data.db")
    rows = conn.execute("SELECT * FROM s_road")
    return render_template("result.html",rows=rows)
# main function
if __name__ == '__main__':
    app.run(host="0.0.0.0")