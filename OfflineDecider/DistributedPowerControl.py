import sys
frontend_characterization_file = str(sys.argv[1])
backend_characterization_file = str(sys.argv[2])
power_cap = float(sys.argv[3])
mini_performance_gain = 0.03
static_power=20
dist_ratio=0.5

def ReadTradeoffFile(filename):
    lines = open(filename,'r').readlines()
    power_performance_list =[]
    for line in lines:
        cap = float(line.split()[0])
        power = float(line.split()[2]) +float(line.split()[3])
        perf = 1/float(line.split()[1])
        energy = power/perf
        power_performance_list.append((cap,power,perf,energy))
    return power_performance_list

frontend_tradeoff_list = ReadTradeoffFile(frontend_characterization_file)
backend_tradeoff_list = ReadTradeoffFile(backend_characterization_file)

def PowerToPerf(power, tradeoff_list):
    if len(tradeoff_list) !=15:
        perf = -1
	print "characterization length is wrong!"
        return perf
    if power < tradeoff_list[0][0] or power > tradeoff_list[14][0]:
        print 'power is not in range. ERROR!!!'+str(power) +'  '+ str(tradeoff_list[0][0])+'  '+str(tradeoff_list[14][0])
        perf = -1
    elif power >= tradeoff_list[0][0] and power < tradeoff_list[1][0]:
         perf = (tradeoff_list[1][2] -tradeoff_list[0][2])/10.0 *(power - tradeoff_list[0][0]) +tradeoff_list[0][2]
    elif power >= tradeoff_list[1][0] and power < tradeoff_list[2][0]:
         perf = (tradeoff_list[2][2] -tradeoff_list[1][2])/10.0 *(power - tradeoff_list[1][0]) +tradeoff_list[1][2]
    elif power >= tradeoff_list[2][0] and power < tradeoff_list[3][0]:
         perf = (tradeoff_list[3][2] -tradeoff_list[2][2])/10.0 *(power - tradeoff_list[2][0]) +tradeoff_list[2][2]
    elif power >= tradeoff_list[3][0] and power < tradeoff_list[4][0]:
         perf = (tradeoff_list[4][2] -tradeoff_list[3][2])/10.0 *(power - tradeoff_list[3][0]) +tradeoff_list[3][2]
    elif power >= tradeoff_list[4][0] and power < tradeoff_list[5][0]:
         perf = (tradeoff_list[5][2] -tradeoff_list[4][2])/10.0 *(power - tradeoff_list[4][0]) +tradeoff_list[4][2]
    elif power >= tradeoff_list[5][0] and power < tradeoff_list[6][0]:
         perf = (tradeoff_list[6][2] -tradeoff_list[5][2])/10.0 *(power - tradeoff_list[5][0]) +tradeoff_list[5][2]
    elif power >= tradeoff_list[6][0] and power < tradeoff_list[7][0]:
         perf = (tradeoff_list[7][2] -tradeoff_list[6][2])/10.0 *(power - tradeoff_list[6][0]) +tradeoff_list[6][2]
    elif power >= tradeoff_list[7][0] and power < tradeoff_list[8][0]:
         perf = (tradeoff_list[8][2] -tradeoff_list[7][2])/10.0 *(power - tradeoff_list[7][0]) +tradeoff_list[7][2]
    elif power >= tradeoff_list[8][0] and power < tradeoff_list[9][0]:
         perf = (tradeoff_list[9][2] -tradeoff_list[8][2])/10.0 *(power - tradeoff_list[8][0]) +tradeoff_list[8][2]
    elif power >= tradeoff_list[9][0] and power < tradeoff_list[10][0]:
         perf = (tradeoff_list[10][2] -tradeoff_list[9][2])/10.0 *(power - tradeoff_list[9][0]) +tradeoff_list[9][2]
    elif power >= tradeoff_list[10][0] and power < tradeoff_list[11][0]:
         perf = (tradeoff_list[11][2] -tradeoff_list[10][2])/10.0 *(power - tradeoff_list[10][0]) +tradeoff_list[10][2]
    elif power >= tradeoff_list[11][0] and power < tradeoff_list[12][0]:
         perf = (tradeoff_list[12][2] -tradeoff_list[11][2])/10.0 *(power - tradeoff_list[11][0]) +tradeoff_list[11][2]
    elif power >= tradeoff_list[12][0] and power < tradeoff_list[13][0]:
         perf = (tradeoff_list[13][2] -tradeoff_list[12][2])/10.0 *(power - tradeoff_list[12][0]) +tradeoff_list[12][2]
    elif power >= tradeoff_list[13][0] and power <= tradeoff_list[14][0]:
         perf = (tradeoff_list[14][2] -tradeoff_list[13][2])/10.0 *(power - tradeoff_list[13][0]) +tradeoff_list[13][2]
    return perf

def EEmode(h_list, l_list, power_cap):
    mini_performance = PowerToPerf(power_cap,l_list) * (1 - mini_performance_gain)
    fixed_time = 1/mini_performance 
    index =  int(power_cap -60) / 10 + 1
    energy_h = power_cap / PowerToPerf(power_cap,h_list) + static_power * max(0,(fixed_time - 1/PowerToPerf(power_cap,h_list)))
    energy_l = power_cap / PowerToPerf(power_cap,l_list) + static_power * max(0,(fixed_time - 1/PowerToPerf(power_cap,l_list)))
#    initial_energy = energy_h + energy_l
    h_power=power_cap
    l_power=power_cap
    for i in range(index):
        if h_list[i][2] >= mini_performance and  h_list[i][3] + static_power * max(0,(fixed_time - 1/h_list[i][2])) < energy_h:
            energy_h =  h_list[i][3] + static_power * max(0,(fixed_time - 1/h_list[i][2]))
            h_power = h_list[i][0]
        if l_list[i][2] >= mini_performance and l_list[i][3] + static_power * max(0,(fixed_time - 1/l_list[i][2]))  >energy_l:
            energy_l = l_list[i][3]
            l_power = l_list[i][0]
#    final_energy = energy_h + energy_l
#    print str(final_energy/initial_energy)
    return h_power, l_power




#decide to improve performance or ee
performance_delta=1
h_list=[]
l_list=[]
reverse_flag = 1
frontend_power = 0
backend_power = 0

power_check = 0
last_power_check = 0

power_h=0
power_l=0
final_perf = 0
mode = 0
if power_cap - 60 >= 200 - power_cap:
    power_check = 200 - power_cap
else:
    power_check = power_cap - 60
#print str(PowerToPerf(power_cap, frontend_tradeoff_list)),str(PowerToPerf(power_cap, backend_tradeoff_list))
if PowerToPerf(power_cap, frontend_tradeoff_list) > PowerToPerf(power_cap, backend_tradeoff_list):
# h_list, low_list
    h_list = frontend_tradeoff_list
    l_list = backend_tradeoff_list
else:
    h_list = backend_tradeoff_list
    l_list = frontend_tradeoff_list
    reverse_flag = -1

if PowerToPerf(power_cap -power_check, h_list) > PowerToPerf(power_cap + power_check, l_list):
    if PowerToPerf(power_cap + power_check, l_list) < (1+ mini_performance_gain) * PowerToPerf(power_cap, l_list):
        #enter EE mode
        power_h, power_l = EEmode(h_list,l_list,power_cap)
        if reverse_flag == -1:
            frontend_power = power_l
            backend_power = power_h
        else:
            frontend_power= power_h
            backend_power = power_l
    else:
        #enter performance mode
        mode =1
        frontend_power= power_cap - reverse_flag * power_check
        backend_power= power_cap + reverse_flag* power_check
else:
    power_h = power_cap -power_check
    power_l = power_cap + power_check
    while power_check > 0.5:
        power_check = power_check/2
        if PowerToPerf(power_h, h_list) > PowerToPerf(power_l, l_list):
            power_h -= power_check
            power_l += power_check
        else:
            power_h += power_check
            power_l -= power_check
    final_perf = min(PowerToPerf(power_h,h_list),PowerToPerf(power_l,l_list))
    if final_perf < (1 + mini_performance_gain)* PowerToPerf(power_cap, l_list):
        #enter EE mode
        power_h, power_l = EEmode(h_list,l_list,power_cap)

    else:
        #enter performance mode
        mode =1
    if reverse_flag == -1:
        frontend_power = power_l
        backend_power = power_h
    else:
        frontend_power= power_h
        backend_power = power_l
if ( PowerToPerf(frontend_power + 1,frontend_tradeoff_list) - PowerToPerf(frontend_power,frontend_tradeoff_list)) !=0:
    dist_ratio= ( PowerToPerf(backend_power + 1,backend_tradeoff_list) - PowerToPerf(backend_power,backend_tradeoff_list)) / ( PowerToPerf(frontend_power + 1,frontend_tradeoff_list) - PowerToPerf(frontend_power,frontend_tradeoff_list))

return_string = str(mode)+' '+str(frontend_power) + ' '+str(backend_power) + ' '+ str(dist_ratio)
print return_string
