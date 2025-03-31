import re
from collections import UserDict
from datetime import datetime, timedelta
from functools import wraps


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

            birthday_data_obj = record.birthday.value  # datetime.date
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
                        "congratulation_date": congrats_date.strftime("%Y.%m.%d"),
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


def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, TypeError, IndexError):
            match func.__name__:
                case "parse_input":
                    print("Command can not be blank")
                case "add_contact":
                    print("Usage: add NAME PHONE_NUMBER")
                case "change_contact":
                    print("Usage: change NAME OLD_NUMBER NEW_NUMBER")
                case "show_phone":
                    print("Usage: phone NAME")
                case "add_birthday":
                    print("Usage: add-birthday NAME DATE(DD.MM.YYYY)")
                case _:
                    print(f"error in {func.__name__}")
        except PhoneFormatError:
            print("Wrong phone format.")
        except DateFormatError:
            print("Invalid date format. Use DD.MM.YYYY")

    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name.strip().capitalize())
    if record is None:
        return "Contact does not exist."
    return (
        "Contact updated."
        if record.edit_phone(old_phone, new_phone)
        else "Old phone number not found"
    )


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name.strip().capitalize())
    return str(record) if record else "Contact not found"


def show_all(book: AddressBook):
    if not book:
        return "Contacts not found."
    return str(book)


@input_error
def add_birthday(args, book: AddressBook):
    name, b_date = args
    record = book.find(name)
    if record:
        record.add_birthday(b_date)
        return "Added"
    return "Contact not found"


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not (parsed_user_input := parse_input(user_input)):
            continue
        command, *args = parsed_user_input

        match command:
            case "close" | "exit":
                print("Good bye!")
                break
            case "hello":
                print("How can I help you?")
            case "add":
                if message := add_contact(args, book):
                    print(message)
            case "all":
                print(show_all(book))
            case "add-birthday":
                if message := add_birthday(args, book):
                    print(message)
            case "change":
                if message := change_contact(args, book):
                    print(message)
            case "phone":
                if message := show_phone(args, book):
                    print(message)
            case _:
                print("Invalid command.")


if __name__ == "__main__":
    main()
