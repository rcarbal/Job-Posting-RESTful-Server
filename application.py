#!/usr/bin/env python3
from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Company, Item

app = Flask(__name__)

engine = create_engine('sqlite:///job_postings.db')
Base.metadata.bind = engine

DBsession = scoped_session(sessionmaker(bind=engine))
session = DBsession()


@app.route('/')
@app.route('/companies/<int:company_id>')
def companies(company_id):
    company = session.query(Company).filter_by(id=company_id).one()
    jobs = session.query(Item).filter_by(company_id=company_id)
    return render_template('company.html', company=company, jobs=jobs)


# New Company
@app.route('/company/<int:company_id>/new/')
def newCompanyJob(company_id):
    return "page to create a new company job post. Task 1 complete!"


# Edit company job post
@app.route('/company/<int:company_id>/<int:job_id>/edit/')
def editJobItem(company_id, job_id):
    return "page to edit a Job item. Task 2 complete!"


@app.route('/company/<int:company_id>/<int:job_id>/delete/')
def deleteJobItem(company_id, job_id):
    return "page to delete a menu item. Task 3 complete!"


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
