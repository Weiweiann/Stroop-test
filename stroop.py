# coding: utf-8
# get_ipython().magic('save stroop_test2.py 1-72')

# %load "./stroop_test.py"
from flask  import Flask, request, render_template, url_for, redirect, g
import sqlite3
import random
from datetime import datetime as time
from time import sleep
import random
app = Flask(__name__)


# example from offical website of flask---
DATABASE = "./stroop.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
# ---

@app.route('/')
def home():
    speechjs = url_for('static', filename = 'js/speechRecognition_continous.js')
    return render_template('index.html',speechjs=speechjs)

@app.route('/ready', methods=['POST','GET'])
def ready():
    global username
    global test_times
    global correct_times
    global max_testtimes
    global total_right_time
    global total_wrong_time
    global random_img
    global userid

    max_testtimes = 5    # the exam times, set any number as you want!
    test_times = 0
    correct_times = 0
    total_right_time = 0
    total_wrong_time = 0

    db = get_db()
    with db:
        cursor = db.execute("SELECT image_name from image")
    images=[
            row[0] for row in cursor
            ]
    random_img = [images[1],images[3],images[5],images[7],images[9]]
   

    if request.method == "POST":
        db = get_db()
        global username
        username = request.form.get("username")
        with db:
            db.execute("insert into persons(name) values(?);", (username,))
            cursor = db.execute("select id from persons where name=(?) order by id desc limit 1", (username,))
            userid = [row[0] for row in cursor][0]
        return redirect(url_for('start'))
    elif request.method == 'GET':
        return 'GET method is not supported'
    else:
        return 'error occurs'

@app.route('/start')
def start():
    global test_times
    global r_img_name
    global starttime
    
    
    test_times += 1

    if test_times <= max_testtimes:
        print("this is the ", test_times, "test.")
        starttime = time.now()

        r_img_name = str(random_img[test_times-1])
        print(r_img_name)

        random_img_path = url_for('static', filename = 'img/' + r_img_name + '.png')
        speechjs = url_for('static', filename = 'js/speechRecognition.js')
        return render_template('stroop.html',img=random_img_path, speechjs=speechjs)
    else:
        sleep(random.choice([2,3,2.5]))
        return redirect(url_for('finished'))

@app.route('/answer', methods=['POST','GET'])
def answer():
    global test_times
    global max_testtimes
    global correct_times
    global endtime
    global r_img_name
    global starttime
    global total_time
 

    if request.method == 'POST':
        # answer = request.get_json(force=True)
        answer = request.form['ans']
        if answer == "紅色":
            answer_real = "R"
        elif answer == "藍色":
            answer_real = "B"
        elif answer == "綠色":
            answer_real = "G"
        elif answer == "黃色":
            answer_real = "Y" 
        else:
            answer_real = ""

        db = get_db()
        c = db.execute("SELECT color FROM image WHERE image_name = ?", (r_img_name,))
        right_answer = [r[0] for r in c][0]
    else:
        return 'ooops'


    if request.method == 'POST':
        time = request.form['time']
        print(type(time),flush=True)
        time = round(float(time),2)
        print(type(time),time,flush=True)
        print(type(userid),userid,flush=True)
        if answer_real == right_answer:
            correct_times += 1
            print("Correct! " + answer)
            global total_right_time
            total_right_time += time

            db = get_db()
            with db:
                cursor = db.execute("update persons set test" + str(test_times) + " = ? where id = ?", (time,userid))
     
            sleep(random.choice([2,3,2.5]))
            return redirect(url_for('start'))
        else:
            print("Oops. " + answer)
            global total_wrong_time
            total_wrong_time += time
            db = get_db()
            with db:
                cursor = db.execute("update persons set test" + str(test_times) + " = ? where id = ?", (time,userid))

            sleep(random.choice([2,3,2.5]))
            return redirect(url_for('start'))
    else:
        return "You shall not GET here!"

        
@app.route('/finished')
def finished():
    global correct_times
    global total_time
    global max_testtimes
    global total_right_time
    global total_wrong_time

    accuracy = (correct_times / (max_testtimes))*100
    db = get_db()
    time = total_right_time + total_wrong_time

    with db:
        db.execute('update persons set accuracy = ?  where id = ?',(accuracy,userid))
        db.execute('update persons set timespend = ? where id = ?', (time, userid))
        db.execute('update persons set wrong_time = ? where id = ?', (total_wrong_time, userid))
        db.execute('update persons set right_time = ? where id = ?', (total_right_time, userid))
        db.execute('update persons set timespend = ? where id = ?', (time, userid))
    return render_template('finished.html', name=username,accuracy=accuracy, time_spend=time)



@app.route('/history')
def history():
    db = get_db();
    with db:
        history = db.execute('select * from persons order by time desc limit 30')
    history_fetch = [
               row[1:] for row in history
               ]
    return render_template('history.html', history_fetch=history_fetch)



if __name__ == '__main__':
    app.debug = True
    app.run("0.0.0.0")



