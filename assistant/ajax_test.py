from flask import Flask, render_template
app = Flask(__name__)

# two decorators, same function
@app.route('/')
def index():
    return render_template('ajax_test.html')

if __name__ == '__main__':
    app.run(debug=True, port=8888)