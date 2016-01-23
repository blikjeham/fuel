import datetime
import getpass

DEFAULT_MAX_LINES = 40


def wait_prompt():
    value = input(str(InputLine('Press return', prompt_char='...')))


def more_prompt():
    value = input(str(InputLine(
        '--- press q to quit, or return to continue ---')))
    if value.lower() in ['q']:
        return False
    return True


def prompt(line, default=None, allow_empty=False, **kwargs):
    if not isinstance(line, InputLine):
        line = InputLine(line, default=default, **kwargs)

    value = input(line).strip()
    if value:
        return value
    elif line.default is not None:
        return line.default
    elif not allow_empty:
        return prompt(line, default)
    else:
        return None


def prompt_pass(line):
    if not isinstance(line, InputLine):
        line = InputLine(line)
    return getpass.getpass(line)


def prompt_float(line, default=None, allow_empty=False, **kwargs):
    if not isinstance(line, InputLine):
        line = InputLine(line, default=default, **kwargs)

    value = input(line).strip()
    if not value:
        if line.default is not None:
            value = line.default
        elif not allow_empty:
            return prompt_float(line, default)
        else:
            value = 0.0
    if value is not None:
        try:
            return float(value)
        except ValueError:
            return prompt_float(line, default)


def prompt_date(line, **kwargs):
    value = prompt(line, **kwargs)
    if not isinstance(value, datetime.date):
        try:
            value = datetime.datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            value = datetime.date.today()
    return value


def prompt_bool(line, default=False):
    if not isinstance(line, InputLine):
        line = InputLine(line, default=default)

    value = input(line).strip().lower()
    if value in ['y', 'yes', 'true']:
        return True
    elif value in ['n', 'no', 'false']:
        return False
    else:
        return default


def prompt_choice(line, choices=None, default=None):
    if not isinstance(line, InputLine):
        line = InputLine(line, default=default, choices=choices)

    value = input(line).strip().lower()
    for choice in line.choices:
        if value == str(choice[0]):
            return choice[0]
    return prompt_choice(line, choices=choices, default=default)


class InputLine(object):
    def __init__(self, line, default=None, prompt_char=': ', choices=None):
        self.line = line
        self.default = default
        self.prompt_char = prompt_char
        self.choices = choices

    def default_string(self):
        print(self.choices)
        if self.default is None and self.choices is None:
            return ''

        # set booleans
        if isinstance(self.default, bool):
            return '{}/{}'.format(
                'Y' if self.default else 'y',
                'n' if self.default else 'N'
            )
        elif self.choices is not None:
            return '/'.join(['{}'.format(c[0]) for c in self.choices])
        else:
            return self.default

    def __unicode__(self):
        if self.default is not None or self.choices is not None:
            return '{} [{}]{}'.format(
                self.line, self.default_string(),
                self.prompt_char)
        else:
            return '{}{}'.format(self.line, self.prompt_char)

    def __str__(self):
        return str(self.__unicode__())


class OutputLines(object):
    buffer = None
    lines = 0

    def __init__(self, lines=None):
        self.buffer = []
        if lines is not None:
            self.append(lines)

    def _assure_buffer(self):
        if self.buffer is None:
            self.buffer = []

    def append(self, lines):
        self._assure_buffer()
        if not isinstance(lines, list):
            lines = [lines]

        for line in lines:
            if not isinstance(line, str):
                line = str(line)

            self.buffer.append(line)
            self.lines += 1

    def append_csv(self, lines):
        self._assure_buffer()
        if not isinstance(lines, list):
            lines = [lines]

        for line in lines:
            if not isinstance(line, str):
                line = line.csv()

            self.buffer.append(line)
            self.lines += 1

    def output(self, num_lines=DEFAULT_MAX_LINES):
        if num_lines is None:
            num_lines = DEFAULT_MAX_LINES

        index = 1
        for line in self.buffer:
            if index > num_lines:
                if not more_prompt():
                    self.buffer = None
                    return
                index = 1
            index += 1
            print(line)
        self.buffer = None


    def csv(self, filename):
        with open(filename, 'w+') as f:
            for line in self.buffer:
                f.write(line + '\n')
        self.buffer = None
