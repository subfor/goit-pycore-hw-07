import re
from collections import UserDict
from datetime import datetime, timedelta


class PhoneFormatError(Exception):
    pass


class DateFormatError(Exception):
    pass


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name: str):
        super().__init__(name.strip().capitalize())


class Phone(Field):
    def __init__(self, phone: str):
        if self.__validate_phone(phone):
            super().__init__(phone)
        else:
            raise PhoneFormatError(f"wrong phone format {phone}")

    def __validate_phone(self, value: str) -> bool:
        pattern = re.compile(r"^\d{10}$")
        return bool(pattern.match(value))


class Birthday(Field):
    def __init__(self, value):
        if self.__validate_date(value):
            b_date = datetime.strptime(value.strip(), "%d.%m.%Y").date()
            super().__init__(b_date)
        else:
            raise DateFormatError("Invalid date format. Use DD.MM.YYYY")

    def __validate_date(self, value):
        pattern = re.compile(r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$")
        return bool(pattern.match(value.strip()))

    def __str__(self):
        return f"Birthday: {self.value.strftime("%d.%m.%Y")}"


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, new_phone: str) -> bool:
        if self.__get_phone_index(new_phone) is None:
            self.phones.append(Phone(new_phone))
            return True
        return False

    def remove_phone(self, phone_number: str) -> bool:
        index = self.__get_phone_index(phone_number)
        if index is not None:
            self.phones.pop(index)
            return True
        return False

    def edit_phone(self, old_number: str, new_number: str) -> bool:
        index = self.__get_phone_index(old_number)
        if index is not None:
            self.phones[index] = Phone(new_number)
            return True
        return False

    def find_phone(self, phone_number: str) -> str:
        return phone_number if self.__get_phone_index(phone_number) else ""

    def add_birthday(self, b_date: str) -> None:
        self.birthday = Birthday(b_date)

    def __get_phone_index(self, phone_number: str) -> int | None:
        for index, phone in enumerate(self.phones):
            if phone.value == phone_number:
                return index
        return None

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = (
            self.birthday.value.strftime("%d.%m.%Y")
            if self.birthday is not None
            else "not set"
        )
        return (
            f"Contact name: {self.name.value}, "
            f"phones: {phones} "
            f"Birthday: {birthday}"
        )


class AddressBook(UserDict):

    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        return self.data.get(name.strip().capitalize())

    def delete(self, name: str) -> bool:
        try:
            del self.data[name.strip().capitalize()]
            return True
        except KeyError:
            return False

    def get_upcoming_birthday(self) -> list:
        today_date = datetime.today().date()
        congrat_list = []
        congrats_date = None

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday_data_obj = record.birthday.value
            birthday_this_year = birthday_data_obj.replace(year=today_date.year)

            if birthday_this_year < today_date:
                birthday_this_year = birthday_this_year.replace(
                    year=today_date.year + 1
                )

            days_until_birthday = (birthday_this_year - today_date).days

            if 0 <= days_until_birthday < 7:
                congrats_date = birthday_this_year + timedelta(
                    days=self.__check_weekend(birthday_this_year)
                )

                congrat_list.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": congrats_date.strftime("%d.%m.%Y"),
                    }
                )

        return congrat_list

    def __check_weekend(self, date: datetime.date) -> int:
        match date.isoweekday():
            case 6:
                return 2
            case 7:
                return 1
            case _:
                return 0

    def __str__(self):
        result = ""
        for record in self.data.values():
            result += str(record) + "\n"
        return result
