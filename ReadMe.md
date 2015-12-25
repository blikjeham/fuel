# Fuel Consumption Log

## Introduction

While there are maybe multiple programs to calculate your mileage with, I've
written this program to meet up to my needs. It is directly impacted by the
way I refuel my car.

## Measuring

Let's say I want to measure my mileage over a longer period of time. The first
time I refuel, I fill my tank completely. The fuel hoses use a feedback
pressure valve to stop when the tank is full. I reset the trip-counter to 0.0,
and I start driving.

The next time I refuel my car, I fill it to the same full level using the same
feed-back pressure stop. I now know what volume of fuel I've consumed, because
it says so on the pump. I look at the trip-counter to see what distance I have
traveled using that amount of fuel. I write the distance down on the receipt
and I reset the trip-counter for the next measurement.
When I get home, I enter the distance, volume, and price per liter into this
system.

Sometimes I need to refuel on the highway, where the price is usually higher.
In that situation, I just want to fill 'er up so I can reach a cheaper petrol
station. What I do then is pump a few liters into my car, pay and get away. I
don't reset my trip-counter, nor do I write down the distance. When I get home
I enter the volume and price in the system. This will be added to the next
complete refueling.
After refuelling completely at a cheaper station I write down the total distance
from the trip-counter, which include the distance of the complete and incomplete
refuelling. I reset the counter and drive home, where I will enter this one
into the system. The incomplete volume and price will be added to the complete
volume and price. The distance was already the complete distance. The combined
entries are just as if I had a massive fuel tank in my car.

### Adding entries

To add an entry, type `add`. The system will prompt you for distance, volume,
price per liter, and date. The distance can be left empty, or set to 0.0 if
it's an incomplete entry.

### Listing entries

`list` will show you all entries in the log. The output is paginated to, but
you can add the number of entries per page to the command: `list 25` will show
25 entries per page.

### Editing entries

The `edit` command allows you to change any parameter of an entry. You will be
prompted for the entry to edit, and all its values. You can also supply the
number of the entry to edit: `edit 12` will edit entry 12.

### Deleting entries

To delete an entry, just type `del`. The system will ask you which entry to
delete. You can also suplly the number of the entry to delete after the
command: `del 42` will delete entry 42.


## Processing

When listing all the entries with `list`, you will see that for all complete
entries, the km per liter and liter per 100km is shown. Those are the most
common measurements for fuel consumption. Incomplete entries will not receive a
calculated mileage, and the first complete entry afterwards will have a skewed
mileage, because the distance of the preceding incomplete entries is added, but
not the volume or price.

### Calculating the entries

Using the `calc` command will show you a similar output to `list`, but it will
merge the incomplete entries with the next complete entry. You can recognize
these entries by the 'combined' instead of the number.

As with the `list` command, you can also supply the number of lines per page
with the `calc` command

### Calculating the total

To calculate the total average mileage, use the `total` command.

## Installing and running

### Requirements

Fuel Log requires:
* sqlalchemy
* cmd

### Running

To run Fuel log, type: `fuel.py`

To quit, type `quit` at the 'Fuel> ' prompt
