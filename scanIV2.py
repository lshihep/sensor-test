import Kei2400CControl as kei2400
import visa
import time
import pylab
import csv
import numpy as np
import platform
import sys

def csv_writer(data,path):
    with open(path,"w") as csv_file:
        writer=csv.writer(csv_file,lineterminator='\n')
        writer.writerow(['Bias Voltage[V]','Measured Voltage[V]','Signal Current[A]','Total Current[A]'])
        for val in data:
            writer.writerows([val])

# prevent from running with python2
if platform.python_version().startswith('2'):
   print('You are running with',platform.python_version(),'.')
   print('Please run with python3.')
   print('Exit.')
   sys.exit()

# Source meter for power supply (Keithley 2410)
biasSupply=kei2400.keithley2400c("ASRL1::INSTR")
biasSupply.set_current_protection(100E-6) # current protection in A
biasSupply.set_voltage_protection(500) # voltage protection in V
positiveHV=True # sign of the voltage
HVrange=3.0*1e3  # voltage scan range in mV in absolute value

# Source meter as a current meter (Keithley 2400)
curMeter=kei2400.keithley2400c("ASRL4::INSTR")
curMeter.set_current_protection(100E-6) # current protection in A
curMeter.set_voltage_protection("min") # voltage protection in V

vols=[]
mvols=[]
current_sig=[]
current_tot=[]

if positiveHV:
    sign=1
else:
    sign=-1
iStart=int(0*1e3)
iEnd=int(sign*HVrange+sign*1)
iStep=int(sign*1.0*1e3)
biasSupply.output_on()
curMeter.output_on()
for iBias in range(iStart,iEnd,iStep):
    biasvol=iBias/1000 # mV to V
	#if biasvol>2:
    #    break
    vols.append(biasvol)
    mvols.append(biasSupply.set_voltage(biasvol))
    current_sig.append(curMeter.display_current())
    current_tot.append(biasSupply.display_current())
    if biasSupply.hit_compliance():
        break
    if curMeter.hit_compliance():
        break

print("Bias Vols: "+str(vols))
print("Measured Vols: "+str(mvols))
print("Signal Current: "+str(current_sig))
print("Total Current: "+str(current_tot))

data=[vols,mvols,current_sig,current_tot]
dataarray=np.array(data)

filename="test.csv"
csv_writer(dataarray.T,filename)

biasSupply.set_voltage(0*1e3)
biasSupply.output_off()
curMeter.output_off()
