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

    plt.xlim(0,10)
    plt.ylim(0,50000)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)


    final_string = 'graphs/' + full_string + '.pdf'
    print(final_string)
    plt.savefig(final_string)
    plt.show()
    
dut = "Atmega328P-AU - All Fs"
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

TRY_SWEEP = """
*RST
:ARM:COUN 1
:ARM:SOUR IMM
:SENS:FUNC 'RES'
:SENS:RES:NPLC 1
:SENS:RES:MODE MAN
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
    

def str2lines(str):
	return [ l.strip() for l in str.split('\n') if l ]

# def initialize ():
# 	
# 	blue_sweep = L.load_default()
# 	assert len(blue_sweep) == 41, "length is not 41"
# 	blue_sweep[1] = 1		#sets spi mode
# 	blue_sweep[24] = 1		#load signal
# 	blue_sweep[25] = 1		#monitor enable signal
# 	blue_sweep[26] = 1		#precharge signal
# 	blue_sweep[27] = 0		#select strong signal
# 	blue_sweep[34] = 1		#monitor nmos of pixel
# 	blue_sweep[7]  = 0 	#monitor pmos
# 	blue_sweep[27]	=	1 #sels signal

# 	blue_sweep_payload =  u.array_of_regs_to_payload(blue_sweep)
# 	assert len(blue_sweep_payload) == 6, "length is not 6"
# 	return blue_sweep_payload


if __name__ == '__main__':
    name = sys.argv[1:]
    comment = ''
    # assert len(name),"you forgot to give it the damn name"
    # #timelog = DL.get_time()
    # if len(name) > 1:
    #     comment = '-'+name[1]
    #name = name[0]
    # runName = "tcsa1-"
    # waferNum = "w2-"
    # logname = runName+waferNum+name+ "-SNMOS-Final"
    #blue_sweep_payload = initialize()
    time.sleep(2)	
    smu = RS232_Keithley24xx.discover_connected( baudrate=9600 )
    print(smu)
    with smu[0] as source_dev:
#        sc =  Serial_Com()
        nplc = 0.02
        v_start = 0.5
        v_stop = 3
        n_pts = 100
        v_step = float( v_stop - v_start )/(n_pts-1)
        set_datetime()
        create_fullstring()
		
        print('programming SOURCE!')
        for cmd in str2lines( TRY_SWEEP.format( **locals() ) ):
            print(cmd)
            source_dev.send_cmd(str.encode(cmd))
        try:
            read_resp = source_dev.ask_cmd(":READ?")
            print("Response: " + str(read_resp))
            s = np.fromstring( read_resp, sep=',' )
            print(str(s))
            s = splitArray(3, s)
            print(s)
            plot_data(s[0], s[2], "Voltage vs. Current", "Volts", "Current")
            f = open("log.txt", "a")
            write_string = "\n" + full_string + "\n" + str(s) + "\n"
            #print(write_string)
            f.write(write_string)
            f.close()
        except:
                print("Failed to get data or something")
                
        
        
        
        source_dev.clear_instrument()
        
        #source_dev.send_cmd(str.encode(":OUTP ON"))
        #source_dev.send_cmd(str.encode(":READ?"))
        #time.sleep(5)
        #source_dev.send_cmd(str.encode(":OUTP OFF"))
# 		
# 		print 'programming METER!'
# 		for cmd in str2lines( METER_SETUP.format( **locals() ) ):
# #			print cmd
# 			meter_dev.send_cmd( cmd )		
# 			
# 		print; print
        #source_dev.set_output('ON')
        #source_dev.set_panel('OFF')
# 		meter_dev.set_output('ON')
# 		meter_dev.set_panel('OFF')

# 		Ta = time.time()
# 		
# 		Is = []
# 		Im = []
# 		Imf =[]
# 		Vm = linspace(10,10,1)
# 		x_range = 256
# 		y_range = 256
# 		xy_range =  x_range*y_range;
# 		
# 		strz = []
# 		meter_dev.set_fixed_V(10)
# 		for y in range(y_range):
# 			print("checkpoint...",y)
# 			for x in range (x_range):
# 				z = str(x)+","+str(y)
# 				strz.append(z)
# 				blue_sweep_payload[1] = x
# 				blue_sweep_payload[2] = y
# 				blue_sweep_pack = u.make_packs_payload(ins,direction,version,"00","00",blue_sweep_payload)
# 				sc.send_serial_data(blue_sweep_pack)
# 				# for v in Vm:	# repeat triggered sweep 10x real fast

# 				# meter_dev.set_fixed_V(v)
        #source_dev.flushInput()
        #source_dev.send_cmd(str.encode(":TRIG:COUN {n_pts}".format( **locals() )))
        #time.sleep(3)
        #source_dev.send_cmd(str.encode(":READ?")) # can this be pipelined??
# 				meter_dev.flushInput()
# 				meter_dev.write(':TRIG:COUN {n_pts}\rREAD?\r'.format( **locals() )) # reset trigger count and go

        #s = np.fromstring( source_dev.readline(), sep=',' )
        #print(str(s))
# 				s[s == 9.91e37] = nan
# 				Is += [s]
# 				m = np.fromstring( meter_dev.readline(), sep=',' )
# 				m[m == 9.91e37] = nan
# 				Im += [m]
# 			Imf += [Im[y*y_range-1]]
# 				
# 			
# 			
# 		Tb = time.time()
# 		
# 		secs = (Tb - Ta)/(len(Vm)*n_pts)
# 		total = (Tb - Ta)
# 		# print ('time for a single pixel',secs, 'seconds') 
# 		# print ('total time = ',total)
# 		
        #source_dev.set_output('OFF')
        #source_dev.set_panel('ON')
# 		meter_dev.set_output('OFF')
# 		meter_dev.set_panel('ON')
# 		
# #	Vs = repeat( [linspace(v_start, v_stop, n_pts)], len(Vm), 0 )
# 	Vs = linspace(v_start, v_stop, n_pts)
# 	
# 	Is = array(Is)
# 	Im = array(Im)
# 	path = "logs/"
# 	fullName = path+logname+'-'+timelog+comment
# 	np.save(fullName,Im)
# 	# xls.xlsWrite(fullName)
# 	# xls.colWrite(linspace(v_start,v_stop,n_pts),'voltage',0)
# 	# col = 1  
# 	# for i in range (xy_range):
# 	# 	xls.colWrite(Im[i],strz[i],col)
# 	# 	col+=1
# 	# xls.close
# 	Tc = time.time()
# 	allTime = (Tc-Ta)
# 	# print ('totaltime2',allTime)
# 	# np.save(logname2+timelog,Is)
# 	# print Is
# 	# print ("---------------------------------------------")
# 	Imf = Imf[1:]
# 	# print sum(isnan(Is))/float(len(Is)), '% NaNs'
# 	figure()
# 	for m in Imf:
# 		# plot(Vs, s, 'g' )
# 		plot(Vs, m, 'b' )
# 	legend()
# 	show()	
