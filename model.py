from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy_utils.types.password import PasswordType
from sqlalchemy.orm import relationship
import sqlalchemy as sa

import datetime

Base = declarative_base()


def parse_date(line):
    try:
        return datetime.datetime.strptime(line, '%d/%m/%y')
    except ValueError as e:
        try:
            return datetime.datetime.strptime(line, '%Y-%m-%d')
        except ValueError as e:
            print(e)
            return datetime.date.today()


def parse_line(line, car):
    line = line.split(',')
    car = int(1)
    date = parse_date(line[0])
    distance = float(line[1]) if len(line[1]) else float(0.0)
    liters = float(line[2])
    price = float(line[3])
    return FuelEntry(
        car=car, liters=liters, price=price,
        distance=distance, date=date, full=not not distance)


def import_entries(filename, car):
    entry_list = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            if ',' not in line:
                continue
            entry = parse_line(line, car)
            if entry:
                entry_list.append(entry)
    return entry_list


class FuelEntry(Base):

    __tablename__ = 'fuel_entries'

    id = sa.Column(sa.Integer, primary_key=True)
    car = sa.Column(sa.Integer, sa.ForeignKey('cars.id'))
    liters = sa.Column(sa.Float)
    price = sa.Column(sa.Float)
    distance = sa.Column(sa.Float)
    full = sa.Column(sa.Boolean)
    date = sa.Column(sa.Date)

    def kmpl(self):
        if self.full:
            return self.distance / self.liters

    def lphkm(self):
        if self.full:
            return self.liters / (self.distance / 100)

    def __repr__(self):
        ret = '{id:8}: {d} {l:6.02f} l/{k:7.02f} km a {p:5.03f} euro/l'.format(
            id=self.id if self.id is not None else 'combined',
            d=self.date, l=self.liters,
            k=self.distance, p=self.price)
        if self.full:
            ret += ' ({:5.2f} | {:4.1f})'.format(self.kmpl(), self.lphkm())
        else:
            ret += ' ( incomplete )'

        return ret

    def csv(self, delim=','):
        '''Output character separated values'''
        ret = '{d},{k:.02f},{l:.02f},{p:.03f}'.format(
            d=self.date, k=self.distance,
            l=self.liters, p=self.price)
        return ret

class Car(Base):

    __tablename__ = 'cars'

    TYRES = [
        ('w', 'Winter tyres'),
        ('s', 'Summer tyres'),
        ('a', 'All-weather tyres')
    ]

    id = sa.Column(sa.Integer, primary_key=True)
    licence = sa.Column(sa.Unicode(30))
    tyres = sa.Column(ChoiceType(TYRES, impl=sa.Unicode(5)))
    owner_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    fuel_entries = relationship('FuelEntry')

    def __repr__(self):
        ret = '{id:8}: {l} ({t})'.format(
            id=self.id, l=self.licence, t=self.tyres.code)
        return ret


class User(Base):

    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.Unicode(255))
    password = sa.Column(PasswordType(schemes=['pbkdf2_sha512']))
    cars = relationship('Car')
    admin = sa.Column(sa.Boolean)
    last_login = sa.Column(sa.DateTime)

    def __repr__(self):
        ret = '{id:8}: {name}'.format(id=self.id, name=self.username)
        return ret
