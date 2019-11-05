'''
:Author : SAINT-AMAND Matthieu
'''
import csv

data_power_ports = []
data_status_ports = []

"""
Allow to extract data from a CSV file into a list of string.
"""


def extract_data_power():
    global data_power_ports
    with open('washed_power_port.csv', newline='') as f:
        reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
        for row in reader:
            if row[7] != 'Disabled':
                data_power_ports.append(row)
        extract_data_status()


"""
Some description than extract_data_power().
"""


def extract_data_status():
    global data_status_ports
    with open('python_status_ports.csv', newline='') as f:
        reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
        for row in reader:
            data_status_ports.append(row)


"""
Convert into float.
"""


def check_string_to_float(s):
    return float(s)


"""
To know if a float value is close to 0 or not because the condition float==0 doesn't work for this type.
"""


def is_close(a, b, tol=1e-9):
    return abs(a - b) <= tol


"""The main algorithm which allow to know what ports are wrong in the switch configuration. Thi function distinguish 
between ToIP, Down and NoToIP ports. """


def find_useless_ports():
    uselessPorts = []
    toipPorts = []
    downports = []
    data = []
    optimize_status_port = []

    #print(optimize_status_port)
    #print(data_power_ports)
    extract_data_power()
    # take the lenght of data power ports to take PoE only in optimize_status_port that contains PoE only from the
    # interface command which take all ports

    for i in range(0, len(data_power_ports)):
        for j in range(0, len(data_status_ports)):
            if data_power_ports[i][0] == data_status_ports[j][0]:
                optimize_status_port.append(data_status_ports[j])
    #print(len(optimize_status_port))
    #print(len(data_power_ports))
    for i in range(0, len(optimize_status_port)):
        if optimize_status_port[i][0] == data_power_ports[i][0] and data_power_ports[i][7] != "Disabled":
            if (optimize_status_port[i][4] == 'Up' and is_close(check_string_to_float(data_power_ports[i][5][:-1]),
                                                                0.0)):  # 0 is True and others are False
                #print(optimize_status_port[i][0] + ' it\'s not ToIP')
                uselessPorts.append(optimize_status_port[i][0])
            elif optimize_status_port[i][4] == 'Down':
                downports.append(optimize_status_port[i][0])
            elif (optimize_status_port[i][4] == 'Up' and not is_close(
                    check_string_to_float(data_power_ports[i][5][:-1]),
                    0.0)):
                toipPorts.append(optimize_status_port[i][0])
    data.append(uselessPorts)
    data.append(toipPorts)
    data.append(downports)
    data.append(len(uselessPorts))  # data 3
    data.append(len(toipPorts))  # data 4
    data.append(len(downports))  # data 5

    print('\n\n')
    print(uselessPorts)  # data 0
    print(toipPorts)  # data 1
    print(downports)  # data 2
    return data

# find_useless_ports()  # test only
