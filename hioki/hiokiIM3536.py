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

TriggerSourceMapping = {
        'bus': 'bus',
        'external': 'ext',
        'immediate': 'imm'}

AmplitudeUnits = set(['dBm', 'dBmV', 'dBuV', 'volt', 'watt'])
DetectorType = set(['auto_peak', 'average', 'maximum_peak', 'minimum_peak', 'sample', 'rms'])
TraceType = set(['clear_write', 'maximum_hold', 'minimum_hold', 'video_average', 'view', 'store'])
VerticalScale = set(['linear', 'logarithmic'])
AcquisitionStatus = set(['complete', 'in_progress', 'unknown'])

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
        #self._write(":pres") # returns to known preset values. a "factory reset"

    #redundant, error checking parameter setter
    def _set_param(self, cmd, value, delay=0.0, rnd=None, timeout=10 ):
        cmddelay = delay
        timeo = timeout
        while (timeo > 0):
            cmddelay = cmddelay + (0.01 * cmddelay) #delay gets exponentially longer with each failed command.
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

    #
    # def _get_disable(self):
    #     if not self._driver_operation_simulate and not self._get_cache_valid():
    #         resp = self._ask("disable?").split(' ')[1]
    #         self._disable = bool(int(resp))
    #         self._set_cache_valid()
    #     return self._disable
    #
    # def _set_disable(self, value):
    #     value = bool(value)
    #     if not self._driver_operation_simulate:
    #         self._write("disable %d" % (int(value)))
    #     self._disable = value
    #     self._set_cache_valid()


#instrument specific stuff
#actually need to do error checking here.


    #Measurement Mode
    def _get_mode(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("mode?").split(' ')[0]
            self._set_cache_valid()
            self._mode = resp
        return self._mode

    def _set_mode(self, value):
        #value can = LCR, CONT (continuous)
        if value not in OperationMode:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write("mode %e" % (value))
        self._mode = value
        self._set_cache_valid()

    #measurement frequency
    def _get_measurement_frequency(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            resp = self._ask("freq?").split()[0]
            self._measurement_frequency = float(resp)
            self._set_cache_valid()
        return self._measurement_frequency

    def _set_measurement_frequency(self, value):
        value = float(value)
        if not self._minimum_meas_frequency <= value <= self._maximum_meas_frequency:
            raise ivi.InvalidOptionValueException()
        if not self._driver_operation_simulate:
            self._write("freq %e" % (value))
        self._measurement_frequency = value
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


    def set_display_item(self, param_num, item):
        if item not in ParameterMapping\
                or param_num not in range(1,5): #1,2,3,4
            raise ivi.ValueNotSupportedException()
        else:
            item = ParameterMapping[item]

        self._write(':PAR{num!s:s} {pmtr:s}'.format(num=param_num, pmtr=item))


    def set_measurement_items(self, items):
        #dev.lcr.set_measurement_items([ 'CONDUCTANCE','IMPEDANCE'])

        itemEnBytes = bytearray([0, 0, 0]) #set to 0,0,0 to go back to returning default display values.


        for item in items:
            if item not in ParameterBitMapping:
                raise ivi.ValueNotSupportedException(item)
            itembits = ParameterBitMapping[item]
            #set bit in corrisponding register according to bit number
            itemEnBytes[itembits[1]] = (itemEnBytes[itembits[1]] | (0x01 << itembits[0]))

        self._write(':MEAS:ITEM {mr0!s:s},{mr1!s:s},{mr2!s:s}'
                    .format(mr0=itemEnBytes[0],
                            mr1=itemEnBytes[1],
                            mr2=itemEnBytes[2]))
        #save after successful write
        self._current_meas_items = items


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


    def get_measurements(self):
        # get measurements and assign with keys.
        # Does not work when no measurements configured

        # paralell arrays. order contains designation, resp contains data
        order = self._get_measurement_item_order()
        resp = self._ask(":MEAS?").replace(',',' ').split()

        #if we don't get the # of values we expect, something is wrong
        if len(resp) != len(order):
            raise ivi.IOException('data config doesnt match data recieved')

        self._last_measurement_set = {}
        for (item, value) in zip(order, resp):
            self._last_measurement_set[item] = float(value)

        return self._last_measurement_set


    def do_lcr_measurement(self, frequency, parameters,
                             voltage = 1, current = 0.01, averaging = None,  ):
        self.set_measurement_items(parameters)
        time.sleep(0.1)
        return get_measurements()


    # def find_capacitance(self, frequency, ): pass
    # def find_inductance(self): pass
    # def find_inductance(self): pass
    # def find_resistance(self): pass
    # def find_impediance(self): pass




    #measurement aquire frequency vs applied frequency

    def set_display_items(self, items):
        # takes in list of up to 4 items to display on screen
        # example = ['REACTANCE','CONDUCTANCE','SUBSEPTANCE','LOSS_FACTOR']
        for itemNum in ramge(0,4):
            self.set_display_item(items[itemNum], itemNum)


    #interesting utility functions

    def do_frequency_sweep(self, min_freq, max_freq, step, parameters):
        # sweeps through frequency by defined steps and returns
        # dictonary of collected parameters

        #parameters = list of parameters to collect -> ['IMPEDANCE', 'CONDUCTANCE', ..etc]

        self.set_measurement_items(parameters)

        sweepResults = {}
        for step in range(min_freq, max_freq + step, step):
            self._set_measurement_frequency(step)
            time.sleep(0.1) #todo - generate this based on frequency
            sweepResults[step] = self.get_measurements()

        return sweepResults


    # def csv_frequency_sweep(min_freq, max_freq, step, parameters, filepath)
    #     #filepath = '?'
    #     sweepRes = dev.lcr.do_frequency_sweep(min_freq, max_freq, step, parameters,)
    #
    #     #open file
    #     import csv
    #     with open(filepath, 'w', newline = '') as csvfile:
    #
    #         csvWriter = csv.writer(csvfile, delimiter = ' ',
    #                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #
    #
    #         #create 'ordered' list for header and data order
    #         headeritem = sweepRes[ sweepRes.keys()[0]]
    #         headerlist = []
    #         for key in headeritem:
    #             headerlist.append(key)
    #
    #         #populate header with headerlist
    #         csvWriter.writerow(headerList)
    #
    #         #fill out file
    #         for step in sweepRes:
    #             data = sweepRes[step]
    #             row = []
    #             for header in headerlist:
    #                 row.append(data[header])
    #             csvWriter.writerow(row)