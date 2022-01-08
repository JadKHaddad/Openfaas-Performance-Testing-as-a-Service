# Performance Testing Service - Evaluation - Instractions

## Old system

Log in to the test server with **SSH** using the given username and password:
```sh
ssh user_56@167.172.184.208
```
```sh
user_56@167.172.184.208`s password: 123456
```
Start **tmux** to be able to open multiple tabs:
```sh
tmux
```
Navigate to the old system's folder:
```sh
cd locust_scripts
```
To see all available tests use:
```sh
ls locust
```
```sh
gen_gs_alarm_device_workload.py  gen_gs_prod_workload.py  locust_teastore.py
```
Now run **gen_gs_prod_workload** test, remember you should be in **locust_scripts** directory:
```sh
python3 executor.py locust/gen_gs_prod_workload.py
```
While this test is running open a new tab: hold ```ctr + b``` then click ```c``` .
<br /><br />
To start a new test, for example **gen_gs_alarm_device_workload**, navigate to the old system's folder again and run the test:
```sh
cd locust_scripts
python3 executor.py locust/gen_gs_alarm_device_workload.py
```
To stop the test hit ```ctr + b``` . Exit the current tmux tab:
```sh
exit
```
Now you are in the old tmux tab. Stop the runnig test with ```ctr + c``` .
<br /><br />
To see the results of the last test run:
```sh
python3 loadtest_plotter.py
```
Pass the log file path:
```sh
Path to the logfile: locust_log.log
```
You won't see any plots because you are in a shell :) , if you really want to see a colorful plot, clone the original project to your desktop environment: ```github.com/jtpgames/Locust_Scripts```
<br /><br />
Delete the generated files:
```sh
rm *.csv
rm executor.log
rm locust_log.log
```
Now exit the tmux tab
```sh
exit
```
Log out:
```sh
exit
```
Or you can stay a bit longer and explore the old system.

## New system