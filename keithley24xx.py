import sys
import serial
from pprint import pprint, pformat
from time import sleep
import binascii

#def readline(port):

def removeXONXOFF( instr ):
	print(binascii.hexlify(instr))
	r = instr.replace('\x13\x11', '')
	print(binascii.hexlify(r))
	return r

def ensure_ON_OFF( s ):
	s = s.strip().upper()
	assert s in ["ON", "OFF"]
	return s
	
class RS232_Keithley24xx(serial.Serial):
    @classmethod
    def discover_connected(klass, startPort=1, endPort=40, **portsetup):
        portsettings = portsetup.copy()
        portsettings['timeout'] = 0.5
        found = []
        for port in range(startPort, endPort+1):
            try:
                possible = RS232_Keithley24xx('COM'+str(port), **portsettings)
                possible.clear_instrument()
                found += [possible]
            except (serial.serialutil.SerialException, AssertionError): 
                pass
        return found
		
    def readline(self, size=None):
        line = bytearray()
        while True:
            c = self.read(1)
            if not c or c == '\r' or (size and len(line) >= size):
                break
            if c not in ['\x11', '\x13', '\x0a']:
                line += c
        if not line:
            print('timeout!')
		# print line
        return bytes(line)


    def ask_cmd( self, cmdstr ):
        self.flushInput()
        self.write(str.encode(cmdstr + "\r"))
#		self.flush()
        resp = self.readline()
#		print len(resp), binascii.hexlify(resp)
        assert len(resp), str(cmdstr) + " RESPONSE ERROR: [" + str(binascii.hexlify(resp)) + "]"
        return resp


    def get_errs( self ):
        errs = []
        while True:	
            emsg = self.ask_cmd(":STAT:QUE?")
            emsg = str(emsg)
            if emsg.split(',')[0] == '0':
                break
            errs += [emsg]
        return errs

    def wait_until_cmd_done(self):
        while True:
            self.write("*OPC?\r")
            while True:
                resp = self.readline()
                if len(resp) != 0:
                    break
                print('.',)
            if resp[0] == '1':
                return
            sleep(0.2)
            print('~')

    def send_cmd(self, cmdstr):
		#		print( cmdstr )
        self.write(str.encode("*CLS\r"))
        self.write(str.encode(cmdstr + '\r'))
        self.flush()
        sleep(0.02)
        errs = self.get_errs()
        assert not errs, cmdstr + " HAD ERRORS!\n" + pformat(errs)

    def run_cmd(self, cmdstr):
        self.send_cmd(cmdstr)
        self.wait_until_cmd_done()

    def device_info(self):
        self.run_cmd("*CLS")
        idstr = self.ask_cmd("*IDN?")
        print(self.port, "is", idstr)
        return (x.strip() for x in idstr.split(',')[:4])

    def clear_instrument(self):
        self.flushInput()
        self.write(str.encode('\x03\r'))  # control-c clears any half-sent commands
        self.flush()
        self.readline()		# it responds with "\x13DCL\x11\r\n" for some reason

        self.run_cmd("*RST")  # Reset instrument to default parameters.
        manufacturer, model, serialnum, fw_rev = self.device_info()

        assert 'MODEL 24' in model

    def read_ohms(self):
        self.clear_instrument()

#		run_cmd( self. ":FORM:SREG HEX" )
        self.run_cmd(":SENS:FUNC 'RES'")  # Select ohms measurement function.
        self.run_cmd(":SENS:RES:NPLC 1")  # Set measurement speed to 1 PLC.
        self.run_cmd(":SENS:RES:MODE MAN")  # Select manual ohms mode.
        self.run_cmd(":SOUR:FUNC CURR")  # Select current source function.
        self.run_cmd(":SOUR:CURR 0.01")  # Set source to output 10mA.
        self.run_cmd(":SOUR:CLE:AUTO ON")  # Enable source auto output-off.
        self.run_cmd(":SENS:VOLT:PROT 10")  # Set 10V compliance limit.
        self.run_cmd(":TRIG:COUN 1")  # Set to perform one measurement.
        self.run_cmd(":FORM:ELEM RES")  # Set to output ohms reading to PC.

    def setup_voltage_sweep(self, start, stop, n_pts, rsense=None):
		#		self.run_cmd( ":TRAC:POIN MAX")
		#		self.run_cmd( ":TRAC:FEED SENS")
        self.run_cmd(":SENS:FUNC:CONC OFF")
        self.run_cmd(":SOUR:FUNC VOLT")
        self.run_cmd(":SENS:FUNC 'CURR:DC'")
        self.run_cmd(":SENS:CURR:PROT 1.0")
#		self.run_cmd( ":SOUR:CLE:AUTO ON")
        self.run_cmd(":SOUR:VOLT:STAR %f" % start)
        self.run_cmd(":SOUR:VOLT:STOP %f" % stop)
        self.run_cmd(":SOUR:VOLT:STEP %f" % (float(stop-start)/(n_pts-1)))
        self.run_cmd(":SOUR:VOLT:MODE SWE")
        self.run_cmd(":FORM:ELEM CURR")
        self.run_cmd(":SOUR:SWEEP:RANG BEST")
        self.run_cmd(":SOUR:SWEEP:SPAC LIN")
	#:SOUR:SWE:POIN <n>
        if rsense is not None:
            self.run_cmd(":SYST:RSEN " + ("ON" if rsense else "OFF"))
        self.run_cmd(":SOUR:SWEEP:DIRECTION UP")
        self.run_cmd(":TRIG:COUN %d" % n_pts)
        self.run_cmd(":SOUR:DEL 0.001")

    def set_data_fields(self, *itemlist):
        x = ', '.join([a.upper() for a in itemlist])
        self.run_cmd(":FORM:ELEM " + x)

    def set_output(self, state):
        state = ensure_ON_OFF(state)
        self.run_cmd(":OUTP " + state)

    def set_panel(self, state):
        state = ensure_ON_OFF(state)
        self.run_cmd(":DISP:ENAB " + state)

    def initiate(self):
        self.write(":INIT\r")

    def fetch_results(self):
        #		self.write("*OPC?")
		#		self.wait_until_cmd_done()
		#		self.run_cmd( ":OUTP OFF")
        tmp_timeout = self.timeout
        self.timeout = 1.0
        result = self.ask_cmd("FETC?")
        self.timeout = tmp_timeout
        return result

    def setup_fixed_V_measure_I(self, limit_I=1.0):
        self.run_cmd(":SOUR:FUNC VOLT")
        self.run_cmd(":SENS:FUNC 'CURR:DC'")
        self.run_cmd(":SENS:CURR:PROT %f" % limit_I)
        self.run_cmd(":SOUR:VOLT:MODE FIXED")

    def setup_fixed_I_measure_V(self, limit_V=5.0):
        self.run_cmd(":SOUR:FUNC CURR")
        self.run_cmd(":SENS:FUNC 'VOLT:DC'")
        self.run_cmd(":SENS:VOLT:PROT %f" % limit_V)
        self.run_cmd(":SOUR:CURR:MODE FIXED")

    def set_fixed_V(self, V):
        self.run_cmd(":SOUR:VOLT:LEV:IMM %f" % V)

    def set_fixed_I(self, I):
        self.run_cmd(":SOUR:CURR:LEV:IMM %f" % I)

    def set_sense_current_range(self, imax=None):
        if not imax:
            self.run_cmd(":SENS:CURR:RANG:AUTO ON")
        else:
            self.run_cmd(":SENS:CURR:RANG:AUTO OFF")
            self.run_cmd(":SENS:CURR:RANG:UPP % f" % imax)

    def set_sense_voltage_range(self, vmax=None):
        if not vmax:
            self.run_cmd(":SENS:VOLT:RANG:AUTO ON")
        else:
            self.run_cmd(":SENS:VOLT:RANG:AUTO OFF")
            self.run_cmd(":SENS:VOLT:RANG:UPP % f" % vmax)

    def set_measurement_integration(self, n_line_cycles):
        self.send_cmd(':SENS:CURR:DC:NPLC %f' % n_line_cycles)

    def measure(self):
        return self.ask_cmd(":READ?")
