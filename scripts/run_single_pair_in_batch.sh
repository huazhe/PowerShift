#global variables
source /scratch/huazhe/Project/DistPwrCtrl/environment.sh
RAPL_POWER_MON=/scratch/huazhe/tool/power/RaplPowerMonitor_1s_serverID
RAPL_POWER_LMT=/scratch/huazhe/tool/power/RaplSetPower
OFFLINE_DECIDER=/scratch/huazhe/Project/DistPwrCtrl/scripts/DistributedPowerControl.py
POWER_ALLOCATOR=/scratch/huazhe/Project/DistPwrCtrl/scripts/powerAllocator.py
DIST_POWER_RUNTIME=/scratch/huazhe/Project/DistPwrCtrl/scripts/run_distribute_runtimer.sh
SIGNAL_PATH=/scratch/huazhe/signal

app_pair=$1
controller=$2
env_file=/scratch/huazhe/Project/DistPwrCtrl/scripts/arg/"$app_pair".sh
source node_list.sh
source $env_file

FRONTEND_CHARACTERIZATION=/scratch/huazhe/Project/DistPwrCtrl/results/characterization/"$frontend_app_name"_"$backend_app_name"/"$frontend_app_name"_characterization.results
BACKEND_CHARACTERIZATION=/scratch/huazhe/Project/DistPwrCtrl/results/characterization/"$frontend_app_name"_"$backend_app_name"/"$backend_app_name"_characterization.results
mkdir -p /scratch/huazhe/Project/DistPwrCtrl/results/"$frontend_app_name"_$backend_app_name/$controller/$frontend_app_name
mkdir -p /scratch/huazhe/Project/DistPwrCtrl/results/"$frontend_app_name"_$backend_app_name/$controller/$backend_app_name


#for POWER_CAP in 70 80 90 100 110 120;do
for POWER_CAP in 70;do
    if [ $controller != 'naive' ];then
        output_string="$(python $OFFLINE_DECIDER $FRONTEND_CHARACTERIZATION $BACKEND_CHARACTERIZATION $POWER_CAP)" 
        frontend_cap=$(echo $output_string| awk '{print $2}') 
        backend_cap=$(echo $output_string| awk '{print $3}')
        mode=$(echo $output_string|awk '{print $1}')
        dist_ratio=$(echo $output_string|awk '{print $4}')

    else
        frontend_cap=$POWER_CAP
        backend_cap=$POWER_CAP
        mode='void'
    fi
    power_cap_one_idle=$((2*$POWER_CAP - 20))
    if [ -f $SIGNAL_PATH/END_runtime ];then
        rm $SIGNAL_PATH/END_runtime
    fi
  #  cd /scratch/huazhe/Project/DistPwrCtrl/scripts/"$frontend_app_name"_$backend_app_name/

    ssh -tt ubuntu-6 "sudo rm -r $SIGNAL_PATH/END_'$frontend_app_name'_*"
    start_time=`date +%s`
    ssh -tt ubuntu-6 "/scratch/huazhe/Project/DistPwrCtrl/scripts/backend_batch.sh $backend_cap $controller $power_cap_one_idle $env_file" &
#    sudo rm PowerResults*.txt
    for i in {1..10}
        do
        tmp_time=`date +%s`
	if [ $i -eq 1 ];then
	    for node in "${frontend_node_list[@]}";do
                ssh -tt $node "sudo $RAPL_POWER_LMT $power_cap_one_idle" &
	    done
	    cd /scratch/huazhe/Project/DistPwrCtrl/results/"$frontend_app_name"_$backend_app_name/$controller_name
#	    if [ -f PowerResultsnode-20.cs.uchicago.edu ];then
	    sudo rm -f PowerResults*
#	    fi
            for node in "${frontend_node_list[@]}"; do
                ssh -n -f $node "sh -c 'cd /scratch/huazhe/Project/DistPwrCtrl/results/'$frontend_app_name'_$backend_app_name/'$controller'; nohup sudo $RAPL_POWER_MON $node > /dev/null 2>&1 &'" &>/dev/null &

            done
	   #sudo $RAPL_POWER_MON &> /dev/null &
        else
            if [ $i -eq 2 ];then
                for node in "${frontend_node_list[@]}"; do
                    ssh -t $node "sudo $RAPL_POWER_LMT $frontend_cap" &
                done
                #launch power allocator
                cd /scratch/huazhe/Project/DistPwrCtrl/results/"$frontend_app_name"_$backend_app_name/$controller
	        rm -f END
                if [ $controller = 'dynamic' ];then
                    python $POWER_ALLOCATOR $frontend_cap $backend_cap $dist_ratio &
	        fi
                ##distributing verstion
                if [ $controller = 'distributed' ];then
                    echo "run distributed runtimer, frontend power cap is $frontend_cap, backend power cap is  $backend_cap ."
                    $DIST_POWER_RUNTIME $frontend_cap $backend_cap &
                fi
                ##
                #for node in "${frontend_node_list[@]}"; do
		#    ssh -t $node "sudo $RAPL_POWER_LMT $frontend_cap" &
	        #done
            fi
        fi	

	echo "start $i th $frontend_app_name"

        cd $frontend_folder
        eval $frontend_cmd        

        ssh -tt ubuntu-6 "touch $SIGNAL_PATH/END_'$frontend_app_name'_$i"
	echo "finished $i th $frontend_app_name"
        crt_time=`date +%s`
	
	echo `expr $crt_time - $tmp_time` >>/scratch/huazhe/Project/DistPwrCtrl/results/"$frontend_app_name"_$backend_app_name/$controller/$frontend_app_name/time_line.txt
	done
#sudo pkill powerAllo
    touch $SIGNAL_PATH/END_runtime
    cd /scratch/huazhe/Project/DistPwrCtrl/results/"$frontend_app_name"_$backend_app_name/$controller
    #for j in 6 7 8;do
    #    ssh -t ubuntu-$j "sudo $RAPL_POWER_LMT $power_cap_one_idle"
    #done


    end_time=`date +%s`
    for node in ${frontend_node_list[@]}; do
        ssh -tt $node "sudo pkill Rapl" &
    done
    time=`expr $end_time - $start_time`
    socket_power_array=()
    index=0
    total_power=0
    for node in ${frontend_node_list[@]}; do
    socket_power_array[$index]=`cat PowerResults"$node" |awk '{ if ($2 > 0) {total += $2;count += 1}} END { print total/count}'`
    total_power=$( echo $total_power + ${socket_power_array[$index]} |bc)
    index=$((index + 1))
    socket_power_array[$index]=`cat PowerResults"$node" |awk '{ if ($3 > 0) {total += $3;count += 1}} END { print total/count}'`
    total_power=$( echo $total_power + ${socket_power_array[$index]} |bc)
    index=$((index + 1))
    done
    frontend_energy=$(echo "scale=10;$total_power * $time "|bc) 
    echo $start_time $time ${socket_power_array[*]} $frontend_energy >> ./"$frontend_app_name"/"$frontend_app_name"_"$backend_app_name"_frontend.results
#fi 
    while [ ! -f $SIGNAL_PATH/backend_END ];do
        sleep 1
    done

    sleep 10

    mkdir -p time-series
    sudo mv -f PowerResult* ./time-series
    total_time=$(cat ./"$backend_app_name"/"$frontend_app_name"_"$backend_app_name"_backend.results| tail -1|awk '{print $2}')
    backend_energy=$(cat ./"$backend_app_name"/"$frontend_app_name"_"$backend_app_name"_backend.results| tail -1|awk '{print $9}') 
    total_energy=$(echo "scale=10; $backend_energy + 390 * ($total_time - $time) + $frontend_energy"|bc)
    echo $POWER_CAP $mode $total_time $total_energy >> ./"$frontend_app_name"_"$backend_app_name".results
    sleep 3
done

ssh -tt ubuntu-6 "rm -r $SIGNAL_PATH/END_'$frontend_app_name'_*"
