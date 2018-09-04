source /scratch/huazhe/Project/DistPwrCtrl/environment.sh
RAPL_POWER_MON=/scratch/huazhe/tool/power/RaplPowerMonitor_1s_serverID
RAPL_POWER_LMT=/scratch/huazhe/tool/power/RaplSetPower
backend_cap=$1
controller_name=$2
power_cap_one_idle=$3
env_file=$4
source $env_file
SIGNAL_PATH=/scratch/huazhe/signal
source /scratch/huazhe/Project/DistPwrCtrl/scripts/node_list.sh


cd /scratch/huazhe/Project/DistPwrCtrl/results/"$frontend_app_name"_"$backend_app_name"/"$controller_name"


ssh -tt ubuntu-3 "rm -f $SIGNAL_PATH/backend_END"

echo "start monitor!!!!"
for node in "${backend_node_list[@]}";do
	ssh -n -f $node "sh -c 'cd /scratch/huazhe/Project/DistPwrCtrl/results/"$frontend_app_name"_"$backend_app_name"/$controller_name; nohup sudo $RAPL_POWER_MON $node > /dev/null 2>&1 &'" &
done

#sudo $RAPL_POWER_MON &>/dev/null &
start_time=`date +%s`
for i in {1..10}
    do
    while [ ! -f $SIGNAL_PATH/END_"$frontend_app_name"_$i ]
        do
        sleep 1
    done
    tmp_time=`date +%s`
	
    if [ $i -eq 1 ];then
        for node in ${backend_node_list[@]};do
            ssh -t $node "sudo $RAPL_POWER_LMT $backend_cap" &
        done
    fi
    
    if [ $i -eq 10 ];then
        for node in ${backend_node_list[@]};do
           ssh -t $node "sudo $RAPL_POWER_LMT $power_cap_one_idle" &
         done
    fi
    
            
    echo "$backend_app_name running at $i th run"

    cd $backend_folder
    eval $backend_cmd

    crt_time=`date +%s`
    echo "$backend_app_name $i th run finished"
    echo `expr $crt_time - $tmp_time` >>/scratch/huazhe/Project/DistPwrCtrl/results/"$frontend_app_name"_"$backend_app_name"/"$controller_name"/$backend_app_name/time_line.txt
done    
cd /scratch/huazhe/Project/DistPwrCtrl/results/"$frontend_app_name"_$backend_app_name/$controller_name

touch $SIGNAL_PATH/backend_END
end_time=`date +%s`

for node in ${backend_node_list[@]};do
	ssh -tt $node "sudo pkill Rapl"
done
echo "sudo pkill backend RAPL"
time=`expr $end_time - $start_time`
socket_power_array=()
index=0
total_power=0
for node in ${backend_node_list[@]}; do
    socket_power_array[$index]=`cat PowerResults"$node" |awk '{ if ($2 > 0) {total += $2;count += 1}} END { print total/count}'`
    total_power=$(echo ${socket_power_array[$index]} + $total_power |bc)
    index=$((index + 1))
    socket_power_array[$index]=`cat PowerResults"$node" |awk '{ if ($3 > 0) {total += $3;count += 1}} END { print total/count}'`
    total_power=$(echo ${socket_power_array[$index]} + $total_power |bc)
    index=$((index + 1))
done
backend_energy=$(echo "scale=10;$total_power * $time "|bc) 
echo $end_time $time ${socket_power_array[*]} $backend_energy >> ./$backend_app_name/"$frontend_app_name"_"$backend_app_name"_backend.results

#reset power cap
for node in ${frontend_node_list[@]};do
    ssh -t $node "sudo $RAPL_POWER_LMT 220" &
done
for node in ${backend_node_list[@]};do
    ssh -t $node "sudo $RAPL_POWER_LMT 220" &
done
