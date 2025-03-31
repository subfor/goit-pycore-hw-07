from functools import wraps

from addressbook import AddressBook, DateFormatError, PhoneFormatError, Record


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
                case "show_birthday":
                    print("Usage: show-birthday NAME")
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
    existing_record = book.find(name)

    if existing_record:
        if existing_record.add_phone(phone):
            return "Phone number added to existing contact."
        else:
            return "Phone number already exists."
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "New contact added."


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


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return str(record.birthday)
        else:
            return "Birthday not set"
    return "Contact not found"


@input_error
def show_birthdays_next_week(book: AddressBook):
    birthdays = book.get_upcoming_birthday()
    if birthdays:
        text = ""
        for person in birthdays:
            text += (
                f"Name: {person['name']}, "
                f"Congratulation date: {person['congratulation_date']}\n"
            )
        return text.strip()
    return "Birthdays not found"


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
            case "show-birthday":
                if message := show_birthday(args, book):
                    print(message)
            case "birthdays":
                if message := show_birthdays_next_week(book):
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
