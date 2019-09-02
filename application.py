#!/usr/bin/env python3

from flask import Flask, render_template, request, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from urllib3.connectionpool import xrange
from werkzeug.utils import redirect

from database_setup import Base, Company, Item, User

from flask import session as login_session
import random, string
from oauth2client import client
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine('sqlite:///jobpostingwithuser.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/companies')
def get_all_companies():
    companies = session.query(Company).order_by(asc(Company.name))
    if 'username' not in login_session:
        return render_template('publicindex.html', companies=companies)
    else:
        return render_template("index.html", companies=companies)


@app.route('/companies/new', methods=['POST', 'GET'])
def create_new_company():
    if 'username' not in login_session:
        return render_template("login.html")
    if request.method == 'POST':
        new_company = Company(name=request.form['name'], slogan=request.form['slogan'],
                              user_id=login_session['user_id'])
        session.add(new_company)
        session.commit()
        flash('New Company %s Successfully Created' % new_company.name)
        return redirect(url_for('get_all_companies'))
    else:
        return render_template("newcompany.html")


@app.route('/companies/edit', methods=['POST', 'GET'])
def edit_company():
    return "IN COMPANY EDIT ROUTE"


@app.route('/companies/<int:company_id>')
def single_company(company_id):
    company = session.query(Company).filter_by(id=company_id).one()
    creator = get_user_info(company.user_id)
    jobs = session.query(Item).filter_by(company_id=company_id).all()

    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publiccompany.html', company=company, jobs=jobs, creator=creator)
    else:
        return render_template('company.html', company=company, jobs=jobs, creator=creator)


@app.route('/companies/<int:company_id>/<int:job_id>', methods=['GET'])
def single_post(company_id, job_id):
    job_post = session.query(Item).filter_by(id=job_id).one()
    if request.method == 'GET':
        return render_template('job_post.html', company_id=company_id, job=job_post)


# New Company
@app.route('/companies/<int:company_id>/job/new/', methods=['GET', 'POST'])
def new_company_job(company_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        company = session.query(Company).filter_by(id=company_id).one()
        description = request.form["description"]
        name = request.form["name"]
        salary = request.form["salary"]
        new_job = Item(job_title=name,
                       job_description=description,
                       salary=salary,
                       company_id=company_id,
                       user_id=company.user_id)
        session.add(new_job)
        session.commit()
        flash("New job post created!")
        return redirect(url_for('single_company', company_id=company_id))
    else:
        return render_template('newjobpost.html', company_id=company_id)


# Edit company job post
@app.route('/companies/<int:company_id>/<int:job_id>/edit/', methods=['GET', 'POST'])
def edit_job_item(company_id, job_id):
    if 'username' not in login_session:
        return redirect('/login')
    edited_job_post = session.query(Item).filter_by(id=job_id).one()
    if request.method == 'POST':
        if request.form['title']:
            edited_job_post.job_title = request.form['title']
            edited_job_post.job_description = request.form['description']
            edited_job_post.salary = request.form['salary']
        session.add(edited_job_post)
        session.commit()
        flash("Edited Job post " + request.form['title'])
        return redirect(url_for('single_company', company_id=company_id))
    else:
        return render_template('editjobpost.html', company_id=company_id, job_ID=edited_job_post)


@app.route('/companies/<int:company_id>/<int:job_id>/delete/', methods=['GET', 'POST'])
def delete_job_item(company_id, job_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleted_job_post = session.query(Item).filter_by(id=job_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    # In case user tries delete via url
    if deleted_job_post.user_id != login_session['user_id']:
        return """
        <script>function myFuntion(){
        alert('You are not authorized to delete this post. Please create your own post in order to delete');
        </script><body onload='myFunction()''> 
        """
    if request.method == 'POST':
        session.delete(deleted_job_post)
        session.commit()
        flash("Deleted job post " + deleted_job_post.job_title)
        return redirect(url_for('single_company', company_id=company_id))
    return render_template('deletepost.html', company_id=company_id, item=deleted_job_post)


@app.route('/companies/<int:company_id>/JSON')
def company_posts_json(company_id):
    # company = session.query(Company).filter_by(id=company_id).one()
    posts = session.query(Item).filter_by(company_id=company_id).all()
    return jsonify(JobPosts=[i.serialize for i in posts])


@app.route('/companies/<int:company_id>/<int:post_id>/JSON')
def job_post_json(company_id, post_id):
    # company = session.query(Company).filter_by(id=company_id).one()
    post = session.query(Item).filter_by(id=post_id).one()
    return jsonify(JobPost=post)


@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state token is %s"%login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
        # Obtain authorization code
    code = request.data
    CLIENT_SECRET_FILE = 'client_secret.json'
    try:
        # Upgrade the authorization code into a credentials object
        credentials = client.credentials_from_clientsecrets_and_code(
            CLIENT_SECRET_FILE,
            ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
            code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    g_id = credentials.id_token['sub']
    if result['user_id'] != g_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_g_id = login_session.get('g_id')
    if stored_access_token is not None and g_id == stored_g_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['g_id'] = g_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exist, if it doesnt create a new one
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return (output)

@app.route("/gdisconnect")
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HHTP GET request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session
        del login_session['access_token']
        del login_session['g_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content_type'] = 'application/json'
        return response
    else:
        # Something went wrong
        response = make_response(json.dumps('Failed to revoke token for given user'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response


def create_user(loggin_session):
    new_user = User(name=login_session['username'], email=loggin_session['email'], picture=loggin_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=loggin_session['email']).one()
    return user.id


def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    # port = 6001
    # host = '127.0.0.1'
    app.debug = True
    app.run(host='0.0.0.0', port=6001)
    # app.run(host=host, port=port)
