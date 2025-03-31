import re
from collections import UserDict
from functools import wraps


class PhoneFormatError(Exception):
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
        if self.validate_phone(phone):
            super().__init__(phone)
        else:
            raise PhoneFormatError(f"wrong phone format {phone}")

    def validate_phone(self, value: str) -> bool:
        pattern = re.compile(r"^\d{10}$")
        return bool(pattern.match(value))


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []

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

    def __get_phone_index(self, phone_number: str) -> int | None:
        for index, phone in enumerate(self.phones):
            if phone.value == phone_number:
                return index
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


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
                case _:
                    print(f"error in {func.__name__}")
        except PhoneFormatError:
            print("Wrong phone format.")

    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


# TODO:Додати пізніше перевірку на кількість аргументів та анотаціі
@input_error
def add_contact(args, contacts: AddressBook):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    contacts.add_record(record)
    return "Contact added."


@input_error
def change_contact(args, contacts: AddressBook):
    name, old_phone, new_phone = args
    record = contacts.find(name.strip().capitalize())
    if record is None:
        return "Contact does not exist."
    return (
        "Contact updated."
        if record.edit_phone(old_phone, new_phone)
        else "Old phone number not found"
    )


@input_error
def show_phone(args, contacts: AddressBook):
    name = args[0]
    record = contacts.find(name.strip().capitalize())
    return str(record) if record else "Contact not found"


def show_all(contacts):
    if not contacts:
        return "Contacts not found."
    return str(contacts)


def main():
    contacts = AddressBook()
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
                if message := add_contact(args, contacts):
                    print(message)
            case "all":
                print(show_all(contacts))
            case "change":
                if message := change_contact(args, contacts):
                    print(message)
            case "phone":
                if message := show_phone(args, contacts):
                    print(message)
            case _:
                print("Invalid command.")


if __name__ == "__main__":
    main()
