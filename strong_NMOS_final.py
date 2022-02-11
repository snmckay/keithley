from keithley24xx import RS232_Keithley24xx
from bitData import bitData
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
    global data_pop
    global cut_type
    global trans_active
    global bit_num
    global sourcing
    global sensing
    global full_datetime
    global full_string
    
    full_string = dut + ' - ' + data_pop + ' - ' + cut_type + ' - Bit ' + str(bit_num) + ' - ' + trans_active + ' - ' + sourcing + " vs. " + sensing + ' - ' + full_datetime
    full_string = full_string.replace('/', "_")
    full_string = full_string.replace(':', "-")
    full_string = full_string.replace('.', '')
    print(full_string)
    
def findRange(data):
    lowest = float(data[0])
    highest = float(data[0])
    calc_range = []
    for num in data:
        num = float(num)
        if lowest > num:
            lowest = num
        if highest < num:
            highest = num
    calc_range.append(float(lowest))
    calc_range.append(float(highest))
    return calc_range

def plot_bitAverage(bitNum, chop=False):
    global bits
    global dut
    global trans_active
    global full_datetime
    global full_string
    array_location = locateBit(bitNum)
    curr_data = 0
    bitData = bits[array_location].getAverages()
    xRange = findRange(bitData[0])
    yRange = findRange(bitData[1])
    
    #print("Data for bit " + str(bitNum) + ": " + str(bits[array_location].x_data) + "/" + str(bits[array_location].y_data))
    plt.scatter(bitData[0], bitData[1])
        
    #print("Limits: " + str(xRange) + "/" + str(yRange))
    plt.xlim(int(xRange[0]), int(xRange[1]))
    plt.ylim(int(yRange[0]), float(yRange[1]))

    plt.title("Bit " + str(bitNum) + " Average Data Plot")
    plt.xlabel("Voltage")
    plt.ylabel("Resistance")

    print("Made Plot")
    if chop:
        final_string = 'graphs/Average_Bit_' + str(bitNum) + '_chopped.jpg'
    else:
        final_string = 'graphs/Average_Bit_' + str(bitNum) + '.jpg'
    print(final_string)
    print("Saving")
    plt.savefig(final_string)
    print("Saved")
    plt.show()
    print("Shown")
    return

def plot_bitAverageCombined(chop=False):
    global bits
    global dut
    global trans_active
    global full_datetime
    global full_string
    xRange = [0, 0]
    yRange = [0, 0]
    
    for bit in bits:
        tempData = bit.getAverages()
        
        plt.scatter(tempData[0], tempData[1], label = ("Bit " + str(bit.bitNum)))
        
        tempXRange = findRange(tempData[0])
        tempYRange = findRange(tempData[1])
        if (float(tempXRange[1]) > 0):
            if float(xRange[1]) < float(tempXRange[1]):
                xRange[1] = float(tempXRange[1])
        if (float(tempYRange[1]) > 0):
            if float(yRange[1]) < float(tempYRange[1]):
                yRange[1] = float(tempYRange[1])
        if (float(tempYRange[0]) > 0):
            if float(yRange[0]) > float(tempYRange[0]):
                yRange[0] = float(tempYRange[0])
        
        
    #print("Limits: " + str(xRange) + "/" + str(yRange))
    plt.xlim(int(xRange[0]), int(xRange[1]))
    #plt.ylim(int(yRange[0]), float(yRange[1]))
    plt.ylim(int(yRange[0]), 2E-6)
    plt.legend()

    plt.title("Average Bits Data Plot")
    plt.xlabel("Voltage")
    plt.ylabel("Resistance")

    print("Made Plot")
    if chop:
        final_string = 'graphs/Averages_chopped.jpg'
    else:
        final_string = 'graphs/Averages.jpg'
    print(final_string)
    print("Saving")
    plt.savefig(final_string)
    print("Saved")
    plt.show()
    print("Shown")
    return

def plot_bitData(bitNum, chop=False):
    global bits
    global dut
    global trans_active
    global full_datetime
    global full_string
    array_location = locateBit(bitNum)
    curr_data = 0
    xRange = [0, 0]
    yRange = [0, 0]
    
    #print("Data for bit " + str(bitNum) + ": " + str(bits[array_location].x_data) + "/" + str(bits[array_location].y_data))
    
    for xData in (bits[array_location]).getXData():
        yData = (bits[array_location].getYData())[curr_data]
        curr_data = curr_data + 1
        print(str(len(xData)), str(len(yData)))
        if ((len(xData) > 5) and (len(xData) == len(yData))):
            #print("Bit/Array " + str(bitNum) + "/" + str(curr_data) + "\n")
            print("In the function", str(xData), str(yData))
            plt.scatter(xData, yData)
            
            tempXRange = findRange(xData)
            tempYRange = findRange(yData)
            print("Y Range: " + str(tempYRange))
            if (float(tempXRange[1]) > 0):
                if float(xRange[1]) < float(tempXRange[1]):
                    xRange[1] = float(tempXRange[1])
            if (float(tempYRange[1]) > 0):
                if float(yRange[1]) < float(tempYRange[1]):
                    yRange[1] = float(tempYRange[1])
            if (float(tempYRange[0]) > 0):
                if float(yRange[0]) > float(tempYRange[0]):
                    yRange[0] = float(tempYRange[0])
    #print("Limits: " + str(xRange) + "/" + str(yRange))
    print("Final Y Range: " + str(yRange))
    plt.xlim(int(xRange[0]), int(xRange[1]))
    plt.ylim(int(yRange[0]), float(yRange[1]))

    plt.title("Bit " + str(bitNum) + " Data Plot")
    plt.xlabel("Voltage")
    plt.ylabel("Current")

    print("Made Plot")
    if chop:
        final_string = 'graphs/Combined_Bit_' + str(bitNum) + '_chopped.jpg'
    else:
        final_string = 'graphs/Combined_Bit_' + str(bitNum) + '.jpg'
    print(final_string)
    print("Saving")
    plt.savefig(final_string)
    print("Saved")
    plt.show()
    print("Shown")
    return
    

def plot_data(dataIn, dataCount, title, xlabel, ylabel):
    #X = [590,540,740,130,810,300,320,230,470,620,770,250]
    #Y = [32,36,39,52,61,72,77,75,68,57,48,48]
    print("XData: " + str(dataIn[0]))
    print("YData: " + str(dataIn[1]))

    global dut
    global trans_active
    global full_datetime
    global full_string
    if dataCount == 2:
        plt.scatter(dataIn[0],dataIn[1])
    
        xRange = findRange(dataIn[0])
        yRange = findRange(dataIn[1])
        plt.xlim(xRange[0], xRange[1])
        plt.ylim(yRange[0], yRange[1])
    
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
    
        print("Made Plot")
        final_string = 'graphs/' + full_string + '.jpg'
        print(final_string)
        print("Saving")
        plt.savefig(final_string)
        print("Saved")
        plt.show()
        print("Shown")
        return
    elif dataCount == 3:
        plt.scatter(dataIn[0],dataIn[1])
        plt.scatter(dataIn[0],dataIn[2])
    
        xRange = findRange(dataIn[0])
        yRange1 = findRange(dataIn[1])
        yRange2 = findRange(dataIn[2])
        
        if yRange1[0] > yRange2[0]:
            yRange1[0] = yRange2[0]
        if yRange1[1] < yRange2[1]:
            yRange1[1] = yRange2[1]
        plt.xlim(xRange[0], xRange[1])
        plt.ylim(yRange1[0], yRange1[1])
    
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
    
        print("Made Plot")
        final_string = 'graphs/' + full_string + 'CombinedResAndCurr.jpg'
        print(final_string)
        print("Saving")
        plt.savefig(final_string)
        print("Saved")
        plt.show()
        print("Shown")
        return

meter = "Keithley 6430"    
dut = "Atmega328P-AU"
data_pop = "All Cs"
cut_type = "Rectangle Cut"
trans_active = "Not Active"
bit_num = 0
sourcing = "Voltage_Volts"        #This DOES NOT change the keithley settings. Just for document naming
sensing = "Resistance_Ohms"    #This DOES NOT change the keithley settings. Just for document naming
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
:SENS:FUNC 'CURR:DC'
:SENS:CURR:RANG:AUTO ON
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
:FORM:ELEM VOLT, CURR"""

TRY_SWEEP_RES = """
*RST
:SYST:AZER ON
:ARM:COUN 1
:ARM:SOUR IMM
:SENS:FUNC \"RES\"
:SENS:RES:RANG:AUTO ON
:SOUR:FUNC CURR
:SOUR:CURR 1E-6
:SOUR:CLE:AUTO ON
:SOUR:DEL:AUTO ON
:TRIG:COUN {n_pts}
:FORM:ELEM VOLT, CURR"""

CONST_VOLT_MEAS_BOTH = """
*RST
:SYST:AZER ON
:ARM:COUN 1
:ARM:SOUR IMM
:SENS:FUNC 'CURR:DC'
:SENS:CURR:RANG:AUTO ON
:SOUR:FUNC VOLT
:SOUR:VOLT:MODE FIXED
:SOUR:VOLT:RANG 5
:SOUR:VOLT:LEV 2
:SOUR:CLE:AUTO ON
:SOUR:DEL:AUTO ON
:TRIG:COUN {n_pts}
:FORM:ELEM VOLT, CURR"""

TRY_SWEEP_BOTH = """
*RST
:SYST:AZER ON
:ARM:COUN 1
:ARM:SOUR IMM
:SENS:FUNC 'RES'
:SENS:RES:RANG:AUTO ON
:SOUR:FUNC VOLT
:SOUR:VOLT:STAR {v_start}
:SOUR:VOLT:STOP {v_stop}
:SOUR:VOLT:STEP {v_step}
:SOUR:VOLT:MODE SWE
:SOUR:CLE:AUTO ON
:SOUR:SWEEP:SPAC LIN
:SOUR:DEL:AUTO ON
:TRIG:COUN {n_pts}
:FORM:ELEM VOLT, RES, CURR"""

MEASURE_CURR_6485 = """
*RST
:CONF:CURR
:RANG:AUTO ON
"""

TRY_SWEEP = """
*RST
:SYST:AZER ON
:ARM:COUN 1
:ARM:SOUR IMM
:SENS:FUNC 'RES'
:SENS:RES:RANG:AUTO ON
:SOUR:FUNC VOLT
:SOUR:VOLT:STAR {v_start}
:SOUR:VOLT:STOP {v_stop}
:SOUR:VOLT:STEP {v_step}
:SOUR:VOLT:MODE SWE
:SOUR:CLE:AUTO ON
:SOUR:SWEEP:SPAC LIN
:SOUR:DEL:AUTO ON
:TRIG:COUN {n_pts}
:FORM:ELEM VOLT, RES"""

TRY_SWEEP_CURR = """
*RST
:SYST:AZER ON
:ARM:COUN 1
:ARM:SOUR IMM
:SENS:FUNC 'CURR:DC'
:SENS:CURR:RANG:AUTO ON
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
:FORM:ELEM VOLT, CURR"""

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
:SENS:CURR:PROT 0.0001
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

bits = []
		
def bitExists(numBit):
    global bits
    for bit in bits:
        if bit.bitNum == numBit:
            return True
    return False

def locateBit(numBit):
    global bits
    bitNum = -1
    for bit in bits:
        bitNum = bitNum + 1
        if bit.bitNum == numBit:
            return bitNum
    return -1

def readFromLogFile(chop=False):
    global bits
    with open('log.txt', 'r') as file:
        myline = file.readline()
        curr_bit = -1
        while myline:
            curr_arrayX = []
            curr_arrayY = []
            #print("CURR_BIT: " + str(curr_bit))
            myline = myline.strip('\n')
            if len(myline) > 0:
                #print(myline)
                if myline[0] == '[':
                    counter = 1
                    end = -1
                    while myline[counter] == '[':
                        counter = counter + 1
                    end = counter
                    while myline[end] != ']':
                        end = end + 1
                    curr_arrayX = myline[counter:end]
                    curr_arrayX = curr_arrayX.split(',')
                    curr_arrayX = np.array(curr_arrayX)
                    curr_arrayX = curr_arrayX.astype(np.float_)
                    print("CurrArrayX: " + str(curr_arrayX) + "\n")
                    curr_bit_loc = locateBit(curr_bit)
                    
                    
                    while myline[end] != '[':
                        end = end + 1
                    counter = end + 1
                    end = counter
                    while myline[end] != ']':
                        end = end + 1
                    curr_arrayY = myline[counter:end]
                    curr_arrayY = curr_arrayY.split(',')
                    curr_arrayY = np.array(curr_arrayY)
                    curr_arrayY = curr_arrayY.astype(np.float_)
                    print("Curr_ArrayY: " + str(curr_arrayY) + "\n")
                    
                    #print("Curr Bit Location: " + str(curr_bit_loc))
                    #print(str(curr_array))
                    if(chop):
                        low_pos = np.where(curr_arrayY > 0, curr_arrayY, np.inf).argmin()
                        curr_arrayY = curr_arrayY[low_pos:end]
                        curr_arrayX = curr_arrayX[low_pos:end]
                    (bits[curr_bit_loc]).appendYData(array(curr_arrayY))
                    (bits[curr_bit_loc]).appendXData(array(curr_arrayX))
                    #print("Bit " + str(curr_bit) + " lengths: " + str((bits[curr_bit_loc]).x_data) + "/" + str((bits[curr_bit_loc]).y_data))
                else:
                    pos = myline.find("Bit")
                    print(myline[pos+4])
                    curr_bit = int(myline[pos+4])
                    if not bitExists(curr_bit):
                        #print("Added")
                        bits.append(bitData(curr_bit))
            myline = file.readline()
    #print(str(bits))
    for bit in bits:
        print(str(len(bit.x_data)))
        plot_bitData(bit.bitNum, chop)
        plot_bitAverage(bit.bitNum, chop)
    plot_bitAverageCombined(chop)

def readFromSettingsFile():
    global meter
    global dut
    global data_pop
    global cut_type
    global trans_active
    global bit_num
    global sourcing
    global sensing
    
    with open('settings.txt', 'r') as file:
        meter = (file.readline()).strip('\n')
        dut = (file.readline()).strip('\n')
        data_pop = (file.readline()).strip('\n')
        cut_type = (file.readline()).strip('\n')
        bit_num = int((file.readline()).strip('\n'))
        trans_active = (file.readline()).strip('\n')
        sourcing = (file.readline()).strip('\n')
        sensing = (file.readline()).strip('\n')

def updateSettingsFile():
    global meter
    global dut
    global data_pop
    global cut_type
    global trans_active
    global bit_num
    global sourcing
    global sensing
    with open('settings.txt', 'w') as file:
        file.write(meter + '\n')
        file.write(dut + '\n')
        file.write(data_pop + '\n')
        file.write(cut_type + '\n')
        file.write(str(bit_num) + '\n')
        file.write(trans_active + '\n')
        file.write(sourcing + '\n')
        file.write(sensing + '\n')
        
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
    print("\t 2.) Change Strings")
    print("\t 3.) Graph Log File")
    print("\t 4.) Graph Log File - Chopped")
    print("\t 5.) Exit")
    
def get_input():
    global selected
    selected = input("Please type the number for your chosen option: ")
    while not selected.isnumeric():
        selected = input("Please type the number for your chosen option: ")
    return int(selected)

def keithley_run_hardcoded_current(dev):
    global sourcing
    global sensing
    global full_string
    with dev[0] as source_dev:
#        sc =  Serial_Com()
        nplc = 0.02
        v_start = .4
        v_stop = 2
        n_pts = 100
        v_step = float( v_stop - v_start )/(n_pts-1)
        set_datetime()
        create_fullstring()
		
        print('programming SOURCE!')
        for cmd in str2lines( TRY_SWEEP_CURR.format( **locals() ) ):
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
            source_split = sourcing.split('_')
            sense_split = sensing.split('_')
            title = "Bit " + str(bit_num) + " Voltage vs.Current"
            plot_data(s, 2, title, "Volts", "Amps")
            print("Trying to open")
            f = open("log_curr.txt", "a")
            print("opened")
            write_string = "\n" + full_string + "\n" + str(s) + "\n"
            #print(write_string)
            f.write(write_string)
            f.close()
        except:
                print("Failed to get data or something")
                
        source_dev.clear_instrument()

def keithley_run_hardcoded(dev):
    global sourcing
    global sensing
    global full_string
    with dev[0] as source_dev:
#        sc =  Serial_Com()
        nplc = 0.02
        v_start = .5
        v_stop = 3
        n_pts = 100
        v_step = float( v_stop - v_start )/(n_pts-1)
        set_datetime()
        create_fullstring()
		
        print('programming SOURCE!')
        for cmd in str2lines( TRY_SWEEP3.format( **locals() ) ):
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
            source_split = sourcing.split('_')
            sense_split = sensing.split('_')
            title = "Bit " + str(bit_num) + " " + source_split[0] + " vs. " + sense_split[0]
            plot_data(s, 2, title, source_split[1], sense_split[1])
            print("Trying to open")
            f = open("log.txt", "a")
            print("opened")
            write_string = "\n" + full_string + "\n" + str(s) + "\n"
            #print(write_string)
            f.write(write_string)
            f.close()
        except:
                print("Failed to get data or something")
                
        source_dev.clear_instrument()
        
def keithley_6485_run_hardcoded(dev):
    global sourcing
    global sensing
    global full_string
    read_resp = ""
    with dev as source_dev:
        set_datetime()
        create_fullstring()
		
        print('programming SENSE!')
        for cmd in str2lines( MEASURE_CURR_6485.format( **locals() ) ):
            print(cmd)
            source_dev.send_cmd(str.encode(cmd))
        try:
            print("Reading Now")
            time.sleep(1)
            read_resp = source_dev.ask_cmd(":READ?")
            print("Response: " + str(read_resp))
            #s = np.fromstring( read_resp, sep=',' )
            #print(str(s))
            #print("Splitting Array")
            #s = splitArray(2, s)
            #print(s)
            #print("Trying to plot")
            #source_split = sourcing.split('_')
            #sense_split = sensing.split('_')
            #title = "Bit " + str(bit_num) + " " + source_split[0] + " vs. " + sense_split[0]
            #plot_data(s, 2, title, source_split[1], sense_split[1])
            #print("Trying to open")
            #f = open("log.txt", "a")
            #print("opened")
            #write_string = "\n" + full_string + "\n" + str(s) + "\n"
            #print(write_string)
            #f.write(write_string)
            #f.close()
        except:
                print("Failed to get data or something")
                
        source_dev.clear_instrument()
        return read_resp
        
def keithley_run_hardcoded_both(dev):
    global sourcing
    global sensing
    global full_string
    with dev[0] as source_dev:
#        sc =  Serial_Com()
        nplc = 0.02
        v_start = .5
        v_stop = 3
        n_pts = 10
        v_step = float( v_stop - v_start )/(n_pts-1)
        set_datetime()
        create_fullstring()
		
        print('programming SOURCE!')
        for cmd in str2lines( CONST_VOLT_MEAS_BOTH.format( **locals() ) ):
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
            source_split = sourcing.split('_')
            sense_split = sensing.split('_')
            title = "Bit " + str(bit_num) + " " + source_split[0] + sense_split[0]
            plot_data(s, 2, title, source_split[1], sense_split[1])
            print("Trying to open")
            f = open("log.txt", "a")
            print("opened")
            write_string = "\n" + full_string + "\n" + str(s) + "\n"
            #print(write_string)
            f.write(write_string)
            f.close()
        except:
                print("Failed to get data or something")
                
        source_dev.clear_instrument()

def changeStrings():
    global meter
    global dut
    global data_pop
    global cut_type
    global trans_active
    global bit_num
    global sourcing
    global sensing
    
    while True:
        print("Current strings to modify: ")
        print("1.) Meter: "             + meter)
        print("2.) DUT: "               + dut)
        print("3.) Populated Data: "    + data_pop)
        print("4.) Cut Type: "          + cut_type)
        print("5.) Bit Number: "        + str(bit_num))
        print("6.) Transistor Active: " + trans_active)
        print("7.) Sourcing: "          + sourcing)
        print("8.) Sensing: "           + sensing)
        print("9.) Exit (Modifications complete)")
        choice = get_input()
        if choice == 1:
            meter = input("Enter Meter Model: ")
        elif choice == 2:
            dut = input("Enter chip model: ")
        elif choice == 3:
            data_pop = input("Enter data populated on the chip: ")
        elif choice == 4:
            cut_type = input("Enter the cut type: ")
        elif choice == 5:
            bit_num = int(input("Enter bit line number being probed currently: "))
        elif choice == 6:
            trans_active = input("Transistor is (Active/Inactive)? ")
        elif choice == 7:
            sourcing = input("What is the Keithley sourcing? ")
        elif choice == 8:
            sensing = input("What is the Keithley sensing? ")
        elif choice == 9:
            source_split = sourcing.split('_')
            sense_split = sensing.split('_')
            title = source_split[0] + " vs. " + sense_split[0]
            print(title)
            updateSettingsFile()
            return
        else:
            print("Invalid selection. Try again.")
            
def check_SMU_for(smu, model):
    for device in smu:
        if model in str(device.clear_device()):
            return True
    return False

def keithley_init_and_menu():
    choice = -1
    found_6430 = False
    found_6485 = False
    smu = RS232_Keithley24xx.discover_connected( baudrate=9600 )
    print(smu)
    print(len(smu))
    deviceInfo = smu[0].clear_instrument()
    print("Device Info: " + str(deviceInfo))
    
    #Check for devices using the new function
    if not(b'6430' in deviceInfo):
        if len(smu) == 1:
            smu.append(smu[0])
            found_6485 = True
        elif len(smu) == 2:
            found_6430 = True
            found_6485 = True
            smu.append(smu[0])
            smu[0] = smu[1]
            smu[1] = smu[2]
            smu.remove(smu[2])
        else:
            print("List of SMU devices too long. Exiting.")
            sys.exit()
    else:
        print("6430 found")
            
    
    while True:
        if len(smu) > 0:
            print("Keithley 6430 Options:")
            print("\t 1.) Run the hard-coded test. (More added later)")
            print("\t 2.) Clear settings Keithley 6430")
            print("\t 3.) Change Strings")
            print("\t 4.) Exit")
            print("\t 5.) Run the hard-coded test (CURRENT). (More added later)")  
            print("\t 6.) Run the hard-coded test (BOTH). (More added later)")
            print("\t 7.) Run the hard-coded 6485 Current measurement. (More added later)")
            choice = get_input()
            if choice == 1:
                keithley_run_hardcoded(smu)
            elif choice == 2:
                smu[0].clear_instrument()
            elif choice == 3:
                changeStrings()
            elif choice == 4:
                sys.exit()
            elif choice == 5:
                keithley_run_hardcoded_current(smu)
            elif choice == 6:
                keithley_run_hardcoded_both(smu)
            elif choice == 7:
                keithley_6485_run_hardcoded(smu[1])
            else:
                print("Invalid input. Try again.")
        else:
            print("No Keithley 6430 Found:")
            print("\t 1.) Search for Keithley 6430")
            print("\t 2.) Change Strings")
            print("\t 3.) Exit")
            choice = get_input()
            if choice == 1:
                smu = RS232_Keithley24xx.discover_connected( baudrate=9600 )
            elif choice == 2:
                changeStrings()
            elif choice == 3:
                sys.exit()
            else:
                print("Invalid input. Try again.")
        
        

def str2lines(str):
	return [ l.strip() for l in str.split('\n') if l ]


if __name__ == '__main__':
    name = sys.argv[1:]
    comment = ''
    readFromSettingsFile()
    while True:
        set_datetime()
        create_fullstring()
        print_menu()
        choice = get_input()
        if choice == 1:
            keithley_init_and_menu()
        elif choice == 2:
            changeStrings()
        elif choice == 3:
            readFromLogFile()
        elif choice == 4:
            readFromLogFile(True)
        elif choice == 5:
            sys.exit()
        else:
            print("Invalid input. Try again.")
    sys.exit()
