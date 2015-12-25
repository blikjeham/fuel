import datetime


def wait_prompt():
    value = input(str(InputLine('Press any key', prompt_char='...')))


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


class InputLine(object):
    def __init__(self, line, default=None, prompt_char=': '):
        self.line = line
        self.default = default
        self.prompt_char = prompt_char

    def default_string(self):
        if self.default is None:
            return ''

        # set booleans
        if isinstance(self.default, bool):
            return '{}/{}'.format(
                'Y' if self.default else 'y',
                'n' if self.default else 'N'
            )
        else:
            return self.default

    def __unicode__(self):
        if self.default is not None:
            return '{} [{}]{}'.format(
                self.line, self.default_string(),
                self.prompt_char)
        else:
            return '{}{}'.format(self.line, self.prompt_char)

    def __str__(self):
        return str(self.__unicode__())
