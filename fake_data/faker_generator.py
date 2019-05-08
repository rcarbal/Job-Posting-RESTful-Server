from faker import Faker


def generate_salary():
    fake = Faker()
    job_price = fake.pyfloat(left_digits=5, right_digits=2, positive=True)
    salary = '${:,.2f}'.format(job_price)
    print(salary)


def generate_fake_company():
    fake = Faker()
    name = fake.company()
    return name


def generate_fake_job():
    fake = Faker()
    job = fake.job()
    print(job)


def generate_fake_job_description():
    fake = Faker()
    description = fake.text(max_nb_chars=200, ext_word_list=None);
    print(description)


def create_companies():
    # get fake data
    # make 10 companies
    companies = {}

    for x in range(10):
        name = generate_fake_company()
        companies.update({x: name})
    return companies


#
def create_jobs(companies):
    print(companies.keys())
    for company in companies:
        print(companies[company])


all_companies = create_companies()
create_jobs(all_companies)
