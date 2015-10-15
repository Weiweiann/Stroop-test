# coding: utf-8
# get_ipython().magic('save stroop_test2.py 1-72')

# %load "./stroop_test.py"
from flask  import Flask, request, render_template, url_for, redirect, g
import sqlite3
import random
from datetime import datetime as time

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
    global test_times
    global correct_times
    global max_testtimes
    global total_right_time
    global total_wrong_time


    max_testtimes = 10    # the exam times, set any number as you want!
    test_times = 0
    correct_times = 0
    total_right_time = 0
    total_wrong_time = 0



    return render_template('index.html')

@app.route('/ready', methods=['POST','GET'])
def ready():
    global username

    if request.method == "POST":
        db = get_db()
        global username
        username = request.form.get("username")
        with db:
            db.execute("insert into persons(name) values(?);", (username,))
        return redirect(url_for('stroop'))
    else:
        return 'GET method is not supported'



@app.route('/stroop')
def stroop():
    global test_times

    test_times += 1
    print("this is the ", test_times, "test.")
    global starttime
    starttime = time.now()
    return render_template('stroop.html')


@app.route('/start', methods=['GET','POST'])
def color_selection():
    global test_times
    global max_testtimes
    global correct_times
    global endtime
    global r_img_name
    global starttime
    global total_time

    db = get_db()
    with db:
        cursor = db.execute("SELECT image_name from image")
    images=[
            row[0] for row in cursor
            ]
    random_img = random.choice(images)
    r_img_name = random_img
    random_img_path = url_for('static', filename = 'img/' + random_img + '.png')

    return render_template('stroop.html',img=random_img_path)



@app.route('/answer', methods=['POST'])
def speech_comparsion():
    if request.method == 'POST':
        answer = request.get_json(force=True)
        print(answer)
        return("finally")
       
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
        db.execute('update persons set accuracy = ?  where name = ?',(accuracy,username))
        db.execute('update persons set timespend = ? where name = ?', (time, username))
        db.execute('update persons set wrong_time = ? where name = ?', (total_wrong_time, username))
        db.execute('update persons set right_time = ? where name = ?', (total_right_time, username))
        db.execute('update persons set timespend = ? where name = ?', (time, username))
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



