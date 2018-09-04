echo "Bash version " ${BASH_VERSION} "..."

for  c in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
#for c in {0..11}
  do

  echo $c
  chmod a+w /sys/devices/system/cpu/cpu$c/cpufreq/scaling_setspeed
  chmod a+w /sys/devices/system/cpu/cpu$c/cpufreq/scaling_min_freq
  chmod a+w /sys/devices/system/cpu/cpu$c/cpufreq/scaling_max_freq
  chmod a+r /sys/devices/system/cpu/cpu$c/cpufreq/cpuinfo_cur_freq
  chmod a+r /dev/cpu/$c/msr

  echo "userspace" >  /sys/devices/system/cpu/cpu$c/cpufreq/scaling_governor
done



