"""
:Author : SAINT-AMAND Matthieu
"""
from __future__ import annotations

from tkinter import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException
from paramiko import SSHException

from controller import find_useless_ports

# from main import calculate_data_result

"""
@:param string device_type : you can get it on the switch prompt from the "show version" command
@:param string ip : the ip of your switch master
@:param string username : the login
@:param string password : password to be connected to the switch
"""
"""
@:param string command : contains the command send to the prompt terminal
"""


def switch_init_connection(command, ip, device_type, username, password, l5):
    # Global declaration allow to have an access outside the function. This one allow to launch a CLI command inside
    # the switch prompt.
    #print("Connecting...")
    global output_buffer
    switch = {
        'device_type': device_type,  # hp_procurve for example
        'ip': ip,
        'username': username,
        'password': password,
    }
    global device
    try:
        device = ConnectHandler(**switch)
        output_buffer = device.send_command(command)
        l5.config(text='Init connection. Trying cli commands...')
        #print("End of command.")
    except (NetMikoTimeoutException, NetMikoAuthenticationException,) as e:
        #reason = 'Wrong values.'
        l5.config(text='Failed to execute cli due to wrong values.')
        #raise ValueError('Failed to execute cli on %s due to %s', switch['ip'], reason)

    except SSHException as e:
        # reason = 'Wrong values.'
        l5.config(text='Failed to execute cli due to wrong values.')
        #raise ValueError('Failed to execute cli due to wrong values.', switch['ip'], reason)
    except Exception as e:
        #reason = 'Wrong values.'
        # This is in case of I/O Error, which could be due to
        # connectivity issue or due to pushing commands faster than what
        #  the switch can handle
        l5.config(text='Failed to execute cli due to wrong values.')
        #raise ValueError('Failed to execute cli on %s due to %s', switch['ip'], reason)
    if not device:
        device.disconnect()


"""
This function write the content of a data inside a text file.
@:param string fileName : name of the file created (or already created)
@:param string data : the data wanted
"""


def writeInFile(fileName, data, mode='w'):
    # Create it if !isExist
    print("Write text file...")
    file = open(fileName, mode)
    file.write(data)
    file.close()


"""
This function allows to reshape the text file to make the treatment easier.
@:param string fileName : retrieve the file nam which contains the output of the command
"""


def del_to_fstab(fileName, begin, end):
    # Use with if the file is already open or anything else about it
    with open(fileName, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(fileName, 'w') as fout:
        fout.writelines(data[begin:end])  # [(+)first:(-)end]


"""
This function convert a txt file which contains an array into a CSV file with ; delimiter. 
Use Regex to replace all n space inside the text.
"""


def convertToCSV_file(fileName, csvFile):
    print("Convert in CSV file..")
    file = open(fileName, 'r')
    tmp_file = open(csvFile, 'w')
    lines = file.readlines()
    for line in lines:
        data = re.sub('[ ]{2,}', ';', line)
        tmp_file.write(data[1:])
    file.close()


'''This function allow to remove the headers appeared in CSV file when there are 2 PoE switchs or more in 1 stack. In 
this case, some data are infected and the CSV file gotta be cleanup . '''


def remove_array_header(fileName, washedCsvFile):
    print("Delete bad lines...")
    file = open(fileName, 'r')
    tmp_file = open(washedCsvFile, 'w')
    lines = file.readlines()
    for line in lines:
        if line.__contains__('Member'):
            print(line)
        elif line.__contains__('Available'):
            print(line)

        elif line.__contains__('Allow'):
            print(line)

        elif line.__contains__('----'):
            print(line)

        elif line.__contains__('Port'):
            print(line)

        else:
            tmp_file.write(line)
    file.close()


"""
Allow to retrieve data from CLI commands was previously wrote in a text file, and convert them into CSV file.
"""


def calculate_data_result(ip_address, device_type, login, password, l5):
    # Take few time... // 'hp_procurve', '10.80.160.41'
    l5.config(text='Wait until connection...')
    switch_init_connection('sh power-over-ethernet brief', ip_address, device_type, login,
                           password, l5)  # Launch the command you want
    # print(output_buffer)
    # Create a file and delete the content if this one is not empty
    #l5.config(text='First command executed, creating files...')
    writeInFile('python_power_ports.txt', output_buffer)  # Write the output in a file like command > file.ext in shell
    del_to_fstab('python_power_ports.txt', 8, -4)  # remove the lines you want
    switch_init_connection('sh interfaces brief', ip_address, device_type, login, password, l5)
    # print(output_buffer)
    # Take the previous file and write without delete over the text
    writeInFile('python_status_ports.txt', output_buffer)
    del_to_fstab('python_status_ports.txt', 5, -1)
    # Converting part ... #############################################
    l5.config(text='Converting into CSV files...')
    convertToCSV_file('python_power_ports.txt', 'python_power_ports.csv')
    convertToCSV_file('python_status_ports.txt', 'python_status_ports.csv')
    remove_array_header('python_power_ports.csv', 'washed_power_port.csv')
    device.disconnect()
    l5.config(text='End of treatment, connection ended.')
    print("End of treatment, connection ended.")


# remove_array_header('python_power_ports.csv','washed_power_port.csv')

'''
This function allow to retrieve a value from an entry.
@:param Entry i : the entry value you want to get
'''
sizes = [100, 100, 100]


def get_entry_value(i):
    switcher = {
        0: e1.get(),
        1: 'hp_procurve',
        2: e3.get(),
        3: e4.get(),
    }
    return switcher.get(i, "Invalid")


''' For graphics charts'''


def use_graphics(size=None):  # very bad way to update the frame but no time to search in the deep of internet
    if size is None:
        size = sizes
    labels = 'NoToIP', 'ToIP', 'Down'
    colors = ['gold', 'lightskyblue', 'lightcoral']
    fig = Figure(figsize=(6, 4), dpi=96)
    plt = fig.add_subplot(111)
    explode = (0.1, 0, 0)
    plt.pie(size, startangle=90, labels=labels, colors=colors, shadow=True, autopct='%1.1f%%', explode=explode)
    graph = FigureCanvasTkAgg(fig, master=window)
    canvas = graph.get_tk_widget()
    canvas.grid(row=0, column=5, rowspan=8, columnspan=3)
    canvas.configure(width=300, height=250)
    canvas.config(highlightbackground="red")


'''
This function allow connect with a button and notify the user when h'es connected to the switch.
'''


def view_command():
    # make sure we've cleared all entries in the listbox every time we press the View all button
    # list1.del    ete(0, END)  # from 0 to end
    if not get_entry_value(0) or not get_entry_value(1) or not get_entry_value(2) or not get_entry_value(3):
        l5.config(text='Empty fields, please use entries above.')
    else:
        l5.config(text='Connecting... It will take few seconds.')
        print('ip= ' + get_entry_value(0) + '\ndevice_type= ' + get_entry_value(1) + '\nusername= ' + get_entry_value(
            2) + '\npassword= ' + get_entry_value(3))
        ##########################################
        calculate_data_result(get_entry_value(0), get_entry_value(1), get_entry_value(
            2), get_entry_value(3), l5)
        ##########################################
        valuesToUnplug = find_useless_ports()  # from controller.py
        list1.delete(0, END)
        for count in range(0, len(valuesToUnplug[0])):
            list1.insert(0, valuesToUnplug[0][count])
        values = [valuesToUnplug[3], valuesToUnplug[4], valuesToUnplug[5]]
        use_graphics(values)


# All the code below is a front-end code, allow to place each component in the frame and the style sheet with it.
# code for the GUI (front end)
"""
Allow to create the GUI and its components.
"""


def init_GUI():
    global e1, e2, e3, e4, window, list1, l5

    window = Tk()
    window.wm_title("PoE Washer")
    window.resizable(False, False)
    ##########################################
    l1 = Label(window, text="IP")
    l1.grid(row=0, column=0)

    l2 = Label(window, text="Device Type")
    l2.grid(row=0, column=2)

    l3 = Label(window, text="Login")
    l3.grid(row=1, column=0)

    l4 = Label(window, text="Password")
    l4.grid(row=1, column=2)

    l5 = Label(window, text="")
    l5.grid(row=2, column=1, columnspan=2)
    ##########################################

    e1 = Entry(window, borderwidth=2)
    e1.grid(row=0, column=1)

    rd1 = Radiobutton(window, text="Aruba HP", value=0, highlightthickness=0)
    rd1.grid(row=0, column=3)
    rd2 = Radiobutton(window, text="Enterasys", value=1)
    rd2.grid(row=0, column=4)

    e3 = Entry(window, borderwidth=2)
    e3.grid(row=1, column=1)

    e4 = Entry(window, borderwidth=2, show='*')
    e4.grid(row=1, column=3, padx=5)

    list1 = Listbox(window, height=6, width=35)
    list1.grid(row=2, column=0, rowspan=6, columnspan=2, padx=5)

    ##########################################

    # now we need to attach a scrollbar to the listbox, and the other direction,too
    sb1 = Scrollbar(window)
    sb1.grid(row=2, column=2, rowspan=10)
    list1.config(yscrollcommand=sb1.set)
    sb1.config(command=list1.yview)

    b1 = Button(window, text="View all", width=16, command=view_command)
    b1.grid(row=2, column=3)

    b6 = Button(window, text="Close", width=12, command=window.destroy)
    b6.grid(row=7, column=3)

    use_graphics()
    window.mainloop()


# explode = (0.1, 0, 0, 0)  # explode 1st slice
##########################################

init_GUI()

##########################################
