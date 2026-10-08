# LinkedIn Job Alert email Parser - Documentation

## Overview
This Python script parses saved LinkedIn job alert emails (HTML format) and extracts job posting information into a structured CSV file. It's designed to help you organize and track job opportunities from multiple email alerts efficiently.

Microsoft Outlook's "Save as HTML" feature is NOT compartible with this script!

You can use VBA script provided at Companion VBA files section to generate .html files without relying on Word. 

The test setup also used Thunderbird with the ImportExportTools NG plugin to save LinkedIn job alert emails as `.html` files



## Features

### Core Functionality
- **Batch Processing**: Processes all HTML files in a specified folder
- **Data Extraction**: Extracts job title, company name, location, work type, and URLs
- **Deduplication**: Automatically removes duplicate job postings across multiple emails
- **Date Tracking**: Adds extraction date to track when jobs were found
- **Clean URLs**: Removes tracking parameters and decodes Outlook Safe Links

### Extracted Information
1. **Job Title**: Position name (e.g., "IT Support Engineer")
2. **Company**: Company/organization name (e.g., "SOCi.ai")
3. **Location**: Geographic location (e.g., "Toronto, ON")
4. **Work Type**: Remote, Hybrid, or On-site/Unspecified
5. **Job ID**: LinkedIn's unique job identifier for deduplication
6. **URL**: Clean LinkedIn job posting link
7. **Source File**: Original HTML filename
8. **Extracted Date**: Date when the script was run

## Requirements

### Python Version
- Python 3.6 or higher

### Dependencies
```bash
pip install beautifulsoup4
```

### System Requirements
- Works on Windows, macOS, and Linux
- Requires read access to source HTML files
- Requires write access for CSV output

## Installation

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)

2. **Install Beautiful Soup**
   ```bash
   pip install beautifulsoup4
   ```

3. **Save the script**
   - Save as `linkedin_parser.py` or any name you prefer

## Configuration

### Folder Setup
The script expects HTML files in this folder:
```python
SOURCE_FOLDER = r'C:\SavedEmails\Linkedin-parser'
```

**To change the folder:**
- Edit line 35 in the script
- Use raw string (`r'...'`) or escape backslashes (`\\`)
- Examples:
  ```python
  SOURCE_FOLDER = r'D:\MyJobs\LinkedIn'
  SOURCE_FOLDER = '/Users/username/Documents/LinkedIn'
  ```

### Output Filename
The script generates files with the current date:
```
linkedin_jobs_enhanced-list-YYYY-MM-DD.csv
```

Example: `linkedin_jobs_enhanced-list-2026-02-10.csv`

0utput file is saved in the same directory where you run the script.

## Usage

### Basic Usage

1. Save LinkedIn job alert emails as HTML files
   - Script is tested with Thunderbird mail client and ImportExportTools NG plugin, but any HTML file, with LinkedIn job listings should work
   - Microsoft Outlook's save-to-HTML is not working well due to extra wrappers!
  
   

2. Place all HTML files in the configured folder

3. Run the script:
  
   python linkedin_jobs_alerts-parser-with-day-stamp.py
  

4. Find the output CSV in the same directory where you ran the script

### Expected Output
```
Found 15 HTML files. Processing...
Success! Extracted 42 unique jobs to 'linkedin_jobs_enhanced-list-2026-02-10.csv'.
Columns added: Location, Work Type, Job ID
```

## Code Architecture

Code Architecture

The linkedin_jobs_alerts-parser-with-day-stamp.py script is a batch-oriented HTML parser.

It reads saved LinkedIn job-alert emails from a configured folder, extracts structured job information, 
removes duplicate postings, adds the date on which each job was extracted, and writes the results to a CSV file.

File handling, HTML parsing, URL normalization, duplicate detection, and CSV generation are separated by responsibility, while main() coordinates the complete workflow.

**Workflow**:

Read matching files from SOURCE_FOLDER

Parse HTML with BeautifulSoup

Find LinkedIn job-title links

Clean URLs and extract Job IDs

Extract company, location, and work type

Deduplicate by Job ID

Add extraction date

Write structured CSV output


### Configuration and Constants

The script begins with configuration values that control its input and output behavior:

SOURCE_FOLDER identifies the directory containing saved email HTML files.

FILE_PATTERN specifies which files should be processed, such as *.html.

OUTPUT_FILE defines the generated CSV filename.

CSV_FIELDS defines the order of the columns written to the output file.


#### Work Type Detection
- **Remote**: Contains `(Remote)` in location text
- **Hybrid**: Contains `(Hybrid)` in location text
- **On-site/Unspecified**: No work type indicator found

#### Job ID Extraction
LinkedIn URLs follow this pattern:
```
/comm/jobs/view/4359970532/
                ^^^^^^^^^^
                Job ID
```

## Output Format

### CSV Structure
| Column | Description | Example |
|--------|-------------|---------|
| job_title | Position name | IT Support Engineer |
| company | Company name | SOCi.ai |
| location | City/region | Toronto, ON |
| work_type | Remote/Hybrid/On-site | Remote |
| url | Clean LinkedIn URL | https://www.linkedin.com/... |
| job_id | Unique LinkedIn ID | 4359970532 |
| source_file | Original HTML filename | job_alert_2026-02-10.html |
| extracted_date | Processing date | 2026-02-10 |

### Sample Output
```csv
job_title,company,location,work_type,url,job_id,source_file,extracted_date
IT Support Engineer,SOCi.ai,Toronto ON,Remote,https://www.linkedin.com/comm/jobs/view/4359970532/,4359970532,email1.html,2026-02-10
Infrastructure Engineer,Prelude,Canada,Remote,https://www.linkedin.com/comm/jobs/view/4367664757/,4367664757,email1.html,2026-02-10
```

## Deduplication Strategy

### How It Works
1. Extracts Job ID from each LinkedIn URL
3. Skips jobs with already-seen IDs

The deduplication key is the LinkedIn Job ID rather than the
complete URL, making the process more reliable when URLs contain different tracking
parameters.


### Limitations
- Deduplication only works within a single script execution
- If you run the script twice, it will create two CSV files (by design, dated differently)
- To deduplicate across multiple runs, you'd need to merge CSV files manually or modify the script

## Troubleshooting

### Common Issues

#### 1. "No module named 'bs4'"
**Solution**: Install Beautiful Soup
```bash
pip install beautifulsoup4
```

#### 2. "The folder does not exist"
**Solution**: Check the `SOURCE_FOLDER` path
- Verify the folder exists
- Check for typos in the path
- Use raw string: `r'C:\Path\To\Folder'`

#### 3. "No job titles found"
**Possible Causes**:
- HTML files are not LinkedIn job alerts
- LinkedIn changed their email format
- Files are corrupted or incomplete

**Solution**: Open one HTML file in a browser to verify it contains job listings

#### 4. "Could not write to CSV"
**Solution**: Close the CSV file if it's open in Excel or another program

#### 5. Script runs but extracts 0 jobs
**Causes**:
- LinkedIn changed their HTML structure
- Files are from a different LinkedIn email type (not job alerts)

**Debug**:
- Add print statements to see what links are found
- Inspect HTML structure manually


## Limitations

1. **HTML Format Dependency**: Script relies on LinkedIn's current email HTML structure
2. **Single Run Deduplication**: Only deduplicates within one execution
3. **Outlook Safe Links**: Primarily tested with Outlook-saved emails
4. **English Language**: Parsing logic assumes English location separators ("·")
5. **No API Access**: Scrapes saved emails rather than using LinkedIn API

## Best Practices

1. **Regular Backups**: Keep original HTML files as backup
2. **Consistent Naming**: Use consistent filenames for source HTML files
3. **Periodic Updates**: Check if LinkedIn changes email format

## Future Enhancement Ideas

- Add support for salary extraction
- Include posting date/time
- Extract job description snippets
- Add filtering options (location, work type, keywords)
- Create Excel output with formatting
- Build a simple GUI for non-technical users
- Add email parsing (directly read from .eml files)
- Implement cross-run deduplication with a database

## License & Support

This script is provided as-is for personal use. Feel free to modify and adapt it to your needs.

**Disclaimer**: This tool is for personal job search organization only. 
Respect LinkedIn's Terms of Service and do not use for commercial scraping or automated access to LinkedIn's platform.



