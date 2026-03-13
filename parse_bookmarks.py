#!/usr/bin/env python3
"""Parse browser bookmarks HTML and organize into categorized markdown files for MkDocs."""

import re
import json
from datetime import datetime
from collections import defaultdict

# Bookmarks data extracted from the Netscape bookmark file
bookmarks = [
    # GIS & Mapping Tools
    {"title": "10 Best Laptops for GIS in 2023", "url": "https://gisrsstudy.com/best-laptops-for-gis/#Best_Laptop_for_GIS_Software_in_2023", "category": "GIS & Remote Sensing", "tags": ["GIS", "hardware", "laptops"]},
    {"title": "1000 GIS Applications & Uses - How GIS Is Changing the World", "url": "https://gisgeography.com/gis-applications-uses/", "category": "GIS & Remote Sensing", "tags": ["GIS", "applications"]},
    {"title": "GISjobs.com - The Most Popular GIS Jobs Website", "url": "https://www.gisjobs.com/", "category": "Career & Jobs", "tags": ["GIS", "jobs", "career"]},
    {"title": "Find Jobs for GIS Specialist, Cartographer and Drone Pilot", "url": "https://jobingis.com/", "category": "Career & Jobs", "tags": ["GIS", "jobs", "cartography", "drones"]},
    {"title": "GIS & Beers Blog", "url": "https://www.gisandbeers.com/blog/", "category": "GIS & Remote Sensing", "tags": ["GIS", "blog", "tutorials"]},
    {"title": "Maps of Paintings Converted to Art with QGIS", "url": "https://www.gisandbeers.com/mapas-de-cuadros-convertidos-en-arte-con-qgis/", "category": "GIS & Remote Sensing", "tags": ["QGIS", "cartography", "art"]},
    {"title": "Sixteen Square Inches of Map: A Map Course by Evan Applegate", "url": "https://youshouldmakemaps.com/", "category": "GIS & Remote Sensing", "tags": ["cartography", "course", "mapping"]},
    {"title": "Kernel Density (Spatial Analyst) - ArcGIS Pro", "url": "https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/kernel-density.htm", "category": "GIS & Remote Sensing", "tags": ["ArcGIS", "spatial analysis", "kernel density"]},
    {"title": "Geographically Weighted Regression Tutorial in R", "url": "https://rpubs.com/quarcs-lab/tutorial-gwr1", "category": "GIS & Remote Sensing", "tags": ["R", "GWR", "spatial statistics", "tutorial"]},
    {"title": "Download Shapefiles For Any Country", "url": "https://mapscaping.com/download-shapefiles-for-any-country/", "category": "Geospatial Data Sources", "tags": ["shapefiles", "data", "download"]},
    {"title": "Lat Long to UTM Converter", "url": "https://www.latlong.net/lat-long-utm.html", "category": "GIS & Remote Sensing", "tags": ["coordinates", "UTM", "converter", "tools"]},
    {"title": "QGIS Downloads (Windows)", "url": "https://ftp.osuosl.org/pub/osgeo/download/qgis/windows/", "category": "GIS & Remote Sensing", "tags": ["QGIS", "download", "software"]},
    {"title": "SVG Repository - Free SVG Icons", "url": "https://www.svgrepo.com/collections/", "category": "GIS & Remote Sensing", "tags": ["SVG", "icons", "design"]},
    {"title": "Prettymaps - Beautiful Maps with Python", "url": "https://colab.research.google.com/github/marceloprates/prettymaps/blob/master/notebooks/examples.ipynb", "category": "GIS & Remote Sensing", "tags": ["Python", "cartography", "visualization"]},

    # Google Earth Engine
    {"title": "Google Earth Engine Code Editor", "url": "https://code.earthengine.google.com/", "category": "Google Earth Engine", "tags": ["GEE", "remote sensing", "code editor"]},
    {"title": "Earth Engine Data Catalog", "url": "https://developers.google.com/earth-engine/datasets", "category": "Google Earth Engine", "tags": ["GEE", "datasets", "catalog"]},
    {"title": "Earth Engine Data Catalog (Full)", "url": "https://developers.google.com/earth-engine/datasets/catalog", "category": "Google Earth Engine", "tags": ["GEE", "datasets", "catalog"]},
    {"title": "QGIS Earth Engine Examples (300+ Python Scripts)", "url": "https://github.com/giswqs/qgis-earthengine-examples/tree/master", "category": "Google Earth Engine", "tags": ["GEE", "QGIS", "Python", "examples"]},
    {"title": "Earth Engine Image Visualization Example", "url": "https://github.com/giswqs/qgis-earthengine-examples/blob/master/Image/image_vis.py", "category": "Google Earth Engine", "tags": ["GEE", "visualization", "Python"]},
    {"title": "Earth Map - Interactive GEE Explorer", "url": "https://earthmap.org/", "category": "Google Earth Engine", "tags": ["GEE", "interactive", "mapping"]},
    {"title": "TerraClimate App (Hemedi)", "url": "https://ee-hemedlungo.projects.earthengine.app/view/terraclimateapp", "category": "Google Earth Engine", "tags": ["GEE", "climate", "TerraClimate", "app"]},
    {"title": "Masai Mara GEE Script", "url": "https://code.earthengine.google.com/5245263e464d2302f68d11090e382542?noload=1", "category": "Google Earth Engine", "tags": ["GEE", "Masai Mara", "script"]},

    # Remote Sensing & Earth Observation
    {"title": "Sentinel-1 Mission", "url": "https://sentiwiki.copernicus.eu/web/s1-mission", "category": "Remote Sensing", "tags": ["Sentinel-1", "SAR", "Copernicus"]},
    {"title": "Sentinel-2 Applications", "url": "https://sentiwiki.copernicus.eu/web/s2-applications", "category": "Remote Sensing", "tags": ["Sentinel-2", "applications", "Copernicus"]},
    {"title": "Sentinel-2 Land Use/Land Cover Timeseries Downloader", "url": "https://www.arcgis.com/apps/instant/media/index.html?appid=fc92d38533d440078f17678ebc20e8e2", "category": "Remote Sensing", "tags": ["Sentinel-2", "LULC", "download"]},
    {"title": "Review of Remote Sensing for Environmental Monitoring in China", "url": "https://www.mdpi.com/2072-4292/12/7/1130", "category": "Remote Sensing", "tags": ["remote sensing", "environmental monitoring", "review"]},
    {"title": "Burn Severity Mapping with QGIS (Landsat 8)", "url": "https://www.un-spider.org/advisory-support/recommended-practices/recommended-practice-burn-severity/Step-by-Step/QGIS", "category": "Remote Sensing", "tags": ["burn severity", "QGIS", "Landsat", "fire"]},
    {"title": "EarthExplorer - USGS", "url": "https://earthexplorer.usgs.gov/", "category": "Geospatial Data Sources", "tags": ["USGS", "satellite imagery", "download"]},
    {"title": "FIRMS - Fire Information for Resource Management", "url": "https://firms.modaps.eosdis.nasa.gov/download/list.php", "category": "Geospatial Data Sources", "tags": ["fire", "MODIS", "NASA", "FIRMS"]},
    {"title": "30-Meter SRTM Elevation Data Downloader", "url": "https://dwtkns.com/srtm30m/", "category": "Geospatial Data Sources", "tags": ["DEM", "SRTM", "elevation", "download"]},
    {"title": "Visible Band NDVI (vNDVI) Using Genetic Algorithms", "url": "https://www.sciencedirect.com/science/article/abs/pii/S016816991932383X", "category": "Remote Sensing", "tags": ["NDVI", "vegetation index", "RGB", "research"]},
    {"title": "Platforms and Orbits - STARS Project", "url": "https://www.stars-project.org/en/knowledgeportal/magazine/remote-sensing-technology/introduction/platforms-and-orbits/", "category": "Remote Sensing", "tags": ["satellite", "orbits", "platforms", "education"]},

    # Geospatial Data Sources
    {"title": "GBIF - Global Biodiversity Information Facility", "url": "https://www.gbif.org/search?q=elephant", "category": "Geospatial Data Sources", "tags": ["biodiversity", "GBIF", "species data"]},
    {"title": "OpenTopography", "url": "https://opentopography.org/", "category": "Geospatial Data Sources", "tags": ["topography", "LiDAR", "DEM", "elevation"]},
    {"title": "CHIRPS Rainfall Data (East Africa Monthly)", "url": "https://data.chc.ucsb.edu/products/CHIRPS-2.0/EAC_monthly/tifs/", "category": "Geospatial Data Sources", "tags": ["rainfall", "CHIRPS", "climate", "East Africa"]},
    {"title": "MODIS Land Surface Temperature Data", "url": "https://e4ftl01.cr.usgs.gov/MOLT/MOD11C3.061/", "category": "Geospatial Data Sources", "tags": ["MODIS", "temperature", "LST"]},
    {"title": "LandScan Global Population Database", "url": "https://www.eastview.com/resources/e-collections/landscan/", "category": "Geospatial Data Sources", "tags": ["population", "LandScan", "demographics"]},
    {"title": "LandScan - Oak Ridge National Laboratory", "url": "https://www.ornl.gov/project/landscan", "category": "Geospatial Data Sources", "tags": ["population", "LandScan", "ORNL"]},
    {"title": "HydroRIVERS - Global River Network", "url": "https://www.hydrosheds.org/products/hydrorivers#downloads", "category": "Geospatial Data Sources", "tags": ["rivers", "hydrology", "HydroSHEDS"]},
    {"title": "WorldClim - Historical Climate Data", "url": "https://worldclim.org/data/worldclim21.html", "category": "Geospatial Data Sources", "tags": ["climate", "WorldClim", "temperature", "precipitation"]},
    {"title": "Geofabrik - OpenStreetMap Data Extracts", "url": "https://www.geofabrik.de/", "category": "Geospatial Data Sources", "tags": ["OSM", "OpenStreetMap", "data"]},
    {"title": "Global Human Settlement Layer Download", "url": "https://human-settlement.emergency.copernicus.eu/download.php?ds=smod", "category": "Geospatial Data Sources", "tags": ["urban", "settlement", "population", "Copernicus"]},
    {"title": "WMS Tiles - EOX Maps", "url": "https://tiles.maps.eox.at/wms?service=wms&request=getcapabilities", "category": "Geospatial Data Sources", "tags": ["WMS", "basemap", "tiles"]},
    {"title": "Biodiversity Monitoring Datasets", "url": "https://datasources.speciesmonitoring.org/", "category": "Geospatial Data Sources", "tags": ["biodiversity", "monitoring", "species"]},
    {"title": "Spatial Reserves - Public Domain Spatial Data", "url": "https://spatialreserves.wordpress.com/page/2/", "category": "Geospatial Data Sources", "tags": ["spatial data", "public domain", "resources"]},
    {"title": "Geofolio - Country Profiles", "url": "https://geofolio.org/f/711109820", "category": "Geospatial Data Sources", "tags": ["country profiles", "statistics", "data"]},

    # ArcGIS Online & Portals
    {"title": "Africa GeoPortal", "url": "https://africageoportal.maps.arcgis.com/home/index.html", "category": "ArcGIS & Web GIS", "tags": ["ArcGIS Online", "Africa", "geoportal"]},
    {"title": "UDSM RISE ArcGIS Online", "url": "https://udsmrise.maps.arcgis.com/home/index.html", "category": "ArcGIS & Web GIS", "tags": ["ArcGIS Online", "UDSM", "Tanzania"]},
    {"title": "RCMRD ArcGIS Training Platform", "url": "https://rcmrd-training.maps.arcgis.com/home/index.html", "category": "ArcGIS & Web GIS", "tags": ["ArcGIS", "RCMRD", "training"]},
    {"title": "Africa WDPA Protected Areas - ArcGIS Hub", "url": "https://hub.arcgis.com/datasets/e5f2344bd8d6476a9921d6c77c10f152_18/explore", "category": "ArcGIS & Web GIS", "tags": ["protected areas", "WDPA", "Africa", "conservation"]},
    {"title": "Mapbox Console", "url": "https://console.mapbox.com/", "category": "ArcGIS & Web GIS", "tags": ["Mapbox", "web mapping", "API"]},
    {"title": "Africapolis - Urban Data", "url": "https://africapolis.org/en", "category": "ArcGIS & Web GIS", "tags": ["urbanization", "Africa", "population"]},

    # Conservation & Wildlife
    {"title": "IUCN Red List of Threatened Species", "url": "https://www.iucnredlist.org/", "category": "Conservation & Wildlife", "tags": ["IUCN", "endangered species", "conservation"]},
    {"title": "IUCN Eastern and Southern Africa", "url": "https://iucn.org/our-work/region/eastern-and-southern-africa", "category": "Conservation & Wildlife", "tags": ["IUCN", "Eastern Africa", "conservation"]},
    {"title": "Convention on Biological Diversity", "url": "https://www.cbd.int/", "category": "Conservation & Wildlife", "tags": ["CBD", "biodiversity", "international"]},
    {"title": "MegaDetector - AI for Camera Traps", "url": "https://github.com/agentmorris/MegaDetector/blob/main/megadetector.md", "category": "Conservation & Wildlife", "tags": ["AI", "camera traps", "wildlife detection"]},
    {"title": "AddaxAI - Camera Trap Image Analysis", "url": "https://addaxdatascience.com/addaxai/", "category": "Conservation & Wildlife", "tags": ["AI", "camera traps", "image analysis"]},
    {"title": "Sensing Clues - Conservation Technology Platform", "url": "https://www.sensingclues.org/portal", "category": "Conservation & Wildlife", "tags": ["conservation", "technology", "monitoring"]},
    {"title": "WCS Mongolia - Priority Species", "url": "https://mongolia.wcs.org/Priority-Species.aspx", "category": "Conservation & Wildlife", "tags": ["WCS", "Mongolia", "wildlife"]},

    # Human-Wildlife Conflict Research
    {"title": "Building Human-Elephant Relationships (Semantic Scholar)", "url": "https://www.semanticscholar.org/paper/Building-human%E2%80%93elephant-relationships-based-on-and-Terada/30f855d551e85f649b7c50210116fc220bba74de", "category": "Human-Wildlife Conflict", "tags": ["human-elephant conflict", "SDGs", "research"]},
    {"title": "Temporal and Spatial Patterns of Human-Elephant Conflict in Nepal", "url": "https://www.researchgate.net/publication/261551760", "category": "Human-Wildlife Conflict", "tags": ["HEC", "Nepal", "spatial patterns"]},
    {"title": "Impact of Wildlife on Food Crops in Eastern Nepal", "url": "https://www.tandfonline.com/doi/abs/10.1080/10871209.2021.1926601", "category": "Human-Wildlife Conflict", "tags": ["crop raiding", "Nepal", "human dimensions"]},
    {"title": "KWS Elephant Conservation Strategy (PDF)", "url": "https://maraelephantproject.org/wp-content/uploads/2016/04/KWS-Elephant-Strategy.pdf", "category": "Human-Wildlife Conflict", "tags": ["Kenya", "elephant", "strategy", "KWS"]},
    {"title": "Crop-Raiding Patterns by Elephants in Laikipia, Kenya", "url": "https://www.tandfonline.com/doi/full/10.1080/14772000.2010.533716", "category": "Human-Wildlife Conflict", "tags": ["crop raiding", "elephants", "Kenya", "management"]},
    {"title": "GIS-Based Multi-Criteria Evaluation for Asian Elephant Conflict", "url": "https://web.p.ebscohost.com/ehost/pdfviewer/pdfviewer?vid=7", "category": "Human-Wildlife Conflict", "tags": ["GIS", "MCE", "Asian elephant", "conflict mapping"]},
    {"title": "Coexistence Between Human and Wildlife - Bale Mountains, Ethiopia", "url": "https://bmcecol.biomedcentral.com/articles/10.1186/s12898-020-00319-1", "category": "Human-Wildlife Conflict", "tags": ["coexistence", "Ethiopia", "Bale Mountains", "mitigation"]},
    {"title": "Human-Elephant Conflict: Implications for Livelihoods (Handbook Chapter)", "url": "https://www.elgaronline.com/edcollchap/book/9781839106071/book-part-9781839106071-9.xml", "category": "Human-Wildlife Conflict", "tags": ["HEC", "livelihoods", "tourism", "conservation"]},

    # Academic Research & Databases
    {"title": "ResearchGate", "url": "https://www.researchgate.net/", "category": "Academic Resources", "tags": ["research", "papers", "academic network"]},
    {"title": "DOAJ - Directory of Open Access Journals", "url": "https://doaj.org/", "category": "Academic Resources", "tags": ["open access", "journals", "research"]},
    {"title": "BMC - BioMed Central", "url": "https://www.biomedcentral.com/", "category": "Academic Resources", "tags": ["biomedical", "open access", "journals"]},
    {"title": "Emerald Insight - Journals & Books", "url": "https://www.emerald.com/insight/", "category": "Academic Resources", "tags": ["journals", "books", "research"]},
    {"title": "Taylor & Francis eBooks", "url": "https://www.taylorfrancis.com/", "category": "Academic Resources", "tags": ["books", "journals", "academic"]},
    {"title": "EBSCOhost - Academic Search", "url": "https://web.p.ebscohost.com/ehost/search/basic", "category": "Academic Resources", "tags": ["database", "search", "academic"]},
    {"title": "Library Genesis", "url": "https://libgen.rs/", "category": "Academic Resources", "tags": ["books", "library", "download"]},
    {"title": "Library Genesis (Mirror)", "url": "https://libgenesis.net/", "category": "Academic Resources", "tags": ["books", "library", "download"]},
    {"title": "ScienceDirect", "url": "https://www.sciencedirect.com/", "category": "Academic Resources", "tags": ["journals", "Elsevier", "research"]},
    {"title": "Semantic Scholar", "url": "https://www.semanticscholar.org/", "category": "Academic Resources", "tags": ["AI", "search", "papers"]},
    {"title": "Decision Support Systems: Concepts and Resources", "url": "https://scholarworks.uni.edu/facbook/67/", "category": "Academic Resources", "tags": ["DSS", "decision support", "book"]},
    {"title": "Spatial Decision Support Systems (Unit 127)", "url": "https://escholarship.org/uc/item/73p320mb", "category": "Academic Resources", "tags": ["SDSS", "spatial", "GIS"]},
    {"title": "Turnitin - Plagiarism Checker", "url": "https://www.turnitin.com/", "category": "Academic Resources", "tags": ["plagiarism", "academic integrity"]},

    # OpenStreetMap & Community Mapping
    {"title": "OpenStreetMap Changesets", "url": "https://www.openstreetmap.org/history", "category": "OpenStreetMap", "tags": ["OSM", "mapping", "changesets"]},
    {"title": "MapRoulette - Fix Building/Highway Intersections (Tanzania)", "url": "https://maproulette.org/challenge/40222/task/170768515", "category": "OpenStreetMap", "tags": ["OSM", "MapRoulette", "Tanzania", "quality"]},

    # Career & Professional
    {"title": "LinkedIn - Christina Mapunda", "url": "https://www.linkedin.com/in/christina-mapunda-316074173/", "category": "Career & Jobs", "tags": ["LinkedIn", "profile", "networking"]},
    {"title": "My Perfect Resume Dashboard", "url": "https://www.myperfectresume.com/dashboard", "category": "Career & Jobs", "tags": ["resume", "CV"]},
    {"title": "Upwork Profile", "url": "https://www.upwork.com/nx/create-profile/finish", "category": "Career & Jobs", "tags": ["freelancing", "Upwork"]},
    {"title": "MSF GIS Specialist Position", "url": "https://msf.or.ke/en/ads/geographical-information-systems-specialist-gis", "category": "Career & Jobs", "tags": ["GIS", "MSF", "humanitarian", "job"]},
    {"title": "Remote4Africa - Operations Manager", "url": "https://remote4africa.com/jobs/contract-operations-manager-marketplace", "category": "Career & Jobs", "tags": ["remote", "Africa", "job"]},
    {"title": "TPC One Suite - Recruitment", "url": "https://onesuite.tpc.co.tz/Account/Recruitment/Login", "category": "Career & Jobs", "tags": ["Tanzania", "TPC", "recruitment"]},

    # Scholarships & Grants
    {"title": "The Explorers Club - Grants", "url": "https://www.explorers.org/grants/", "category": "Scholarships & Grants", "tags": ["grants", "exploration", "funding"]},
    {"title": "Karimjee Conservation Scholarships - University of Glasgow", "url": "https://www.gla.ac.uk/scholarships/karimjeeconservationscholarships/", "category": "Scholarships & Grants", "tags": ["scholarship", "conservation", "Glasgow"]},
    {"title": "ALU Admissions", "url": "https://start.alueducation.com/", "category": "Scholarships & Grants", "tags": ["ALU", "admissions", "university"]},
    {"title": "HESLB - Student Loan Portal", "url": "https://olas.heslb.go.tz/", "category": "Scholarships & Grants", "tags": ["loans", "Tanzania", "HESLB"]},

    # Disaster Risk Reduction
    {"title": "Sendai Framework - Words into Action", "url": "https://www.preventionweb.net/sendai-framework/words-into-action", "category": "Disaster Risk Reduction", "tags": ["Sendai Framework", "DRR", "UN"]},

    # Training & Courses
    {"title": "W3Schools HTML Tutorial", "url": "https://www.w3schools.com/html/default.asp", "category": "Learning & Tutorials", "tags": ["HTML", "web development", "tutorial"]},
    {"title": "National Geographic & TNC Data Visualization Externship", "url": "https://www.extern.com/externships/national-geographic-society-the-nature-conservancy-community-conservation-data-visualization-and-mapping-externship", "category": "Learning & Tutorials", "tags": ["NatGeo", "TNC", "data visualization", "externship"]},
    {"title": "Advanced GIS Training 2024 - Penn State", "url": "https://psu.mediaspace.kaltura.com/media/Advanced+GIS+Training+2024A+Opening+session/1_wx4l523a", "category": "Learning & Tutorials", "tags": ["GIS", "training", "Penn State"]},

    # Everyday Tools
    {"title": "Google Search", "url": "https://www.google.com/", "category": "Everyday Tools", "tags": ["search", "Google"]},
    {"title": "Gmail", "url": "https://accounts.google.com/b/0/AddMailService", "category": "Everyday Tools", "tags": ["email", "Google"]},
    {"title": "Google Maps", "url": "https://maps.google.com/", "category": "Everyday Tools", "tags": ["maps", "Google", "navigation"]},
    {"title": "YouTube", "url": "https://youtube.com/", "category": "Everyday Tools", "tags": ["video", "YouTube"]},
    {"title": "Pinterest", "url": "https://www.pinterest.com/pin-creation-tool/", "category": "Everyday Tools", "tags": ["design", "Pinterest", "inspiration"]},
    {"title": "Dropbox", "url": "https://www.dropbox.com/home", "category": "Everyday Tools", "tags": ["cloud storage", "Dropbox"]},
    {"title": "iLovePDF", "url": "https://www.ilovepdf.com/", "category": "Everyday Tools", "tags": ["PDF", "tools"]},
    {"title": "ChatGPT", "url": "https://chat.openai.com/", "category": "Everyday Tools", "tags": ["AI", "chatbot", "OpenAI"]},
    {"title": "Bible Gateway - Genesis 9:1 (KJV)", "url": "https://www.biblegateway.com/passage/?search=Genesis%209%3B1&version=KJV", "category": "Everyday Tools", "tags": ["Bible", "scripture"]},

    # Entertainment & Media
    {"title": "Zilizopendwa Best Ever - YouTube", "url": "https://www.youtube.com/watch?v=BUQ-tyXoNE4", "category": "Entertainment", "tags": ["music", "Swahili", "classic"]},
    {"title": "Beautiful Hymns For Relaxing & Prayer", "url": "https://www.youtube.com/watch?v=m9LgCRp0B0Q", "category": "Entertainment", "tags": ["hymns", "prayer", "worship"]},
    {"title": "Swahili Worship Songs - 30 Minutes", "url": "https://www.youtube.com/watch?v=vP7Hol7V2ps", "category": "Entertainment", "tags": ["worship", "Swahili", "music"]},
    {"title": "Mighty Name of Jesus - The Belonging Co", "url": "https://www.youtube.com/watch?v=SiNTfREV7oM", "category": "Entertainment", "tags": ["worship", "music"]},
    {"title": "Koinonia Watch TV - YouTube", "url": "https://www.youtube.com/@koinoniawatchtv/videos", "category": "Entertainment", "tags": ["church", "sermons"]},
    {"title": "Savage Kingdom - Nat Geo Wild Playlist", "url": "https://www.youtube.com/playlist?list=PLNxd9fYeqXeYhu-E3T5CC_XjgO9aNuzjq", "category": "Entertainment", "tags": ["documentary", "wildlife", "Nat Geo"]},
    {"title": "Human (2015) - Documentary", "url": "https://www.filmsforaction.org/watch/human/", "category": "Entertainment", "tags": ["documentary", "film", "humanity"]},
    {"title": "Documentary Heaven", "url": "https://documentaryheaven.com/", "category": "Entertainment", "tags": ["documentaries", "streaming"]},
    {"title": "Nkiri - International Films", "url": "https://nkiri.com/category/international/", "category": "Entertainment", "tags": ["movies", "streaming"]},

    # Tanzania Resources
    {"title": "Tanzania Census 2022 - Population Distribution Report", "url": "https://www.nbs.go.tz/nbs/takwimu/Census2022/Administrative_units_Population_Distribution_Report_Tanzania_Mainland_volume1b.pdf", "category": "Tanzania Resources", "tags": ["census", "population", "Tanzania", "NBS"]},
    {"title": "TANAPA Park Tariffs", "url": "https://www.tanzaniaparks.go.tz/uploads/publications/en-1615966435-NEWTARIFF.pdf", "category": "Tanzania Resources", "tags": ["national parks", "Tanzania", "TANAPA", "tariffs"]},
    {"title": "UDSM Module Details", "url": "http://196.192.79.35/student.modules.php", "category": "Tanzania Resources", "tags": ["UDSM", "university", "modules"]},
    {"title": "GBIF Global Biodiversity", "url": "https://www.gbif.org/", "category": "Geospatial Data Sources", "tags": ["GBIF", "biodiversity", "species"]},

    # Database & IT
    {"title": "Data Manipulation Language (DML) - Techopedia", "url": "https://www.techopedia.com/definition/1179/data-manipulation-language-dml", "category": "Learning & Tutorials", "tags": ["SQL", "DML", "database"]},
    {"title": "SQL Data Control Language (DCL)", "url": "https://www.tutorialride.com/dbms/sql-data-control-language-dcl.htm", "category": "Learning & Tutorials", "tags": ["SQL", "DCL", "database"]},
    {"title": "Intellectual Property Issues in Cyberspace", "url": "https://www.legalserviceindia.com/legal/article-3233-intellectual-property-issues-in-cyberspace.html", "category": "Learning & Tutorials", "tags": ["IP", "cybersecurity", "law"]},

    # Habitat Connectivity Training
    {"title": "Habitat Connectivity Training - Day 2 (Gmail)", "url": "https://mail.google.com/mail/u/0/?tab=rm&ogbl#search/AGT", "category": "Learning & Tutorials", "tags": ["habitat connectivity", "training", "GIS"]},
    {"title": "Pattern Analysis Submission Folder (Google Drive)", "url": "https://drive.google.com/drive/folders/179M8gbpAUc6m-8khBFH0VnBj2BMu0xP7", "category": "Learning & Tutorials", "tags": ["pattern analysis", "training", "GIS"]},
    {"title": "Advanced GIS Analysis - Climatology Graph", "url": "file:///D:/A_RISE%20TRAINING/R%20Work/Study_Area_Climatology_Graph_07082024.html", "category": "Learning & Tutorials", "tags": ["R", "climatology", "GIS", "analysis"]},
]

def generate_category_page(category, items):
    """Generate a markdown page for a category."""
    lines = [f"# {category}\n"]
    lines.append(f"*{len(items)} bookmarks in this collection*\n")

    for item in sorted(items, key=lambda x: x["title"].lower()):
        lines.append(f"## [{item['title']}]({item['url']})\n")
        tags_str = " ".join([f"`{tag}`" for tag in item["tags"]])
        lines.append(f"**Tags:** {tags_str}\n")
        lines.append("")

    return "\n".join(lines)


def generate_index():
    """Generate the main index page."""
    categories = defaultdict(list)
    for bm in bookmarks:
        categories[bm["category"]].append(bm)

    lines = [
        "# Christina's Bookmarks Collection\n",
        "Welcome to my curated collection of bookmarks organized by topic. This site contains **{}** bookmarks across **{}** categories, covering GIS, remote sensing, conservation, academic research, and more.\n".format(len(bookmarks), len(categories)),
        "Use the **search bar** above to find specific resources by keyword, or browse by category below.\n",
        "---\n",
        "## Categories\n",
    ]

    category_order = [
        "GIS & Remote Sensing",
        "Google Earth Engine",
        "Remote Sensing",
        "Geospatial Data Sources",
        "ArcGIS & Web GIS",
        "Conservation & Wildlife",
        "Human-Wildlife Conflict",
        "OpenStreetMap",
        "Academic Resources",
        "Learning & Tutorials",
        "Disaster Risk Reduction",
        "Career & Jobs",
        "Scholarships & Grants",
        "Tanzania Resources",
        "Everyday Tools",
        "Entertainment",
    ]

    icons = {
        "GIS & Remote Sensing": ":material-map:",
        "Google Earth Engine": ":material-earth:",
        "Remote Sensing": ":material-satellite-variant:",
        "Geospatial Data Sources": ":material-database:",
        "ArcGIS & Web GIS": ":material-web:",
        "Conservation & Wildlife": ":material-paw:",
        "Human-Wildlife Conflict": ":material-elephant:",
        "OpenStreetMap": ":material-map-marker:",
        "Academic Resources": ":material-school:",
        "Learning & Tutorials": ":material-book-open-variant:",
        "Disaster Risk Reduction": ":material-alert:",
        "Career & Jobs": ":material-briefcase:",
        "Scholarships & Grants": ":material-cash:",
        "Tanzania Resources": ":material-flag:",
        "Everyday Tools": ":material-toolbox:",
        "Entertainment": ":material-movie:",
    }

    for cat in category_order:
        if cat in categories:
            count = len(categories[cat])
            slug = cat.lower().replace(" & ", "-").replace(" ", "-")
            lines.append(f"- [{cat}]({slug}.md) — *{count} links*")

    lines.append("\n---\n")
    lines.append("*Built with MkDocs and organized with the help of Claude Code.*\n")

    return "\n".join(lines), categories


if __name__ == "__main__":
    index_content, categories = generate_index()

    # Write index
    with open("docs/index.md", "w") as f:
        f.write(index_content)

    # Write category pages
    for cat, items in categories.items():
        slug = cat.lower().replace(" & ", "-").replace(" ", "-")
        content = generate_category_page(cat, items)
        with open(f"docs/{slug}.md", "w") as f:
            f.write(content)

    print(f"Generated {len(categories)} category pages with {len(bookmarks)} total bookmarks.")
