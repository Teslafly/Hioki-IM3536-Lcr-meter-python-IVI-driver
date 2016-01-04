"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2015 Marshall Scholz

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



AmplitudeUnits = set(['dBm', 'dBmV', 'dBuV', 'volt', 'watt'])
DetectorType = set(['auto_peak', 'average', 'maximum_peak', 'minimum_peak', 'sample', 'rms'])
TraceType = set(['clear_write', 'maximum_hold', 'minimum_hold', 'video_average', 'view', 'store'])
VerticalScale = set(['linear', 'logarithmic'])
AcquisitionStatus = set(['complete', 'in_progress', 'unknown'])

#actual stuff

#Measurement Mode
# :MODE?
OnOff = set(['ON','OFF'])
OperationMode = set(['LCR','CONT'])
#Measurement Range/s
MeasurementSignalMode = set(['V','CV', 'CC'])
AquireSpeed = set(['FAST','MED', 'SLOW', 'SLOW2']) # convert to dict
TriggerSourceMapping = {
        'external': 'ext',
        'immediate': 'imm'}
ComparatorBinMode = set(['','']) #ABSolute/PERcent/DEViation
OpenCircuitCompensationReturn = set(['OFF','All','SPOT'])
BeepJudgement = set(['OFF','IN','NG'])
Beeptone = set(['A','B','C','D'])



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
        'EQUIVALENT_PARALLEL_RESISTANCE': 'RP',
        'EQUIVALENT_SERIES_INDUCTANCE': 'LS',
        'EQUIVALENT_PARALLEL_INDUCTANCE': 'LP',
        'EQUIVALENT_SERIES_CAPACITANCE': 'CS',
        'EQUIVALENT_PARALLEL_CAPACITANCE': 'CP',
        'NO_PARAMETER': 'OFF',
        }


ParameterBitMapping = {
        # for :MEASure:ITEM commands
        # param : [bitNum, regNum]
        # reg0
        'IMPEDANCE':[0,0],
        'ADMITTANCE':[1,0],
        'IMPEDANCE_PHASE_ANGLE':[2,0],
        'EQUIVALENT_SERIES_CAPACITANCE':[3,0],
        'EQUIVALENT_PARALLEL_CAPACITANCE':[4,0],
        'LOSS_FACTOR':[5,0],
        'EQUIVALENT_SERIES_INDUCTANCE':[6,0],
        'EQUIVALENT_PARALLEL_INDUCTANCE':[7,0],
        # reg1
        'Q_FACTOR': [0,1],
        'EQUIVALENT_SERIES_RESISTANCE': [1,1],
        'EQUIVALENT_PARALLEL_RESISTANCE': [3,1],
        'CONDUCTANCE': [2,1],
        'REACTANCE': [4,1],
        'SUBSEPTANCE': [5,1],
        'DC_RESISTANCE': [6,1],
        # reg2
        'CONDUCTIVITY': [0,2],
        'PERMITTIVITY': [1,2],
        }

# ESR0_BitMapping = {
#     'eng of compensation data':0, #CEM
#     'end of measurement':1, #EOM
#     'data incorperation end bit':2,#IDX
#     'inpedance underflow':3, # MUF
#     'impedance overflow':4, #MOF
#     'limit oerflow':5, #LOF
#     "CC and CV overflow":6, #COF
#     'non gaurenteed accuracy bit':7, #REF
# }
#
# #todo - only return measurement when EOM bit is set

RangeMapping = {
    #range : rangeNum
    '0.100_ohm':1,
    '1_ohm':2,
    '10_ohm':3,
    '100_ohm':4,
    '1k_ohm':5,
    '10k_ohm':6,
    '100k_ohm':7,
    '1M_ohm':8,
    '10M_ohm':9,
    '100M_ohm':10,
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

        self._minimum_meas_frequency = 4.0  #4 Hz
        self._maximum_meas_frequency = 8000000.0 # 8 MHz

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

        self._rdc_mode_enabled = False

        self._self_test_delay = 5

        self._disable = False

        self._add_property('measurement_frequency',
                        self._get_measurement_frequency,
                        self._set_measurement_frequency,
                        None,
                        ivi.Doc("""
                        Specifies the ac frequency applied to the test device
                        """))

        #make bitsorted list of above dict keys
        self.sortedParameterBitMappingKeys = \
            self._generate_sorted_param_map_keys(ParameterBitMapping)



    # FIXME: Most of the stuff in this class is wrong, blindly copied from
    # another driver.  Mostly harmless from the way we currently use it,
    # but it should bematpl fixed eventually.

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
            self._utility_reset()
            self.write(':PRES') # presets for initialising instrument. actually needed?

        #instrument automatically enters remote control state whenever we write to it
        #self._write(":pres") # returns to known preset values. a "factory reset"


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


    def _utility_unlock_object(self):
        pass


    def _utility_reset(self):
        if not self._driver_operation_simulate:
            self._write("*RST")
            self._clear()
            self.driver_operation.invalidate_all_attributes()


    def _utility_Initialize(self):
        if not self._driver_operation_simulate:
            self._write(":PRES")
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


    def _wait_sampling_finished(self):
        #blocks until lcr finished current command
        #self._write('*TRG') #for external trigger only. we don't support that right now
        resp = int(self._ask('*opc?').split()[0])
        #print(resp)
        return

    def _wait_cmd_processing_finished(self):
        #blocks until lcr finished current command
        resp = int(self._ask('*opc?').split()[0])
        #print(resp)
        return

    #Measurement Mode
    def _get_mode(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("MODE?").split(' ')[0]
            self._set_cache_valid()
            self._mode = resp
        return self._mode


    def _set_mode(self, value):
        #value can = LCR, CONT (continuous)
        if value not in OperationMode:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write("MODE %e" % (value))
        self._mode = value
        self._set_cache_valid()


    #measurement frequency
    def _get_measurement_frequency(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("FREQ?").split()[0]
            self._measurement_frequency = float(resp)
            self._set_cache_valid()
        return self._measurement_frequency


    def _set_measurement_frequency(self, value):
        value = float(value)
        if not self._minimum_meas_frequency <= value <= self._maximum_meas_frequency:
            raise ivi.InvalidOptionValueException()
        if not self._driver_operation_simulate:
            self._write("FREQ %e" % (value))
        self._measurement_frequency = value
        self._set_cache_valid()


    #measurement range
    def _get_range(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask(":RANGE?").split()[0]
            #self.range = float(resp)
            #self._set_cache_valid()
        return resp

    def _set_range(self, value):
        #value = float(value)
        if not self._driver_operation_simulate:
            self._write(":RANGE %e" % (value))
        #self._range = value
        self._set_cache_valid()

        #measurement range
    def _get_autorange(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask(":RANGE:AUTO?").split()[0]
            #self._set_cache_valid()
        return resp

    def _set_autorange(self, value):
        if value not in OnOff:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":RANGE:AUTO %e" % (value))
        #self._set_cache_valid()

#Measurement aquiration Speed
    def _get_aquire_speed(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("SPEE?").split()[1]
            self._aquire_speed = resp
            self._set_cache_valid()
        return self._aquire_speed


    def _set_aquire_speed(self, value):
        if value not in self.AquireSpeed:
            raise ivi.InvalidOptionValueException()
        if not self._driver_operation_simulate:
            self._write("SPEE %e" % (value))
        self._aquire_speed = value
        self._set_cache_valid()

# averaging_setting
    def _get_averaging_setting(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("AVER?").split()[1]
            self._averaging_setting = resp
            self._set_cache_valid()
        return self._averaging_setting


    def _set_averaging_setting(self, value):
        #setting value to 1 or 'off' turns averaging off

        if value is 'off' or value is None or value is False:
            value = 'off'
        elif  1 <= int(value) <= 256:
            raise ivi.InvalidOptionValueException()

        if not self._driver_operation_simulate:
            self._write(":AVER %e" % (value))
        self._averaging_setting = value
        self._set_cache_valid()
        return

    #todo - finish range section

    # measurement mode and c/v goals for those goals
    #Measurement Signal Level mode
    def _get_meas_sig_mode(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask(":LEV?").split(' ')[0]
            self._set_cache_valid()
            self._meas_sig_mode = resp
        return self._meas_sig_mode


    def _set_meas_sig_mode(self, value):
        #value can = LCR, CONT (continuous)
        if value not in MeasurementSignalMode:
            raise ivi.InvalidOptionValueException()
        if not self._driver_operation_simulate:
            self._write(":LEV %e" % (value))
        self._meas_sig_mode = value
        self._set_cache_valid()


        #Measurement Signal Constant current
    def _get_meas_sig_cc(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask(":LEV:CCURR?").split(' ')[0]
            self._set_cache_valid()
            self._meas_sig_cc = float(resp)
        return self._meas_sig_cc


    def _set_meas_sig_cc(self, value):
        value = float(value)
        #if  <= value <= : ivi.InvalidOptionValueException() # add error checking
        if not self._driver_operation_simulate:
            self._write(":LEV:CCURR %e" % (value))
        self._meas_sig_cc = value
        self._set_cache_valid()


    #Measurement Signal Constant voltage
    def _get_meas_sig_cv(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask(":LEV:CVOLT?").split(' ')[0]
            self._set_cache_valid()
            self._meas_sig_cv = float(resp)
        return self._meas_sig_cv


    def _set_meas_sig_cv(self, value):
        value = float(value)
        #if  <= value <= : ivi.InvalidOptionValueException() # add error checking
        if not self._driver_operation_simulate:
            self._write(":LEV:CVOLT %e" % (value))
        self._meas_sig_cv = value
        self._set_cache_valid()


    #measurement applied current / voltage limiting functions
    #Measurement Signal Level mode
    def _get_meas_limit_mode(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask(":LIM?").split(' ')[0]
            self._set_cache_valid()
            self._meas_limit_mode = resp
        return self._meas_limit_mode


    def _set_meas_limit_mode(self, value):
        #value can = LCR, CONT (continuous)
        if value not in OnOff:
            raise ivi.InvalidOptionValueException()
        if not self._driver_operation_simulate:
            self._write(":LIM %e" % (value))
        self._meas_limit_mode = value
        self._set_cache_valid()


    #Measurement Signal Constant current limit
    def _get_meas_limit_c(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask(":LIM:CURR?").split(' ')[0]
            self._set_cache_valid()
            self._meas_limit_c = float(resp)
        return self._meas_limit_c


    def _set_meas_limit_c(self, value):
        value = float(value)
        #if  <= value <= : ivi.InvalidOptionValueException() # add error checking
        if not self._driver_operation_simulate:
            self._write(":LIM:CURR %e" % (value))
        self._meas_limit_c = value
        self._set_cache_valid()


    #Measurement Signal Constant voltage limit
    def _get_meas_limit_v(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask(":LIM:VOLT?").split(' ')[0]
            self._set_cache_valid()
            self._meas_limit_v = float(resp)
        return self._meas_limit_v


    def _set_meas_limit_v(self, value):
        value = float(value)
        #if  <= value <= : ivi.InvalidOptionValueException() # add error checking
        if not self._driver_operation_simulate:
            self._write(":LIM:VOLT %e" % (value))
        self._meas_limit_v = value
        self._set_cache_valid()


    #dc bias functions
    def _get_dc_bias_en(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask(":DCBIAS").split(' ')[1]
            self._dc_bias_en = resp
            self._set_cache_valid()
        return self._dc_bias_en


    def _set_dc_bias_en(self, value):
        #value = bool(value)
        if not self._driver_operation_simulate:
            self._write(":DCBIAS %d" % (value))
        self._dc_bias_en = value
        self._set_cache_valid()


    def _get_dc_bias(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask(":DCBIAS:LEV?").split(' ')[0]
            self._dc_bias = float(resp)
            self._set_cache_valid()
        return self._dc_bias


    def _set_dc_bias(self, value):
        value = float(value)
        #if  <= value <= : ivi.InvalidOptionValueException() # add error checking
        if not self._driver_operation_simulate:
            self._write(":DCBIAS:LEV %e" % (value))
        self._dc_bias = value
        self._set_cache_valid()

    def _control_dc_bias(self, enable, value):
        if enable is True:
            self._set_dc_bias_en('ON')
            self._set_dc_bias(value)
        elif enable is False:
            self._set_dc_bias_en('OFF')
            self._set_dc_bias(0)
        else:
            raise ivi.ValueNotSupportedException()


    # sets one of the 4 digit displays to a parameter
    def _set_display_item(self, param_num, item):
        if item not in ParameterMapping\
                or param_num not in range(1,5): #1,2,3,4
            raise ivi.ValueNotSupportedException()
        else:
            item = ParameterMapping[item]

        self._write(':PAR{num!s:s} {pmtr:s}'.format(num=param_num, pmtr=item))

    #sets the items to be returned when asking for a measurement value
    def _set_measurement_items(self, itemEnBytes):

        if len(itemEnBytes) is not 3:
            raise ivi.ValueNotSupportedException()

        self._write(':MEAS:ITEM {mr0!s:s},{mr1!s:s},{mr2!s:s}'
                    .format(mr0=itemEnBytes[0],
                            mr1=itemEnBytes[1],
                            mr2=itemEnBytes[2]))


    def _get_measurement_items(self):
        itemEnBytes = self._ask(':MEAS:ITEM?').replace(',',' ').split()
        itemEnBytes = [int(i) for i in itemEnBytes]

        if len(itemEnBytes) != 3:
            raise ivi.IOException('bad number of bytes recieved')

        return itemEnBytes


    def _generate_sorted_param_map_keys(self, ParamBitMapping):
        # beacuse we need to iterate though ParameterBitMapping in acending
        # list bit# and byte#, create a list of keys ordered by that standard.
        sortedMapping = {}

        #convert to dict with sortable values first
        for item in ParamBitMapping:
            itembits = ParamBitMapping[item]
            sortedMapping[item] = itembits[0] + (itembits[1] * 8)

        #convert dict to list of keys sorted by dict value
        self.sortedParameterBitMappingKeys = \
            sorted(sortedMapping, key=sortedMapping.get, reverse=False)

        #print(self.sortedParameterBitMappingKeys)
        return self.sortedParameterBitMappingKeys


    def _get_measurement_item_order(self):
        #read back item register set and populate measure order list
        #self._expected_meas_order = ['parameter1', 'parameter2', ..etc]

        #get bits of enabled results
        itemEnBytes = self._get_measurement_items()

        # if all en bytes are 0 we have no data to use
        # (in actuality, this isn't true, it just returns disply
        # values, but we have no idea what those are and thefore don't support it.)
        if all(v == 0 for v in itemEnBytes):
                raise ivi.IOException('no measurement order possible '
                                      'as no measurements configured')

        self._expected_meas_order = []
        #check if parameter is enabled and add it to the list if so.
        for item in self.sortedParameterBitMappingKeys:
            itembits = ParameterBitMapping[item]

            if itemEnBytes[itembits[1]] & (0x01 << itembits[0]):
                self._expected_meas_order.append(item)

        return self._expected_meas_order


    def _get_measurements(self):
        # get measurements and assign with keys.
        # fails when no measurements configured

        self._wait_sampling_finished() #blocks until measurement ready

        # paralell arrays. order contains designation, resp contains data
        order = self._get_measurement_item_order()
        resp = self._ask(":MEAS?").replace(',',' ').split()
        #print (resp) #debug

        #if we don't get the # of values we expect, something is wrong
        if len(resp) != len(order):
            raise ivi.IOException('data config doesnt match data recieved')

        self._last_measurement_set = {}
        for (item, value) in zip(order, resp):
            self._last_measurement_set[item] = float(value)

        return self._last_measurement_set


    def _set_measurements(self, items):
        #dev.lcr.set_measurement_items([ 'CONDUCTANCE','IMPEDANCE'])

        itemEnBytes = bytearray([0, 0, 0]) #set to 0,0,0 to go back to returning default display values.

        for item in items:
            if item not in ParameterBitMapping:
                raise ivi.ValueNotSupportedException(item)
            itembits = ParameterBitMapping[item]
            #set bit in corrisponding register according to bit number
            itemEnBytes[itembits[1]] = (itemEnBytes[itembits[1]] | (0x01 << itembits[0]))

        self._set_measurement_items(itemEnBytes)

        #save after successful write
        self._current_meas_items = items


    def do_lcr_measurement(self, frequency, parameters,
                             voltage = 1, current = 0.01, averaging = None,  ):
        self._set_measurements(parameters)
        time.sleep(0.1)
        return get_measurements()


    def set_display_items(self, items):
        # takes in list of up to 4 items to display on screen
        # example = ['REACTANCE','CONDUCTANCE','SUBSEPTANCE','LOSS_FACTOR']
        for itemNum in ramge(0,4):
            self.set_display_item(items[itemNum], itemNum)


    #implemented in _set_meas_sig_mode and assosiated functions
    # def _set_measurement_powers(self, vac, iac, vdc, idc):
    #     self.write('')
    #
    #
    # def _get_measurement_powers(self):
    #     resp = self.ask('')


    def _get_actual_measurement_powers(self):
        order = ['VAC','IAC','VDC','IDC']
        resp = self.ask(':MONI?').replace(',',' ').split()

        vAndI = {}
        for (item, value) in zip(order, resp):
            self.vAndI[item] = float(value)

        return vAndI




    # ESR0_BitMapping = {
    #     'eng of compensation data':0, #CEM
    #     'end of measurement':1, #EOM
    #     'data incorperation end bit':2,#IDX
    #     'inpedance underflow':3, # MUF
    #     'impedance overflow':4, #MOF
    #     'limit oerflow':5, #LOF
    #     "CC and CV overflow":6, #COF
    #     'non gaurenteed accuracy bit':7, #REF
    # }
    #
    # #todo - only return measurement when EOM bit is set

    def _get_event_register(self):
        self.esrContents = self._ask('*esr?')
        #todo map to dict of bits


    # TODO
    # Open Circuit Compensation
    # Short Circuit Compensation
    # Load Compensation
    # Cable length compensation
    # HIGH- Z reject
    # Display on/off
    # SOUND
    # EXT I/O
    # System Settings


    # def find_capacitance(self, frequency, ): pass
    # def find_inductance(self): pass
    # def find_inductance(self): pass
    # def find_resistance(self): pass
    # def find_impediance(self): pass


    #useful utility function/s
    # def csv_frequency_sweep(lcr, filepath, min_freq, max_freq,
    #                     steps, parameters, style = 'log'):
    # # creates csv file of parameters over frequency
    # # style - log or linear - not implemented yet - replace range function
    # # steps = number of descrete steps
    #
    # # example
    # # csv_frequency_sweep(lcr, 'lcrCSVtest.csv', 100, 1000, 100,['IMPEDANCE'])
    #
    # import numpy as np
    # import csv
    #
    # #open file
    # print('creating new csv in ' + filepath)
    # with open(filepath, 'w', newline = '') as csvfile:
    #     frequency_column_header = 'FREQUENCY'
    #
    #     #create 'ordered' list for header and data order
    #     headerlist = [frequency_column_header]
    #     headerlist.extend(parameters)
    #     print(headerlist)
    #
    #     writer = csv.DictWriter(csvfile, fieldnames=headerlist)
    #     writer.writeheader()
    #
    #     lcr._set_measurement_items(parameters)
    #
    #     #select linear or logrithmic scales
    #     if style == 'log':
    #         sweepPoints = np.logspace(np.log10(min_freq),
    #                                   np.log10(max_freq),
    #                                   num=steps)
    #     elif style == 'linear':
    #         sweepPoints = np.linspace(min_freq,
    #                                   max_freq,
    #                                   num=steps)
    #     else:
    #         raise Exception('Style: {st!s:s} not supported'.format(st=style))
    #
    #     #print(sweepPoints)
    #
    #     #collect data
    #     for step in sweepPoints:
    #         freq = round(step, 3)
    #         lcr._set_measurement_frequency(freq)
    #         #or write function to make sure a measurement was taken with current parameters befor reciving it.
    #         sweepResults = lcr._get_measurements()
    #         sweepResults[frequency_column_header] = freq # add frequency key
    #         writer.writerow(sweepResults) #store
    #
    #     #close file?
