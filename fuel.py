#!/usr/bin/env python

from datetime import datetime
import ui
import command
import model
import db

if __name__ == '__main__':
    database = db.configure_session()

    command.FuelCommand().cmdloop()


    # while True:
    #     command = ui.prompt('Fuel', prompt_char='> ').lower()
    #     clist = command.split()
    #     args = []
    #     if len(clist) > 1:
    #         command = clist[0]
    #         args = clist[1:]
    #     if command in cmd.COMMANDS:
    #         c = cmd.COMMANDS[command]()
    #         c.run(*args)
    #     else:
    #         print('invalid command')
