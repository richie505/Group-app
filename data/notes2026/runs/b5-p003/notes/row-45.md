=== GIS – Concept, Components and Uses
- **GIS = Geographic Information System**: a computer system to **store, manipulate, analyse and present** all types of geographical (**spatial**) data – the most complete system for modelling spatial data and community vulnerability.
- **Father of GIS:** **Roger Tomlinson** – coined the term for the Canada GIS (1960s).
- Each theme is a **layer**; **overlay analysis** combines layers; data = spatial (vector, raster) + attribute tables.
| Component | Examples |
|---|---|
| Hardware | Computer, **digitizer** (tablet/table converting analog data to digital), scanner, GPS receiver, plotter |
| Software | **QGIS** – free, open-source, cross-platform desktop GIS |
| Data | Spatial (points, lines, polygons; satellite images) + attributes |
- **Remote sensing + GIS:** maps prepared from satellite data or aerial photos are digitised and stored in GIS; manual maps are slow to prepare and hard to update.
- **Decision Support System:** data systems for planning.
- **Survey of India** prepares India's **topographical maps**.
# GIS in disasters
- **Situational awareness map:** real-time weather, hospitals and shelters, damage imagery; **pre-disaster population density maps** are least useful in the live response.
- Real-time sources: satellite imagery, weather data, sensor networks – **not news channels**.
| Remote sensing | GIS |
|---|---|
| Rainfall estimation during a cyclone; post-disaster damage | Mapping spread of infectious diseases; landslide hazard zonation |
- Earthquake **magnitude and epicentre** come from **seismographs**, not GIS.
~~ Sources: app notes 5:45 sub 1; general knowledge (Tomlinson, Survey of India)

=== Disaster Management from Space
| Can be monitored from space | Cannot |
|---|---|
| Floods, cyclones, drought, forest fires, tsunami inundation, landslides, post-quake ground deformation | **Spread of a disease among humans**, **heart attack**; **earthquake prediction** |
- Satellites give **near-real-time images** (remote sensing) for disaster management.
- Fire hotspots: thermal-infrared **MODIS** (Terra/Aqua) and **VIIRS** (Suomi-NPP), received at **Shadnagar** (NRSC) → **Forest Survey of India** alert system (not IMD) – the modern **fire alert system**.
- **NRSC activities:** near-real-time flood and cyclone mapping, forest-fire alerts, spatial flood early warning, **rapid damage assessment of landslides**; **Decision Support Centre**; **NDEM** (National Database for Emergency Management).
- **Bhuvan disaster services:** NDEM, drought monitoring, flood monitoring – no nuclear-hazard warning.
- **Ganga-Brahmaputra basin** = most flood-prone area (NRSC).
- **Landslides:** **DInSAR** gives repeat-pass slope-deformation monitoring, before visible failure, without a ground instrument network.
- **Global Forest Watch (WRI):** custom maps, forest trends, alerts.
| Satellite | Use |
|---|---|
| RISAT / SAR | Flood mapping through clouds |
| INSAT-3DS | Cyclone tracks |
| Cartosat | Damage mapping |
- **DMSP** (ISRO): INSAT and IRS for imaging and communication; States must request data from NRSC.
- **INSAT Disaster Warning System:** Cyclone Warning Centre **Chennai → C-band uplink → S-band downlink**.
- **NDMA** uses GIS for planning, decision support, guidelines; **ISRO** led the **International Charter Space and Major Disasters** from **April 2025** (6 months).
~~ Sources: app notes 5:45 sub 5

=== Remote Sensing Basics and Spectral Indices
- **Remote sensing:** gathering **images**/information about Earth **without physical contact**, from reflected or emitted radiation; covers dangerous or inaccessible areas.
| Type | Energy | Example |
|---|---|---|
| Active | Sends its own signal | **RISAT** radar, LiDAR |
| Passive | Natural radiation (sunlight) | Resourcesat, Oceansat |
- **Microwave / SAR** sees through cloud and darkness; **soil moisture** best measured by microwave/SAR.
- **InSAR:** compares the **phase** of radar images from **orbiting** satellites → **ground deformation** (quakes, subsidence, landslides).
- **NISAR:** radar, **L-band and S-band**; centimetre-scale ground movement.
- Applications: land cover, vegetation, forests, **surface and groundwater**, snow, wetlands, **minerals and hydrocarbons**, crop area and **crop yield** – "all of the above".
- Soil nutrient testing by **chemical analysis is NOT remote sensing**.
| Term | Meaning |
|---|---|
| **NDVI** | **Normalized Difference Vegetation Index** = (NIR − Red)/(NIR + Red); healthy vegetation reflects **near-infrared**; −1 to +1; most used for **drought** |
| VCI | From NDVI; drought declaration |
| Ecology index | Vegetation, water content, biological quantity – not cost and production |
| NH Green Cover Index 2025-26 | NHAI + NRSC; satellite green cover of **national highways** |
- **National Carbon Project** (ISRO-GBP): **carbon pools, fluxes and net carbon balance** of the terrestrial biosphere – vegetation pools, soil pools, fluxes.
~~ Sources: NextGen S&T Group 2 Part 2 p.4-5; Rocket Disaster Management p.23; app notes 5:45 sub 0-1, 9

=== Agencies, Bhuvan and Geoportals
| Agency | Role |
|---|---|
| **NRSC, Hyderabad** | Nodal agency – data acquisition, processing, dissemination, aerial remote sensing, disaster decision support; runs Bhuvan; earth station at **Shadnagar** |
| IIRS, Dehradun | Training and education in remote sensing and GIS |
| SAC, Ahmedabad | Sensors; MOSDAC, VEDAS, Nabhmitra |
| NESAC, Umiam (Meghalaya) | North-East applications |
| RRSCs | **5** (Bengaluru, Jodhpur, Kharagpur, Nagpur, Delhi) – not Hyderabad |
- SPOT, EROS are foreign satellites, not Indian agencies.
- **Bhuvan:** ISRO's **geoportal** ("India's Google Earth"), by **NRSC**, launched **2009**; 2D/3D imagery – not a spacecraft or telescope.
| Portal | Use |
|---|---|
| **Bhuvan Panchayat** | Gram panchayat planning; powered by **ISRO/NRSC** (not DRDO) |
| Bhoonidhi (NRSC) | EO data archive since 1988 |
| **MOSDAC** (SAC) | **Meteorological & Oceanographic Satellite Data Archival Centre**; disaster alerts |
| Yuktdhara | MGNREGA asset planning |
| SVAMITVA | Drone mapping with **Survey of India** |
| PM Gati Shakti | National Master Plan GIS, by **BISAG-N** |
~~ Sources: NextGen S&T Group 2 Part 2 p.4; app notes 5:45 sub 2-3

=== Agriculture Applications
| Programme | Purpose |
|---|---|
| **FASAL** | Forecasting Agricultural output using **Space, Agro-meteorology and Land-based observations** (no revenue records) |
| MNCFC (2012) | Mahalanobis National Crop Forecast Centre – runs FASAL |
| YES-TECH | **Yield estimation** (rice) for PMFBY |
| CHAMAN | Horticulture area and production |
| NADAMS | Agricultural drought monitoring |
| CROP framework | Rabi 2024-25 wheat 122.724 MT |
- **Resourcesat:** crop acreage, watershed management, precision farming; **SLUSI** maps soils.
- **Meghdoot:** agro-met advisory app of **IMD and ICAR**.
~~ Sources: app notes 5:45 sub 4, 7

=== Fisheries, Weather Apps and AP Applications
- **PFZ advisories** from **chlorophyll and SST**, issued by **INCOIS, Hyderabad** (EOS-06); INCOIS also issues the Ocean State Forecast.
| Device | Developer | Fact |
|---|---|---|
| **Nabhmitra** | ISRO **SAC, Ahmedabad** | Fishermen safety device; tested at **Neendakara (Kerala), Aug 2023** |
| GEMINI | INCOIS with AAI (GAGAN) | PFZ, ocean-state, disaster alerts |
| DAT-SG | ISRO | NavIC distress transmitter; sends acknowledgement back |
| App | Developer / purpose |
|---|---|
| Damini | Lightning – IITM Pune |
| Mausam | IMD |
| **Andhra Pradesh Varuna** (2017) | AP: **automatic weather stations + groundwater piezometers + ISRO forecasts** |
| City Flood Alert (AP) | RTGS + APSDMA + IIT Gandhinagar; first in Vijayawada |
# APSAC and AP
| Technology | Purpose |
|---|---|
| Drought monitoring (VCI) | **Assessment of vegetation**; 103 drought mandals (2024-25) |
| YES-TECH | **Rice yield** estimation; pilots in Nandyal and Kakinada |
| RWS pipeline mapping | Water-supply assets via a **mobile app** and dashboard |
| APMVTS | **Real-time tracking of mineral vehicles** (AIS-140, 50,000) |
- APSSDI: **74** GIS layers; PM Gati Shakti AP: **271** layers; APSDMA–NRSC MoU (15 Apr 2026) on lightning deaths; RTGS hub Vijayawada alerts fishermen on cyclones, high waves, fish shoals; shoreline mapping of the 1,053 km coast.
~~ Sources: PMF Lens Aug 2026 p.56; web: yovizag.com (AP Varuna); app notes 5:45 sub 6-7, 10

=== Tele-education, Telemedicine and Navigation
- INSAT/GSAT enable **tele-education (EDUSAT, GRAMSAT)**, **telemedicine** and ISRO **Village Resource Centres** (not IMD).
- **Swayam Prabha:** group of **40 free educational DTH channels on GSAT-15**.
- **Eklavya:** educational TV channel for **engineering and technology** subjects.
- Satellite timing: banks time-stamp transactions, power grids synchronise phase; GPS is still the IST reference.
- **March 2026:** IRNSS-1F clock failed – only **3 PNT-capable** NavIC satellites; **NVS-02** stranded in an incorrect orbit.
- **GAGAN** (ISRO-AAI) payloads on **GSAT-8, 10, 15**.
~~ Sources: PMF Lens Apr 2026 p.11; PMF S&T Part 2 p.50; app notes 5:45 sub 8
