import setupDB
import config

from flask import Flask, render_template, request, url_for, redirect, session
import requests
import records
import os

app = Flask(__name__, static_url_path='')

db = records.Database('postgresql://{user}:{pw}@{url}/{dbName}'.format(user=config.POSTGRES_USER, pw=config.POSTGRES_PW, url=config.POSTGRES_URL, dbName=config.POSTGRES_DB))

#needed to maintain login state
#app.secret_key = config.SECRET_KEY

#how do we plan on passing this from login?
currUser = 12

#----------------------------------------------------------------------
#User page homescreen
#----------------------------------------------------------------------
@app.route('/', methods=['GET'])
def main():
    #query for the username for greeting
    username = db.query('SELECT * FROM user_data WHERE id=:currUser', currUser=currUser)    

    #ensure that the name is a string
    for i in username:
        name = str(i.user_name)
 
    #query for the specific user's health, but only return the most recently
    #created row
    user_health = db.query('SELECT * FROM health WHERE user_id=:currUser ORDER BY time_created DESC FETCH FIRST 1 ROW ONLY', currUser=currUser)

    #add the results to an array and include the bmi found in the query 
    #in user_health
    health = []
    for i in user_health:
        health.append(i.bmi)

    #if the query result was empty, using "None as an identifier in html to
    #tell user that they have not provided health info
    if (len(health) < 1):
	health = "None"

    #query for the specific user's goals, sort and grab only the last 5 goals
    #created
    user_goals = db.query('SELECT * FROM goals WHERE user_id=:currUser ORDER BY time_created DESC FETCH FIRST 5 ROws ONLY', currUser=currUser)

    #add results to an array
    goals=[]
    for i in user_goals:
        goals.append(i.notes)

    #if query is empty, "None" identifies to html to inform user
    if (len(goals) < 1):
        goals = "None"

    #query for the specific user's activities, sort and grab only the last
    #5 goals created
    user_activities = db.query('SELECT * FROM activities WHERE user_id=:currUser ORDER BY time_created DESC FETCH FIRST 5 ROWS ONLY', currUser=currUser)
   
    #add results to an array 
    activities = []
    for i in user_activities:
        activities.append(i)

    #if query is empty, "None" identifies to html to inform user
    if (len(activities) < 1):
        activities = "None"
 
    return render_template("index.html", health=health, goals = goals, activities=activities, name=name)

#-------------------------------------------------------------------------
#User's health page (view, add, and delete functions)
#-------------------------------------------------------------------------
@app.route('/health', methods=['GET', 'POST'])
def health():
    #query for the user's most recently created health record
    user_health = db.query('SELECT * FROM health WHERE user_id=:currUser ORDER BY time_created DESC FETCH FIRST 1 ROW ONLY', currUser=currUser)
    
    #add the query results to an array
    health = []
    for i in user_health:
        health.append(i)

    #if query is empty, "None" identifies to html to inform user
    if (len(health) < 1):
        health = "None"
 
    #Inserting a new row
    if request.method == 'POST':
        newWeight = request.form['newWeight']
        newHeight = request.form['newHeight']
        newWeight = float(newWeight)
        newHeight = float(newHeight)
        #most be calculated after user has provided their health info
        newBmi = ((newWeight/newHeight)/newHeight) * 703
	newBmi = round(newBmi,0)
	newBmi = int(newBmi)
        newHeight = int(newHeight)
	newWeight = int(newWeight)
        db.query('INSERT INTO health (user_id, height, weight, bmi) VALUES(:currUser, :newHeight, :newWeight, :newBmi)', newHeight=newHeight, newWeight=newWeight, newBmi=newBmi, currUser=currUser)
        return redirect(url_for('health'))

    return render_template('health.html', health=health)

#-------------------------------------------------------------------------
#User's activities page (view and add functionality)
#-------------------------------------------------------------------------
@app.route('/activities', methods=['GET', 'POST'])
def activities():
    #query for the user's 5 most recent activities, inner join goals to provide the
    #description of the goal associated with the activity logged
    user_activities = db.query('SELECT activities.id, activities.activity_type, activities.distance, activities.duration, goals.notes FROM activities INNER JOIN goals ON activities.goal_id=goals.id WHERE activities.user_id = :currUser ORDER BY activities.time_created DESC FETCH FIRST 5 ROWS ONLY', currUser=currUser)
    #get all the goals for that user
    user_goals = db.query('SELECT * FROM goals WHERE goals.user_id = :currUser', currUser=currUser)
    
    #add results to an array
    activities=[]
    for i in user_activities:
        activities.append(i)


    #if query is empty, "None" identifies to html to inform user
    if (len(activities)) < 1:
	user_activities = "None"

    #insert new row
    if request.method == 'POST':
        newType = request.form['newType']
        forGoal = request.form['forGoal']
        newDist = request.form['newDist']
        newDur = request.form['newDur']
        goalLookup = db.query('SELECT * FROM goals WHERE goals.notes = :forGoal AND goals.user_id = :currUser', forGoal=forGoal, currUser=currUser)

        #get the id for the goal the user selected
	for i in goalLookup:
	    forGoalID = i.id
        db.query('INSERT INTO activities (user_id, activity_type, goal_id ,duration, distance) VALUES (:currUser, :newType, :forGoalID, :newDur, :newDist)', currUser=currUser, newType=newType, forGoalID=forGoalID, newDist=newDist, newDur=newDur)
        return redirect(url_for('activities'))

    return render_template('activities.html', user_activities=user_activities, user_goals=user_goals)

#-------------------------------------------------------------------------
#Route for deleting a row from the activities table
#-------------------------------------------------------------------------
@app.route('/deleteActivity/<aid>', methods=['POST', 'DELETE'])
def delete_activity(aid):
    if request.method == 'POST':
        db.query('DELETE FROM activities WHERE id = :aid', aid=aid)
        #reroute back to the activities page
        return redirect(url_for('activities'))

#-------------------------------------------------------------------------
#User's goals page (view and add functionality)
#-------------------------------------------------------------------------
@app.route('/goals', methods=['GET', 'POST'])
def goals():
    #query for the 5 most recently created goals
    user_goals = db.query('SELECT * FROM goals WHERE user_id = :currUser ORDER BY time_created DESC FETCH FIRST 5 ROW ONLY', currUser=currUser)
    
    #add the results to an array
    goals=[]
    for i in user_goals:
        goals.append(i)

    #if the results are empty, "None" tells html to inform user
    if (len(goals)) < 1:
	user_goals = "None"

    #insert new row
    if request.method == 'POST':
        newNote = request.form['newNote']
        newType = request.form['newType']
        newDist = request.form['newDist']
        newDur = request.form['newDur']
        db.query('INSERT INTO goals (user_id, activity_type, distance, duration, notes) VALUES (:currUser, :newType, :newDist, :newDur, :newNote)', currUser=currUser, newType=newType, newDist=newDist, newDur=newDur, newNote=newNote)
        return redirect(url_for('goals'))
    
    return render_template('goals.html', user_goals=user_goals)

#-------------------------------------------------------------------------------------
#Route for deleting rows in goals table
#-------------------------------------------------------------------------------------
@app.route('/deleteGoal/<gid>', methods=['POST'])
def delete_goal(gid):
    if request.method == 'POST':
	db.query('DELETE FROM goals WHERE id = :gid', gid=gid)
	return redirect(url_for('goals'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='13667', debug=True)
