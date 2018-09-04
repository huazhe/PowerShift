# PowerShift
Project Description
----------------------------------------
PowerShift is a power capping technique for distribtued dependent workloads.

It tries to maximize the performance while strictly respecting power cap during runtime. For more detailed information, please refer to our paper, Performance & Energy Tradeoffs for Dependent Distributed Applications Under System-wide Power Caps: https://dl.acm.org/citation.cfm?id=3225098

This repo is still under construction, if you have any question, plz contact huazhe@cs.uchicago.edu.

Directory Structure  
----------------------------------------
.  

├── OfflineDecider  -- Offline decider deriving the optimal static power allocation

├── PowerShift-C    -- Centralized dynamic power capping approach 

├── PowerShift-D    -- Distributed dynamic power capping approach

├── scripts   -- Scripts used to launch paired application with PowerShift runtime

└── tools     -- Tools for node-level power capping(through RAPL) and setting up experiment environment
