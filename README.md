# Communication-Database-Converter
## Overview

Communication Database Converter is a standalone desktop application designed for automotive engineers, system engineers, network architects, validation engineers, calibration engineers, and AUTOSAR developers to efficiently convert communication database files into structured Excel and CSV formats.

The tool simplifies the analysis and documentation of vehicle communication networks by extracting communication data from multiple automotive network description formats and exporting it into easily readable and shareable spreadsheets.

The application is developed as a portable Windows executable and can be used without installing Python or additional dependencies.

---

## Key Features

### Supported Input Formats

The tool supports parsing and conversion of:

* DBC (CAN and CAN FD)
* AUTOSAR ARXML
* XML Communication Files
* FlexRay FIBEX
* LIN Description Files (LDF)

### Supported Output Formats

* Microsoft Excel (.xlsx)
* CSV (.csv)

### Communication Data Extraction

The converter extracts key communication information including:

#### CAN / CAN FD

* Network Information
* Message Definitions
* Message IDs
* DLC
* Cycle Times
* Transmitters and Receivers
* Signal Definitions
* Scaling and Offset
* Units
* Multiplexed Signals

#### AUTOSAR ARXML

* Communication Clusters
* Frames and PDUs
* Signals
* Data Types
* Sender/Receiver Relationships
* Compu Methods
* Initial Values
* Communication Parameters

#### FlexRay FIBEX

* Clusters
* Channels
* Frames
* Slot Information
* Cycles
* Signals
* Sender and Receiver Mapping

#### LIN LDF

* LIN Clusters
* Frames
* Publishers
* Subscribers
* Signals
* Schedule Tables

---

## Excel Export Structure

Generated Excel files can include:

* Network Summary
* Messages / Frames
* Signals
* Nodes / ECUs
* Diagnostics Information
* Errors and Warnings

---

## User-Friendly Interface

* Modern graphical user interface
* Drag-and-drop file support
* Batch file conversion
* Progress tracking
* Conversion logs
* Output location selection
* File validation and error reporting

---

## Industrial Use Cases

This tool can be used for:

* Communication Matrix Generation
* Network Architecture Analysis
* AUTOSAR Communication Review
* Signal Database Documentation
* Vehicle Integration Activities
* ECU Interface Analysis
* System Validation Preparation
* Calibration and Testing Support
* Communication Database Comparison
* Supplier/OEM Data Exchange

---

## Benefits

* Eliminates manual extraction of communication data
* Reduces engineering effort and documentation time
* Supports multiple automotive communication standards
* Generates structured reports for analysis and reviews
* Simplifies communication database management
* Enables quick conversion of large communication files

---

## Technology Stack

Built using:

* Python
* PySide6 / PyQt6
* Pandas
* OpenPyXL
* Cantools
* lxml
* XML Parsing Libraries

Packaged as a standalone Windows executable using PyInstaller.

---

## Target Users

* Automotive System Engineers
* Network Communication Engineers
* AUTOSAR Engineers
* Software Integration Engineers
* Validation & Verification Engineers
* Calibration Engineers
* Test Engineers
* Vehicle Architecture Engineers
* Functional Safety Engineers
* Technical Project Teams

---

## License

This project is intended to support automotive communication engineering workflows and can be adapted for OEM, Tier-1, and engineering service applications. it is still underdevelopment

Contributions, feature requests, and improvements are welcome.

---

**Communication Database Converter** – A professional utility for converting CAN, CAN FD, LIN, FlexRay, and AUTOSAR communication databases into engineer-friendly Excel and CSV reports.

