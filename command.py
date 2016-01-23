import datetime
import cmd
import sys
import ui
import model

from db import Session
from sqlalchemy.sql import func

incomplete_queue = []


def combine_entries(entry):
    global incomplete_queue
    total_liters = 0.0
    total_price = 0.0
    total_distance = 0.0
    num_entries = 0

    incomplete_queue.append(entry)

    for ie in incomplete_queue:
        total_liters += ie.liters
        total_price += ie.liters * ie.price
        total_distance += ie.distance
        num_entries += 1
    total_price = total_price / total_liters

    incomplete_queue = []

    return model.FuelEntry(
        liters=total_liters, price=total_price, distance=total_distance,
        date=ie.date, full=True)


def calculate_entries(session, num_lines=None):
    out = ui.OutputLines()
    for entry in session.query(model.FuelEntry):
        if not entry.full:
            incomplete_queue.append(entry)
            continue

        if len(incomplete_queue):
            entry = combine_entries(entry)
        out.append(entry)

    out.output(num_lines=num_lines)


def total(session, car):
    global incomplete_entries
    total_liters = 0.0
    total_price = 0.0
    total_distance = 0.0
    num_entries = 0

    for entry in session.query(model.FuelEntry).filter_by(car=car):
        if not entry.full:
            incomplete_queue.append(entry)
            continue

        if len(incomplete_queue):
            entry = combine_entries(entry)

        total_liters += entry.liters
        total_price += entry.liters * entry.price
        total_distance += entry.distance

    return model.FuelEntry(
        liters=total_liters, price=total_price, distance=total_distance,
        date=datetime.date.today(), full=True)


class BaseCommand(cmd.Cmd):

    prompt = '> '
    session = Session()
    user = None
    car = None

    def parseline(self, line):
        command, arg, line = super().parseline(line)
        if command is not None:
            command = command.lower()
        return command, arg, line

    def emptyline(self):
        pass

    def do_quit(self, line):
        return True

    def help_quit(self):
        pass

    def do_exit(self, line):
        return True

    def help_exit(self):
        pass


class FuelCommand(BaseCommand):

    prompt = 'Fuel> '

    def do_add(self, line):
        date = ui.prompt_date('Date', default=datetime.date.today())
        distance = ui.prompt_float('Distance', allow_empty=True)
        liters = ui.prompt_float('Volume')
        price = ui.prompt_float('Price')
        full = not not distance

        entry = model.FuelEntry(liters=liters, price=price, distance=distance,
                                date=date, full=full, car=self.car.id)

        self.session.add(entry)
        self.session.commit()

    def help_add(self):
        print('add\n\nAdd an entry to the fuel log')

    def do_calc(self, line):
        num_lines = None
        if line:
            try:
                num_lines = int(line)
            except ValueError:
                num_lines = None
        calculate_entries(self.session, num_lines=num_lines, car=self.car)

    def help_calc(self):
        print('calc [number_of_lines]\n\nCalculate the fuel entries')
        print('number_of_lines defaults to {}'.format(ui.DEFAULT_MAX_LINES))

    def do_cheapest(self, line):
        entries = self.session.query(
            model.FuelEntry,
            func.min(model.FuelEntry.price)).filter_by(car=self.car.id)
        out = ui.OutputLines()
        for entry in entries:
            out.append(entry[0])
        out.output()

    def help_cheapest(self):
        print('cheapest\n\nReturn the cheapest entries')

    def do_del(self, line):
        id = line if len(line) else None
        if id is None:
            id = ui.prompt('Enter the ID to delete')
        try:
            id = int(id)
        except ValueError:
            return

        entry = self.session.query(
            model.FuelEntry).filter_by(id=id, car=self.car.id).first()

        print('Deleting entry {}'.format(entry))

        self.session.delete(entry)
        self.session.commit()

    def help_del(self):
        print('\n'.join([
            'del [id]\n',
            'Delete an item from the Fuel Log. This will ask for an id if',
            'you don\'t supply one']))

    def do_edit(self, line):
        id = line if len(line) else None
        if id is None:
            id = ui.prompt('Enter the ID to edit')

        try:
            id = int(id)
        except ValueError:
            return

        entry = self.session.query(
            model.FuelEntry).filter_by(id=id, car=self.car.id).first()

        entry.date = ui.prompt_date('Date', default=entry.date)
        entry.distance = ui.prompt_float(
            'Distance', default=float(entry.distance),
            allow_empty=True)
        entry.liters = ui.prompt_float('Volume', default=entry.liters)
        entry.price = ui.prompt_float('Price', default=entry.price)
        entry.full = not not entry.distance
        self.session.commit()

    def help_edit(self):
        print('edit [id]\n\nEdit an entry')

    def do_export(self, line):
        filename = line if len(line) else None
        if filename is None:
            filename = ui.prompt('Filename')

        out = ui.OutputLines()
        for entry in self.session.query(
                model.FuelEntry).filter_by(car=self.car.id):
            out.append_csv(entry)

        out.csv(filename)

    def do_flush(self, line):
        if ui.prompt_bool('Are you sure you wish to flush the Fuel Log',
                          default=False):
            self.session.query(
                model.FuelEntry).filter_by(car=self.car.id).delete()
            self.session.commit()

    def help_flush(self):
        print('flush\n\nFlush all entries from the Fuel Log')

    def do_import(self, line):
        filename = line if len(line) else None
        if filename is None:
            filename = ui.prompt('Filename')

        entry_list = model.import_entries(filename, car=self.car)
        self.session.add_all(entry_list)
        self.session.commit()

    def help_import(self):
        print('import [filename]\n\nImport records from CSV file')

    def do_list(self, line):
        num_lines = None
        if line:
            try:
                num_lines = int(line)
            except ValueError:
                num_lines = None
        out = ui.OutputLines()
        for entry in self.session.query(
                model.FuelEntry).filter_by(car=self.car.id):
            out.append(entry)

        out.output(num_lines=num_lines)

    def help_list(self):
        print('list [number_of_lines]\n\nList the entries in the Fuel Log')
        print('number_of_lines defaults to {}'.format(ui.DEFAULT_MAX_LINES))

    def do_total(self, line):
        print(total(self.session, car=self.car.id))

    def help_total(self):
        print('total\n\nCalculate and print the total stats')


class UserCommand(BaseCommand):
    prompt = 'User> '
    user = None

    def do_login(self, line):
        if self.user is not None:
            print('Already logged in. Use logout to log out')
            return False
        username = ui.prompt('Username')
        password = ui.prompt_pass('Password')
        user_entry = self.session.query(model.User).filter_by(
            username=username).first()
        if user_entry:
            if user_entry.password == password:
                self.user = user_entry
        return False

    def do_add(self, line):
        if self.user is None:
            self.do_login('')
        if not self.user.admin:
            return False
        username = ui.prompt('Username')
        password = ui.prompt('Password')
        admin = ui.prompt_bool('Administartor', default=False)
        entry = model.User(username=username, password=password, admin=admin)
        self.session.add(entry)
        self.session.commit()

    def do_list(self, line):
        if self.user is None:
            self.do_login('')
        if not self.user.admin:
            return False
        out = ui.OutputLines()
        for entry in self.session.query(model.User):
            out.append(entry)
        out.output()


class CarCommand(BaseCommand):

    prompt = 'Car> '

    def do_add(self, line):
        licence = ui.prompt('Licence')
        tyres = ui.prompt_choice('Tyre type', choices=model.Car.TYRES)

        entry = model.Car(licence=licence, tyres=tyres,
                          owner_id=self.user.id)

        self.session.add(entry)
        self.session.commit()

    def do_list(self, line):
        out = ui.OutputLines()
        for entry in self.session.query(
                model.Car).filter_by(owner_id=self.user.id):
            out.append(entry)
        out.output()

    def do_select(self, line):
        cars = self.session.query(model.Car).filter_by(owner_id=self.user.id)
        choices = []
        for car in cars:
            choices.append((car.id, car.licence))
        if len(choices) == 1:
            print('Selecting only car')
            return cars.first()
        car = ui.prompt_choice('Select your car', choices=choices)
        self.car = cars[car-1]
        return False


class AllCommand(BaseCommand):

    prompt = '> '
    user = None

    def do_login(self, line):
        if self.user is not None:
            print('Already logged in. Use logout to log out')
            return False
        username = ui.prompt('Username')
        password = ui.prompt_pass('Password')
        user_entry = self.session.query(model.User).filter_by(
            username=username).first()
        if user_entry:
            if user_entry.password == password:
                self.user = user_entry
        return False

    def do_logout(self, line):
        if self.user is None:
            print('Not logged in')
            return False
        self.user = None
        self.car = None
        return False

    def get_user(self):
        if self.user is None:
            self.do_login('')
        return self.user

    def get_car(self):
        user = self.get_user()
        cars = self.session.query(model.Car).filter_by(
            owner_id=user.id)

        choices = []
        for car in cars:
            choices.append((car.id, car.licence))
        if len(choices) == 1:
            print('Selecting only car')
            return cars.first()
        car = ui.prompt_choice('Select your car', choices=choices)
        self.car = cars[car-1]
        return self.car

    def do_car(self, line):
        c = CarCommand()
        c.user = self.get_user()
        if c.user is None:
            return False
        return c.cmdloop()

    def do_fuel(self, line):
        f = FuelCommand()
        f.car = self.get_car()
        return f.cmdloop()

    def do_user(self, line):
        u = UserCommand()
        u.user = self.get_user()
        return u.cmdloop()
