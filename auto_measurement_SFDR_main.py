import pyvisa
import os
import numpy as np
from matplotlib import pyplot as plt
import pandas
from ThorlabsPM100 import ThorlabsPM100
import winsound
import time
#############################################################################################
# This is used for control two RF signal generators and a RF spectral analyzer for
# automatic measurement. It uses pyvisa and Standard Commands for Programmable Instruments (SCPI)
# to control the instruments.
# The SCPI commands are case-insensitive. The upper cases are abbreviation of the commands.
# eg: FREQuency = FREQ, POWer = POW.
##############################################################################################

rm = pyvisa.ResourceManager()
rm.list_resources()
print(rm.list_resources())
###############################################################################################
# config address of instruments
###############################################################################################
signal_gen_wil = rm.open_resource('GPIB0::5::INSTR')
signal_gen_rs = rm.open_resource('GPIB0::7::INSTR')
power_meter_addr = rm.open_resource('USB0::0x1313::0x8078::P0012058::0::INSTR')
power_meter = ThorlabsPM100(inst=power_meter_addr)
esa = rm.open_resource('USB0::0x2A8D::0x1A0B::MY57100205::0::INSTR')
# print the information of instrument
#  “what are you?” or – in some cases – “what’s on your display at the moment?”
print(esa.query('*IDN?'))
# print(signal_gen_rs.query('*IDN?'))
print(signal_gen_wil.query('*IDN?'))
print(power_meter_addr.query('*IDN?'))
print(rm)
my_instrument_all = rm.list_opened_resources()
print(my_instrument_all)
#########################################################################################
#            config power meter
#########################################################################################
print(power_meter.sense.power.dc.unit)
print(power_meter.read) # Read-only property
# set attenuation of power meter
power_meter.sense.correction.loss.input.magnitude= 20
print(power_meter.sense.correction.loss.input.default_magnitude)
print(power_meter.sense.average.count)  # read property
power_meter.sense.average.count = 10 # write property
power_meter.system.beeper.immediate() # method
print(power_meter.getconfigure)
sensor = power_meter.system.sensor.idn
print(sensor)
power_meter.sense.power.dc.range.auto = 1
PW_config = power_meter.sense.power.dc.range.auto
# print(PW_config)
#######################################################################
#              config signal generator
#######################################################################
# config signal generator wil
# set time out
# signal_gen_wil.timeout = 25000
# set frequency 5.001GHz
freq_wil = "5001000000"
signal_gen_wil.write("SOURce:FREQuency:CW " + freq_wil)
# signal_gen_wil.write("SOURce:FREQuency:CW 5E9")
# set output power eg: 16.8 dbm
# pow_out_wil = "16.8"
pow_out_wil = ["16.5", "16.0", "15.5", "15.0", "14.5", "14.0", "13.5","13.0", "12.5", "12.0", "11.5", "11.0","10.5","10.0", "9.5","9.0","8.5","8.0","7.5","7.0","6.5"]
signal_gen_wil.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude " + pow_out_wil[0])
# signal_gen_wil.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude -20")
# set the increment of output power
signal_gen_wil.write(":SOURce:POWer:STEP:INCRement 1")
#######################################################
# config signal generator RS
# set time out
# signal_gen_wil.timeout = 25000
# set frequency 5.00GHz
freq_rs = "5000000000"
signal_gen_rs.write("SOURce:FREQuency:CW " + freq_rs)
# signal_gen_rs.write("SOURce:FREQuency:CW 5.01E9")
# set output power eg: 17.3 dbm
# pow_out_rs = "17.3"
pow_out_rs = ["17.3","16.7","16.2","15.6","15.1","14.5","14.o","13.4","12.9","12.3","11.8","11.2","10.7","10.1","9.6","9","8.5","7.9","7.4","6.8","6.3"]
signal_gen_rs.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude " + pow_out_rs[0])
# signal_gen_rs.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude -20")
signal_gen_rs.write(":SOURce:POWer:STEP:INCRement 1.1")
#####################################################
#       esa initialization
#####################################################
# get the date
date_str = time.strftime('%Y%m%d')
# Query current measurement mode in ESA
print(esa.query(':CONFigure?'))
# set measured center frequency
esa.write(":SENSe:FREQuency:CENTer 5.0005 GHz")
esa.write(":SENSe:SWEep:POINts 1001")
# set measured frequency span
esa.write(":SENSe:FREQuency:SPAN 10 MHz")
# set RBW
esa.write(":SENSe:BANDwidth:RESolution 10 KHz")
# set VBW
esa.write(":SENSe:BANDwidth:VIDeo 1 KHZ")
# set continuous measurement or single ON or 1 is continuous OFF or 0 is single
esa.write(":INITiate:CONTinuous ON")
# set attenuation
esa_att = float(esa.query(":SENSe:POWer:RF:ATTenuation?"))
# esa.write(":SENSe:POWer:RF:ATTenuation 30")
# esa_att = esa.write(":SENSe:POWer:RF:ATTenuation?")
# set IF preamplifier  OFF | ON | 0 | 1
esa.write(":SENSe:IF:GAIN:SWEPt:STATe OFF")
# esa.write(":SENSe:IF:GAIN:SWEPt:AUTO:STATe OFF")  # auto
esa_preamp_state = float(esa.query(":SENSe:IF:GAIN:SWEPt:STATe?"))
# create a folder to save data
esa.write(":MMEMory:MDIRectory \"D:\liu\\" + date_str + "\"")
# set the storage directory
esa.write(":MMEMory:CDIRectory \"D:\liu\date_str\"")
print(esa.query(":MMEMory:CDIRectory?"))
# set marker
esa.write(":CALC:MARK1:MODE POSition")
# esa.write(":CALC:MARK1:X 5.005 GHZ")
esa.write(":CALC:MARK2:MODE POS")
# esa.write(":CALC:MARK2:X 5.005 GHZ")
esa.write(":CALC:MARK3:MODE POS")
# esa.write(":CALC:MARK3:X 5.005 GHZ")
esa.write(":CALC:MARK4:MODE POS")
# esa.write(":CALC:MARK4:X 5.005 GHZ")
esa.write(":CALC:MARK7:MODE POS")
######################################################################################################
# create list for saving
######################################################################################################
# create a list to save input power in each circle
pow_in_list = []
pow_in_rs_list = []
# create a list to save output power in each circle (ESA measured power)
pow_out_list = []
# # create a list to save the freq of marker
# freq_marker1 = []
# freq_marker2 = []
# freq_marker3 = []
# freq_marker4 = []
# create a list to save the power of marker
pow_marker1 = []
pow_marker2 = []
pow_marker3 = []
pow_marker4 = []
# list for optical power
opt_pows = []
#####################################################################################################
# start measure loop
#####################################################################################################
# turn on signal generator
signal_gen_rs.write(":OUTPut:STATe ON")
signal_gen_wil.write(":OUTPut:STATe ON")
esa.write(":INITiate:CONTinuous ON")
time.sleep(1)
# # check the maximum RF input power, in case overloaded
# esa.write(":CALC:MARK7:MAXimum")
# pow_max = esa.query(":CALC:MARK7:Y?")
# if esa_preamp_state == 1:
#     if pow_max >= (esa_att - 30):
#         # turn OFF signal generator
#         signal_gen_wil.write(":OUTPut:STATe OFF")
#         signal_gen_rs.write(":OUTPut:STATe OFF")
#     elif pow_max >= 20:
#         # turn OFF signal generator
#         signal_gen_wil.write(":OUTPut:STATe OFF")
#         signal_gen_rs.write(":OUTPut:STATe OFF")
# elif esa_preamp_state == 0:
#     if pow_max >= (esa_att - 10):
#         # turn OFF signal generator
#         signal_gen_wil.write(":OUTPut:STATe OFF")
#         signal_gen_rs.write(":OUTPut:STATe OFF")
#     elif pow_max >= 20:
#         # turn OFF signal generator
#         signal_gen_wil.write(":OUTPut:STATe OFF")
#         signal_gen_rs.write(":OUTPut:STATe OFF")
# time.sleep(3)
# set position of markers
esa.write(":INITiate:CONTinuous OFF")
# marker search
# esa.write(":CALC:MARK1:MAXimum:LEFT")
# esa.write(":CALCulate:MARKer2:MAXimum:RIGHt")
# esa.write(":CALCulate:MARKer3:MAXimum:LEFT")
# esa.write(":CALCulate:MARKer3:MAXimum:LEFT")
# esa.write(":CALCulate:MARKer3:MAXimum:LEFT")
# esa.write(":CALCulate:MARKer4:MAXimum:RIGHt")
# esa.write(":CALCulate:MARKer4:MAXimum:RIGHt")
# get freq of each marker
freq_marker1 = esa.query(":CALC:MARK1:X?")
freq_marker2 = esa.query(":CALC:MARK2:X?")
freq_marker3 = esa.query(":CALC:MARK3:X?")
freq_marker4 = esa.query(":CALC:MARK4:X?")

# number of times of measurement
num_input = 20
count = 1
# number of times of averaging
num_average = 2
# loop
while count <= num_input:
    # get the input power from signal generator wil
    pow_in = signal_gen_wil.query("POWer?")
    pow_in = pow_in.replace('\n', '').replace('\r','')
    # pow_in_list.append(pow_in)
    # print(pow_in)
    # print(type(pow_in))
    esa.write(":INITiate:CONTinuous ON")
    # wait some seconds then single sweep
    time.sleep(3)
    esa.write(":INITiate:CONTinuous OFF")
    # average counting index
    count_av = 1
    while count_av <= num_average:
        # get measured trace
        trace_read = esa.query(":READ:SANalyzer1? ")   # string
        # get the optical power into photodetector
        opt_pow = power_meter.read
        print(type(opt_pow))
        opt_pows.append(opt_pow)
        # slice the string at every null character (eg: space,\n,\t)return string in a list
        trace_read_list = trace_read.split(",")        # list
        # separate the freq and power 0,2,4 is freq, 1,3,4 is power
        measure_freq = trace_read_list[0::2]
        measure_power = trace_read_list[1::2]
        # create a 2 column file to save freq and power
        measure_esa = pandas.DataFrame({'freq(Hz)': measure_freq, 'power(dBm)': measure_power})
        # save measured trace as csv file
        time_str = time.strftime('%Y%m%d_%H%M%S')
        name_read = "C:\liu\project\AutoMeasurement\sfdr_measure_normal0125\measured_esa_spectrum_Pin_" + pow_in + "_dBm_"\
                    + str(count_av) + "_" + time_str + ".csv"
        measure_esa.to_csv(name_read,index=False,sep=',')
        # save measurement data on esa
        esa.write(":MMEMory:STORe:TRACe:DATA TRACE1,\"D:\liu\\" + date_str + "\\" + "esa_spectrum_normal" + pow_in + "_dBm_"\
                  + str(count_av) + "_" + time_str +".csv\"")
        # second way to get trace
        # query trace data
        measure_query = esa.query(":TRACe:DATA? TRACE1 ")
        measure_query_list = measure_query.split(",")
        measure_query_data = pandas.DataFrame({'power(dBm)': measure_query_list})
        name_query = "C:\liu\project\AutoMeasurement\sfdr_measure_normal0125\measure_trace" + pow_in + "_dBm_" + str(count_av)\
                     + "_" + time_str + ".csv"
        measure_query_data.to_csv(name_query, index=False, sep=',')
        ###################################################################################################
        # get the input power from signal generator wil
        pow_in = signal_gen_wil.query("POWer?")
        pow_in = pow_in.replace('\n', '').replace('\r', '')
        pow_in_list.append(pow_in)
        pow_in_rs = signal_gen_rs.query("POWer?")
        pow_in_rs = pow_in_rs.replace('\n', '').replace('\r', '')
        pow_in_rs_list.append(pow_in_rs)
        # print(pow_in)
        # print(type(pow_in))
        # read marker
        # freq_marker1.append(esa.query(":CALC:MARK1:X?"))
        pow_out_list.append(esa.query(":CALC:MARK1:Y?"))
        pow_marker1.append(esa.query(":CALC:MARK1:Y?"))
        # freq_marker2.append(esa.query(":CALC:MARK2:X?"))
        pow_marker2.append(esa.query(":CALC:MARK2:Y?"))
        # freq_marker3.append(esa.query(":CALC:MARK3:X?"))
        pow_marker3.append(esa.query(":CALC:MARK3:Y?"))
        # freq_marker4.append(esa.query(":CALC:MARK4:X?"))
        pow_marker4.append(esa.query(":CALC:MARK4:Y?"))
        count_av = count_av + 1
        time.sleep(0.5)
        ###################################################################################################
    # signal_gen_wil.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude DOWN")
    # signal_gen_rs.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude DOWN")

    signal_gen_rs.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude " + pow_out_rs[count])
    signal_gen_wil.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude " + pow_out_wil[count])

    count = count + 1

    print(pow_in_list)
    print(pow_out_list)

print(pow_in_list)
print(pow_out_list)
# convert char list to number float list
pow_in_list = list(map(float, pow_in_list))
pow_out_list = list(map(float, pow_out_list))
pow_marker1 = list(map(float, pow_marker1))
pow_marker2 = list(map(float, pow_marker2))
pow_marker3 = list(map(float, pow_marker3))
pow_marker4 = list(map(float, pow_marker4))
opt_pows = list(map(float, opt_pows))
# separate different time of average measurement


measure_sfdr = pandas.DataFrame({'Pin(dBm)' + freq_marker1: pow_in_rs_list,
                                 'Pin(dBm)' + freq_marker2: pow_in_list,
                                 'Pout3(dBm)' + freq_marker3: pow_marker3,
                                 'Pout1(dBm)' + freq_marker1: pow_marker1,
                                 'Pout2(dBm)' + freq_marker2: pow_marker2,
                                 'Pout4(dBm)' + freq_marker4: pow_marker4})
# get the current time eg: %Y2021, %y21, %m month 01, %d day 13, %D 01/13/21, %H%M%S hour min sec
time_str = time.strftime('%Y%m%d_%H%M%S')
name_sfdr = "C:\liu\project\AutoMeasurement\sfdr_measure_normal0125\sfdr" + time_str + ".csv"
measure_sfdr.to_csv(name_sfdr,index=False,sep=',')
opt_pows_data = pandas.DataFrame({'power': opt_pows})
name_opt_pow = "C:\liu\project\AutoMeasurement\sfdr_measure_normal0125\opt_pow" + time_str + ".csv"
opt_pows_data.to_csv(name_opt_pow,index=False,sep=',')
#############################
## check data type
# print(type(measure_result_read))
# print(measure_result_read)
# print(type(measure_result_read_list))
# print(measure_result_read_list)
# print(type(measure_result_read_list[0]))
# print(measure_result_read_list[0])
# print(type(pow_in_list[1]))
# print(pow_in_list[1])

print(type(measure_esa))

# turn OFF signal generator
signal_gen_wil.write(":OUTPut:STATe OFF")
signal_gen_rs.write(":OUTPut:STATe OFF")
################################
# beep when finished
duration = 500  # millisecond
freq = 440  # Hz
winsound.Beep(freq, duration)

##################
# plot SFDR
# convert list to array
pow_in_array = np.array(pow_in_list)
pow_out_array = np.array(pow_out_list)
pow_marker1_array = np.array(pow_marker1)
pow_marker2_array = np.array(pow_marker2)
pow_marker3_array = np.array(pow_marker3)
pow_marker4_array = np.array(pow_marker4)
plt.title("SFDR")
plt.ylabel("Pout (dBm)")
plt.xlabel("Pin (dBm)")
plt.scatter(pow_in_array,pow_marker1_array,label='f1')
plt.scatter(pow_in_array,pow_marker2_array,label='f2')
plt.scatter(pow_in_array,pow_marker3_array,label='f3')
plt.scatter(pow_in_array,pow_marker4_array,label='f4')
plt.ylim(-110,-20)
plt.legend()
# plt.plot(pow_in_array,pow_out_array,pow_in_array,pow_marker2_array,pow_in_array,pow_marker3_array,pow_in_array,pow_marker4_array)
plt.savefig("C:\liu\project\AutoMeasurement\sfdr_measure_normal0125\sfdr_fig" + time_str + ".png")
plt.show()