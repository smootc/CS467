from flask import Flask, render_template, request, url_for, redirect
import requests
import records
import dbconfig

app = Flask(__name__, static_url_path='')

db = records.Database('postgresql://{user}:{pw}@{url}/{dbName}'.format(user=dbconfig.POSTGRES_USER, pw=dbconfig.POSTGRES_PW, url=dbconfig.POSTGRES_URL, dbName=dbconfig.POSTGRES_DB))


#how do we plan on passing this from login?
currUser = 12

@app.route('/', methods=['GET'])
def main():
    #updated to sort then select first row
    user_health = db.query('SELECT * FROM health WHERE user_id=:currUser ORDER BY time_created DESC FETCH FIRST 1 ROW ONLY', currUser=currUser)

    health = []
    for i in user_health:
        health.append(i.bmi)

    if (len(health) < 1):
	health = "None"

    user_goals = db.query('SELECT * FROM goals WHERE user_id=:currUser ORDER BY time_created DESC FETCH FIRST 5 ROws ONLY', currUser=currUser)

    goals=[]
    for i in user_goals:
        goals.append(i.notes)

    if (len(goals) < 1):
        goals = "None"

    user_activities = db.query('SELECT * FROM activities WHERE user_id=:currUser ORDER BY time_created DESC FETCH FIRST 5 ROWS ONLY', currUser=currUser)
    
    activities = []
    for i in user_activities:
        activities.append(i)

    if (len(activities) < 1):
        activities = "None"
 
    return render_template("index.html", health=health, goals = goals, activities=activities)

@app.route('/health', methods=['GET', 'POST'])
def health():
    user_health = db.query('SELECT * FROM health WHERE user_id=:currUser ORDER BY time_created DESC FETCH FIRST 1 ROW ONLY', currUser=currUser)
    
    health = []
    for i in user_health:
        health.append(i)

    if (len(health) < 1):
        health = "None"
 
    if request.method == 'POST':
        newWeight = request.form['newWeight']
        newHeight = request.form['newHeight']
        newWeight = float(newWeight)
        newHeight = float(newHeight)
        newBmi = ((newWeight/newHeight)/newHeight) * 703
	newBmi = round(newBmi,0)
	newBmi = int(newBmi)
        newHeight = int(newHeight)
	newWeight = int(newWeight)
        db.query('INSERT INTO health (user_id, height, weight, bmi) VALUES(:currUser, :newHeight, :newWeight, :newBmi)', newHeight=newHeight, newWeight=newWeight, newBmi=newBmi, currUser=currUser)
        return redirect(url_for('health'))

    return render_template('health.html', health=health)

@app.route('/activities', methods=['GET', 'POST'])
def activities():
    user_activities = db.query('SELECT activities.id, activities.activity_type, activities.distance, activities.duration, goals.notes FROM activities INNER JOIN goals ON activities.goal_id=goals.id WHERE activities.user_id = :currUser ORDER BY activities.time_created DESC FETCH FIRST 5 ROWS ONLY', currUser=currUser)
    user_goals = db.query('SELECT * FROM goals WHERE goals.user_id = :currUser', currUser=currUser)
    
    activities=[]
    for i in user_activities:
        activities.append(i)

    if (len(activities)) < 1:
	user_activities = "None"

    if request.method == 'POST':
        newType = request.form['newType']
        forGoal = request.form['forGoal']
        newDist = request.form['newDist']
        newDur = request.form['newDur']
        goalLookup = db.query('SELECT * FROM goals WHERE goals.notes = :forGoal AND goals.user_id = :currUser', forGoal=forGoal, currUser=currUser)
	for i in goalLookup:
	    forGoalID = i.id
        db.query('INSERT INTO activities (user_id, activity_type, goal_id ,duration, distance) VALUES (:currUser, :newType, :forGoalID, :newDur, :newDist)', currUser=currUser, newType=newType, forGoalID=forGoalID, newDist=newDist, newDur=newDur)
        return redirect(url_for('activities'))

    return render_template('activities.html', user_activities=user_activities, user_goals=user_goals)


@app.route('/deleteActivity/<aid>', methods=['POST', 'DELETE'])
def delete_activity(aid):
    if request.method == 'POST':
        db.query('DELETE FROM activities WHERE id = :aid', aid=aid)
        return redirect(url_for('activities'))

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    user_goals = db.query('SELECT * FROM goals WHERE user_id = :currUser ORDER BY time_created DESC FETCH FIRST 5 ROW ONLY', currUser=currUser)
    
    goals=[]
    for i in user_goals:
        goals.append(i)

    if (len(goals)) < 1:
	user_goals = "None"

    if request.method == 'POST':
        newNote = request.form['newNote']
        newType = request.form['newType']
        newDist = request.form['newDist']
        newDur = request.form['newDur']
        db.query('INSERT INTO goals (user_id, activity_type, distance, duration, notes) VALUES (:currUser, :newType, :newDist, :newDur, :newNote)', currUser=currUser, newType=newType, newDist=newDist, newDur=newDur, newNote=newNote)
        return redirect(url_for('goals'))
    
    return render_template('goals.html', user_goals=user_goals)


@app.route('/deleteGoal/<gid>', methods=['POST'])
def delete_goal(gid):
    if request.method == 'POST':
	db.query('DELETE FROM goals WHERE id = :gid', gid=gid)
	return redirect(url_for('goals'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='13667', debug=True)
