import csv
from random import choice

def read_csv(source):
    '''Reads selected file and returns a list'''
    domain_list = []
    with open(source, "r") as open_file:
        reader = csv.reader(open_file)
        for line in reader:
            domain_list.append(line)
    return domain_list

def random_domain(domain_list):
    '''Selects random domain from list'''
    selected_line = choice(domain_list)
    return selected_line[0]
