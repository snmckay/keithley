from keithley24xx import RS232_Keithley24xx
from pylab import *
from binascii import hexlify
#from serial_com import Serial_Com
#from loading import Loading
#from useful_functions import U_Functions 
import sys
import numpy as np
# import xlsxwriter
import serial
import time
from time import strftime
#from data_logger import DataLogging
#import excelWrite as xls
import matplotlib.pyplot as plt

def set_datetime():
    global full_datetime
    full_datetime = strftime("%m/%d/%y at %I:%M:%S%p")
    print(full_datetime)
    
def create_fullstring():
    global dut
    global trans_active
    global full_datetime
    global full_string
    
    full_string = dut + ' - ' + trans_active + ' - ' + full_datetime
    full_string = full_string.replace('/', "_")
    full_string = full_string.replace(':', "-")
    print(full_string)
    

def plot_data(xplot, yplot, title, xlabel, ylabel):
    #X = [590,540,740,130,810,300,320,230,470,620,770,250]
    #Y = [32,36,39,52,61,72,77,75,68,57,48,48]

    global dut
    global trans_active
    global full_datetime
    global full_string

    plt.scatter(xplot,yplot)

    plt.xlim(0,11)
    plt.ylim(0,100000)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)


    final_string = 'graphs/' + full_string + '.pdf'
    print(final_string)
    plt.savefig(final_string)
    plt.show()
    
dut = "Atmega328P-AU - All Cs - Rectangle Cut"
trans_active = "Not Active"
full_datetime = ""
full_string = ""
    
SIMPLE_RESISTANCE = """
*RST
:SENS:FUNC 'RES'
:SENS:RES:NPLC 1
:SENS:RES:MODE MAN
:SOUR:FUNC CURR
:SOUR:CURR 0.01
:SOUR:CLE:AUTO ON
:SENS:VOLT:PROT 10
:TRIG:COUN 1
:FORM:ELEM RES"""

TRY_SWEEP2 = """
*RST
:SOUR:FUNC VOLT
:SOUR:VOLT:MODE FIXED
:SOUR:VOLT:RANG 20
:SOUR:VOLT:LEV 10
:SENS:FUNC 'RES'
:SOUR:CLE:AUTO ON
:FORM:ELEM VOLT, RES
"""

TRY_SWEEP3 = """
*RST
:ARM:COUN 1
:ARM:SOUR IMM
:SENS:FUNC \"RES\"
:SENS:RES:NPLC 1
:SENS:RES:MODE MAN
:SENS:CURR:PROT 0.0001
:SOUR:FUNC VOLT
:SOUR:VOLT:STAR {v_start}
:SOUR:VOLT:STOP {v_stop}
:SOUR:VOLT:STEP {v_step}
:SOUR:VOLT:MODE SWE
:SOUR:CLE:AUTO ON
:SOUR:SWEEP:RANG BEST
:SOUR:SWEEP:SPAC LIN
:SOUR:DEL 0.001
:TRIG:COUN {n_pts}
:FORM:ELEM VOLT, RES, CURR"""

TRY_SWEEP = """
*RST
:ARM:COUN 1
:ARM:SOUR IMM
:SENS:FUNC \"RES\"
:SOUR:FUNC VOLT
:SOUR:VOLT:STAR {v_start}
:SOUR:VOLT:STOP {v_stop}
:SOUR:VOLT:STEP {v_step}
:SOUR:VOLT:MODE SWE
:SOUR:CLE:AUTO ON
:SOUR:SWEEP:RANG BEST
:SOUR:SWEEP:SPAC LIN
:SOUR:DEL:AUTO ON
:TRIG:COUN {n_pts}
:FORM:ELEM VOLT, RES"""

APPLY_VOLTAGE = """
*RST
:SOUR:FUNC VOLT
:SOUR:VOLT:MODE FIXED
:SOUR:VOLT:RANG 20
:SOUR:VOLT:LEV 10
:SOUR:CLE:AUTO ON
:OUTP ON"""

SOURCE_SETUP = """
*RST
:TRIG:CLE
:SYST:AZER:STAT ONCE
:FORM:ELEM VOLT

:ARM:COUN 1
:ARM:SOUR IMM
:ARM:DIR ACC
:ARM:OUTP NONE

:TRIG:DEL 0
:TRIG:SOUR TLIN
:TRIG:DIR ACC
:TRIG:ILIN 1
:TRIG:OLIN 2
:TRIG:INP SENS
:TRIG:OUTP SOUR
:TRIG:DEL 0

:FORM:ELEM CURR
:SENS:FUNC 'CURR'
:SENS:VOLT:NPLC {nplc}
:SENS:CURR:PROT 0.1
:SENS:CURR:RANG 0.1

:SOUR:FUNC VOLT
:SOUR:VOLT:STAR {v_start}
:SOUR:VOLT:STOP {v_stop}
:SOUR:VOLT:STEP {v_step}
:SOUR:VOLT:MODE SWE

:SOUR:SWEEP:RANG BEST
:SOUR:SWEEP:SPAC LIN
:SOUR:DEL 0.001
:SOUR:CLE:AUTO ON"""

METER_SETUP = """
*RST
:TRIG:CLE
:SYST:AZER:STAT ONCE
:FORM:ELEM CURR

:ARM:COUN 1
:ARM:SOUR IMM
:ARM:DIR ACC
:ARM:OUTP NONE

:TRIG:DEL 0
:TRIG:SOUR TLIN
:TRIG:DIR ACC
:TRIG:ILIN 2
:TRIG:OLIN 1
:TRIG:INP SOUR
:TRIG:OUTP DEL

:FORM:ELEM CURR
:SENS:FUNC 'CURR'
:SENS:CURR:NPLC {nplc}
:SENS:CURR:PROT 0.1
:SENS:CURR:RANG 0.1

:SOUR:FUNC VOLT
:SOUR:VOLT 5
:SOUR:DEL 0.00"""
		

ins = 'b'
direction = '1'
version = '2'



#u =  U_Functions()
#L = Loading()
#DL = DataLogging()

def splitArray(numFields, samples):
    arrays = []
    i = 0
    while i < numFields:
        arrays.append([])
        i += 1
    print(arrays)
    i = 0
    for value in samples:
        arrays[i].append(value)
        i += 1
        if i == numFields:
            i = 0
    return arrays
    
def print_menu():
    print("Keithley 6430 Comms:")
    print("\t 1.) Initialize Keithley 6430")
    print("\t 2.) Quit")
    
def get_input():
    global selected
    selected = input("Please type the number for your chosen option: ")
    while not selected.isnumeric():
        selected = input("Please type the number for your chosen option: ")
    return int(selected)

def keithley_run_hardcoded(dev):
    with dev[0] as source_dev:
#        sc =  Serial_Com()
        nplc = 0.02
        v_start = 0.5
        v_stop = 2
        n_pts = 100
        v_step = float( v_stop - v_start )/(n_pts-1)
        set_datetime()
        create_fullstring()
		
        print('programming SOURCE!')
        for cmd in str2lines( TRY_SWEEP.format( **locals() ) ):
            print(cmd)
            source_dev.send_cmd(str.encode(cmd))
        try:
            print("Reading Now")
            time.sleep(1)
            read_resp = source_dev.ask_cmd(":READ?")
            print("Response: " + str(read_resp))
            s = np.fromstring( read_resp, sep=',' )
            print(str(s))
            print("Splitting Array")
            s = splitArray(2, s)
            print(s)
            print("Trying to plot")
            plot_data(s[0], s[1], "Voltage vs. Resistance", "Volts", "Ohms")
            f = open("log.txt", "a")
            write_string = "\n" + full_string + "\n" + str(s) + "\n"
            #print(write_string)
            f.write(write_string)
            f.close()
        except:
                print("Failed to get data or something")
                
        
        
        
        source_dev.clear_instrument()

def keithley_init_and_menu():
    choice = -1
    smu = RS232_Keithley24xx.discover_connected( baudrate=9600 )
    print(smu)
    print(len(smu))
    
    while True:
        if len(smu) > 0:
            print("Keithley 6430 Options:")
            print("\t 1.) Run the test. (More added later)")
            print("\t 2.) Clear settings Keithley 6430")
            print("\t 3.) Exit")
            if choice == 1:
                keithley_run_hardcoded(smu)
            elif choice == 2:
                smu[0].clear_instrument()
            elif choice == 3:
                sys.exit()
            else:
                print("Invalid input. Try again.")
        else:
            print("No Keithley 6430 Found:")
            print("\t 1.) Search for Keithley 6430")
            print("\t 2.) Exit")
            choice = get_input()
            if choice == 1:
                smu = RS232_Keithley24xx.discover_connected( baudrate=9600 )
            elif choice == 2:
                sys.exit()
            else:
                print("Invalid input. Try again.")
        
        

def str2lines(str):
	return [ l.strip() for l in str.split('\n') if l ]


if __name__ == '__main__':
    name = sys.argv[1:]
    comment = ''
    
    while True:
        print_menu()
        choice = get_input()
        if choice == 1:
            keithley_init_and_menu()
        elif choice == 2:
            sys.exit()
        else:
            print("Invalid input. Try again.")
    sys.exit()
