from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(350))


class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    slogan = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class Item(Base):
    __tablename__ = 'job_title'

    job_title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    job_description = Column(String(250))
    salary = Column(String(8))
    company_id = Column(Integer, ForeignKey('company.id'))
    company = relationship(Company)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.job_title,
            'description': self.job_description,
            'id': self.id,
            'salary': self.salary,
            'company': self.company_id
        }


engine = create_engine('sqlite:///jobpostingwithuser.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()


def add_user():
    name = "Ric"
    email = "admin@admin.com"
    picture = "no picture"
    user = User(name=name, email=email, picture=picture)
    session.add(user)
    session.commit()


def add_company():
    company_name = "Microsoft"
    slogan = "Be What's Next"
    user = session.query(User).one()
    my_company = Company(name=company_name, slogan=slogan, user=user)
    session.add(my_company)
    session.commit()


def add_job():
    company_id = "1"
    company_found = session.query(Company).filter_by(id=company_id).one()
    user = session.query(User).one()

    job_title = "UI Software Engineer"
    job_description = """Shared Services Engineering (SSE) is looking for a UI Software Engineer who has a passion 
    for working on large scale projects and obsessive about customer/user experiences with compliance and who can 
    help us deliver innovative features in CSEO applications/services. CSEO owns and manages applications and 
    services supporting various domains such as Sales, Marketing, HR, Finance, CELA, Field Users, Employee, SAP, 
    Supply Chain. If you have done great full-stack UI development and you consider yourself a successful UI 
    developer, you will feel right at home in our team. Your work will be the face of the team. It is a fast-paced 
    environment with quick iteration cycles and plenty of exploration in new areas. """
    job_salary = "75,000"
    company = company_found
    job = Item(job_title=job_title, job_description=job_description, salary=job_salary, company=company, user=user)
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


if __name__ == '__main__':
    add_user()
    add_company()
    add_job()
