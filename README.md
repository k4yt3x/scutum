[![Join the chat at https://gitter.im/K4YT3X-DEV/SCUTUM](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/K4YT3X-DEV/SCUTUM?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![status](https://travis-ci.org/K4YT3X/scutum.svg)](https://travis-ci.org/K4YT3X/scutum)

# SCUTUM Firewall

## Introduction

**In short, SCUTUM configures your personal computer automatically against malicious TCP/UDP traffic and ARP spoofing attacks.** This software uses UFW to setup conventional firewall for you, determines and locks the gateway MAC address so you won't get ARP-spoofed.

This software is designed to be compact and effective. Currently it can support only one interface at a time. Traffic will only be allowed on one interface. We are looking into possibilities of supporting multiple interfaces at once.

## 2.10.0 (November 2, 2018)

1. Fixed the problem when SCUTUM is first enabled, gateway MAC address is not
   cached and locked.

## 2.10.0 (October 31, 2018)

1. Changed configuration file to JSON
   - Please delete the old INI config and reinstall `scutum`.
1. Added support for `netfilter`.
1. Grouped sections of code into methods for easier code maintenance.
1. Optimized code.

## Quick Install

### Prerequisites

* Designed for Linux OS
* `curl` or `wget` is required for quick install
* `git` should be installed

**Example for a typical Ubuntu environment (18.04)**
```
$ sudo apt install git python3-pip curl
$ sudo pip3 install avalon_framework
```

**Full SCUTUM Dependency list can be found in [DEPENDENCIES.md](https://github.com/K4YT3X/scutum/blob/master/README.md)**

**via curl**

```
$ sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/K4YT3X/scutum/master/bin/quickinstall.sh)"
```

**via wget**

```
$ sudo sh -c "$(wget https://raw.githubusercontent.com/K4YT3X/scutum/master/bin/quickinstall.sh -O -)"
```

![scutum_gui](https://user-images.githubusercontent.com/21986859/29802954-bb3475f2-8c46-11e7-8c21-efae476ac5a6.png)
![effects](https://user-images.githubusercontent.com/21986859/44294941-86b5da80-a26d-11e8-9ed1-f67171a3f4d2.png)

## What is SCUTUM?

**Long story short, ARP firewall. It automatically adds gateways to the whitelist on connect and blocks everthing else to avoid potential threat.**

SCUTUM is an ARP firewall that **prevents your computer from being ARP-spoofed** by other computers on LAN. SCUTUM controls "arptables" in your computer so it accepts ARP packets only from the gateway. This way, when people with malicious intentions cannot spoof your arp table. SCUTUM also prevents other people from detecting your device on LAN if SCUTUM is used with properly configured TCP/UDP firewall.

SCUTUM is also capable of handling tcp/udp/icmp traffic with iptables. You can choose to enable this feature during installation. However, a more professional firewall controller like UFW is recommended. They can handle traffic with more precision.

## Usage & Installation

You should run a installation before running it for the first time for setting up configuration files. 
<b>I am not sure if portable version is necessary. If you think this should be changed, raise an issue and I will change it.</b>

#### Installation

Quick install above is recommended

```
git clone https://github.com/K4YT3X/scutum.git
cd scutum/bin
sudo python3 scutum.py --install
```

#### GUI Usage (Currently not working)

```
ENABLE: Enable SCUTUM (Start spontaneously)
DISABLE: Disable SCUTUM (Never start spontaneously)
DISABLE (Temporarily): Disable SCUTUM until the next time connected to a network
```

#### Usage

SCUTUM starts **automatically** by itself after installation.

Full up-to-date usage can be found by executing:
```
$ scutum --help
```
```
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
```

## SCUTUM Workflow

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
