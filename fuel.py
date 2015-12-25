#!/usr/bin/env python

from datetime import datetime
import ui
import command
import model
import db

if __name__ == '__main__':
    database = db.configure_session()

    command.FuelCommand().cmdloop()
