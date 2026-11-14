=== Web Technologies – Browsers, Search Engines, HTML and Web Terms
# Browser vs search engine (most-asked angle)
| Name | What it is |
|---|---|
| **Chrome** | **Web browser by Google** (2008) – not a search engine |
| Internet Explorer (now Edge), **Firefox**, **Opera**, **Vivaldi**, Safari | Web browsers |
| **Yahoo** | **Search engine / web portal – not a browser** |
| **Bing** | Search engine of **Microsoft**, launched **2009** (not Ming, Buzz) |
| **Baidu** | **Chinese search engine** |
| **DuckDuckGo** | **Search engine** that does not track or collect user information |
| Altavista | Early search engine |
| **Kurrently** | Real-time **social-media search engine** |
| **Orkut** | Closed **social networking site** (Google, shut 2014) – not a search engine |
| **Google Apps** | Office/productivity suite – not a web browser |
| Snapdeal | E-commerce company – not a means of communication (Darknet, Internet, Bluetooth are) |
- **Web browser:** software that requests and **displays web pages** (not a website, interpreter or OS); browsers use HTTP/HTTPS.
- **Search engine:** indexes web pages so they can be found; **Yahoo, Google, MSN** are internet sites (portals).
- **Web crawler** = **web spider** (spiderbot): bot that scans the Web for search-engine indexing.
- **Home page:** the **first page** a browser shows on opening a website.
- **URL (Uniform Resource Locator):** the site address typed to view pages – protocol (`https://`) → domain name → path to the file.
- **Cookie:** a **small piece of data** a website sends and the **browser stores** while the user browses (not a thumbnail or worm).
- **Webmercial:** a commercial message (advertisement) on the Web.
# Languages of the Web
| Term | Meaning |
|---|---|
| **HTML** | **HyperText Markup Language** – the **language of the WWW**; used to **display web pages** in a browser (not HTTP, which is a protocol) |
| Web server | Keeps information in **web pages** whose text is marked with **HTML tags** and serves them on request |
| **`<em>` tag** | Marks **emphasised** text, i.e. indicates the **importance/stress** of the text (shown in italics); not a list tag or font-size tag |
| **PHP** | **Hypertext Preprocessor** – popular **server-side scripting** language for dynamic, data-driven web apps |
| **JSP** | **Java Server Pages** – dynamic web pages; released **1999** by **Sun Microsystems** |
| Front-end core | **HTML5, CSS3, JavaScript** |
| OCEN | **Open Credit Enablement Network** – democratises lending so small borrowers get good credit terms |
- **W3C = World Wide Web Consortium:** main international **web standards body**, founded **1994** by **Tim Berners-Lee**; keeps pages working alike across browsers.
# Web 1.0 → 2.0 → 3.0
| Phase | Nature | User role |
|---|---|---|
| Web 1.0 (1990s) | Static HTML pages | Read-only |
| Web 2.0 (mid-2000s–) | Interactive, social, user-generated content; Big Tech holds data | Read-write |
| **Web 3.0** | **Decentralised** (blockchain), semantic/AI web | **Read-write-own** |
- **Web 3.0 (UPSC 2022, all three correct):** people **control their own data**; **blockchain-based social networks** possible; **operated by users collectively** (DAOs) rather than a corporation.
# Layers of the Web
| Layer | Share | Features |
|---|---|---|
| Surface (clear) web | ~4-5% | Indexed by search engines |
| Deep web | ~90-95% | Not indexed – inboxes, net banking, intranets; not always harmful |
| Dark web | Small hidden part of the deep web | Needs **Tor / I2P**; anonymous; linked with illegal markets |
> ⚠ Trap: Yahoo/Bing/Baidu = search engines; Chrome/Opera/Vivaldi = browsers; Orkut = social network; Google Apps = not a browser.
~~ Sources: PMF S&T Part 5 p.63-66 (Web 1.0-3.0, HTML, UPSC 2022, browsers vs search engines); app notes 5:13 sub 7; general knowledge (PHP, JSP, `<em>`, webmercial, Kurrently)

=== Modem, Network Devices, Servers and the OSI Model
# Modem (asked ~15 times)
- **Modem = MOdulator-DEModulator:** converts **digital → analog** (modulation) and **analog → digital** (demodulation) – **both** ways.
- **Job:** the **hardware unit that connects a home computer to the internet through a telephone line**; it **interfaces telephone lines and computer equipment** and lets computers **send and receive data worldwide**.
- It is **hardware** – not software, an OS or a voltage stabiliser; it does not encrypt or check for viruses.
- **Statement set (UPPCS 2009):** LCD = main use of liquid crystals ✓; modem connects a computer to a phone line ✓; NIO is at **Goa** (not Coimbatore) ✗; **70 Virginis** is a **star** (not a video system) ✗ → **only 1 and 2**.
# Devices
| Device | Job | OSI layer |
|---|---|---|
| **NIC** (network card) | Connects a computer to the network; holds the MAC address | 1-2 (Physical/Data Link) |
| Hub | Broadcasts to all ports | 1 Physical |
| Repeater | Regenerates a weak signal to extend the cable | 1 Physical |
| **Switch / Bridge** | Forwards frames by **MAC address** | 2 Data Link |
| **Router** | Connects different networks; routes by **IP** | 3 Network |
| Firewall | Filters traffic by rules | 3-4 (and above) |
| **Gateway** | Joins networks using **different protocols** | up to 7 Application |
| Modem | Signal conversion | 1 Physical |
- **Physical → application order (TS 2021):** **NIC → switch/bridge → router → firewall → gateway** (D, B, A, E, C).
- **Router, hub and switch are all connecting devices** (MPPSC 2014 asked "which is a connecting device?" – answer "all of these").
# Servers
- **Proxy server:** middleman that **forwards client requests to other servers**; it does **not** provide TCP/IP addresses (DHCP does).
- **Server types:** file, print, application, web, mail, database, proxy servers. "**Network server**" is the generic name for a powerful central computer storing shared data/programs – the MPPSC 2021 key treats it as "not a (type of) server".
- **Nodes:** all computers and printers on a network are its **nodes**.
# OSI model – seven layers (top to bottom)
| Layer | Function | Protocols / devices |
|---|---|---|
| 7 Application | User services | **HTTP, FTP, SMTP, DNS** |
| 6 Presentation | Encryption, compression, formats (JPEG) | – |
| 5 Session | Opens and closes sessions | – |
| 4 Transport | End-to-end delivery | TCP, UDP |
| 3 Network | Routing; **IP addresses** (Internet layer of TCP/IP) | Router |
| 2 Data Link | Framing, **MAC addresses**, error detection; Ethernet, PPP | Switch, bridge, NIC |
| 1 Physical | Signals on the medium | Cables, hub, repeater, modem |
- **Data Link layer** lies **between the Physical and Network layers**; OSI model ratified **1984**.
- **SMTP** = **Application layer**; IP addresses = **Network layer**.
> ⚠ Trap: switch = Layer 2 (MAC), router = Layer 3 (IP); modem is a Physical-layer device, not Transport.
~~ Sources: PMF S&T Part 5 p.28 (networking devices: routers, switches, modems), p.45 (dial-up modem); app notes 5:13 sub 2; testbook.com (MPPSC 2014 "Which of the following is a connecting device?" – All of these); general knowledge (OSI device order, NIO Goa, 70 Virginis)

=== Internet and the World Wide Web – Basics and History
# Internet
- **Internet = "a network of networks"**: global network of interconnected computers working on **TCP/IP**; the **largest WAN**.
- **Uses:** send e-mail, view web pages, connect to servers – **all of the above**.
- **How it works:** data → **packets**; **IP** directs packets, **TCP** checks errors and reassembles; **DNS** turns names into IP addresses.
- **"Founder"/pioneer:** **Leonard Kleinrock** (packet-switching theory; first ARPANET message, 1969); Vint Cerf and Bob Kahn designed TCP/IP ("fathers of the Internet").
# World Wide Web
- **WWW (W3) = World Wide Web:** collection of **linked information (hypertext documents)** on computers available through the internet; accessed via **HTTP**.
- **Inventor:** **Tim Berners-Lee** (British), **1989** at **CERN**; he also wrote the **first web browser (named "WorldWideWeb")**, the first web server, HTML, HTTP and URL. Made public in **1991**.
  - Distractors: Bill Gates, Larry Page, Ted Nelson (coined "hypertext"), Vinod Dham (Pentium), Ray Tomlinson (e-mail), Edward Kasner ("googol").
- **Hypermedia system:** because it **links to other computer resources** (not because it is "hyper fast").
- Internet (infrastructure) ≠ WWW (a service running on it).
# Timeline
| Year | Event |
|---|---|
| 1969 | **ARPANET** – US Department of Defense; forerunner of the internet |
| 1984 | OSI model ratified |
| 1986 | **ERNET** – India's academic network |
| 1989 | **WWW** invented by Tim Berners-Lee at CERN |
| 1994 | W3C founded |
| 1995 | **VSNL** launched public internet in India on **15 August 1995** |
| 1998 | Satyam Infoway (Sify) – first private ISP of India; ICANN set up |
| 2003 | NIXI set up under MeitY |
# Communication basics
- **Channel:** the **medium** through which an encoded message is transferred (sender → encoder → **channel** → decoder → receiver).
- **Networking:** personal computers connected together form a **network**.
~~ Sources: PMF S&T Part 1 p.30 (Berners-Lee, CERN 1989, first browser and server); PMF S&T Part 5 p.29 (ARPANET 1969, WWW public 1991), p.45 (Internet, TCP/IP, packets, DNS), p.65 (Internet vs WWW); app notes 5:13 sub 0; general knowledge (Kleinrock, VSNL 15 Aug 1995, channel)

=== Protocols, DNS and Domain Names
- **Protocol:** a **set of rules that governs data communication**; three elements – **syntax** (format), **semantics** (meaning), **timing**.
# Protocol → function
| Protocol | Function |
|---|---|
| **TCP/IP** | **Set of protocols for all transmission exchanges across the internet**; the standard protocol suite for internet use/surfing |
| **HTTP** | **Hypertext Transfer Protocol** – used for **accessing the WWW / fetching web pages** |
| **HTTPS** | **S = Secure** – HTTP encrypted with **SSL/TLS** |
| **FTP** | **File Transfer Protocol** – exchanging files |
| SMTP | Sends e-mail (Application layer) |
| POP3 | Downloads mail to one device, usually deletes it from the server |
| IMAP | Keeps mail on the server, synced across devices |
| DHCP | Assigns IP addresses automatically |
| TELNET | Remote login |
- ARPANET is a network, not a protocol; CSMA/CD (Ethernet access method) and FDDI (fibre ring LAN) are not the internet protocol suite.
# DNS
- **DNS = Domain Name System** (not "Domain Name Server/Service"): the **database of names and addresses of internet hosts**; converts **domain names → IP addresses**.
# Domain names
| Extension | Meaning |
|---|---|
| **.com / .gov / .net** | Commercial / government / network – **all valid** top-level domains |
| .edu | Education (.edu.us = educational institute in the USA) |
| **.au** | **Australia** (Austria = .at, UAE = .ae, Aruba = .aw) |
| .in | India (registry run by NIXI) |
- **E-mail address:** username@domainname.extension.
> ⚠ Trap: HTML is a language, HTTP a protocol; DNS full form = Domain Name **System**.
~~ Sources: PMF S&T Part 5 p.45 (TCP/IP, DNS), p.66 (HTTP vs HTTPS, SSL/TLS); app notes 5:13 sub 3; general knowledge (ccTLDs, TELNET, CSMA/CD, FDDI)

=== Network Types and Topologies
# Network types by area
| Type | Scope / feature |
|---|---|
| PAN | Personal area (1-10 m); Bluetooth, smartwatch-phone |
| **LAN** | **A single building / small area** – home, office, lab; **Ethernet** is an example (IEEE 802.3) |
| CAN | Campus Area Network – several LANs across a campus |
| **MAN** | **Metropolitan Area Network** – a city |
| **WAN** | Countries/continents; links LANs in different cities; the **Internet is the largest WAN** |
| **VPN** | **Virtual Private Network** – secure, encrypted network **across the public internet** giving users access to their organisation's network |
| WLAN | Wireless LAN (Wi-Fi) |
- **VPN (UPSC 2011):** answer (b) – network across the public internet giving access to the organisation's network securely; "shared pool of computing resources" = cloud computing.
- **Network types vs topologies:** PAN/LAN/CAN/MAN/WAN are **types**; mesh, star, bus, ring are **topologies** (TS Sub Engineers key: **MAN**).
- **APPSC 2019:** a firm linking LANs in **Mumbai, Bengaluru and New Delhi** uses a **WAN**.
- **Intranet** = private internal network; **extranet** = controlled extension for partners; **Internet** = network of networks.
# Topologies
| Topology | Layout | Resilience |
|---|---|---|
| Bus | All nodes on one backbone cable | Backbone break stops the whole network |
| Star | All nodes to a central hub/switch | A failed node is only isolated; hub failure stops all |
| Ring | Each node linked to two neighbours | One break can disrupt the ring |
| Mesh | Every node linked to every other | Most resilient; costliest – n(n-1)/2 links |
| **Tree** | Branching mix of bus and star – **a generalisation of the bus topology** | Exam key: **topology used by the Internet** |
| Hybrid | Mix of types | The Internet is the largest hybrid topology |
- **Grid** is **not** a common network topology.
> ⚠ Trap: "Internet topology" – exam keys say **tree**; strictly the Internet is a hybrid (largely mesh) of networks.
~~ Sources: PMF S&T Part 5 p.30-35 (PAN, LAN, CAN, MAN, WAN, VPN, topologies), p.33 (UPSC 2011 VPN), p.50 (intranet/extranet); app notes 5:13 sub 1; general knowledge (tree = generalisation of bus, Stallings)

=== IP and MAC Addressing
| Address | Length | Notation |
|---|---|---|
| **IPv4** | **32 bits** (~4.3 billion addresses) | Dotted decimal, 4 octets each **0-255**, e.g. 192.168.1.1 |
| **IPv6** | **128 bits** | 8 groups of hexadecimal separated by colons |
| **MAC** (Media Access Control) | **48 bits** (6 bytes, 12 hex digits) | Unique ID burnt into the NIC; used at the Data Link layer |
- **IP address** = the unique number that **identifies a computer on the internet** (not e-mail or street address; SMTP/TCP/UDP are protocols).
- **IPv4 needs fewer bits than IPv6** (32 < 128) (APPSC G1).
- **Invalid IPv4:** "192.23.350" – only three octets and 350 > 255.
# IPv4 classes (first octet)
| Class | Range | Use |
|---|---|---|
| A | 1–126 | Large networks |
| B | 128–191 | Medium networks |
| C | 192–223 | Small networks |
| D | 224–239 | Multicast |
| E | 240–255 | Experimental |
- **There is no Class F.**
~~ Sources: PMF S&T Part 5 p.39 (IP and IP address); app notes 5:13 sub 4; general knowledge (IPv4 octet rule, classes)

=== Internet Connections, Transmission Modes and Wireless Standards
# Connection types
| Connection | Medium | Speed |
|---|---|---|
| **Dial-up** | Telephone line + dial-up modem; not always-on | **Slowest – up to 56 Kbps** |
| **DSL (Digital Subscriber Line)** | **Existing telephone lines** | 2-24 Mbps |
| Cable broadband | Coaxial cable-TV lines (cable modem) | Higher than DSL |
| Fibre | Light pulses in optical fibre | 100s of Mbps – Gbps |
| Leased line | Dedicated always-on business line | High |
| Satellite | GEO (VSAT) / LEO (Starlink, OneWeb); no terrestrial wire | Variable |
- **Wireless web:** internet access from **cellular phones, hand-held and portable gadgets** (Spaceweb, Astroweb, Cosmoweb are not terms).
# Transmission modes
| Mode | Meaning | Example |
|---|---|---|
| Simplex | One way | Radio/TV broadcast, keyboard |
| Half duplex | Both ways, one at a time | Walkie-talkie |
| Full duplex | Both ways at once | Telephone call |
- "G" in **2G** = **Generation**; a **podcast** is a radio-style programme shared via the internet.
# Bluetooth and Wi-Fi
| Feature | Bluetooth | Wi-Fi |
|---|---|---|
| Standard | IEEE 802.15.1 (PAN) | IEEE 802.11 (WLAN) |
| Band | **2.4 GHz** | **2.4 and 5 GHz** (Wi-Fi 6E/7 also 6 GHz) |
| Line of sight | Not needed | Not needed |
- **UPSC 2011:** difference = Bluetooth uses 2.4 GHz, Wi-Fi 2.4 or 5 GHz (Bluetooth is PAN, not WLAN; neither needs line of sight).
- **2.4-2.5 GHz ISM band (UPSC 2010):** **Bluetooth, cordless phones, microwave ovens (2.45 GHz) and Wi-Fi – all four**.
- **Bluetooth versions:** APPSC key "latest" = **5.1** (2019); then 6.0 (2024, **Channel Sounding**), 6.1 (May 2025), 6.2 (Nov 2025), 6.3 (May 2026), **Core 7.0 (Nov 2026, High Data Throughput)** – the latest as of Nov 2026.
- **Wi-Fi 7** = **IEEE 802.11be** (2.4, 5 and 6 GHz); **Wi-Fi Direct** links devices with no LAN; **Li-Fi** carries data on **LED light**.
~~ Sources: PMF S&T Part 5 p.45 (dial-up 56 Kbps), p.47 (DSL, cable, fibre), p.48 (satellite), p.55-57 (Wi-Fi, Bluetooth, UPSC 2011); bluetooth.com blog "Just released: Bluetooth Core 6.3" (6 May 2026); audioxpress.com (Bluetooth HDT in Core 7.0, 4 Nov 2026); app notes 5:13 sub 5-6

=== Internet Governance and India
| Body / Act | Year | Role |
|---|---|---|
| ICANN | 1998 | US non-profit; coordinates the global Domain Name System and IP address allocation |
| NIXI (National Internet Exchange of India) | 2003 | Not-for-profit under MeitY; internet exchange points, the .in registry and IRINN |
| BhashaNet | 2022 | MeitY and NIXI (not ICANN) – Universal Acceptance for Indian languages; .Bharat in Devanagari |
| IT Act, 2000 | 2000 | Sections 69A and 79 – government can order ISPs and intermediaries to block content |
| Telecommunications Act, 2023 | 2023 | Replaced the Indian Telegraph Act, 1885; holds the power to suspend internet services |
| **Orbicom** | – | **International network of UNESCO Chairs in Communication** |
- **Universal Acceptance:** every app and e-mail system accepts all domain names and e-mail IDs, including those in Indian scripts.
- **7 Apr 2026:** a site opening on one ISP but not another = ISP-level **DNS poisoning, HTTP interception or SNI filtering**.
- **Economic Survey 2025-26:** internet connections **25.15 crore (2014) → 96.96 crore (2024)**; **BharatNet** fibre reaches **2.18 lakh gram panchayats**.
- **AP angle (29 Jun 2026):** CM **Chandrababu Naidu** and **Sunil Mittal** discussed **last-mile connectivity, data centres and an undersea cable landing station** for AP.
~~ Sources: app notes 5:13 sub 8; general knowledge (Orbicom = UNESCO network, not checked)
