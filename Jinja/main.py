from flask import Flask, render_template
import requests
from post import Post

response = requests.get('https://api.npoint.io/c790b4d5cab58020d391')
posts_dict = response.json()
posts = [Post(post["id"], post["title"], post["subtitle"], post["body"]) for post in posts_dict]

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html", posts=posts)

@app.route('/blog/<id>')
def blog(id):
    return render_template("post.html", post=posts[int(id)-1])

if __name__ == "__main__":
    app.run(debug=True)
