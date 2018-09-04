import os,sys
import math

front_end_power_per_node = float(sys.argv[1])
back_end_power_per_node = float(sys.argv[2])
server_name_list=[ 'ubuntu-3', 'ubuntu-4', 'ubuntu-5', 'node-5', 'node-19', 'node-408', 'node-50', 'node-28', 'node-52', 'node-37', 'node-14', 'node-4', 'node-18', 'ubuntu-6', 'ubuntu-7', 'ubuntu-8', 'node-64', 'node-49', 'node-3', 'node-13', 'node-46', 'node-45', 'node-24', 'node-11', 'node-10', 'node-56']
#global_power_limit =
cpu_list=[]
num_node=len(server_name_list)
num_cpu=2*num_node
END_signal =0
frequency = 2
#output runtime info
runtime_info=open('runtime_info.txt','w')
power_margin=1.5
distribution_ratio=float(sys.argv[3])
#policy
class cpu:

    def __init__(self,id):
        self.id = id
        self.initial_power_limit=0.0
        self.current_power_limit=0.0
        self.next_power_limit=0.0
        self.current_power=0.0
        self.extra_power=0.0
        self.extra_power_with_margin=0.0
        self.priority = -1
        self.group = -1
        self.continus_priority2 = 0

#read last window average power
def ReadPower(id):
    FileName = 'PowerResults'+str(server_name_list[id])
    Powerlist = open(FileName,'r').readlines()[-9:]
    power1=0.0
    power2=0.0
    for i in range(len(Powerlist)):
        power1 += float(Powerlist[i].split()[1])
        power2 += float(Powerlist[i].split()[2])
    power1 = power1/len(Powerlist)
    power2 = power2/len(Powerlist)
    return power1,power2

# read in initial power limit
for i in range(num_cpu):
    cpu_tmp = cpu(i)

    if i < num_cpu/2:
        cpu_tmp.initial_power_limit = front_end_power_per_node/2
        cpu_tmp.group = 0
    else:
        cpu_tmp.initial_power_limit = back_end_power_per_node/2
        cpu_tmp.group = 1
    cpu_tmp.current_power_limit = cpu_tmp.initial_power_limit
#    print str(cpu_tmp.initial_power_limit)
    cpu_list.append(cpu_tmp)


while(END_signal !=1):

    os.system("sleep "+str(frequency))
    
    for i in range(num_node):
        power1,power2 = ReadPower(i)
        if power1> 0 and power1 <200:
            cpu_list[2*i].current_power = power1
        else:
            cpu_list[2*i].current_power = cpu_list[2*i].current_power_limit
        if power2> 0 and power2 <200:
            cpu_list[2*i+1].current_power = power2
        else:
            cpu_list[2*i+1].current_power = cpu_list[2*i+1].current_power_limit
    for i in range(len(cpu_list)):
        cpu_list[i].extra_power = cpu_list[i].current_power_limit - cpu_list[i].current_power
        cpu_list[i].extra_power_with_margin = cpu_list[i].extra_power - power_margin
	#print 'id: '+str(i) + ' limit: '+ str(cpu_list[i].current_power_limit) +' current power:' +str(cpu_list[i].current_power)
    #decide next_power_limit_list
    #define extra power???
    total_extra_power= sum(cpu.extra_power_with_margin for cpu in cpu_list)
   # if total_extra_power > 0:
    total_absolute_extra_power = 0
    total_pri2_needed_power = 0
    total_pri1_extra_power = 0
    priority_2_list=[]
    priority_1_list=[]
    priority_0_list=[]
    group0_size =0
    group1_size =0
    for i in range(len(cpu_list)):
            #priority 0: not reaching power cap
            #priority 1: reached power cap but power cap higher than initial cap
            #priority 2: reached power cap and power cap lower than initial cap

        if cpu_list[i].extra_power_with_margin < 0:
            if cpu_list[i].current_power_limit < cpu_list[i].initial_power_limit:
                cpu_list[i].priority = 2
                priority_2_list.append(i)
                if cpu_list[i].continus_priority2 == 1:
                    total_pri2_needed_power += cpu_list[i].initial_power_limit - cpu_list[i].current_power_limit
                #force priority 2 cpus to have the initial cap
                    cpu_list[i].next_power_limit= cpu_list[i].initial_power_limit
                else:
                    total_pri2_needed_power += (cpu_list[i].initial_power_limit - cpu_list[i].current_power_limit)/2
                #force priority 2 cpus to have the initial cap
                    cpu_list[i].next_power_limit= cpu_list[i].current_power_limit + (cpu_list[i].initial_power_limit - cpu_list[i].current_power_limit)/2
                    cpu_list[i].continus_priority2 = 1
            else:
                cpu_list[i].priority = 1
                cpu_list[i].continus_priority2 = 0 
                priority_1_list.append(i)
                cpu_list[i].next_power_limit= cpu_list[i].current_power_limit
                total_pri1_extra_power += cpu_list[i].current_power_limit - cpu_list[i].initial_power_limit
        else:
            cpu_list[i].priority = 0
            cpu_list[i].continus_priority2 = 0 
            priority_0_list.append(i)
            cpu_list[i].next_power_limit = cpu_list[i].current_power_limit - cpu_list[i].extra_power_with_margin
            total_absolute_extra_power += cpu_list[i].extra_power_with_margin
    
    for id in priority_1_list:
        if cpu_list[id].group == 0:
            group0_size += 1
        else:
            group1_size += 1                                                  
    for id in priority_0_list:
        if cpu_list[id].group == 0:
            group0_size += 1
        else:
            group1_size += 1
        	
    if total_absolute_extra_power >= total_pri2_needed_power:
        #per_cpu_extra_power0 = (total_absolute_extra_power - total_pri2_needed_power) * distribution_ratio
        per_cpu_extra_power1 = (total_absolute_extra_power - total_pri2_needed_power) / (group0_size * distribution_ratio + group1_size)
        per_cpu_extra_power0 = per_cpu_extra_power1 * distribution_ratio
    
        for id in priority_1_list:
            if cpu_list[id].group == 0:
                cpu_list[id].next_power_limit +=per_cpu_extra_power0
            else:
                cpu_list[id].next_power_limit +=per_cpu_extra_power1
        for id in priority_0_list:
            if cpu_list[id].group == 0:
                cpu_list[id].next_power_limit +=per_cpu_extra_power0
            else:
                cpu_list[id].next_power_limit +=per_cpu_extra_power1


    else:
        if total_pri1_extra_power+ total_absolute_extra_power >= total_pri2_needed_power:
            print "total_pri1_extra_power+ total_absolute_extra_power >= total_pri2_needed_power"
            #per_cpu_extra_power0 = (total_pri1_extra_power+ total_absolute_extra_power - total_pri2_needed_power) * distribution_ratio
            per_cpu_extra_power1 = (total_pri1_extra_power+ total_absolute_extra_power - total_pri2_needed_power) /(group0_size * distribution_ratio + group1_size)
            per_cpu_extra_power0 = per_cpu_extra_power1 * distribution_ratio
            for id in priority_1_list:
                if cpu_list[id].group == 0:
                    cpu_list[id].next_power_limit = cpu_list[id].initial_power_limit +per_cpu_extra_power0
                else:
                    cpu_list[id].next_power_limit = cpu_list[id].initial_power_limit +per_cpu_extra_power1
            for id in priority_0_list:
                if cpu_list[id].group == 0:
                    cpu_list[id].next_power_limit += per_cpu_extra_power0
                else:
                    cpu_list[id].next_power_limit += per_cpu_extra_power1
        else:
            print "total_pri1_extra_power+ total_absolute_extra_power < total_pri2_needed_power"
            for i in range(num_cpu):
        	    cpu_list[i].next_power_limit= cpu_list[i].initial_power_limit
    for id in range(num_cpu):
        print str(id)+'--->next_power_limit:'+str(cpu_list[id].next_power_limit)+',current_power_limit:'+str(cpu_list[id].current_power_limit)+',current_power:'+str(cpu_list[id].current_power)+',priority:'+ str(cpu_list[id].priority) 
    

    for i in range(num_node):
        #RaplSetPower $id $power1 $power2
        os.system('ssh -tt '+server_name_list[i]+' "sudo /scratch/huazhe/tool/power/RaplSetPowerSocket '+str(cpu_list[2*i].next_power_limit)+' '+str(cpu_list[2*i+1].next_power_limit)+' >/dev/null" &')
        runtime_info.write(str(cpu_list[2*i].current_power_limit)+':')
	runtime_info.write(str(cpu_list[2*i].current_power)+':')
        runtime_info.write(str(cpu_list[2*i].priority)+', ')

        runtime_info.write(str(cpu_list[2*i+1].current_power_limit)+':')
        runtime_info.write(str(cpu_list[2*i+1].current_power)+':')
        runtime_info.write(str(cpu_list[2*i+1].priority)+'     ')
        cpu_list[2*i].current_power_limit = cpu_list[2*i].next_power_limit
        cpu_list[2*i+1].current_power_limit = cpu_list[2*i+1].next_power_limit


    runtime_info.write('\n')
    if os.path.isfile('/scratch/huazhe/signal/END_runtime'):
        END_signal = 1
runtime_info.close()
final_power= front_end_power_per_node + back_end_power_per_node - 20
for i in range(len(server_name_list)):
    os.system('ssh -tt '+server_name_list[i]+' "sudo /scratch/huazhe/tool/power/RaplSetPowerSocket '+str(final_power/2)+' '+str(final_power/2)+' >/dev/null" &')

