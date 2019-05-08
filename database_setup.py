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


add_company()
