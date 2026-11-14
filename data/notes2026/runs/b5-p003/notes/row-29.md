=== Malware – Virus, Worm, Trojan and Other Types
# Basics
- **Malware** (malicious software) = single word for viruses, worms, trojans etc.: software **designed to disrupt, damage or gain unauthorised access** to a computer (not merely buggy software).
- **VIRUS** = "**Vital Information Resources Under Siege**"; a program that **replicates itself**, **attaches to files** and spreads from computer to computer – enters via **images, audio/video files, downloads, attachments**; infects storage such as a **pen drive**, not a display or keyboard.
- **Bug** = a fault in a program that stops it working correctly (some GK keys also call a virus a "bug").
- **Father of computer virology:** **John von Neumann** (1949 theory of self-reproducing automata).
# Types → behaviour → example
| Type | Defining behaviour | Example |
|---|---|---|
| **Virus** | **Attaches to files**, reproduces and spreads; user must run the infected file | Brain, Michelangelo |
| **Worm** | Uses the **network to send copies of itself without user action**; does **not** need to attach to a program | WannaCry, Morris |
| **Trojan** | **Looks like legitimate software**, tricks the user into installing it, then acts like a virus/worm; no self-replication; backdoor | Zeus |
| Ransomware | Encrypts files, demands ransom (often crypto) | WannaCry, Petya |
| Spyware | Secret surveillance; steals passwords, banking data | Pegasus |
| Adware | Unwanted ads; bundled with free/pirated software | Fireball |
| **Rootkit** | Administrator-level access; **modifies the host OS to hide malware**; hardest to detect | Stuxnet parts |
| **Stealth virus** | Designed to **hide from antivirus** detection | – |
| Keylogger | Records keystrokes (passwords, PINs, OTPs) | DarkHotel |
| Botnet | Network of hijacked "zombie" devices for DDoS, spam | Mirai (IoT) |
- **Antivirus** software: McAfee, Kaspersky, Avast, **Webroot**, Norton – **Rootkit is malware, not antivirus**; Webroot is not a virus.
- Viruses, worms and trojans all threaten **electronic payment systems**.
> "Self-replicating over the network without user action" = worm; "disguised, no self-replication" = trojan. UPSC 2005: worm statement I correct, II (needs to attach) wrong; malware statement II correct only.
~~ Sources: NextGen S&T Group 2 Part 3 p.22 (cyber security, anti-virus); PMF S&T Part 6 p.18-20 (malware types table); app notes 5:29 sub 0; general knowledge (stealth virus, von Neumann, Webroot, not checked)

=== Named Malware, Attacks and Firsts
| Name | Type | Origin / note |
|---|---|---|
| **Creeper (1971)** | **First** self-copying program/virus | ARPANET (Bob Thomas, BBN); removed by **Reaper** |
| Elk Cloner (1982) | First virus "in the wild" | Apple II, Rich Skrenta |
| **Brain (1986)** | First IBM-PC boot-sector virus | **Alvi brothers, Lahore, Pakistan** |
| **Michelangelo** | Virus | Made to infect **MS-DOS on 6 March 1992**; first found in Australia (1991) |
| **Stuxnet (2010)** | Worm with rootkit parts | **Sabotaged uranium centrifuges** at Natanz, Iran (industrial control systems) |
| **Petya (2016) / NotPetya (June 2017)** | **Ransomware** | Encrypts the master boot record; NotPetya hit Ukraine |
| **WannaCry (May 2017)** | **Ransomware** spreading as a worm | Paralysed networks in 150 countries; used **EternalBlue**; Lazarus group (North Korea) |
| EternalBlue | Exploit of a Windows SMB flaw | US **NSA**; leaked by Shadow Brokers (2017) |
| **StrandHogg (2019)** | **Android** vulnerability | Malware **poses as genuine apps**; MHA alert; found by Promon (Norway) |
| **Pegasus** | Zero-click spyware | **NSO Group, Israel** |
| Mirai | Botnet | Hijacked IoT devices for DDoS |
- CERT-In flags (2014): Hikti, Dyreza Trojan, Shellshock.
> UPSC 2018 / APPSC G2 2025: WannaCry, Petya, EternalBlue = **cyber attacks / ransomware**. "Latest" virus in a 2017 paper = Petya (now many later ransomware strains).
~~ Sources: NextGen S&T Group 2 Part 3 p.7 (CERT-In 2014 malware); PMF S&T Part 6 p.20 (UPSC 2018 WannaCry/Petya/EternalBlue = cyber attacks); app notes 5:29 sub 1

=== Attack Techniques – Phishing, Spoofing, Spam, DoS
| Threat | Meaning |
|---|---|
| **Phishing** | **Deceptive e-mails/texts** that look legitimate, tricking users into **revealing sensitive information** (card details, PIN) or installing software |
| Vishing | Phishing by voice calls |
| **Spoofing** | E-mail **appears to come from one source but is sent from another**; a **fake website posing as a legitimate one** steals user data |
| **Spam** | **Junk / unsolicited bulk e-mail** (a computer term) |
| **E-mail bombing** | **Identical e-mail sent repeatedly** to one address to overflow it |
| Sniffing | Capturing data packets on a network |
| **DoS / DDoS** | **Denial of Service**: **flooding** a server with fake traffic so genuine users **cannot access** it; DDoS uses many machines (botnet) |
| Man-in-the-middle | Secretly intercepts/alters communication between two parties |
| SQL injection | Malicious database code via website input fields |
| Zero-day | Exploits an unknown, unpatched flaw (e.g. Pegasus) |
| Supply-chain attack | Compromise a trusted vendor, e.g. SolarWinds (2020) |
| **Social engineering** | **Exploiting the human element** (trust, urgency, curiosity) to gain access |
- **Cyber attack** = any attempt to harm, damage or threaten a computer system or network.
> Match (APPSC): Hacking – unauthorised access/manipulation; Phishing – fraudulent attempt to get sensitive info; Ransomware – locks data and demands payment.
~~ Sources: app notes 5:29 sub 2; PMF S&T Part 6 p.20-21 (phishing, vishing, DoS/DDoS); general knowledge (sniffing, not checked)

=== Hackers and Cyber Crimes
- **Cybercrime** = any crime involving a computer and a network: **hacking, stalking, DoS attacks**, spam, online fraud, cyber terrorism (**online chatting is not a cybercrime**); deviant acts through IT = **cyber crimes**.
| Actor | Meaning |
|---|---|
| **Hacker** | Person who **gains illegal/unauthorised access** to a computer system |
| **Cracker = black-hat hacker** | Malicious hacker: destroys data, **denies service** |
| White-hat hacker | Ethical hacker |
# Crimes against persons
| Crime | Modus operandi / law |
|---|---|
| **Digital arrest** | **Not a real police power** – a **term used by cyber criminals to scare victims**: posing as police/CBI on video call and extorting money |
| Cyber slavery | Trafficking people and forcing them to run cyber fraud from scam centres (**Myanmar and Laos**, MEA 2025) |
| Identity theft | IT Act Sec. **66C** |
| Sextortion | Blackmail with intimate images; **66E/67A** |
| Dark web | Hidden internet via **Tor**; illegal marketplaces, data dumps |
- **Telangana** police: one of India's first cases of trafficking for cyber fraud (INTERPOL); FIU-India flagged **Rs 800 crore** laundering.
- **Supreme Court**: Centre, States, RBI and **telecom authorities** to frame SOPs, use zero FIRs; digital-arrest complaints on NCRP 1,23,672 (2024) to 58,249 (2025).
# Financial cyber frauds
| Fraud | Modus operandi |
|---|---|
| SIM swap | Duplicate SIM to **intercept OTPs** |
| UPI / QR fraud | QR code is scanned only to **pay**, never to receive |
| Crime-as-a-service | Syndicates rent out ransomware and fraud tools |
| Crypto-jacking | Secretly using a victim's device to mine cryptocurrency |
~~ Sources: NextGen S&T Group 2 Part 3 p.22 (cybercrime definition); PMF S&T Part 6 p.21 (no legal concept of digital arrest); app notes 5:29 sub 3-4

=== Security Tools, Principles and Cryptography
# Tools
| Tool | Function |
|---|---|
| **Firewall** | **Filters** incoming/outgoing internet traffic by rules; **blocks unauthorised access**; hardware, software or both |
| Antivirus | Prevents and heals infections |
| **Password** | Improves **security** |
| MFA / 2FA | Password + OTP/biometric |
| Honeypot | Decoy system to trap attackers |
| **Virtual keyboard** | Defeats **keyloggers**: protects against **password theft, trojans and spyware** |
- Indigenous: **M-Kavach** = **C-DAC Hyderabad**; **CERT-In** = CVE Numbering Authority.
# CIA triad
| Principle | Meaning |
|---|---|
| **Confidentiality** | Procedures, policies and controls securing data **against illicit access or use** |
| Integrity | Protection against alteration |
| Availability | Access for authorised users (denial = availability lost) |
- Full list: confidentiality, integrity, availability, **accountability, non-repudiation**; **IRDAI** (2021) retail cyber cover excludes **gross negligence**.
# Cryptography
| Term | Key point |
|---|---|
| **Symmetric** | Same key encrypts and decrypts – AES, **Blowfish** (**Bruce Schneier, 1993**; faster alternative to DES) |
| Asymmetric | Public-private key pair – **RSA**; basis of PKI |
| Digital signature | Signed with sender's **private** key, verified with **public** key |
| Hashing | One-way, fixed-length digest (**SHA-256**) |
~~ Sources: NextGen S&T Group 2 Part 3 p.22 (firewalls, encryption, passwords); app notes 5:29 sub 5-7

=== Attacks on Indian Systems, Cyber Warfare and Data
| Incident | Target / State |
|---|---|
| **e-Nagarpalika portal (Dec 2023)** | Online civic tax portal, **Madhya Pradesh** |
| **Power utilities (2019)** | **Ransomware** on servers of **Telangana and Andhra Pradesh** power utilities |
| AIIMS Delhi (2022) | Ransomware on hospital servers |
| Kudankulam NPP (2019) | Malware on admin network, Tamil Nadu |
| Cosmos Bank (2018) | ~Rs 94 crore ATM/SWIFT fraud, **Pune** |
- **AP**: **APTS** watches Critical Government Infrastructure via **APCSOC**; audited **270** GoAP apps; AP Police–**IIT Tirupati** MoU (Cyber Crime Investigation and Training Academy).
- **Cyber espionage**: often **state-sponsored** (**APT groups**); **cyber terrorism** targets critical infrastructure; tracing hard (VPNs, proxies, **botnets**).
- Emerging: AI-powered malware, ransomware-as-a-service, deepfakes; **MeitY 2nd Digital Threat Report 2025-26** = **BFSI**; **Exercise Cyber Suraksha** = DRDO-led, **12 days**, armed forces.
| Data | Figure |
|---|---|
| NCRB 2023 cyber crime cases | **86,420** (+31.2%); fraud **~69%** |
| Top state (NCRB 2023) | **Karnataka** (21,889) |
| CERT-In incidents | **29.44 lakh** (2025; highest in five years) |
~~ Sources: app notes 5:29 sub 8-9
