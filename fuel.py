#!/usr/bin/env python

import command
import db

if __name__ == '__main__':
    database = db.configure_session()

    command.AllCommand().cmdloop()
