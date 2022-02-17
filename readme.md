# Performance Testing Service - Evaluation - Instructions

## Old system

Log in to the test server with **SSH** using your given username and password:
```sh
ssh user_56@167.172.184.208
```
```sh
user_56@167.172.184.208`s password: 123456
```
You don't have an SSH client? Use an online SSH client like [sshwifty](https://sshwifty.herokuapp.com/)<br /><br />
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
To stop the test hit ```ctr + c``` . Exit the current tmux tab:
```sh
exit
```
Now you are in the old tmux tab. Stop the running test with ```ctr + c``` .
<br /><br />
To see the results of the last test run:
```sh
python3 loadtest_plotter.py
```
Pass the log file path:
```sh
Path to the logfile: locust_log.log
```
You won't see any plots because you are in a shell :) , if you really want to see a colorful plot, clone the original [project](https://github.com/jtpgames/Locust_Scripts/) to your desktop environment.
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

Navigate to the given URL and choose the first project.

![Home](/screenshots/Home.png)

Choose **gen_gs_prod_workload** to navigate to the test's page.

![Project](/screenshots/Project.png)

Now you are on the test's page. To start the test, click on the ```start button```.

![Start](/screenshots/Start.png)

This window will appear, where you can specify your parameters. This is an evaluation system, so you can't change them. Click on the ```start button``` to start a test.

![TestParameter](/screenshots/TestParameter.png)

The test is now running. To stop it, click on the ```stop button```.

![Stop](/screenshots/Stop.png)

After stopping the test, you will be able to see the results by clicking on the ```show results button```.

![ShowResults](/screenshots/ShowResults.png)

The results look like this!

![Results](/screenshots/Results.png)

Top delete the test, click on the ```delete button```.

![Delete](/screenshots/Delete.png)

Now go back to the previous page and select another test: **gen_gs_alarm_device_workload**, and repeat the same steps if you feel like it :)

![AnotherTest](/screenshots/AnotherTest.png)

You are free to navigate through the website and do whatever you want, However some features are not available, since this is an evaluation system. Can you find them all? ;)

### That's it! Thank you for your time and have a nice day!
