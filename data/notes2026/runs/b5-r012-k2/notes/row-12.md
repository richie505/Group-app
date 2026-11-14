=== Memory and Storage – Units, Primary and Secondary Memory
# Units in order
- **Bit** (binary digit) = the **smallest unit** of data/information; **nibble = 4 bits**; **byte = 8 bits** (APPSC 2025; asked 6 times).
- **Order:** bit < nibble < byte < **KB** < MB < GB < TB < PB < EB < ZB < YB.
| Unit | Equals |
|---|---|
| 1 byte | 8 bits |
| 1 KB | 1024 bytes = **8192 bits** |
| 1 MB | 1024 KB (about a million characters) |
| 1 GB | 1024 MB (about **one billion characters**) |
| 1 TB | 1024 GB |
- **Smallest time unit** among those asked: **picosecond** (10⁻¹²) < nanosecond (10⁻⁹) < microsecond (10⁻⁶) < second (APPSC G1 2004).
# Primary memory
| Memory | Nature |
|---|---|
| RAM (Random Access Memory) | **Primary**, **volatile**, temporary working store – lost when power goes off; not like hard-disc storage; SRAM = cache (faster), DRAM = main memory; RAM sticks use **DDR** (Double Data Rate) |
| ROM (Read-Only Memory) | **Non-volatile**, **permanent** memory built into the computer; holds firmware/**BIOS** (Basic Input-Output System); PROM, EPROM, EEPROM |
| Cache | Small, **extremely fast** memory **between CPU and main memory**; a portion the processor reaches faster than regular RAM; **shortest access time**; speeds up processing; made of **SRAM** |
| Registers | Fastest memory, **embedded on the CPU chip** (electronic memory) |
| Memory | Erased by |
| EPROM | Ultraviolet light |
| EEPROM | Electrically |
- **Speed order:** registers > cache > RAM > SSD > HDD > optical disc > magnetic tape.
- **Static RAM is faster than dynamic RAM**; **primary storage is faster than secondary** (a statement saying the reverse is wrong).
- **Memory types:** **semiconductor** (primary), **magnetic** and **optical** (secondary) – "server" is not a memory type.
- **Virtual memory:** its size (virtual address space) depends on the CPU's **address lines** (32 lines → 2³² bytes).
- **ROM is a memory, not a computer language.** **DIMM = Dual In-line Memory Module** (RAM stick; older SIMM; laptops SO-DIMM).
# Secondary storage
| Storage | Fact |
|---|---|
| HDD | Magnetic disk, non-volatile; first commercial hard disk drive by **IBM** (RAMAC 350, 1956); SATA hard disk = **magnetic**, not capacitive memory |
| SSD | Flash memory, no moving parts, faster |
| Magnetic tape | Sequential access, slowest; backup and archival |
| Flash drive / pen drive | EEPROM-based flash; keeps data without power; low power; **costlier, not cheaper**, than mechanical disk drives |
| CD-ROM (**Compact Disc Read Only Memory**) | about 700 MB |
| DVD (**Digital Versatile Disc**) | 4.7 GB single layer; 8.5 GB dual layer |
| Blu-ray | 25 GB single layer; 50 GB dual layer – **stores more than a DVD** |
- **Capacity order (decreasing):** Blu-ray > **DVD > CD-ROM > floppy disk**.
- **RAM is NOT secondary memory**; SSD, hard disk, optical disk, flash drive, floppy and USB pen drive are.
> Statement angle: "RAM is non-volatile" ✗; "primary is slower than secondary" ✗; "SRAM faster than DRAM" ✓; "Von Neumann = stored-program digital computer" ✓ → answer C and D.
~~ Sources: app notes 5:12 sub 5 (old-notes.txt); PMF S&T 05 (src/science-tech/pmf-science-tech-05.txt) p.27-28 (hardware, storage); unit values and memory hierarchy: general knowledge, not checked

=== CPU and Hardware Components
# CPU – the brain
- **CPU = Central Processing Unit** (NOT "Control Processing Unit") – the **brain**, the **controlling unit** and the **most important part** of the computer; most processing happens here (asked 9 times).
- **CPU is hardware**, not software – a statement "the CPU is the software that carries out instructions" is false.
- **Processor parts:** **Control Unit + ALU** (with registers); main memory and storage are **not** parts of the processor.
| Component | Function |
|---|---|
| ALU (**Arithmetic Logic Unit**) | Arithmetic and logical operations – performs **calculations and makes decisions** |
| CU (Control Unit) | Fetches and **decodes program instructions**, makes control signals, directs the other units |
| Registers | Fastest storage inside the CPU (address, data, instruction registers) |
| PSU | Only supplies power |
- **Main components of a computer:** input unit, output unit, processing unit, memory unit, secondary storage – **"basic unit" is not a component**.
- **After a double-click** of the mouse, information goes to the **CPU**.
# Buses, chips and processors
- **Buses:** the wire pathways that **connect the different parts** of a computer (data, address and control buses).
- **IC chips are made of silicon** (a semiconductor) – not silica (SiO₂), gold, chromium or iron oxide.
- **Celeron, Pentium, Core** = series of Intel **processors**; **Intel Core i9** = high-end processor with **8 to 24 cores**.
- **Clock speed** of a processor is measured in **hertz – gigahertz (GHz)**.
- **IBM = International Business Machine(s)**.
- **Modem = modulator-demodulator**: converts digital data into analog signals and back – "all of the above".
- **UPS = Uninterrupted Power Supply** (keeps the computer running briefly when power fails); **SMPS = Switched Mode Power Supply** (rectified AC to low-voltage DC).
- **Peripheral device:** equipment added to a computer to enhance its functionality (printer, scanner, webcam).
~~ Sources: app notes 5:12 sub 3 (old-notes.txt); PMF S&T 05 (src/science-tech/pmf-science-tech-05.txt) p.27-28 (hardware incl. peripheral devices, modems); CPU parts and processor series: general knowledge, not checked

=== Input, Output Devices and Printers
# Input vs output
| Input | Output |
|---|---|
| Keyboard (most common; **QWERTY** layout) | Monitor (CRT, LCD, OLED) |
| Mouse (**standard pointing device in a GUI**) | Printer |
| Microphone | Speaker, earphones, headphones |
| Scanner | Projector |
| Joystick (lever moving in several directions) | Plotter (drum pen plotter) |
| Trackball, light pen, touchpad | Visual Display Unit |
| Webcam (**compulsory for video conferencing**) | – |
| Digital camera (input, NOT output) | – |
| Barcode reader, OCR, MICR (cheques), OMR (answer sheets), badge reader | – |
- **Touch screen** = both input and output, so it is "not an output device" in exam keys.
- **Only input:** mouse, keyboard, scanner. **Only output:** plotter, printer, monitor.
- **Scanner:** light-sensitive device that turns drawings, printed data and images into digital form.
- **Digitizer:** converts analogue information (drawings, maps) into digital form.
- **Badge reader:** reads data encoded in a small plastic card.
- **Barcode:** machine-readable code of **vertical bars of varying widths** (APPSC 2019). **OCR = Optical Character Recognition**.
- **Caps Lock is a toggle key:** its function goes back and forth each time it is pressed.
- **Telefax (fax):** sends text and pictures over telephone lines (exam answer for "dialled on the telephone and read on a screen").
# Printers and displays
| Impact | Non-impact |
|---|---|
| Dot-matrix, daisy-wheel, line, drum, serial | Inkjet, **laser**, thermal |
- **Laser printer:** the fastest of the common printers, the standard **non-impact** printer and the one used for **desktop printing (DTP)**; it uses a **semiconductor laser** (also in CD/DVD players). **Excimer (exciplex) laser**: ultraviolet; used to make microelectronic devices.
- **OLED advantages over LCD:** can be made on **flexible plastic substrates**, allow **roll-up displays in clothing** and **transparent displays** – all three (UPSC 2017).
~~ Sources: app notes 5:12 sub 4 (old-notes.txt); PMF S&T 05 (src/science-tech/pmf-science-tech-05.txt) p.27 (peripherals: printers, scanners, webcams); device roles: general knowledge, not checked

=== History, Generations and Inventors
# Generations → core technology
| Generation | Basis | Example |
|---|---|---|
| First (1940s-56) | Vacuum tubes | ENIAC, **UNIVAC** |
| Second (1956-63) | **Transistors** | – |
| Third (1964-71) | Integrated circuits | – |
| Fourth | **VLSI and microprocessors** | Intel 4004 era |
| Fifth | Artificial intelligence, ULSI, parallel processing | – |
- **Miniaturisation** of computers came from **IC chips** (invented **1958**, replaced transistors).
- **ICs are classified by the number of transistors per chip:** **SSI 3–30, MSI 30–300, LSI 300–3,000**, then VLSI, ULSI.
# Firsts
| First | Fact |
|---|---|
| Word "computer" | From Latin **computare** (to calculate) |
| Pascaline (1642) | First mechanical calculating machine – **Blaise Pascal** |
| Punched cards (1890 US census) | **Herman Hollerith** – father of punched-card processing |
| ENIAC (1946) | **Electronic Numerical Integrator And Computer** – first general-purpose electronic computer, **Eckert and Mauchly** |
| BESK (1953) | Binary Electronic Sequence Calculator – Sweden's first **electronic computer** |
| Osborne 1 (1981) | First commercial portable computer – **Adam Osborne** (died at **Kodaikanal, 18 March 2003**) |
| Intel 4004 (1971) | First commercial microprocessor |
| TIFRAC | India's first indigenous computer |
| PARAM 8000 (1991) | India's first supercomputer |
| Mobilis (2005) | Bangalore's **Encore Software** "anytime, anywhere" low-cost mobile computer (Encore also made the Simputer) |
# Persons → contribution
| Person | Contribution |
|---|---|
| Charles Babbage | **Father of Computers** (inventor of the computer in exam keys); Analytical Engine; conceptual foundations 1833-1871 |
| Alan Turing | Exam answer for "invented the electronic computer" (Turing machine; wartime code-breaking computers) |
| George Stibitz | Recognised as a **father of the modern digital computer** (relay binary calculator, Bell Labs 1937) |
| Ada Lovelace | First programmer |
| George Boole | **Boolean algebra** – devised the logical operators **AND, OR, NOT** |
| Douglas Engelbart | Mouse |
| Larry Tesler | Cut, **copy and paste** |
| Tim Berners-Lee | WWW (1989-91) |
| Richard Stallman | GNU project (1983), GPL licence |
| Linus Torvalds | Linux kernel (1991) |
| Dennis Ritchie / James Gosling / Guido van Rossum / Bjarne Stroustrup | C / **Java** (1991-95) / Python / C++ |
| Tim Paterson | MS-DOS (from 86-DOS) |
| David S. Lee | Daisy-wheel printer (1969, Diablo Data Systems) |
| Alexander Bain (Scottish) | Fax (1842) |
| Peter Shor | Shor's algorithm (1994) |
> Trap: "Father of the Computer" = **Babbage** (not Hollerith, Pascal or von Neumann); **Berners-Lee** = WWW, not computers.
~~ Sources: PMF S&T 05 (src/science-tech/pmf-science-tech-05.txt) p.29 (ENIAC, UNIVAC; Babbage 1833-1871; Berners-Lee WWW 1991); app notes 5:12 sub 1 (old-notes.txt); Encore Mobilis: engadget.com/2005/05/11/the-mobilis-encores-inexpensive-mobile-pc/ (via web search); other firsts: general knowledge, not checked

=== Computer Types and Supercomputers
| Type | Feature / example |
|---|---|
| Analog | Continuous quantities – **car speedometer**, thermometer |
| Digital | Discrete (binary) data – PCs; works on the **logical** principle (Boolean 0/1) |
| Hybrid | Analog + digital features; **converts analog output into digital form** – ICU monitors, ECG |
| Micro / personal | **Most widely used** – desktop, laptop, tablet, smartphone, wearables |
| Embedded | Dedicated function inside a larger system – **digital watch** |
| Supercomputer | **Largest, fastest and costliest**; speed in FLOPS |
| Quantum computer | Uses **qubits** (superposition, entanglement); exam answer for the "smallest and fastest computer imitating brain working" |
- **Teacube:** a **2-inch cube-shaped computer** (APPSC G1 2004).
- **Q-Day:** when quantum computers may break **RSA-2048** encryption with **Shor's algorithm (1994)**. Oxford researchers made **10 billion quantum entanglements** in silicon.
# Supercomputers – dated
- **PARAM Padma** (C-DAC, 2002-03): an Indian **supercomputer** (UPSC 2004).
- **Tianhe** (Tianhe-1A 2010, Tianhe-2 fastest in TOP500 June 2014): developed by **China** (NUDT) ⚠ an APPSC key gave Japan.
- **2007:** **IBM Blue Gene/L** fastest; India's **Eka** (CRL, Tata) ranked **4th** (Nov 2007).
- **ISC 2026:** **LineShine** (China) fastest, replacing El Capitan.
- **Jan 2026:** **Param Shakti** – 3.1 petaflops, launched by **MeitY** at **IIT Madras** on RUDRA servers, under the **National Supercomputing Mission**.
| Term | Meaning / unit |
|---|---|
| Word length | Bits the CPU handles at once (32-bit, 64-bit) |
| Clock speed | Hertz (GHz) |
| Bandwidth | Data-transfer rate in bits per second (bps) |
| MIPS | Million Instructions Per Second |
| FLOPS | Floating-point Operations Per Second – supercomputer speed |
| Linpack (HPL) | Floating-point benchmark on large dense linear systems – basis of world rankings |
~~ Sources: app notes 5:12 sub 2 and sub 10 (old-notes.txt); PMF S&T 05 (src/science-tech/pmf-science-tech-05.txt) p.29 (quantum computing); Param Padma, Tianhe, Teacube: general knowledge, not checked

=== Software, Office Tools and Operating Systems
# Software types
- **Software** = programs that let the user and the **hardware communicate**/work; two major types: **system** and **application**.
| Type | Examples |
|---|---|
| System software | OS (Windows, Linux, macOS, Android, iOS), device drivers, utilities, firmware, translators |
| Utility software | Antivirus, disk cleanup, backup, compression |
| Application software | Word processors (MS Word, **WordStar** by MicroPro), **spreadsheets ("what if" analysis)**, presentation, DTP, browsers; graphics (Photoshop, CorelDRAW); multimedia (players, editors, **Final Cut Pro – video production**); database (Oracle, MySQL, MS Access); MS Outlook (e-mail) |
| Security software | Firewalls, antivirus, encryption, IDS |
- **Device driver** = system software. **Compiler** and **assembler** are programs, not hardware.
- **MS Office** = office suite (Word, Excel, PowerPoint, Outlook, Access) – **not an OS**; **Media Player is not an Office component**.
- **Open source:** source code free to view, modify and share; **GNU = "GNU's Not Unix"**; **Internet Explorer** = closed source.
- A Word document, video or MP3 is a **file**; the **extension** shows its type (.doc = Word).
# Office shortcuts asked
| Task | Answer |
|---|---|
| MS Word: break column, start new one | **Ctrl + Shift + Enter** |
| Windows logo key + D | Display and hide the desktop |
| Excel: Format as Table | **Home** tab |
| Excel: pop-up comment on a selected cell | Cell Tip |
| PowerPoint chart for a timeline | Line chart (printed key) |
# Operating systems
- **Functions:** manages hardware, memory, processes, files, devices, security and I/O; gives the user interface (not line-by-line translation).
| OS type | Feature / example |
|---|---|
| Time-sharing / multi-user | Many users share CPU time – UNIX (AT&T, **1969**; kernel = main part) |
| Real-time | Fixed response deadlines – missile guidance, air-traffic control |
| Batch | Groups jobs and runs them without user interaction |
| Mobile | Android (**Linux-based**, Google), iOS, BharOS (**IIT Madras**) |
| Interface | Example |
|---|---|
| CLI (command-line) | MS-DOS (Microsoft, Aug 1981, Tim Paterson), UNIX shell |
| GUI (icons, windows, mouse) | Windows (Windows 3 – 1990; **Windows 11 – Oct 2021**), macOS |
- **Linux, Windows, UNIX, Android, MS-DOS** = OSs; **Java, COBOL, MS Office** are not.
- **Android 6.0 = Marshmallow** (2015).
~~ Sources: PMF S&T 05 (src/science-tech/pmf-science-tech-05.txt) p.28 (system, application, enterprise, security software); app notes 5:12 sub 6-7 (old-notes.txt); shortcuts and FCP: general knowledge, not checked

=== Programming Languages, Number Systems and Logic
# Language levels
| Level | Fact |
|---|---|
| 1GL machine language | Only 0 and 1; the only language run directly |
| 2GL assembly | Mnemonics; converted by an **assembler** (not a compiler) |
| 3GL high-level | **FORTRAN** (Formula Translation, IBM 1957, first HLL, scientific), **COBOL** (business), **BASIC** (Beginner's All Purpose Symbolic Instruction Code), PASCAL, C, C++, Java, Python |
| AI languages | **PROLOG** and LISP |
- **Cobra, Python, Squirrel, Java** are computer languages; **Linux** and **Paint brush** are not.
| Term | Meaning |
|---|---|
| Compiler | Translates the whole program at once |
| Interpreter | Translates and runs line by line |
| Algorithm / Flowchart / Pseudocode | Step-by-step procedure / its **pictorial** form / English-like outline |
- **Flowchart symbols:** oval = start/end, **parallelogram = input/output**, rectangle = process, **diamond = decision**.
# Number systems and logic
- Binary (2), octal (8), decimal (10), **hexadecimal (16; 0–9 and A–F)**; (1010)₂ = 10; **(FF)₁₆ = 255**.
- **Universal gates: NAND and NOR**; **XOR** = 1 when inputs differ.
- **Boolean:** A + A = A; A·A′ = 0; **De Morgan: (A + B)′ = A′·B′**.
~~ Sources: app notes 5:12 sub 8 (old-notes.txt); PROLOG for AI: general knowledge, not checked

=== ICT – Nature, Scope and Terms
- **ICT = Information and Communication Technology**: devices and applications used to **access, store, transmit and manipulate digital information** – hardware, software, networks, data, people, services and infrastructure.
- **Aim:** smooth **human-human, human-machine and machine-machine (M2M)** communication.
- **Information Technology** = **connectivity + hardware** in the printed key (JPSC 2016); also taught as computers + communication.
- **Concerns:** privacy, **digital divide**, job insecurity, over-reliance. **Positive impact of the internet:** best source of knowledge at a click.
- **Cybernetics:** study of **automation and communication between human and machine** – term by **Norbert Wiener**.
- **Artificial Intelligence** makes machines intelligent and mimics human actions.
- **Technology preservation** = **computer museum** (APPSC 2019).
- **IT terms:** cyberspace, upload, modem ✓ – **"light storage" is not an IT term**.
- **Smart card:** plastic card with an **embedded microchip**; **digital technology** works with satellite and fibre-optic transmission; a **digital library is NOT only on the internet** (UPSC 2002 → I and II).
- **Aarogya Setu, CoWIN, DigiLocker, DIKSHA** – all on **open-source digital platforms**.
~~ Sources: PMF S&T 05 (src/science-tech/pmf-science-tech-05.txt) p.27-28 (ICT features and components); app notes 5:12 sub 0 (old-notes.txt); IT definition: testbook.com question 60475258aabf2ed433e87984 (via web search)

=== File Formats, Acronyms and Transmission Modes
| Acronym | Expansion | Type |
|---|---|---|
| PDF | Portable Document Format (Adobe) | Document |
| MP3 | MPEG-1 Audio Layer 3 | Audio (not video) |
| MP4 / MOV / AVI | MPEG-4 Part 14 / QuickTime Movie (Apple) / Audio Video Interleave (Microsoft) | Video |
| JPEG | Joint Photographic Experts Group | Image |
| GIF / PNG | Graphics Interchange Format / Portable Network Graphics | Image |
| ASCII | American Standard Code for Information Interchange | 7-bit, 128 characters; Unicode extends it |
- **LED = Light Emitting Diode** – light by **electroluminescence**.
| Mode | Example |
|---|---|
| Simplex (one-way) | Television; **mouse to computer** (APPSC 2019) |
| Half duplex | Walkie-talkie |
| Full duplex | Telephone |
- **Multiplexing** joins several signals on one channel.
~~ Sources: app notes 5:12 sub 9 (old-notes.txt)
