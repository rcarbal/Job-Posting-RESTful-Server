#!/usr/bin/env python3
from flask import Flask, render_template, request, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib3.connectionpool import xrange
from werkzeug.utils import redirect

from database_setup import Base, Company, Item

from flask import session as login_session
import random, string

app = Flask(__name__)

engine = create_engine('sqlite:///job_postings.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/companies')
def get_all_companies():
    companies = session.query(Company).first()
    return 'Companies'


@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return "The current session state token is %s"%login_session['state']

@app.route('/companies/<int:company_id>')
def single_company(company_id):
    company = session.query(Company).filter_by(id=company_id).one()
    jobs = session.query(Item).filter_by(company_id=company_id)
    return render_template('company.html', company=company, jobs=jobs)


# New Company
@app.route('/companies/<int:company_id>/new/', methods=['GET', 'POST'])
def new_company_job(company_id):
    if request.method == 'POST':
        description = request.form["description"]
        name = request.form["name"]
        salary = request.form["salary"]
        new_job = Item(job_title=name,
                       job_description=description,
                       salary=salary,
                       company_id=company_id)
        session.add(new_job)
        session.commit()
        flash("New job post created!")
        return redirect(url_for('single_company', company_id=company_id))
    else:
        return render_template('newjobpost.html', company_id=company_id)


# Edit company job post
@app.route('/companies/<int:company_id>/<int:job_id>/edit/', methods=['GET', 'POST'])
def edit_job_item(company_id, job_id):
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
    deleted_job_post = session.query(Item).filter_by(id=job_id).one()
    if request.method == 'POST':
        session.delete(deleted_job_post)
        session.commit()
        flash("Deleted job post " + deleted_job_post.job_title)
        return redirect(url_for('single_company', company_id=company_id))
    return render_template('deletepost.html', company_id=company_id, item=deleted_job_post)


@app.route('/companies/<int:company_id>/posts/JSON')
def company_posts_json(company_id):
    # company = session.query(Company).filter_by(id=company_id).one()
    posts = session.query(Item).filter_by(company_id=company_id).all()
    return jsonify(JobPosts=[i.serialize for i in posts])


@app.route('/companies/<int:company_id>/posts/<int:post_id>/JSON')
def job_post_json(company_id, post_id):
    # company = session.query(Company).filter_by(id=company_id).one()
    post = session.query(Item).filter_by(id=post_id).one()
    return jsonify(JobPost=post)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
