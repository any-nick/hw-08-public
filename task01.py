from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    # реалізація класу
    def __init__(self, name):
        super().__init__(name)


class Phone(Field):
    # реалізація класу
    required_num_of_digits = 10

    def __init__(self, phone=None):
        # Перевіряємо чи всі введені дані є цифрами і чи їх кількість відповідає заданому формату
        try:
            if int(phone) and len(phone) == Phone.required_num_of_digits:
                super().__init__(phone)
            else:
                print("Phone not equals 10 digits")
        except:
            print("All characters are not digits")


class Birthday(Field):
    def __init__(self, value):
        # Перевіряємо чи введена дата відповідає заданому формату і чи дата народження не з майбутнього
        try:
            date = datetime.strptime(value, "%d.%m.%Y").date()
            if date.year <= datetime.today().date().year:
                super().__init__(date)
        except:
            raise "Invalid date format. Use DD.MM.YYYY"


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    # реалізація класу

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(p for p in self.phones)}"

    def add_phone(self, phone):
        # Додаємо номеру. У разі присутності повідомляємо. Якщо формат не правильний, обробляємо помилку
        try:
            if phone not in self.phones:
                self.phones.append(Phone(phone).value)
                return f"Phone {phone} was added to contact {self.name}."
            else:
                return f"Phone {phone} already exists in the record."
        except AttributeError:
            return f"Phone number format is incorrect and was not added."

    def edit_phone(self, old_number, new_number):
        # Робимо редагування номеру. У разі відсутності обробляємо помилку.
        try:
            index = self.phones.index(old_number)
            verified_new_phone = Phone(new_number).value
            self.phones[index] = verified_new_phone
            return f"Phone {old_number} was changed to {new_number}"
        except ValueError:
            return f"Phone was not changed. {old_number} not found in the list of phones."
        except AttributeError:
            return f"New phone number format is incorrect and was not changed."

    def find_phone(self, phone):
        # Робимо перевірку присутності телефону. У разі відсутності обробляємо помилку.
        try:
            index = self.phones.index(phone)
            return self.phones[index]
        except ValueError:
            return "Phone not found"

    def remove_phone(self, phone):
        # Видаляємо запис. У разі його відсутності, обробляємо виняток.
        try:
            self.phones.remove(phone)
        except ValueError:
            print(f"Cannoe remove phone. {phone} not found in record.")

    def add_birthday(self, birthday):
        # Додаємо день народження. Обробляємо помилку у разі неправильного формату.
        try:
            verified_birthday = Birthday(birthday)
            self.birthday = verified_birthday.value
            return f"Birthday {self.birthday} was set for {self.name}"
        except TypeError:
            return "Invalid date format. Use DD.MM.YYYY"
        except AttributeError:
            return f"Invalid date. Birthday cannot be set in future"

    def show_birthday(self):
        # Повертаємо дату дня народження, якщо була задана
        if self.birthday is None:
            return (f"Birthday for {self.name} is not set")
        else:
            return f"{self.name} birthday is {self.birthday}"


class AddressBook(UserDict):
    # реалізація класу

    def add_record(self, record):
        # Робимо перевірку наявності запису в адресній книзі, щоб запобігти дублюванню
        record_exists = list(
            filter(lambda contact: contact == record.name.value, self.data))
        if record_exists:
            return f"Record with name {record.name.value} already exist in address book."
        else:
            self.data[record.name.value] = record
            return f"Record {record.name.value} was added to address book."

    def find(self, name):
        # Робимо перевірку присутності запису в адресній книзі. У разі відсутності обробляємо помилку.
        try:
            return self.data[name]
        except KeyError:
            return None

    def delete(self, name):
        # Видаляємо запис. У разі його відсутності, обробляємо виняток.
        try:
            del self.data[name]
        except KeyError:
            print(f"Record {name} not found in the address book.")


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            if func.__name__ in ["add_contact", "change_contact"]:
                return "ValueError: Name and phone are missing. Please specify them in the command."
            elif func.__name__ in ["show_phone", "show_birthday"]:
                return "ValueError: Name is missing. Please specify it in the command."
            elif func.__name__ in ["add_birthday"]:
                return "ValueError: Name or birthday date missing. Please specify it in the command."
            else:
                return "ValueError: unknown error. Please contact support."
        except IndexError:
            return "IndexError: Argument is missing. Check your input."
        except KeyError:
            return "KeyError: Name was not found in dictionary. Please create new contact or check input name."

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        message = book.add_record(record)
        if phone:
            message += record.add_phone(phone)
    elif record != None:
        message = record.add_phone(phone)
    return message


@input_error
def show_phone(args, book):
    name, *_ = args
    res = book.find(name)
    if res != None:
        return res
    else:
        return f"{name} not found in the address book."


def show_all(book):
    result = "List of stored contacts:"
    for name, record in book.data.items():
        result += f"\n\r{record}"
    return result


@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return f"Record {name} was not found, please create it firstly"
    elif record != None:
        message = record.edit_phone(old_phone, new_phone)
    return message


@input_error
def add_birthday(args, book):
    name, date, *_ = args
    record = book.find(name)
    if record is None:
        return f"Record {name} was not found, please create it firstly"
    elif record != None:
        message = record.add_birthday(date)
    return message


@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Record {name} was not found, please create it firstly"
    elif record != None:
        message = record.show_birthday()
    return message


@input_error
def birthdays(book):
    today = datetime.today().date()
    upcoming_birthdays = []

    for name, record in book.data.items():
        if record.birthday == None:
            continue
        birthday_this_year = record.birthday.replace(year=today.year)

        if birthday_this_year < today:
            birthday_this_year = record.birthday.replace(year=today.year + 1)

        days_before_birthday = (birthday_this_year - today).days

        if 0 <= days_before_birthday <= 7:
            if birthday_this_year.weekday() >= 5:
                birthday_this_year += timedelta(days=(7 -
                                                birthday_this_year.weekday()))

            upcoming_birthdays.append(f"{record.name} : {record.birthday}")
    if len(upcoming_birthdays) == 0:
        return "There is no birthday on this week"
    else:
        return f"Upcoming birthdays:\n {'\n '.join(b for b in upcoming_birthdays)}"

def save_data(book, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(book, f)
        print(f"Address Book was saved to {filename}")

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            print  (f"Address Book was loaded from {filename}")
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = AddressBook()
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
