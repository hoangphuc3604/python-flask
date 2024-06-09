from flask import Flask
import random

num = random.randint(0, 9)
app = Flask(__name__)

@app.route("/")
def hello():
    return ("<h1>Guess a number between 0 and 9</h1>"
            "<img src='https://media.giphy.com/media/3o7aCSPqXE5C6T8tBC/giphy.gif'>")

@app.route("/<int:number>")
def answer_int(number):
    if number > num:
        return (f"<h1 style='color: purple'>Too high, try again!</h1>"
                f"<img src='https://media.giphy.com/media/3o6ZtaO9BZHcOjmErm/giphy.gif'>")
    elif number < num:
        return (f"<h1 style='red: purple'>Too low, try again!</h1>"
                f"<img src='https://media.giphy.com/media/jD4DwBtqPXRXa/giphy.gif'>")
    else:
        return (f"<h1 style='green: purple'>You found me!</h1>"
                f"<img src='https://media.giphy.com/media/4T7e4DmcrP9du/giphy.gif'>")
if __name__ == "__main__":
    app.run(debug=True)

