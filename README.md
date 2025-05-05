# mePROD-LMM-GUI  
  
A graphical user interface for analyzing proteomics data using linear mixed models (LMM), specifically designed for Multiplexed enhanced Protein Dynamic mass spectrometry (mePROD MS) experiments.  

## Versions

mePROD-LMM-GUI @2.2.0 (2023-10-22)
DynaTMT-py-SB version @2.6.0 - 2023-10-05 (not-up-to-date)
PBLMM @2.1.1 - 2023-10-23 (up-to-date)

## Overview  
  
mePROD-LMM-GUI is a specialized tool for processing and analyzing proteomics data from mePROD experiments, focusing on protein synthesis measurements. The application provides a user-friendly interface for data normalization, statistical analysis, and identification of mitochondrial proteins.

Multiplexed enhanced Protein Dynamic mass spectrometry (mePROD MS) can be used for protein translation (mePROD) and mitochondrial protein import (mePROD^mt) MS results.  
  
## Features  
  
- **Data Processing**: Filter peptides, adjust for injection time variations, and apply normalization  
- **Statistical Analysis**: Perform linear mixed model analysis or unpaired t-tests  
- **Protein Annotation**: Annotate proteins with gene names using UniProt database  
- **Mitochondrial Protein Identification**: Identify mitochondrial proteins using MitoCarta database  
- **Comprehensive Reporting**: Generate detailed Excel reports with analysis results  
  
## System Requirements  
  
- Python with tkinter support for the GUI  
- Supporting libraries: pandas, openpyxl, requests  
- Custom modules: DynaTMT_SB, PBLMM  
  
## Installation  
  
1. Clone this repository  
2. Install required dependencies:
```
pip install pandas openpyxl requests
```
3. Install custom modules (DynaTMT_SB, PBLMM) as per their installation instructions  

## Usage  

1. Run the application:  
```
python main.py
```
2. Load PSM (Peptide Spectrum Match) data file using the "Browse" button  
3. Enter an output name for your results  
4. Configure experimental conditions (comma-separated list)  
5. Configure condition pairs for comparison (slash-separated pairs)  
6. Select normalization method (Total intensity, Median, TMM)  
7. Select statistical method (Linear mixed model, Unpaired t-test)  
8. Click "RUN" to process the data  
9. Use the "Open" button to view results after processing  

## Configuration Files  

The application uses two primary configuration files:  

1. **Conditions File** (`conditions.txt`): Defines the experimental conditions for each channel  
   - Format: Comma-separated list of condition names (e.g., `Light,DMSO,DMSO,DMSO,Treatment1,Treatment1,Treatment1`)  
   - The first condition is typically the baseline (Light, Baseline, Base, or Noise)  

2. **Pairs File** (`pairs.txt`): Defines which conditions to compare in statistical analysis  
   - Format: Semicolon-separated list of condition pairs (e.g., `DMSO/Treatment1;DMSO/Treatment2`)  
   - Each pair is defined as two condition names separated by a slash  

## Data Processing Workflow  

1. **Data Filtering**: Removes invalid peptides and filters PSM data  
2. **IT Adjustment**: Adjusts for injection time variations  
3. **Normalization**: Applies selected normalization method (Total, TMM, or Median)  
4. **Heavy Peptide Extraction**: Isolates heavy-labeled peptides for analysis  
5. **Baseline Correction**: Normalizes against baseline/light channel  
6. **Statistical Analysis**: Applies the selected statistical method  
7. **Annotation and Identification**: Assigns gene names and identifies mitochondrial proteins  
8. **Report Generation**: Creates a comprehensive Excel report with all results  

## Output  

The application generates an Excel report containing:  

1. **Analysis Information**:  
   - Version of the program  
   - Number of total/heavy peptides and proteins  
   - Number of mitochondrial peptides and proteins  
   - Input file, conditions, pairs, and analysis parameters  

2. **Analysis Results**:  
   - Protein/peptide data with measurements for each condition  
   - Statistical analysis results (p-values, q-values)  
   - Gene name annotations  
   - Mitochondrial protein identification  
   - Significance indicators for statistically significant changes  

## Reference Databases  

The application integrates with two essential reference databases:  

1. **UniProt Database** (`Uniprot_database_2021.xlsx`): Maps protein accession numbers to gene symbols  
2. **MitoCarta Database** (`database.xlsx`): Identifies mitochondrial proteins  

## License  

MIT License

Copyright (c) 2023 Süleyman Bozkurt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Author  

Süleyman Bozkurt (2023)  

## Contact  

Email: bozkurt@med.uni-frankfurt.de
