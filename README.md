# dreamr-botnet
Dreamr peer-to-peer botnet. Other security analysts can use this code for the purpose of education, writing protection software, and prevention of future cyber attacks.

Authors:
reoky and C-0x1

## Notice
This code has been posted here in good faith that security researchers can use this code to improve their software, and overall Internet security. It is not intended for evil. That being said, there are several intentional mistakes to prevent malicious use.

## Okay so what can this code do?
Upon execution this implant copies itself into memory, reads from the PE Manifest, or the area just outside the PE container. (That does not corrupt it), and obtains an initial list of hosts. Then the implant generates a key pair and uses it to communicate and join the network.

Commands are issued via the lucid-dreamr panel. Lucid's keys are ultimately trusted, and are used to issue commands to any single bot that will then propagate the message throughout the network. The network follows a decentralized client-server model where each implant chooses which roles can be fulfill. The implant may become a server if it has a global IP, or a client, if the infected machine is behind a firewall and UPnP is not available. 

## Features
dreamr is rather verbose as it will disable UAC, Windows Firewall, Corrupt AV programs, suppress system notifications, system restore, shadow files, defender, telemetry services, lock the hidden file setting (and hide self), turn off automatic sample submission, shutdown a range of debugging programs including Wireshark.
You may also find the implant forwarding ports, hosting a webserver, ftp server, and hooking into the browser. The inplant swaps out the Firefox keystore with one that has exceptions for its own interal proxy, then it configures Firefox to forward traffic through the proxy. Often called a 'grabber', this technique allows for the collection of POSTed form data and sensitive credentials.

## Spreading
One area of particular concern for vendors is malware that can manipulate network traffic. Dreamr uses a module called mare which will conduct TCP timing attacks in order to inject malicious executables into web pages, or swap out downloaded executables with malicious ones. This technique in combination with social engineering is very powerful.

## Collection
In order to retrive logs from a host or range of hosts a command can be issued, along with a selector that matches any number of hosts, instructing them to return keystrokes, files, certs, docs, etc.

## Source
Have a look at the source code: https://github.com/YinAndYangSecurityAwareness/dreamr-botnet/tree/master/drmctchr

## How do I test?
In an airgapped environment. Dreamr detects your VM and self-destructs.
