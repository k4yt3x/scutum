# SCUTUM Firewall
### Usage:

1. Put this application in wicd post connect scripts folder:
	cp scutum.py /etc/wicd/scripts/postconnect/scutum

2. Set the attributes correctly:
~~~~
	chmod 755 /etc/wicd/scripts/postconnect/scutum
	chown root: /etc/wicd/scripts/postconnect/scutum
~~~~
3. Reload wicd service:
~~~~
	service wicd restart
	#If this doesn't work, reboot
~~~~

4. You're ready to roll

Log file is at /var/log/scutum.log
