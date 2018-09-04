frontend_powercap=$1
backend_powercap=$2
final_power=$(echo "$frontend_powercap + $backend_powercap -20"|bc)
frontend_list=(ubuntu-3 ubuntu-4 ubuntu-5 node-5 node-19 node-408 node-50 node-28 node-52 node-37 node-14 node-4 node-18)
backend_list=(ubuntu-6 ubuntu-7 ubuntu-8 node-64 node-49 node-3 node-13 node-46 node-45 node-24 node-11 node-10 node-56)
server_binary=/scratch/huazhe/Project/DistPwrCtrl/scripts/DistPwrServer.py
client_binary=/scratch/huazhe/Project/DistPwrCtrl/scripts/DistPwrClient.py
path=$(pwd)



python $server_binary &

#cd $path;python $binary $frontend_powercap $node $final_power &
for node in ${frontend_list[@]};do
#    ssh -n -f $node "sh -c 'cd $path; nohup python $binary $frontend_powercap $node $final_power &'" &
    ssh $node "cd $path; python $client_binary $frontend_powercap $node $final_power" &
done

for node in ${backend_list[@]};do
#    ssh -n -f $node "sh -c 'cd $path; nohup python $binary $backend_powercap $node $final_power &'" &
    ssh $node "cd $path; python $client_binary $backend_powercap $node $final_power" &
done
