# CanBusMonitor
Simple python scrip for viewing, filtering and logging system frame on the CAN BUS of your car.

The script toggles the ELM to monitoring mode "AT MA" and increases the serial speed up to 230400 bps. (You can do it only on USB ELM. Bluetooth one do not support such speed)

The script can setup hardware filter by -a parameter or software filter by editing "filter = []" list  

statsfilter = ['OK','at ','AT ','ELM','STO','327','CAN'] is using for excluding lines from statistics

