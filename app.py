from flask import Flask, render_template, request, url_for, redirect
import json
import requests
import records
import dbconfig

app = Flask(__name__, static_url_path='')

db = records.Database('postgresql://{user}:{pw}@{url}/{dbName}'.format(user=dbconfig.POSTGRES_USER, pw=dbconfig.POSTGRES_PW, url=dbconfig.POSTGRES_URL, dbName=dbconfig.POSTGRES_DB))


#will need to implement how the current user's ID is identified and shared in our code
user_id = 6

@app.route('/', methods=['GET'])
def main():
    bmi = db.query('SELECT bmi FROM health WHERE user_id=6')
    return render_template("index.html", bmi=bmi)

@app.route('/health', methods=['GET', 'POST'])
def health():
    if request.method == 'POST':
        weight = request.form['new_Weight']
        height = request.form['new_Height']
        db.query('INSERT INTO health (user_id, height, weight) VALUES (:user_id, :height, :weight)', user_id=user_id, height=height, weight=weight)
        #return render_template('health.html')
        return weight,height

    return render_template('health.html')

@app.route('/activities', methods=['GET'])
def activities():
    return render_template('activities.html')

@app.route('/goals', methods=['GET'])
def goals():
    return render_template('goals.html')

        
if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5432', debug=True)
