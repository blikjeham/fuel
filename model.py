from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, Boolean, Date

import datetime

Base = declarative_base()


def parse_date(line):
    try:
        return datetime.datetime.strptime(line, '%d/%m/%y')
    except ValueError as e:
        print(e)
        return datetime.date.today()


def parse_line(line):
    line = line.split(',')
    date = parse_date(line[0])
    distance = float(line[1]) if len(line[1]) else float(0.0)
    liters = float(line[2])
    price = float(line[3])
    return FuelEntry(
        liters=liters, price=price, distance=distance,
        date=date, full=not not distance)


def import_entries(filename):
    entry_list = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            if ',' not in line:
                continue
            entry = parse_line(line)
            if entry:
                entry_list.append(entry)
    return entry_list


class FuelError(Exception):
    pass


class FuelEntry(Base):

    __tablename__ = 'fuel_entries'

    id = Column(Integer, primary_key=True)
    liters = Column(Float)
    price = Column(Float)
    distance = Column(Float)
    full = Column(Boolean)
    date = Column(Date)

    def kmpl(self):
        if self.full:
            return self.distance / self.liters

    def lphkm(self):
        if self.full:
            return self.liters / (self.distance / 100)

    def __repr__(self):
        ret = '{id:8}: {d} {l:6.02f} l/{k:7.02f} km a {p:5.03f} cent'.format(
            id=self.id if self.id is not None else 'combined',
            d=self.date, l=self.liters,
            k=self.distance, p=self.price)
        if self.full:
            ret += ' ({:5.2f} | {:4.1f})'.format(self.kmpl(), self.lphkm())
        else:
            ret += ' ( incomplete )'

        return ret


class FuelLog:

    def __init__(self):
        self.entries = []
        self.liters = 0
        self.distance = 0
        self.price = 0

    def add_entry(self, entry):
        if not isinstance(entry, FuelEntry):
            raise FuelError('Not a FuelEntry')
        self.entries.append(entry)
        self.add_metrics(entry)

    def add_metrics(self, entry):
        self.liters += entry.liters
        self.distance += entry.distance
        self.price += entry.price

    def __str__(self):
        return '{} km/liter'.format(self.distance/self.liters)
