from flask import Flask, render_template, request, url_for, redirect
import json
import requests
import records
import dbconfig

app = Flask(__name__, static_url_path='')

db = records.Database('postgresql://{user}:{pw}@{url}/{dbName}'.format(user=dbconfig.POSTGRES_USER, pw=dbconfig.POSTGRES_PW, url=dbconfig.POSTGRES_URL, dbName=dbconfig.POSTGRES_DB))


#how do we plan on passing this from login?
currUser = 6

@app.route('/', methods=['GET'])
def main():
    users_health = db.query('SELECT * FROM health')
    for i in users_health:
        if i.user_id == currUser:
            bmi = i.bmi
    all_goals = db.query('SELECT * FROM goals')
    goals=[]
    for i in all_goals:
        if i.user_id == currUser:
            goals.append(i.notes)
    all_activities = db.query('SELECT * FROM activities')
    activities=[]
    for i in all_activities:
        if i.user_id == currUser:
            activities.append(i)
                
    return render_template("index.html", bmi = bmi, goals = goals, activities=activities)

@app.route('/health', methods=['GET', 'POST'])
def health():
    users_health = db.query('SELECT * FROM health')
    for i in users_health:
        if i.user_id == currUser:
            bmi = i.bmi
            weight = i.weight
            height = i.height
            
    if request.method == 'POST':
        newWeight = request.form['newWeight']
        newHeight = request.form['newHeight']
        newWeight = int(newWeight, 10)
        newHeight = int(newHeight, 10)
        newBmi = ((newWeight/newHeight)/newHeight)*703
        newBmi = round(newBmi)
        db.query('UPDATE health SET height=:newHeight, weight=:newWeight,bmi=:newBmi WHERE user_id = :currUser', newHeight=newHeight, newWeight=newWeight, newBmi=newBmi, currUser=currUser)
        return redirect(url_for('health'))

    return render_template('health.html', bmi=bmi, weight=weight, height=height)

@app.route('/activities', methods=['GET', 'POST'])
def activities():
    user_activities = db.query('SELECT activities.activity_type, activities.distance, activities.duration, goals.notes FROM activities INNER JOIN goals ON activities.goal_id=goals.id WHERE activities.user_id = :currUser', currUser=currUser)
    user_goals = db.query('SELECT * FROM goals WHERE goals.user_id = :currUser', currUser=currUser)

    if request.method == 'POST':
        newType = request.form['newType']
        forGoal = request.form['forGoal']
        newDist = request.form['newDist']
        newDur = request.form['newDur']
        forGoalID = db.query('SELECT id FROM goals WHERE goals.notes LIKE :forGoal AND goals.user_id = :currUser', forGoal=forGoal, currUser=currUser)
        db.query('INSERT INTO activities (user_id, activity_type, goal_id ,duration, distance) VALUES (:currUser, :newType, :forGoalID, :newDur, :newDist)', currUser=currUser, newType=newType, forGoalID=forGoalID, newDist=newDist, newDur=newDur)
        return redirect(url_for('activities'))

    return render_template('activities.html', user_activities=user_activities, user_goals=user_goals)

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    user_goals = db.query('SELECT * FROM goals WHERE user_id = :currUser', currUser=currUser)

    if request.method == 'POST':
        newNote = request.form['newNote']
        newType = request.form['newType']
        newDist = request.form['newDist']
        newDur = request.form['newDur']
        db.query('INSERT INTO goals (user_id, activity_type, distance, duration, notes) VALUES (:currUser, :newType, :newDist, :newDur, :newNote)', currUser=currUser, newType=newType, newDist=newDist, newDur=newDur, newNote=newNote)
        return redirect(url_for('goals'))
    
    return render_template('goals.html', user_goals=user_goals)

@app.route('/deleteActivities', methods=['POST'])
def deleteActivities():
    user_activities = db.query('SELECT activities.activity_type, activities.distance, activities.duration FROM activities WHERE activities.user_id = :currUser', currUser=currUser)

    if request.method == 'POST':
        delID = request.POST['activity.activity_id']
        db.query('DELETE FROM activities WHERE delID = id', delID=delID)
        return redirect(url_for('deleteActivities'))

    return render_template('deleteActivities.html', user_activities=user_activities)
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5432', debug=True)
