from flask import Flask, request, render_template
from filter_words import format_statement

app = Flask(__name__)


@app.route('/')
def my_form():
    return render_template('my-form.html')


@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    return format_statement(text)


if __name__ == "__main__":
    app.run()
