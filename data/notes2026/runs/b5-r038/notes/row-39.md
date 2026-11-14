=== Remote Sensing – Definition, Components and Platforms
- **Remote sensing:** gathering information about an object **without physical contact**, by measuring **reflected and emitted electromagnetic radiation** from a distance (satellite, aircraft, drone); it uses **electromagnetic waves**, not sonar or electric waves.
# Components (stages)
- 1. Energy source / illumination → 2. Radiation through the atmosphere → 3. **Interaction with the target** → 4. Recording by the sensor → 5. **Transmission, reception and processing** → 6. Interpretation and analysis → 7. Application.
- "Interaction of Energy with **Minimisation**" is **not** a component (APPSC 2022).
# Disaster uses and platforms
- Disaster applications: **glacial lakes**, **wildfires**, **wind/cyclone tracking**, floods, landslides – "hills management" is not one.
- **UAV (drone)** is best for **detailed, localised** damage assessment; satellites for wide areas.
- **Infrared (thermal) cameras** detect people trapped under **rubble** after an earthquake by their body heat.
- **GEOSS = Global Earth Observation System of Systems** (built by the Group on Earth Observations, GEO).
~~ Sources: NextGen S&T Group 2 Part 2 p.5; PMF S&T Part 1 p.80-81; app notes 5:39 sub 0

=== Electromagnetic Spectrum, Sensors and Bands
# Spectrum order
- Wavelength falls: **radio (incl. microwave) → infrared → visible (red … violet) → ultraviolet → X-rays → gamma rays**.
- **Colour** of light is set by its **wavelength**; in visible light **red** is longest and **violet** shortest.
- **Infrared** is longer than red; gamma rays shortest of all.
- **X-rays** strongly darken (expose) **photographic plates and film** – the basis of radiography.
# Passive vs active sensors
| Type | Energy | Examples |
|---|---|---|
| Passive | Reflected sunlight or emitted heat | Cameras (visible, infrared, multispectral), radiometers, MODIS |
| Active | Sends its own pulse, reads the echo | **Radar/SAR** (microwave), **laser / LiDAR**, altimeters |
- **Laser** is the active sensor in a list of cameras (APPSC 2023).
- **LiDAR = Light Detection And Ranging**: pulsed laser measures distances → elevation, 3D terrain, canopy height. **Airborne Laser Terrain Mapping (ALTM)** is airborne LiDAR: a fast, accurate, cost-effective 3D picture of the ground, used mainly for mapping and survey.
- Laser uses: LASIK, LiDAR, holography – **MRI is not** a laser use (it uses magnets and radio waves).
# Which band for what
| Band | Use |
|---|---|
| Optical (visible/NIR) | Reflected light; needs daylight and clear sky |
| **Thermal infrared** | Emitted heat → **volcanic eruptions**, forest fires, urban heat |
| **Microwave (radio region)** – SAR | **Penetrates clouds** and darkness → all-weather imaging of cloud-covered disaster areas |
| Hyperspectral | Hundreds of narrow bands → materials and chemicals |
> ⚠ Cloud-covered disaster area: the answer is the **radio/microwave** band; visible light cannot pass through cloud (the APPSC 2021 key "Visible" is a factual error).
~~ Sources: NextGen S&T Group 2 Part 2 p.5; PMF S&T Part 1 p.80-81, 94 (RISAT all-weather), p.69 (active sensors)

=== Resolution and Remote-sensing Techniques
- Four resolutions: **spatial** (smallest object seen), **spectral** (number and width of bands), **temporal** (**how often** a satellite revisits the same place), **radiometric** (sensitivity to small energy differences). "**Chemical**" resolution does not exist (APPSC 2025).
| Technique | Maps |
|---|---|
| InSAR | Ground deformation – subsidence, earthquake/volcano uplift |
| LiDAR | Elevation, 3D terrain, canopy height |
| NDVI | Vegetation health (**chlorophyll**) from red vs near-infrared reflectance |
| Thermal infrared | Land surface temperature, fires, volcanic heat |
| Hyperspectral | Materials and chemicals |
- Satellite data estimate **chlorophyll**, **greenhouse-gas emissions from rice paddies** and **land surface temperature** – all three (UPSC 2019).
- **MODIS = Moderate Resolution Imaging Spectro-radiometer** (NASA Terra/Aqua): **52,785 forest fires** detected Nov 2020 – Jun 2021.
- **Tectonic plate movement** is monitored by **VLBI, SLR and GPS** – not flood or cyclone mapping.
~~ Sources: PMF S&T Part 1 p.106-110; UPSC 2019 key; app notes 5:39 sub 1-2

=== Orbits for Earth Observation and Communication
| Orbit | Altitude | Use |
|---|---|---|
| LEO (Low Earth Orbit) | 200–2,000 km | Earth observation, ISS |
| SSPO (sun-synchronous polar) | ~500–900 km | Most EO satellites (IRS, Cartosat, NISAR) |
| MEO | 2,000–35,786 km | Navigation (GPS) |
| GEO (geostationary) | **35,786 km** (22,236 miles) over the equator | Communication, weather; appears fixed |
| GSO (geosynchronous, inclined) | Same height | Figure-8 track; NavIC's 4 inclined satellites |
- **Geostationary** = geosynchronous + **circular** + in the **plane of the equator**; also **Clarke's orbit**; period one sidereal day, **23 h 56 min 4 s**. The "22,236 km" statement is wrong (that figure is in miles) → UPSC 2011 key **1, 2 and 3 only**.
- **Sun-synchronous:** passes each place at the **same local solar time** → even lighting.
- A satellite does not fall because Earth's gravity **provides the centripetal acceleration** for its orbit (UPSC 2011).
- LEO imagers = finer detail, periodic revisit; geosynchronous imagers = coarser detail, near-continuous viewing.
~~ Sources: PMF S&T Part 1 p.65-66 (UPSC 2011 explanation); app notes 5:39 sub 3

=== IRS Programme – Origins and Firsts
- IRS began **17 Mar 1988** with **IRS-1A**: India's **first operational remote-sensing satellite**, launched from **Baikonur** (USSR, Kazakhstan) on a Soviet **Vostok** rocket – not Sriharikota.
- One of the **world's largest civilian remote-sensing constellations**; data via NRSC and **Bhuvan**.
| Satellite | Year | Fact |
|---|---|---|
| Bhaskara I | 1979 | First experimental EO satellite |
| Rohini RS-1 / **RS-D1** | 1980 / 31 May 1981 | Satellites launched by **SLV-3** (SLV-3 is a **launch vehicle, not a satellite**) |
| IRS-1A | 1988 | Baikonur, Vostok |
| IRS-1B / 1C | 1991 / 1995 | Baikonur, Soviet/Russian rockets |
| IRS-P2 | 1994 | First IRS launched successfully by **PSLV** (PSLV-D2) |
| IRS-1D | 1997 | PSLV-C1 – first operational PSLV |
- **IRS uses:** crop productivity, **groundwater**, **mineral exploration**, land use, forests, floods, drought – **not telecommunications or traffic studies** (UPSC 2015: 1, 2 and 3 only).
~~ Sources: PMF S&T Part 1 p.106-108, 112 (UPSC 2015 explanation); NextGen S&T Group 2 Part 2 p.4, 6-7

=== EO Satellite Series and Their Functions
| Series / satellite | Function |
|---|---|
| **Resourcesat** (2003, 2011, 2016) | Crops, watershed, precision farming (LISS-III/IV, AWiFS) |
| **Cartosat** | **Mapping** (cartography), city mapping, surveillance |
| **Oceansat-1** (1999, PSLV-C2), **Oceansat-2** (2009, **PSLV-C14**), **Oceansat-3 = EOS-06** (2022, PSLV-C54) | Ocean colour, SST, winds; **PFZ** fishing advisories |
| **RISAT** | **Microwave SAR** – all-weather, day-night imaging |
| **SCATSAT-1** (2016) | Scatterometer – ocean winds → **weather forecasting**, cyclones |
| HySIS | Hyperspectral imaging (not DTH) |
| **SARAL** | ISRO–**CNES (France)** **AltiKa** Ka-band **altimeter** (sea-surface height) – no thermometer |
| IMS-1 (2008) | Small satellite with multispectral and hyperspectral cameras – no scatterometer |
- **Match (TSPSC 2018):** GAGAN – navigation; GSAT – communication; **Cartosat – Earth observation**; Mangalyaan – traces of methane.
- **CNES** is the space agency of **France**; ISRO-CNES **maritime surveillance** pact, March 2019.
# EOS renamings
| EOS name | Earlier name | Note |
|---|---|---|
| **EOS-03** | GISAT-1 | **Geo-imaging** for near-real-time flood/cyclone watch (announced July 2021); lost on GSLV-F10, Aug 2021 (cryogenic stage) |
| EOS-04 | RISAT-1A | SAR; used in NRSC CROP wheat estimates |
| EOS-05 | GISAT-1A | GSLV-F17, 4 Sep 2026 – first geosynchronous land imager |
| EOS-06 | Oceansat-3 | PFZ advisories |
~~ Sources: PMF S&T Part 1 p.107-112; TSPSC 2018 key; app notes 5:39 sub 5

=== Cartosat Series
| Satellite | Launch | Feature |
|---|---|---|
| **Cartosat-1** | 2005, PSLV-C6 | **India's first mapping satellite**; stereo images for 3D maps |
| Cartosat-2 series | 2007-2018, PSLV | Sub-metre; **Cartosat-2E** (land survey) on PSLV-C38, **June 2017**; Cartosat-2 + 30 co-passengers (**31** satellites) on **PSLV-C40, 12 Jan 2018** |
| **Cartosat-3** | **27 Nov 2019**, **PSLV-C47** (not C40) | Third-generation agile satellite, **~25 cm**, with **13 US nanosatellites** |
- Cartosat-2 series (714 kg): PSLV-C37, 15 Feb 2017, record **104** satellites into a 506 km SSO.
- **Cartosat-2S** images showed **Joshimath** subsidence (NRSC, Jan 2023).
- Cartosat-3 imagery: Gati Shakti, borders, KASTURI and Bharat Darshan heritage apps.
~~ Sources: PMF S&T Part 1 p.108-109; app notes 5:39 sub 6

=== NISAR and Recent EO Missions
- **NISAR** (NASA-ISRO Synthetic Aperture Radar): joint **Earth-observation** mission, partnership signed **2014**; **NASA L-band + ISRO S-band** – world's first dual-frequency radar satellite; **12 m** reflector.
- Launched **30 July 2025** on **GSLV-F16** from Sriharikota into a **sun-synchronous LEO** (about 747 km) – not a High Earth Orbit; now operational.
> ⚠ Outdated stems: "to be launched in January 2024" / "set to launch in June 2025" – NISAR flew on 30 July 2025.
- **EOS-05** (GISAT-1A): GSLV-F17, **4 Sep 2026**, 2,367 kg; visible to long-wave IR; floods, cyclones, fires, crops.
| Lost satellite | Vehicle / date |
|---|---|
| EOS-03 (GISAT-1) | GSLV-F10, Aug 2021 |
| EOS-09 (RISAT-1B, C-band SAR) | PSLV-C61, May 2025 |
| DRDO EOS-N1 "Anvesha" | PSLV-C62, Jan 2026 |
~~ Sources: PMF S&T Part 2 p.55-56; app notes 5:39 sub 7

=== NRSC, Bhuvan and EO in the News; Andhra Pradesh
- Data chain: ground station → processing at **NRSC, Hyderabad** (nodal) → users. Training: **IIRS** and **CSSTEAP**, both **Dehradun**.
- **Bhuvan:** ISRO's web-based **geoportal** with **3-D imaging**, open to the public (UPSC 2010) – not a satellite or telescope. Other platforms: **Bhoonidhi, MOSDAC, VEDAS**.
- Uses: groundwater prospects, wastelands, **FASAL** crop forecasting, drought, NUIS, SIS-DP, **INFFRAS** (Indian Forest Fire Response and Assessment System).
| In news | Agency / satellite |
|---|---|
| Joshimath subsidence (Jan 2023) | NRSC with **Cartosat-2S** |
| Landslide Atlas of India | NRSC (2023) |
| CROP crop-progress framework | NRSC with EOS-04 SAR |
| Glacial lakes | CWC since 2011 with NRSC imagery; Glacial Lake Atlas 2023: 7,570 lakes; Himalayan lake area up ~9% 2011-2025 |
- **AP:** **APSAC** (AP Space Applications Centre) is the state remote-sensing agency; **SDSC-SHAR** (Tirupati district) gives Bay of Bengal cyclone data to **APSDMA**.
~~ Sources: NextGen S&T Group 2 Part 2 p.4, 9, 13; app notes 5:39 sub 10
