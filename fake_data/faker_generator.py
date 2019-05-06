from faker import Faker


def generate_salary():
    fake = Faker()
    job_price = fake.pyfloat(left_digits=5, right_digits=2, positive=True)
    salary = '${:,.2f}'.format(job_price)
    print(salary)

def generate_fake_company():
    fake = Faker()
    item_name = fake.company()
    print(item_name)

def generate_fake_job():
    fake = Faker()
    job = fake.job()
    print(job)
