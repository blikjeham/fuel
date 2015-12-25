import datetime
import cmd
import sys
import ui
import model

from db import Session

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


def total(session):
    global incomplete_entries
    total_liters = 0.0
    total_price = 0.0
    total_distance = 0.0
    num_entries = 0

    for entry in session.query(model.FuelEntry):
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


class FuelCommand(cmd.Cmd):

    prompt = 'Fuel> '

    session = Session()

    def parseline(self, line):
        command, arg, line = super().parseline(line)
        if command is not None:
            command = command.lower()
        return command, arg, line

    def emptyline(self):
        pass

    def do_add(self, line):
        date = ui.prompt_date('Date', default=datetime.date.today())
        distance = ui.prompt_float('Distance', allow_empty=True)
        liters = ui.prompt_float('Volume')
        price = ui.prompt_float('Price')
        full = not not distance

        entry = model.FuelEntry(liters=liters, price=price, distance=distance,
                                date=date, full=full)

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
        calculate_entries(self.session, num_lines=num_lines)

    def help_calc(self):
        print('calc [number_of_lines]\n\nCalculate the fuel entries')
        print('number_of_lines defaults to {}'.format(ui.DEFAULT_MAX_LINES))

    def do_del(self, line):
        id = line if len(line) else None
        if id is None:
            id = ui.prompt('Enter the ID to delete')
        try:
            id = int(id)
        except ValueError:
            return

        entry = self.session.query(model.FuelEntry).filter_by(id=id).first()

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

        entry = self.session.query(model.FuelEntry).filter_by(id=id).first()

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

    def do_flush(self, line):
        if ui.prompt_bool('Are you sure you wish to flush the Fuel Log',
                          default=False):
            self.session.query(model.FuelEntry).delete()
            self.session.commit()

    def help_flush(self):
        print('flush\n\nFlush all entries from the Fuel Log')

    def do_import(self, line):
        filename = line if len(line) else None
        if filename is None:
            filename = ui.prompt('Filename')

        entry_list = model.import_entries(filename)
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
        for entry in self.session.query(model.FuelEntry):
            out.append(entry)

        out.output(num_lines=num_lines)

    def help_list(self):
        print('list [number_of_lines]\n\nList the entries in the Fuel Log')
        print('number_of_lines defaults to {}'.format(ui.DEFAULT_MAX_LINES))

    def do_total(self, line):
        print(total(self.session))

    def help_total(self):
        print('total\n\nCalculate and print the total stats')

    # line do_EOF(self, line):
    #     print('')
    #     return self.do_quit(line)

    def do_quit(self, line):
        return True

    def help_quit(self):
        print('quit\n\nExit the Fuel Log')
