#!/usr/bin/env python3
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Company, Item

app = Flask(__name__)

engine = create_engine('sqlite:///job_postings.db')
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()

@app.route('/')
@app.route('/companies/<int:company_id>')
def companies(company_id):
    companies = session.query(Company).filter_by(id=company_id).one()
    return companies.name

#New Company
@app.route('/company/<int:company_id>/new/')
def newCompanyJob(company_id):
    return "page to create a new company job post. Task 1 complete!"

#Edit company job post
@app.route('/company/<int:company_id>/<int:job_id>/edit/')
def editMenuItem(company_id, job_id):
    return "page to edit a Job item. Task 2 complete!"


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)