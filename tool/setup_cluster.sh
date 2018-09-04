cmd1="sudo modprobe msr"
cmd2="sudo /scratch/huazhe/tool/power/set-perms.sh"
cmd3="/scratch/huazhe/tool/power/pySetCPUSpeed.py -S 0"
node_list=(ubuntu-3 ubuntu-4 ubuntu-5 node-5 node-19 node-408 node-50 node-28 node-52 node-37 node-14 node-4 node-18 ubuntu-6 ubuntu-7 ubuntu-8 node-64 node-49 node-3 node-13 node-46 node-45 node-24 node-11 node-10 node-56)

for node in "${node_list[@]}";do
ssh -t $node $cmd1 
ssh -t $node $cmd2
ssh -t $node $cmd3
done
