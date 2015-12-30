"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 20115 Marshall Scholz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
#from .. import scpi
#from .. import ivi
# While not part of upstream python-ivi distribution.
import ivi
import time


MeasurementFunctionMapping = {
        'dc_volts': 'volt',
        'ac_volts': 'volt:ac',
        'dc_current': 'curr',
        'ac_current': 'curr:ac',
        'two_wire_resistance': 'res',
        'four_wire_resistance': 'fres',
        'frequency': 'freq',
        'period': 'per',
        'temperature': 'temp',
        'capacitance': 'cap',
        'continuity': 'cont',}


MeasurementRangeMapping = {
        'dc_volts': 'volt:dc:range',
        'ac_volts': 'volt:ac:range',
        'dc_current': 'curr:dc:range',
        'ac_current': 'curr:ac:range',
        'two_wire_resistance': 'res:range',
        'four_wire_resistance': 'fres:range',
        'frequency': 'freq:range:lower',
        'period': 'per:range:lower',
        'capacitance': 'cap:range'}

MeasurementAutoRangeMapping = {
        'dc_volts': 'volt:dc:range:auto',
        'ac_volts': 'volt:ac:range:auto',
        'dc_current': 'curr:dc:range:auto',
        'ac_current': 'curr:ac:range:auto',
        'two_wire_resistance': 'res:range:auto',
        'four_wire_resistance': 'fres:range:auto',
        'capacitance': 'cap:range:auto'}

MeasurementResolutionMapping = {
        'dc_volts': 'volt:dc:resolution',
        'ac_volts': 'volt:ac:resolution',
        'dc_current': 'curr:dc:resolution',
        'ac_current': 'curr:ac:resolution',
        'two_wire_resistance': 'res:resolution',
        'four_wire_resistance': 'fres:resolution'}

TriggerSourceMapping = {
        'bus': 'bus',
        'external': 'ext',
        'immediate': 'imm'}

AmplitudeUnits = set(['dBm', 'dBmV', 'dBuV', 'volt', 'watt'])
DetectorType = set(['auto_peak', 'average', 'maximum_peak', 'minimum_peak', 'sample', 'rms'])
TraceType = set(['clear_write', 'maximum_hold', 'minimum_hold', 'video_average', 'view', 'store'])
VerticalScale = set(['linear', 'logarithmic'])
AcquisitionStatus = set(['complete', 'in_progress', 'unknown'])

OutputMode = set(['function', 'arbitrary', 'sequence'])
OperationMode = set(['continuous', 'burst'])
StandardWaveform = set(['sine', 'square', 'triangle', 'ramp_up', 'ramp_down', 'dc'])
SampleClockSource = set(['internal', 'external'])
MarkerPolarity = set(['active_high', 'active_low'])
BinaryAlignment = set(['left', 'right'])
TerminalConfiguration = set(['single_ended', 'differential'])
TriggerSlope = set(['positive', 'negative', 'either'])

Scaling = set(['linear', 'logarithmic'])
ExternalCoupling = set(['ac', 'dc'])
Source = set(['internal', 'external'])
Polarity = set(['normal', 'inverse'])
Slope = set(['positive', 'negative'])
LFGeneratorWaveform = set(['sine', 'square', 'triangle', 'ramp_up', 'ramp_down'])
SweepMode = set(['none', 'frequency_sweep', 'power_sweep', 'frequency_step', 'power_step', 'list'])
TriggerSource = set(['immediate', 'external', 'software'])
IQSource = set(['digital_modulation_base', 'cdma_base', 'tdma_base', 'arb_generator', 'external'])
DigitalModulationBaseDataSource = set(['external', 'prbs', 'bit_sequence'])
DigitalModulationBasePRBSType = set(['prbs9', 'prbs11', 'prbs15', 'prbs16', 'prbs20', 'prbs21', 'prbs23'])
ClockType = set(['bit', 'symbol'])


#actual stuff

#Measurement Mode
# :MODE?
OperationMode = set(['LCR','CONT'])

EventMapping = {
                'event_enable_0': ':ESE0',
                'event_enable_1': ':ESE1',
                'event_enable_2': ':ESE2',
                'event_enable_3': ':ESE3',
                'event_status_0': ':ESR0',
                'event_status_1': ':ESR1',
                'event_status_2': ':ESR2',
                'event_status_3': ':ESR3',
                }

ParameterMapping = {
        'IMPEDANCE': 'Z',
        'ADMITTANCE': 'Y',
        'IMPEDANCE_PHASE_ANGLE': 'PHASE',
        'REACTANCE': 'X',
        'CONDUCTANCE': 'G',
        'SUBSEPTANCE': 'B',
        'LOSS_FACTOR': 'D',
        'Q_FACTOR': 'Q',
        'DC_RESISTANCE': 'RDC',
        'CONDUCTIVITY': 'S',
        'PERMITTIVITY': 'E',
        'EQUIVALENT_SERIES_RESISTANCE': 'RS',
        'EQUIVALENT_PARALELL_RESISTANCE': 'RP',
        'EQUIVALENT_SERIES_INDUCTANCE': 'LS',
        'EQUIVALENT_PARALELL_INDUCTANCE': 'LP',
        'EQUIVALENT_SERIES_CAPACITANCE': 'CS',
        'EQUIVALENT_PARALELL_CAPACITANCE': 'CP',
        'NO_PARAMETER': 'OFF',
        }

class hiokiIM3536(ivi.scpi.common.IdnCommand,
             ivi.scpi.common.ErrorQuery,
             ivi.scpi.common.Reset,
             ivi.scpi.common.SelfTest,
             ivi.Driver):
    "HIOKI IM3536 LCR Meter driver"
    
    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')
        
        super(hiokiIM3536, self).__init__(*args, **kwargs)
        
        self._identity_description = "HIOKI IM3536 LCR Meter"
        self._identity_identifier = ""
        self._identity_revision = ""
        self._identity_vendor = "hioki"
        self._identity_instrument_manufacturer = "HIOKI"
        self._identity_instrument_model = "IM3536"
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 0
        self._identity_specification_minor_version = 0
        self._identity_supported_instrument_models = ['IM3536']

        self._mode = 'lcr'
        self._measurement_frequency = 1000.0
        self._measurement_range = 4
        self._measurment_type = 'v'
        self._measurment_level_v = 1
        self._measurment_level_cv = 1
        self._measurment_level_cc = 0.01
        self._measurment_speed = 'MEDIUM'
        self._measurment_limit_en = True
        self._measurment_limit_c = 0.1
        self._measurment_limit_v = 5
        self._measurment_averaging = 'OFF'

        self._self_test_delay = 5

        self._disable = False

        self._add_property('measurement_frequency',
                        self._get_measurement_frequency,
                        self._set_measurement_frequency,
                        None,
                        ivi.Doc("""
                        Specifies the ac frequency applied to the test device
                        """))

    # FIXME: Most of the stuff in this class is wrong, blindly copied from
    # another driver.  Mostly harmless from the way we currently use it,
    # but it should be fixed eventually.

    def _initialize(self, resource = None, id_query = False, reset = False, **keywargs):
        "Opens an I/O session to the instrument."

        super(hiokiIM3536, self)._initialize(resource, id_query, reset, **keywargs)

        self._interface.term_char = '\r' #doesn't use '\n'

        # interface clear
        if not self._driver_operation_simulate:
            self._clear()

        # check ID
        if id_query and not self._driver_operation_simulate:
            id = self.identity.instrument_model
            id_check = self._instrument_id
            id_short = id[:len(id_check)]
            if id_short != id_check:
                raise Exception("Instrument ID mismatch, expecting %s, got %s", id_check, id_short)

        # reset
        if reset:
            self.utility_reset()

        #instrument automatically enters remote control state whenever we write to it
        self._write(":pres") # returns to known preset values. a "factory reset"



    def _load_id_string(self):
        if self._driver_operation_simulate:
            self._identity_instrument_manufacturer = "Not available while simulating"
            self._identity_instrument_model = "Not available while simulating"
            self._identity_instrument_firmware_revision = "Not available while simulating"
        else:
            lst = self._ask("*IDN?").split(",")
            self._identity_instrument_manufacturer = lst[0]
            self._identity_instrument_model = lst[1]
            self._identity_instrument_firmware_revision = lst[3]
            self._set_cache_valid(True, 'identity_instrument_manufacturer')
            self._set_cache_valid(True, 'identity_instrument_model')
            self._set_cache_valid(True, 'identity_instrument_firmware_revision')

    def _get_identity_instrument_manufacturer(self):
        if self._get_cache_valid():
            return self._identity_instrument_manufacturer
        self._load_id_string()
        return self._identity_instrument_manufacturer

    def _get_identity_instrument_model(self):
        if self._get_cache_valid():
            return self._identity_instrument_model
        self._load_id_string()
        return self._identity_instrument_model

    def _get_identity_instrument_firmware_revision(self):
        if self._get_cache_valid():
            return self._identity_instrument_firmware_revision
        self._load_id_string()
        return self._identity_instrument_firmware_revision

    def _utility_disable(self):
        pass

    def _utility_lock_object(self):
        pass

    def _utility_reset(self):
        if not self._driver_operation_simulate:
            self._write("*RST")
            self._clear()
            self.driver_operation.invalidate_all_attributes()

    def _utility_reset_with_defaults(self):
        self._utility_reset()

    def _utility_self_test(self):
        code = 0
        message = "Self test passed"
        if not self._driver_operation_simulate:
            # This device returns "0," on PASS
            resp = self._ask('*TST?').split(',')
            code = int(resp[0])
            if code != 0:
                message = "Self test failed"
        return (code, message)

    def _utility_unlock_object(self):
        pass

#instrument specific stuff
#actually do error checking here.

    #redundant, error checking parameter setter
    def _set_param(self, cmd, value, delay=0.0, rnd=None, timeout=10 ):
        cmddelay = delay
        timeo = timeout
        while (timeo > 0):
            cmddelay = cmddelay + 0.01 #delay gets steadily longer with each failed command.
            if (rnd == None):
                self._write(cmd + " " + value)
                time.sleep(cmddelay) #some equipment will fail to apply parameter if asked about that same parameter very short succession.
                read = origRead = self._ask(cmd + "?")[0:len(value)]
            else:
                value = round(float(value),rnd)
                self._write(cmd + " %e" % value)
                time.sleep(cmddelay)
                read = origRead = self._ask(cmd + "?")
                read = round(float(read),rnd)
            if(read == value):
                break
            timeo -= 1

        if (timeo <= 0):
            raise AssertionError("Timeout during setting of %s. expecting '%s', got '%s'" % (cmd, value, read))

        return origRead


    #Measurement Mode
    def _get_mode(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("mode?").split(' ')[1]
            self._set_cache_valid()
        return self._attenuation

    def _set_mode(self, value):
        #value can = LCR, CONT (continuous)
        if not self._driver_operation_simulate:
            self._write("mode %e" % (value))
        self._attenuation = value
        self._set_cache_valid()

    #measurement frequency
    def _get_measurement_frequency(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("freq?").split()[1]
            self._measurement_frequency = float(resp)
            self._set_cache_valid()
        return self._measurement_frequency

    def _set_measurement_frequency(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write("freq %e" % (value))
        self._attenuation = value
        self._set_cache_valid()


    #measurement range
    def _get_range(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("range?").split()[1]
            self._attenuation = float(resp)
            self._set_cache_valid()
        return self._attenuation

    def _set_range(self, value):
        value = float(value)
        if not self._driver_operation_simulate:
            self._write("range %e" % (value))
        self._attenuation = value
        self._set_cache_valid()


    #todo - finish range section

    #Measurement Signal Level
    #LEV

    #Constant current level
    #LEV:CCURR


    #Constant voltage level
    #LEV:CVOLT

    #Measurement Speed



    def _get_disable(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("disable?").split(' ')[1]
            self._disable = bool(int(resp))
            self._set_cache_valid()
        return self._disable

    def _set_disable(self, value):
        value = bool(value)
        if not self._driver_operation_simulate:
            self._write("disable %d" % (int(value)))
        self._disable = value
        self._set_cache_valid()

    def release(self):
        self._write('CONF:REM OFF')


    def find_capacitance(self, frequency, ): pass
    def find_inductance(self): pass
    def find_inductance(self): pass
    def find_resistance(self): pass
    def find_impediance(self): pass

 
