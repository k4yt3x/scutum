[![Join the chat at https://gitter.im/K4YT3X-DEV/SCUTUM](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/K4YT3X-DEV/SCUTUM?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![status](https://travis-ci.org/K4YT3X/SCUTUM.svg)](https://travis-ci.org/K4YT3X/SCUTUM)

# SCUTUM Firewall

#### Current Version: 2.6.0 beta 4

### This is an UNSTABLE version

~~**It is now recommended to upgrade scutum with --upgrade parameter** (since 2.5.2)~~  
Never mind. Please run the installation below again manually.

<br>

## Quick Install
### Prerequisites
* Designed for Linux OS
* `curl` or `wget` is required for quick install
* `git` should be installed

**SCUTUM Dependencies can be found in [DEPENDENCIES.md](https://raw.githubusercontent.com/K4YT3X/SCUTUM/master/DEPENDENCIES.md))**

**via curl**
~~~~
$ sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/K4YT3X/SCUTUM/master/quickinstall.sh)"
~~~~

**via wget**
~~~~
$ sudo sh -c "$(wget https://raw.githubusercontent.com/K4YT3X/SCUTUM/master/quickinstall.sh -O -)"
~~~~

</br>

#### Current Version Change log:
1. Fixed & Improved the Installation Mathod
1. Changed TCP/UDP/ICMP Firewall to UFW
1. Added new logger
1. Added Easy TCP port manager
1. Created different class for adapter controller
1. Created different class for Installer
1. Registers SCUTUM as a systemd system service
1. Changed the way configurations are being stored (configparser)

![scutum_gui](https://user-images.githubusercontent.com/21986859/29802954-bb3475f2-8c46-11e7-8c21-efae476ac5a6.png)

#### TODO:
1. Change SCUTUM GUI to adapt systemd
1. Create .deb package
1. Add dynamic inspection?
1. Fix loggin format error
1. Fix options for iptables firewall


#### Recent Changes:
1. Added Self-Upgrading Function, now users can execute self-upgrading with $ sudo scutum --upgrade
1. Added AVALON Framework Self-Upgrading function (included when using "--upgrade" parameter)
1. Interfaces are now controlled by a new interface controller class
1. SCUTUM GUI is now avaliable for testing
1. Added option to choose whether to delete the installer file after installation
1. Fixed arptables detection errors on some Linux distributions

<br>
<p align="center"> 
<img src="https://user-images.githubusercontent.com/21986859/27760965-d228eda6-5e29-11e7-9ba6-3d9cc0408fd8.png">
</p>

## What is SCUTUM?
<b>Long story short, ARP firewall. It automatically adds gateways to the whitelist on connect and blocks everthing else to avoid potential threat.</b>

SCUTUM is an ARP firewall that **prevents your computer from being ARP-spoofed** by other computers on LAN. SCUTUM controls "arptables" in your computer so it accepts ARP packets only from the gateway. This way, when people with malicious intentions cannot spoof your arp table. SCUTUM also prevents other people from detecting your device on LAN if SCUTUM is used with properly configured TCP/UDP firewall.

SCUTUM is also capable of handling tcp/udp/icmp traffic with iptables. You can choose to enable this feature during installation. However, a more professional firewall controller like UFW is recommended. They can handle traffic with more precision.

<br>

## Usage & Installation
You should run a installation before running it for the first time for setting up configuration files. 
<b>I am not sure if portable version is necessary. If you think this should be changed, raise an issue and I will change it.</b>
#### Installation
Quick install above is recommended
~~~~
git clone https://github.com/K4YT3X/SCUTUM.git
cd SCUTUM/
sudo python3 scutum.py --install
~~~~

#### GUI Usage (Currently not working)
~~~~
ENABLE: Enable SCUTUM (Start spontaneously)
DISABLE: Disable SCUTUM (Never start spontaneously)
DISABLE (Temporarily): Disable SCUTUM until the next time connected to a network
~~~~


#### Usage
This should be easy
SCUTUM starts <b>automatically</b> by itself after installation
~~~~
$ sudo service scutum start     # Start scutum service
$ sudo service scutum stop      # Stop scutum service
$ sudo systemctl enable scutum  # Start SCUTUM with system
$ sudo systemctl disable scutum # Don't start SCUTUM with system
$ sudo scutum                   # Start SCUTUM Normally
$ sudo scutum --start           # Start SCUTUM Manually for once even it it's disabled
$ sudo scutum --enable          # Enable SCUTUM (Start automatically on connect)
$ sudo scutum --disable         # Disable SCUTUM (Don't start automatically on connect)
$ sudo scutum --reset           # Reset SCUTUM (Allow ALL ARP packages temporarily)
$ sudo scutum --purgelog        # Purge SCUTUM logs
$ sudo scutum --install         # Run scutum installation wizard and install SCUTUM into system
$ sudo scutum --uninstall       # Remove SCUTUM from system completely 
$ sudo scutum --upgrade         # Upgrade SCUTUM and AVALON Framework
~~~~

<br>

## SCUTUM Workflow:
#### postconnect
1. Connect to Wi-Fi
2. Accept all ARP packets
3. Cache gateway MAC address by establishing a socket connection with a timeout of 0
4. Add Gateway MAC to exception
5. DROP all ARP packets

[Finished]


#### postdisconnect
1. Accept all ARP packets

[Finished]
