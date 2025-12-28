---
title: "DECserver"
source: "https://en.wikipedia.org/wiki/DECserver"
---

Product line of terminal servers

**DECserver** is a discontinued family of asynchronous [console server](/wiki/Console_server "Console server"), [terminal server](/wiki/Terminal_server "Terminal server"), and [print server](/wiki/Print_server "Print server") products introduced by [Digital Equipment Corporation](/wiki/Digital_Equipment_Corporation "Digital Equipment Corporation") (DEC). The DECserver brand later became used for a class of UNIX-variant application and file server products based upon the [MIPS](/wiki/MIPS_architecture "MIPS architecture") processor. It was a highly successful series of products for DEC; in February 1998, in anticipation of its acquisition by [Compaq](/wiki/Compaq "Compaq"), the company sold its Network Products Business to [Cabletron](/wiki/Cabletron "Cabletron"), which then spun out as its own company, Digital Networks (later known as Vnetek Communications), in September 2000.

## Model history

[[edit](/w/index.php?title=DECserver&action=edit&section=1 "Edit section: Model history")]

DECservers were introduced in 1985. The first model was the DECserver 100. This and all subsequent DECserver models used the [Local Area Transport](/wiki/Local_Area_Transport "Local Area Transport") (LAT) protocol which was/is also supported by many DEC operating systems including [VMS](/wiki/OpenVMS "OpenVMS"), [RSX-11](/wiki/RSX-11 "RSX-11"), [RSTS/E](/wiki/RSTS/E "RSTS/E") and [Ultrix](/wiki/Ultrix "Ultrix") (an implementation of [UNIX](/wiki/Unix "Unix")). All DECservers were designed to boot their operating systems across the network using [DECnet](/wiki/DECnet "DECnet") MOP [Maintenance Operations Protocol](/wiki/Maintenance_Operations_Protocol "Maintenance Operations Protocol") with later models supporting [TCP/IP](/wiki/Internet_protocol_suite "Internet protocol suite") booting using [bootp](/wiki/Bootstrap_Protocol "Bootstrap Protocol") protocol. Later models also support booting from flash memory cards.  
  
**Model Option Numbers, Description and History**

**DECserver 100**  
The DECserver 100 Terminal Server was a network terminal switch for Ethernet Local Area Networks, providing a convenient method to logically connect up to eight DIGITAL asynchronous terminals to one or more service nodes (hosts) on an Ethernet. Through the use of a simple command, users could establish a logical connection, called a session, to any local service node that implemented the LAT protocol.

Model Number: DSRVA-\*\*
Ports: 8 DB25  
Alternate product: DECserver 708, 8 ports DB9, DSRVW-R\*

**DECserver 200**
The DECserver 200 was a network terminal switch for Ethernet Local Area Networks, providing a convenient method to logically connect up to eight Digital asynchronous terminals to one or more service nodes (hosts) on an Ethernet. The DECserver 200 also provided the capability to connect host systems that did not support the LAT protocol, Digital personal computers, and dial-out modems directly to ports on the server. The DECserver 200 implemented the Local Area Transport (LAT) protocol for communication with service nodes that implemented this protocol on the same Ethernet. There were two options of DECserver 200 hardware: the DECserver 200/MC, which contained RS-232-C lines with full modem control (DSRVB-AB) and the DECserver 200/DL, which contained [DECconnect](/w/index.php?title=DECconnect&action=edit&redlink=1 "DECconnect (page does not exist)") lines with data leads only (DSRVB-BB). The /DL version delivers these data leads through a single connector (similar to Centronics printer connection). A special cable connects the DECserver to a "harmonica", with the same style of mass-connector, plus 8 MMJ jacks, positioned close to the terminals to be connected.

Model Number: DSRVB-\*\*
Ports: 8 DB25 (/MC) or 8 MMJ (/DL)  
Alternate product: DECserver 708, 8 ports DB9, DSRVW-R\*

**DECserver 250**  
The DECserver 250 was a network server for printers for Ethernet Local Area Networks, consisting of a single box that provided the following: (2) Digital Parallel printer ports, each of which used a male 37-pin connector, (4) EIA RS-232-C/CCITT V.24 asynchronous line interfaces for connecting three serial printers and one serial printer or terminal, and (1) Ethernet interface transceiver port. The DECserver 250 implemented the Local Area Transport (LAT) protocol for communication with service nodes that implemented this protocol on the same Ethernet. Software that ran on the DECserver 250 was down-line loaded over the network from a Phase IV DECnet load host.

Model Number: DSRVP-\*\*
Ports: 7 (see above)  
Alternate product: None.

**DECserver 300**  
The DECserver 300 Terminal Server was an Ethernet Communications Server for Ethernet Local Area Networks, providing a convenient method to logically connect up to sixteen digital asynchronous terminals to one or more service nodes (hosts) on an Ethernet. The DECserver 300 used MMJs (Modified Modular Jacks) for the attachment of asynchronous devices. The MMJ segregated a Data from a Voice connection. The DECserver 300 utilized the [EIA 423-A](/wiki/RS-423 "RS-423") electrical interface standard for local connections. EIA 423-A is compatible with the EIA 232-D interface and supports DTR/DSR (Data Terminal Ready/Data Set Ready) signals. EIA 423-A supports longer cable runs and higher signaling speeds. The DECserver 300 implemented the LAT protocol for communication with service nodes that implemented this protocol on the same Ethernet. The DECserver 300 also implemented the TCP/IP protocol suite for communication with host systems that implemented TCP/IP.

Model Number: DSRVF-\*\*
Ports: 16 DB25 or MMJ  
Alternate product: DECserver 708, 8 ports DB9 or DECserver 716, 16 ports RJ45

**DECserver 500/550**  
The DECserver 500 series server was an Ethernet Communications Server for Ethernet Local Area Networks (LANs), configurable to provide 128 EIA-423-A or 64 RS-232 asynchronous port connections to DEC asynchronous terminals. Both RS-232, via the 8 port CXY08 [Q-Bus](/wiki/Q-Bus "Q-Bus") communication option card, and EIA-423-A, via the 16 port CXA16 communication option card and EIA-422 16 port CXB16 communication option card could be mixed together in any combination from two to eight cards in one server. The DECserver 510 and 550 would also support CXM04 [IBM 3270](/wiki/IBM_3270 "IBM 3270") Terminal option cards, but on VMS only.[[1]](#cite_note-1) The DECserver 500 series server provided a convenient method to connect logically up to 128 Digital asynchronous terminals to one or more service nodes (hosts) on an Ethernet. The DECserver 500 series server also allowed for ULTRIX host-initiated connections to asynchronous printers. The DECserver 500 series server implemented the LAT protocol for communication with service nodes that implemented this protocol on the same Ethernet. The 500 series differed from other DECservers in that the configuration was not stored in nonvolatile storage locally on the server itself, but rather downline loaded from a file on a MOP host. Configuration changes which needed to remain permanently had to be changed locally on the DECserver and also updated on the MOP host using the OpenVMS Terminal Server Configurator utility (SYS$COMMON:[DECSERVER]DS5CFG on VMS or /usr/lib/dnet/tsc on Ultrix) so that it would return the next reboot. The 500 and 550 models are based on the [PDP-11](/wiki/PDP-11 "PDP-11")/53 chipset with 512 kb or 1.5 mb of on-board ram and can be reverted to a full PDP-11/53 system with a PROM swap and console port re-wire.

Model Number: DSRVS-\*\*
Ports: up to 128  
Alternate product: CXY08 = DECserver 708; CXA16 = DECserver 716, 732

**DECserver 90L**  
Nicknamed Plain Old Terminal Server (POTS), the DECserver 90L ran ROM-based firmware and supported LAT only. Its stripped-down functionality left out ‘dedicated service’ and ‘preferred service’ features.

Model Number: DSRVD-\*\*
Ports: 8 MMJ; 1 BNC  
Alternate product: DECserver 90M+

**DECserver 90L+**  
The DECserver 90L+ terminal server was an eight line terminal server that supported terminals and printers. Each line or port could establish up to a maximum of four LAT sessions and one MOP session at a time. DECserver 90L+ supported the LAT protocol and was designed to work in a ThinWire Ethernet Local Area Network (LAN),

Model Number: DSRVG-\*\*
Ports: 8 MMJ; 1 BNC  
Alternate product: DECserver 90M+

**DECserver 90TL**  
Designed for asynchronous connections up to 57.6 [kbit](/wiki/Kilobit "Kilobit")/s to UNIX, ULTRIX, VMS, DOS and multi-vendor network services. The DECserver 90TL supported TCP/IP protocols and several remote management systems.

Model Number: DSRVE-\*\*
Ports: 8 RJ45; 1 BNC  
Alternate product: DECserver 90M+

**DECserver 90M**  
There were three iterations of the DECserver 90M: DSRVH-M\*, -A\*, configured without Flash RAM; the DSRVH-N\*, -D\*, configured with 1 [MB](/wiki/Megabyte "Megabyte") of Flash RAM; DSRVH-P\*, -R\* configured with 2 MB of Flash RAM. All supported expanded multi-protocol connections via LAT, Telnet, SLIP, TN3270, CSLIP and PPP. Also supported were remote-node and remote control applications as well as accounting event logging and audit trails.

Model Number: DSRVH-\*\*
Ports: 8 RJ45; 1 BNC; 1 RJ45 LAN  
Alternate product: DECserver 90M+

**DECserver 900MC**  
The DECserver 900MC is an asynchronous network access server with eight on-board V.34 modems.

Model Number: DSRVX-\*\*
Ports: 8 RJ45  
Alternate product: None.

**DECserver 900GM/GMX**  
The DECserver 900GM was a network access server that supported up to 16 full modem control ports, or 32 eight–wire partial modem control ports. The DECserver 900GMX was identical to the DECserver 900GM, except that it supported up to 8 full modem control ports, or 16 eight–wire partial modem control ports. The ports were used to connect asynchronous devices including terminals, printers, modems, or PCs to an Ethernet local area network (LAN). The DECserver 900GM was configured with four 68-pin D-connectors (two for the DECserver 900GMx), and provided full or limited modem control. Each port supported sixteen [data rates](/wiki/Bit_rate "Bit rate") from 75 bit/s to 115.2 kbit/s. The DECserver 900GM included 4 MB of standard memory, and could be expanded to 8 MB.

Model Number: DSRVY-\*\*
Ports:2-4
Type: 68-pin Champ connectors  
Alternate product: DECserver 708, 8 ports DB9 or DECserver 716, 16 ports RJ45

**DECserver 900TM**  
The DECserver 900TM is a 32-port network access server that connects asynchronous devices, including terminals, printers, modems, or PCs to an Ethernet local area network (LAN). The DECserver 900TM is configured with 32 MJ8 (RJ-45) connectors, and provides limited modem control with the 8-pin connectors. Each port supports sixteen data rates from 75 bit/s to 115.2 kbit/s. The DECserver 900TM includes 4 MB of standard memory, and can be expanded to 8 MB.

Model number: DSRVZ-\*\*
Ports: 32 RJ45  
Alternate product: DECserver 732

**DECserver 700-08**  
The original DECserver 700-08 (-A\*, -B\*) was replaced in 1993 with the –E\* and –F\* models. The original units ran DECserver 700 software and were configured with 1 MB of operational memory. The follow on units were configured with 4 MB of operational memory, an internal slot for a 2 MB Flash card and ran DNAS (DECserver Network Access Software). The –E\* and –F\* were retired in 2002.

Model number: DSRVW-A\*, DSRVW-B\*, DSRVW-E\*, DSRVW-F\*
Ports: 8 DB25  
Replaced by: DECserver 708, 8 ports DB9 or DECserver 716, 16 ports RJ45

**DECserver 700-16**  
The original DECserver 700-16 was replaced in 1993 with the –G\* and –H\* models. The original units ran DECserver 700 software and were configured with 1 MB of operational memory. The –G\* and –H\* models were configured with 4 MB of operational memory, an internal slot for a 2 MB Flash card and ran DNAS (DECserver Network Access Software). The –G\* and –H\* were retired in 2001.

Model numbers: DSRVW-C\*, DSRVW-D\*, DSRVW-G\*, DSRVW-H\*
Ports: 16 RJ45  
Replaced by: DECserver 716; DECserver 732

## DECservers today

[[edit](/w/index.php?title=DECserver&action=edit&section=2 "Edit section: DECservers today")]

**DECserver 90M+**  
The DECserver 90M+ was introduced in 2003. A full function asynchronous device and remote access server, it provides eight local or remote asynchronous RJ45 connections over Ethernet LANs. Internal flash is 4 MB. Memory is 8 MB. This product also supports upgradeable ROM code. The DECserver 90M+ supports up to eight sessions per port. It runs DECserver Network Access Software (DNAS). Unlike the DECserver 90M models, the DECserver 90M+ does not have a BNC connector. Speeds were increased to 230.4 kbit/s.

Model number: DCSRV-\*\*
Ports: 8 RJ45

**DECserver 708**  
This model was designed to replace the DECserver 700-08 and was introduced in 2003. It connects devices (such as printers, terminals, PCs, and modems) to local area networks (LANs). The DECserver 708 is Ethernet-based and supports 10BaseT Ethernet directly, and ThinWire Ethernet/IEEE 802.3 through an adapter. It supports Flash RAM capability and other nonvolatile forms of memory. The memory capability is factory installed. The Flash RAM is optional. The DECserver 708 can download the software image from the network or from the Flash RAM option if installed. The Flash RAM option allows for a boot/power up without having to download the image through the network. The DECserver 708 supports up to 4 MB of memory.

Model number: DSRVW-R\*
Ports: 8 DB9

**DECserver 716**  
This model was designed to replace the DECserver 700-16 and was introduced in 2000. It supports throughput rates of up to 115.0 [kbit](/wiki/Kilobit "Kilobit")/s per port. A front panel slot provides support for a flash memory card. It offers RADIUS, Kerberos, RSA SecurID, PAP, CHAP, and CBCP or standard dial-back. Multiple Telnet sessions per port. Multiprotocol support: IP, LAT, and Appletalk. Telnet, LAT, TN3270, Rlogin, LPD and DNS. Dial up protocols: SLIP, CSLIP and PPP with AUTOLINK.

Model number: DSRVW-J\*
Ports: 16 RJ45

**DECserver 732**  
The DECserver 732 offers the same features as the DECserver 716, with 32 ports.

Model number: DSRVW-K\*
Ports: 32 RJ45

**DECserver ConX4/ConX4P**  
Introduced in 2004, the ConX4 offers the same functionality as the DECserver 90M+ in a smaller port density configuration, with 10/100 LAN connectivity and port speeds to 230.4 kbit/s.

Model number: DSC04-\*\*
Ports: 4 RJ45

## Operating software

[[edit](/w/index.php?title=DECserver&action=edit&section=3 "Edit section: Operating software")]

DECserver Operating Software: DNAS (DECserver Network Access Software) includes several software images that run on the different hardware units. The DECserver is configured at the factory to request the correct image at initialization.

As well as connecting terminals and being used as standard terminal servers, DECservers also support reverse connections (either LAT, or on later models [Telnet](/wiki/Telnet "Telnet")) allowing them to be used as [print servers](/wiki/Print_server "Print server") or [console servers](/wiki/Console_server "Console server").

## Firmware filenames

[[edit](/w/index.php?title=DECserver&action=edit&section=4 "Edit section: Firmware filenames")]

The following are the filenames used for the firmware files that get downloaded by various DECserver terminal servers when they boot up and initialize:

These filenames are specified in a network request from the terminal server at boot time, to initiate a MOP download of the firmware.

On an Alpha, Itanium or VAX system running the [OpenVMS](/wiki/OpenVMS "OpenVMS") operating system, these files are located in a directory named SYS$SYSROOT:[MOM$SYSTEM] which has system logical names of MOM$SYSTEM and MOM$LOAD if DECnet has been started.

The DECserver device's hardware address must be specified in the DECnet node database in order for the firmware file to be loaded. The firmware's filename is not specified in the DECnet database, it is found in a network request from the terminal server. If the firmware file does not exist in the MOM$SYSTEM directory at the time of a load request, the terminal server will not complete its boot process, and an error message will be displayed on the OpenVMS operator's console (and written to SYS$MANAGER:OPERATOR.LOG) and this message will give the name of the missing file.

## References

[[edit](/w/index.php?title=DECserver&action=edit&section=5 "Edit section: References")]

1. **[^](#cite_ref-1)** AA-HU80E-TK DECserver 500 Management Manual

## External links

[[edit](/w/index.php?title=DECserver&action=edit&section=6 "Edit section: External links")]

* [MOP for Linux](http://packages.debian.org/unstable/net/mopd)
* [DECnet and LAT for Linux](https://sourceforge.net/apps/mediawiki/linux-decnet/index.php)