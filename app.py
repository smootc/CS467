from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def main():
	return ('index.html')

@app.route('/health')
def health_page():
	return render_template('health.html')

if __name__ == "__main__":
	app.run(port=33223)
