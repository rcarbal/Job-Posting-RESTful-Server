from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    slogan = Column(String(250), nullable=False)


class Item(Base):
    __tablename__ = 'job_title'

    job_title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    job_description = Column(String(250))
    salary = Column(String(8))
    company_id = Column(Integer, ForeignKey('company.id'))
    company = relationship(Company)


engine = create_engine('sqlite:///job_postings.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()


def add_company():
    company_name = "Microsoft"
    slogan = "Be What's Next"
    my_company = Company(name=company_name, slogan=slogan)
    session.add(my_company)
    session.commit()


def add_job():
    company_id = "2"
    company_found = session.query(Company).filter_by(id=company_id).one()

    job_title = "UI Software Engineer"
    job_description = """ Shared Services Engineering (SSE) is looking for a UI Software Engineer who has a passion for working on large scale projects and obsessive about customer/user experiences with compliance and who can help us deliver innovative features in CSEO applications/services. CSEO owns and manages applications and services supporting various domains such as Sales, Marketing, HR, Finance, CELA, Field Users, Employee, SAP, Supply Chain. If you have done great full-stack UI development and you consider yourself a successful UI developer, you will feel right at home in our team. Your work will be the face of the team. It is a fast-paced environment with quick iteration cycles and plenty of exploration in new areas."""
    job_salary = "75,000"
    company = company_found
    job = Item(job_title=job_title,job_description=job_description, salary=job_salary, company=company)
    session.add(job)
    session.commit()

def get_companies():
    companies = session.query(Company).all()
    for company in companies:
        print(company.name)
        print(company.slogan)

def get_jobs():
    jobs = session.query(Item).all()
    for job in jobs:
        print(job.job_title)
        print(job.job_description)
        print(job.salary)
