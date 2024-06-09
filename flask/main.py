from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"
def make_bold(func):
    def wrapper():
        return f"<b>{func()}</b>"
    return wrapper

def make_emphasis(func):
    def wrapper():
        return f"<em>{func()}</em>"
    return wrapper
def make_underline(func):
    def wrapper():
        return f"<U>{func()}</U>"
    return wrapper
@app.route("/bye")
@make_bold
@make_emphasis
@make_underline
def bye():
    return "bye"

if __name__ == "__main__":
    app.run(debug=True)