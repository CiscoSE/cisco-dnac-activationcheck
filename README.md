# Cisco DNA Center Activation Check

*Gathering proof of “in-use” activation for Cisco DNA Center when telemetry is not on.*

---

## Why?
Simplify the customer process and workflow of Gathering proof of “in-use” activation for Cisco DNA Center.
Use this automated process to gather proof of “in-use” activation only when you don't have telemetry turned on.
The preferred method continues to be turning on telemetry.
With this process data is automatically gathered and filtered.


## Features

- Login into the DNA Center Appliance given as input
- Activation Check data gathering for Wireless Assurance
- Activation Check data gathering for SDA
- Data export and encrypt
- Executable created for each OS platform -> **DOWNLOAD** from the **Release Tab**


## Show Me!
![Alt text](/../master/screenshot.png?raw=true "Mac OS Example")


## Technologies & Frameworks Used

This is Cisco Sample Code!

**Cisco Products & Services:**

- Cisco DNA Center
  - Example: https://sandboxdnac.cisco.com

**Prerequisites**

- DNA Center with NB REST API Bundle enabled
  - in order for the Cisco DNA Center Activation Check to work NB REST API Bundle MUST be enabled
- DNA Center hostname and credentials

**Dependencies**

NONE. There are 3 executables one for each supported OS platform:
- Windows OS
- Linux OS
- Mac OS

**Chose the one suited for your Environment, download it and run it.**

**Tools & Frameworks:**

- Python3
- File Encryption


## Usage

**For Windows OS:**
- Download the actcheckwindows from the Release Tab
- Open the executable by double clicking
- Provide the hostname and credentials
- Confirm the Activation Checker process by typing in yes
- Wait for the "DONE - Data saved in file ..." message
  - in case of partial run(fail) acknowledge the error, press enter and try again
- Press enter to close the application
- You will notice two new files in the same folder with the executable
  - One is a .txt file encrypted which is the file that will be emailed for valdiation
  - The other one is a .json file detailing the information gathered

**For Linux OS:**
- Download the actchecklinux from the Release Tab
- Run the executable: ```./actchecklinux```
  - if the app is not executed, verify if the execute option is set, chmod +x actchecklinux
- Provide the hostname and credentials
- Confirm the Activation Checker process by typing in yes
- Wait for the "DONE - Data saved in file ..." message
  - in case of partial run(fail) acknowledge the error, press enter and try again
- Press enter to close the application
- You will notice two new files in the same folder with the executable
  - One is a .txt file encrypted which is the file that will be emailed for valdiation
  - The other one is a .json file detailing the information gathered

**For Mac OS:**
- Download the actcheckmac from the Release Tab
- Run the executable: ```./actcheckmac```
  - if the app is not executed, verify if the execute option is set, chmod +x actcheckmac
- Provide the hostname and credentials
- Confirm the Activation Checker process by typing in yes
- Wait for the "DONE - Data saved in file ..." message
  - in case of partial run(fail) acknowledge the error, press enter and try again
- Press enter to close the application
- You will notice two new files in the same folder with the executable
  - One is a .txt file encrypted which is the file that will be emailed for valdiation
  - The other one is a .json file detailing the information gathered


**Example run on Mac OS**
```./actcheckmac```

```---Welcome - Please enter the following information:
---Host address: sandboxdnac.cisco.com
---Username: devnetuser
---Password:
-----Creating DNAC profile for sandboxdnac.cisco.com
-----Running Activation Check on sandboxdnac.cisco.com
---Please confirm Activation Check on sandboxdnac.cisco.com, type in yes or no: yes
-----Counting system hosts
-----Retrieving system hosts
-----Counting network devices
-----Retrieving network devices inventory list
-----Analyzing fabric and extracting relevant numbers
-----Retrieving fabric domains and transits inventory list
-----Retrieving fabric pool ids inventory by site
-----Retrieving fabric devices inventory by site
-----Filtering fabric devices inventory list
-----Retrieving fabric devices inventory list
---DONE - Data saved in file dna-20190629-200631.txt
```


## Authors & Maintainers

- Cisco DAT TEAM EMEAR (<opreda@cisco.com>, <wrog@cisco.com>)


## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
