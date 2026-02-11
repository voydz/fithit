# Research Findings: Downloading Apple Fitness+ Workout Data

## Overview
Apple Fitness+ does not provide an official API for catalog access or workout downloads. Data is protected by DRM (FairPlay Streaming). However, metadata and personal history can be retrieved through community and personal export methods.

## 1. Workout Catalog Metadata
The most comprehensive and accurate source for the entire workout catalog is a community-maintained database.

- **Primary Source:** [Apple Fitness+ Master List (Seatable)](https://cloud.seatable.io/dtable/external-links/d08506897d274835bdab/)
- **Maintained by:** Reddit user `u/speedr123` (r/AppleFitnessPlus).
- **Data Available:**
    - Workout type (HIIT, Strength, Yoga, etc.)
    - Trainer name
    - Duration
    - Equipment requirements
    - Music genre and playlists
    - Detailed workout descriptions and movements
- **Export Method:** Manual export to CSV or Excel from the Seatable interface.

## 2. Personal Workout Data
To retrieve your own workout history and performance metrics (heart rate, calories, etc.):

- **Native Method:** iOS Health App > Profile > Export All Health Data (Generates a large XML file).
- **Recommended Tool:** **Health Auto Export** (iOS/Mac app) or **HealthFit**. These tools can export data directly to JSON, CSV, or even sync to a private API/database automatically.

## 3. Video Content
- **Status:** **Impossible** to download for offline usage outside the official app.
- **Reasoning:** Videos are encrypted with FairPlay DRM. There are no public scrapers or tools that successfully bypass this to store raw video files.

## Recommended Strategy for Local Database
1. **Schema Design:** Mirror the columns found in the Seatable Master List.
2. **Data Ingestion:**
    - Perform a manual export of the Seatable database.
    - Parse the CSV/Excel file into your local database (SQLite, PostgreSQL, etc.)
3. **Updates:** Periodically re-export the master list to capture new weekly releases.

---
*Date: 2026-02-11*
