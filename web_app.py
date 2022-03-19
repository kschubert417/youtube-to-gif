import os
import functions as fn
from flask import Flask
from flask import request, send_file, render_template

# HTML resources --
# https://www.w3schools.com/html/html_form_elements.asp
# https://www.quackit.com/html/online-html-editor/

# https://www.linkedin.com/learning/flask-essential-training/demo-project-overview?u=102287802
# how to make app run in PowerShell: run below command
# https://flask.palletsprojects.com/en/2.0.x/quickstart/
# $env:FLASK_APP = "web_app"; flask run

# creating database to hold YouTube Link and Filenames
fn.createdb()

# Using this to speed up testing ======================================
# Link of video to download
link = 'https://www.youtube.com/watch?v=9Im-PIs-Ki0'
link2 = 'https://www.youtube.com/watch?v=Gsk6pLLcIFI'

# data structure to make some functions work
test = {link: {'start': ['00:00:09.00', '00:00:15.90'],
               'end': ['00:00:11.50', '00:00:18.30']},
        link2: {'start': ['00:00:09.00', '00:00:15.90'],
                'end': ['00:00:11.50', '00:00:18.30']}}

# =====================================================================
# where zip files are stored
os.path.join(os.getcwd(), "media", "output")

# constructor for flask application
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


# home page ===================================================================
@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template("about.html")


# one video one gif ===========================================================
@app.route('/onevidonegifform', methods=['GET', 'POST'])
def createonevidonegifform():
    return render_template("onevideogifform.html")


@app.route('/onevidonegif', methods=['GET', 'POST'])
def createonevidonegif():
    # http://127.0.0.1:5000/onevidonegif
    # creating gif file
    fpath = fn.onevidonegif(request.form.get('link'),
                            request.form.get('start'),
                            request.form.get('end'))

    print("RETURNING FILE PATH:", fpath)
    # sending gif
    return send_file(fn.returnpath(fpath), as_attachment=True)


# One gif per vid =============================================================
@app.route('/onegifpervidform', methods=['GET', 'POST'])
def createonegifpervidform():
    return render_template("onegifpervidform.html")


@app.route('/onegifpervid', methods=['GET', 'POST'])
def createonegifpervid():
    userinput = {request.form.get('link1'):
                 {'start': [request.form.get('link1start1'),
                            request.form.get('link1start2')],
                  'end': [request.form.get('link1end1'),
                          request.form.get('link1end2')]}}

    # creating gif file/files and getting file names
    fnames = fn.onegifpervid(userinput)

    # sending gif/gifs via zipfile
    return send_file(fn.returnpath(fnames), as_attachment=True)


# Many gif per vid ============================================================
@app.route('/manygifpervidform', methods=['GET', 'POST'])
def manygifpervidform():
    return render_template("manygifpervidform.html")


@app.route('/manygifpervid', methods=['GET', 'POST'])
def createmanygifpervid():
    # http://127.0.0.1:5000/manygifpervid
    userinput = {request.form.get('link1'):
                 {'start': [request.form.get('link1start1'),
                            request.form.get('link1start2')],
                  'end': [request.form.get('link1end1'),
                          request.form.get('link1end2')]}}

    # creating gif file/files and getting file names
    fnames = fn.manygifpervid(userinput)

    # sending gif/gifs via zipfile
    return send_file(fn.returnpath(fnames), as_attachment=True)


# not sure if this will mess things up (do not really need)
if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1")  # for testing on home cpu
# app.run(debug=True, host="127.0.0.1")  # for testing on home cpu

# for Amazon EC2
# if __name__ == '__main__':
#    # app.run(host='0.0.0.0', port=80)
#    app.run(host='127.0.0.0', port=5000)
