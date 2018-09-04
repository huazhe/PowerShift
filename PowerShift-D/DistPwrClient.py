import os,sys,math,subprocess,time,socket,math

server_address = ('ubuntu-3', 10000)


powercap=float(sys.argv[1])
server_name=str(sys.argv[2])
finalpower=float(sys.argv[3])
#exchanger_node='ubuntu-3'
cpu_list=[]
END_signal =0
frequency = 2
default_frequency=2
half_frequency=1
power_margin=3
half_power_margin=1
return_value=''
#runtime_info=open('runtime_info'+server_name+'.txt','w')
#power_lock='/home/huazhe/Project/DistPwrCtrl/scripts/extra_power_lock.sh'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        self.urgent = 0
        self.whichend=-1

#read last window average power
def ReadPower():
    FileName = 'PowerResults'+server_name
    Powerlist = open(FileName,'r').readlines()[-9:]
    power1=0.0
    power2=0.0
    for i in range(len(Powerlist)):
        power1 += float(Powerlist[i].split()[1])
        power2 += float(Powerlist[i].split()[2])
    power1 = power1/len(Powerlist)
    power2 = power2/len(Powerlist)
    return power1,power2

def SetPower(index,power):
    if index ==0:
        os.system("sudo /home/huazhe/tool/power/RaplSetPowerSingleSocket "+str(power)+" 0 >/dev/null")
    else:
        os.system("sudo /home/huazhe/tool/power/RaplSetPowerSingleSocket 0 "+str(power)+" >/dev/null")

for i in range(2):
    cpu_tmp = cpu(i)
    cpu_tmp.initial_power_limit=powercap/2
    cpu_tmp.current_power_limit=powercap/2
    cpu_list.append(cpu_tmp)


#connect to the server
sock.connect(server_address)

while(END_signal !=1):
  #  os.system("sleep "+str(frequency))
    time.sleep(int(frequency))
    
    cpu_list[0].current_power,cpu_list[1].current_power = ReadPower()
    #check if we have extra power
    actual_get_power,release_power=0,0
    for i in range(2):
        actual_get_power,release_power=0,0
        print 'power, power_limit=',cpu_list[i].current_power,cpu_list[i].current_power_limit
        if cpu_list[i].current_power < cpu_list[i].current_power_limit - power_margin - 0.01:
            #post extra power
            extra_power =  math.floor(cpu_list[i].current_power_limit - power_margin *0.5 - cpu_list[i].current_power)
            print 'extra power=',extra_power
            cpu_list[i].next_power_limit = cpu_list[i].current_power_limit - extra_power
            SetPower(i,cpu_list[i].next_power_limit)
            cpu_list[i].current_power_limit = cpu_list[i].next_power_limit
            if cpu_list[i].urgent==1:
         #       return_value=subprocess.check_output(['ssh', exchanger_node, power_lock,str(extra_power),'0','-1'])
                urgent_change = -1
            else:
          #   return_value=subprocess.check_output(['ssh', exchanger_node,power_lock,str(extra_power),'0','0'])
                urgent_change = 0
            msg =str(extra_power)+','+'0'+','+str(urgent_change)+',0,'+str(cpu_list[i].current_power_limit)
            #sock.send(msg)
            try:
                sock.send(msg)
                return_value = sock.recv(1024)
                actual_get_power=float(return_value.split(',')[0])
                release_power=int(return_value.split(',')[1])
            except:
                sock.close()
                break
            cpu_list[i].urgent=0
            if release_power == 1 and cpu_list[i].current_power_limit  > cpu_list[i].initial_power_limit:
                available_release_power= cpu_list[i].current_power_limit - cpu_list[i].initial_power_limit
                cpu_list[i].current_power_limit = cpu_list[i].initial_power_limit
                SetPower(i,cpu_list[i].current_power_limit)
                msg =str(available_release_power)+','+'0'+','+'0'+',0,'+str(cpu_list[i].current_power_limit)
                #sock.send(msg)
                try:
                    sock.send(msg)
                except:
                    sock.close()
                    break
                return_value = sock.recv(1024)


                
        elif cpu_list[i].current_power > cpu_list[i].current_power_limit - power_margin * 0.5:
            #need power
            if cpu_list[i].current_power_limit > cpu_list[i].initial_power_limit: 
                #not necessary, check if need_power file is 0, if not get power from extra
                if cpu_list[i].urgent==1:
                #return_value=subprocess.check_output(['ssh',exchanger_node,power_lock,'0','0','-1'])
                    urgent_change = -1

                else:
                #    return_value=subprocess.check_output(['ssh', exchanger_node,power_lock,'0','0','0'])
                    urgent_change = 0
                msg ='0'+','+'0'+','+str(urgent_change)+',0,'+str(cpu_list[i].current_power_limit)
                #sock.send(msg)
                try:
                    sock.send(msg)
                    cpu_list[i].urgent=0
                    return_value = sock.recv(1024)
                    actual_get_power=float(return_value.split(',')[0])
                    release_power=int(return_value.split(',')[1])
                except:
                    sock.close()
                    break
                               
                if release_power == 1 :
                    available_release_power= cpu_list[i].current_power_limit - cpu_list[i].initial_power_limit
                    cpu_list[i].next_power_limit = cpu_list[i].current_power_limit -available_release_power
                    cpu_list[i].current_power_limit =cpu_list[i].next_power_limit 
                    SetPower(i,cpu_list[i].next_power_limit)
                    msg =str(available_release_power)+','+'0'+','+'0'+',0,'+str(cpu_list[i].current_power_limit)+',initial_limit'
                    #sock.send(msg)
                    try:
                        sock.send(msg)
                    except:
                        sock.close()
                        break
                    cpu_list[i].urgent=0
                    return_value = sock.recv(1024)
                else:
                    cpu_list[i].next_power_limit = cpu_list[i].current_power_limit + actual_get_power
                    SetPower(i,cpu_list[i].next_power_limit)
                    cpu_list[i].current_power_limit =cpu_list[i].next_power_limit

            #necessary
            else:
                necessary_power= math.ceil(cpu_list[i].initial_power_limit - cpu_list[i].current_power_limit)
                if cpu_list[i].urgent==0:
                    urgent_change = 1
                 #   return_value=subprocess.check_output(['ssh', exchanger_node,power_lock,'0','1','1',str(necessary_power)])
                else:
                    urgent_change =0
                    #return_value=subprocess.check_output(['ssh', exchanger_node,power_lock,'0','1','0',str(necessary_power)])
                msg ='0'+','+'1'+','+str(urgent_change) +','+ str(necessary_power)+','+str(cpu_list[i].current_power_limit)
                try:
                    sock.send(msg)
                    return_value = sock.recv(1024)
                    cpu_list[i].urgent= 1
                    actual_get_power,release_power=float(return_value.split(',')[0]),int(return_value.split(',')[1])
                except:
                    sock.close()
                    break
                if actual_get_power >=necessary_power:
                    cpu_list[i].urgent=0
                    
                if actual_get_power != 0:
                    cpu_list[i].next_power_limit = cpu_list[i].current_power_limit + actual_get_power
                    SetPower(i,cpu_list[i].next_power_limit)
                    cpu_list[i].current_power_limit =cpu_list[i].next_power_limit
        else:
            print 'stable state'
            if cpu_list[i].urgent==1:
                urgent_change = -1
            else:
                urgent_change = 0
            msg ='0'+','+'2'+','+str(urgent_change)+',0'+str(cpu_list[i].current_power_limit)
            ##sock.send(msg)
            try:
                sock.send(msg)
                return_value = sock.recv(1024)
                cpu_list[i].urgent=0
                actual_get_power=float(return_value.split(',')[0])
                release_power=int(return_value.split(',')[1])
            except:
                sock.close()
                break

            if release_power == 1 and cpu_list[i].current_power_limit  > cpu_list[i].initial_power_limit:
                # return to initital power limit
                available_release_power= cpu_list[i].current_power_limit - cpu_list[i].initial_power_limit
                cpu_list[i].current_power_limit = cpu_list[i].initial_power_limit
                SetPower(i,cpu_list[i].current_power_limit)
                msg =str(available_release_power)+','+'0'+','+'0'+',0,'+str(cpu_list[i].current_power_limit)+',initial_limit'
                #sock.send(msg)
                try:
                    sock.send(msg)
                except:
                    sock.close()
                    break
                return_value = sock.recv(1024)            


    #runtime_info.write(str(time.ctime())+'-->'+str(cpu_list[0].current_power_limit)+':')
    #runtime_info.write(str(cpu_list[0].current_power)+',')
    #runtime_info.write(str(cpu_list[1].current_power_limit)+':')
    #runtime_info.write(str(cpu_list[1].current_power)+'   '+str(actual_get_power)+','+str(release_power)+'\n')

    if cpu_list[0].urgent ==1 or cpu_list[1].urgent==1:
        frequency = half_frequency
    else:
        frequency = default_frequency
#    print server_name,cpu_list[0].current_power_limit,cpu_list[1].current_power_limit
    if os.path.isfile('/home/huazhe/signal/END_runtime'):
        END_signal = 1
os.system('sudo /home/huazhe/tool/power/RaplSetPowerSocket '+str(finalpower/2)+' '+str(finalpower/2)+' >/dev/null')
#runtime_info.close()
sock.close()
