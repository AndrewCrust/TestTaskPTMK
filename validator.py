import re
from datetime import date


class Validator:
    """
    '__MIN_AGE' связано исключительно с трудовым законодательством
    """

    __MIN_AGE = 16
    __COMMAND_NUMS = ('1', '2', '3', '4', '5')
    __GENDERS = ('male', 'female')
    __FULL_NAME_PATTERN = r'^[a-z]+(?:\-[a-z]+)?(?: [a-z]+){2}$'
    __DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"

    @classmethod
    def get_genders(cls):
        return cls.__GENDERS

    @classmethod
    def get_min_age(cls):
        return cls.__MIN_AGE

    @classmethod
    def validate_inner_data(cls, data: list[str]) -> bool:
        command_num, *arguments = data
        return (cls.__validate_command_num(num=command_num)
                and cls.__validate_format_command(num=command_num, args=arguments))

    @classmethod
    def __validate_command_num(cls, num: str) -> bool:
        return num in cls.__COMMAND_NUMS

    @classmethod
    def __validate_format_command(cls, num: str, args: list) -> bool:
        if num != cls.__COMMAND_NUMS[1]:
            return not args
        else:
            return cls.validate_person_data(args=args)

    @classmethod
    def validate_person_data(cls, args: list) -> bool:
        full_name, birth_date, gender = args
        today = date.today()
        date_flag = date.fromisoformat(f'{today.year - cls.__MIN_AGE}{str(today)[4:]}')

        return (re.match(cls.__FULL_NAME_PATTERN, full_name.strip().lower())
                and re.match(cls.__DATE_PATTERN, birth_date)
                and date_flag >= date.fromisoformat(birth_date)
                and gender.lower() in cls.__GENDERS)
