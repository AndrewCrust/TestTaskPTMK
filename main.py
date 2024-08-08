from datetime import date, timedelta
from random import choice, randint
from sys import argv
from time import monotonic
from pony.orm import *
from russian_names import RussianNames
from validator import Validator

__INNER_PARAM_COMMAND = argv[1:]

db = Database()
db.bind(provider='sqlite', filename='list_of_employees.sqlite', create_db=True)


class Person(db.Entity):
    id = PrimaryKey(int, auto=True)
    full_name = Optional(str, 100)
    birth_date = Optional(date)
    gender = Optional(str, 10, index='gender_index')

    def get_age(self):
        date_today = date.today()
        not_birthday_coming = date_today.day > self.birth_date.day if date_today.month == self.birth_date.month \
            else date_today.month > self.birth_date.month

        return date_today.year - self.birth_date.year - not_birthday_coming


def create_table(example_db: Database) -> None:
    example_db.generate_mapping(create_tables=True)


@db_session
def add_person(data: list[str]) -> None:
    full_name, birth_date, gender = data
    Person(full_name=full_name.title(), birth_date=birth_date, gender=gender.lower())


@db_session
def get_unique_persons() -> None:
    persons = select(r for r in Person if (r.full_name, r.birth_date)
                     in select((p.full_name, p.birth_date) for p in Person if count() == 1)).order_by(Person.full_name)
    for person in persons:
        print(person.full_name, person.birth_date, person.gender, person.get_age())

    # for row in select((r.full_name, r.birth_date, r.gender) for r in Person):
    #     print(row)


@db_session
def automatic_filling(dataset: list[list[str]]) -> None:
    for data in dataset:
        add_person(data=data)


@db_session
def get_by_gender_f() -> None:
    gender = Validator.get_genders()[0]

    start_time = monotonic()

    persons = select(r for r in Person if r.gender == gender and r.full_name.startswith('F'))
    commit()

    end_time = monotonic()

    total_time = end_time - start_time

    with open('time.txt', 'a+', encoding='utf-8') as f:
        f.write(f'{total_time}\n')

    for person in persons:
        print(person.full_name, person.gender)


def generate_person_data(example_gen_full_name: RussianNames, start_letter: str = None, default_gender=None):
    name_dict = example_gen_full_name.get_person()
    surname = f"{start_letter}{name_dict['surname'][1:]}" if start_letter else name_dict['surname']
    full_name = f"{surname} {name_dict['name']} {name_dict['patronymic']}"

    old_date = date(1950, 1, 1)
    young_date = date.fromisoformat(f'{date.today().year - Validator.get_min_age()}{str(date.today())[4:]}')
    random_birth_date = old_date + timedelta(days=randint(0, (young_date - old_date).days))

    gender = default_gender or choice(Validator.get_genders())

    return [full_name, str(random_birth_date), gender]


def generate_dataset():
    r_name = RussianNames(patronymic=True, transliterate=True, output_type='dict')

    dataset = [[] for _ in range(1_000_100)]

    index = 0
    while index < 1_000_000:
        data = generate_person_data(example_gen_full_name=r_name)

        if Validator.validate_person_data(args=data):
            dataset[index][:] = data
            index += 1

    while index < 1_000_100:
        data = generate_person_data(example_gen_full_name=r_name, start_letter='F',
                                    default_gender=Validator.get_genders()[0])

        if Validator.validate_person_data(args=data):
            dataset[index][:] = data
            index += 1

    return dataset


def command_manager(inner_data: list[str], database: Database) -> None:
    command_num, *person_data = inner_data
    match command_num:
        case '1':
            create_table(example_db=database)
        case '2':
            add_person(data=person_data)
        case '3':
            get_unique_persons()
        case '4':
            dataset = generate_dataset()
            automatic_filling(dataset=dataset)
        case '5':
            get_by_gender_f()


if __name__ == '__main__':
    if __INNER_PARAM_COMMAND:
        pass
    else:
        print('The command was not executed. Must be 1 or 4 arguments.')
        exit()

    if Validator.validate_inner_data(data=__INNER_PARAM_COMMAND):

        if __INNER_PARAM_COMMAND[0] != '1':
            try:
                db.generate_mapping(create_tables=False)
            except OperationalError as e:
                print(f'{e}.\nYou should create a table with the command 1.')
                db.disconnect()
                exit()
        command_manager(inner_data=__INNER_PARAM_COMMAND, database=db)
    db.disconnect()
