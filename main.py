from collections import UserDict
from datetime import datetime, date, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    def __str__(self):
        return self.date.strftime("%d.%m.%Y")
    def is_valid(self):
        # Перевірка чи дата народження не знаходиться в майбутньому
        today = datetime.now()
        return self.date <= today

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        if isinstance(birthday, Birthday):
            if not birthday.is_valid():
                raise ValueError("Birthday cannot be in the future.")
            self.birthday = birthday
        elif isinstance(birthday, str):
            birthday = Birthday(birthday)
            if not birthday.is_valid():
                raise ValueError("Birthday cannot be in the future.")
            self.birthday = birthday
        else:
            raise ValueError("Birthday must be a string in DD.MM.YYYY format or a Birthday object.")

    def add_phone(self, phone):
        if isinstance(phone, Phone):
            self.phones.append(phone)
        elif isinstance(phone, str):
            self.phones.append(Phone(phone))
        else:
            raise ValueError("Phone must be a string or a Phone object.")

    def remove_phone(self, phone):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError(f"Phone {phone} not found.")

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            try:
                if not isinstance(new_phone, Phone):
                    new_phone = Phone(new_phone)
            except ValueError as e:
                raise ValueError(f"Failed to replace phone {old_phone}. {e}")
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError(f"Phone {old_phone} not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Record {name} not found.")
        
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.today()
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.date.replace(year = today.year)
                if 0 <= (birthday_this_year - today).days <= days:
                    congratulation_date = birthday_this_year
                    if congratulation_date.weekday() in [5,6]:
                        # Перевірки чи не випадає день народження на вихідіні
                        while congratulation_date.weekday() in [5, 6]:
                            congratulation_date += timedelta(days=1)
                    upcoming_birthdays.append({"name": record.name.value, "congratulation_date" : congratulation_date.strftime("%d.%m.%Y")})
        return upcoming_birthdays

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())


#_______________________________________________________________________________________________________________

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "This contact does not exist."
        except ValueError:
            return "Give me name and value (phone or birthday) please."
        except IndexError:
            return "No avaliable arguments."
    return inner

# Парсер команд
def parse_input(user_input):
    try:
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, *args
    except:
        return None, None

@input_error
# Функція, що додає користувача в словник
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    if not isinstance(name, str) or name.isdigit():
        return "Invalid name. It should be a non-numeric text."
    if not phone.isdigit():
        return "Invalid phone number. It should contain only digits."
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return "Contact updated."
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    
        
@input_error
# Функція, що змінює номер телефону користувача 
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        return "Please provide a name, old phone, and new phone."

    name, old_phone, new_phone, *_ = args
    if not isinstance(name, str) or name.isdigit():
        return "Invalid name. It should be a non-numeric text."
    if not old_phone.isdigit() or not new_phone.isdigit():
        return "Invalid phone number. It should contain only digits."
    record = book.find(name)
    if record is None:
        return "There is no such user."
    if record.find_phone(old_phone):
        record.edit_phone(old_phone, new_phone)
        return "Contact changed."
    else:
        return f"Phone {old_phone} not found for {name}."

@input_error   
# Функція, що виводить номер телефону користувача
def show_phone(args, book: AddressBook):
    name = args[0].strip() 
    record = book.find(name)  
    if record is None:
        return "There is no such user."
    if not record.phones:
        return f"{name} has no phone numbers."
    return f"{name}: {', '.join(phone.value for phone in record.phones)}"


# Функція, що виводить усіх користувачів
def show_all(book):
    if not book:
        return "No contacts available."
    result = ''
    for record in book.values():
        phones = ", ".join(p.value for p in record.phones) if record.phones else "No phone numbers"
        result += f"{record.name.value}: {phones}\n"
    return result 

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return f"There is no such user {name}."
    try:
        record.add_birthday(birthday)
        return f"Birthday added for {name}: {birthday}"
    except ValueError as e:
        return str(e)

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        return f"There is no such user {name}."
    if not record.birthday:
        return f"{name} has no birthday set."
    return f"{name}'s birthday: {record.birthday}"

def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next 7 days."
    result = "Upcoming birthdays:\n"
    for entry in upcoming_birthdays:
        result += f"{entry['name']} - {entry['congratulation_date']}\n"
    return result.strip()

# Головна функція
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
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
    

