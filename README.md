# SCUTUM Firewall

### What is Scutum?
Scutum is an ARP firewall that prevents your computer from being arp spoofed. Scutum controls "arptables" in your computer so it accepts ARP packets only from the gateway. This way, when people with malicious intentions cannot spoof your arp table. Scutum also prevents other people from detecting your device on LAN if scutum is used with properly configured TCP/UDP firewall.

#
### Usage & Installation
~~~~
git clone https://github.com/K4YT3X/SCUTUM.git
cd SCUTUM/
sudo python3 scutum.py --install
cd ../
rm -rf SCUTUM/
~~~~
