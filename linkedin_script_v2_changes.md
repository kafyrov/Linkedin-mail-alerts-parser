## Overview

Version 2 changes the script from a single-function parser into a more structured and defensive HTML-processing tool. The extraction logic is separated into reusable functions, input files are processed in a predictable order, duplicate handling is improved, and several edge cases in LinkedIn alert content are handled more safely.

## Main logic changes

### 1. Refactored into reusable functions

Version 1 places most parsing, de-duplication, and CSV-writing logic inside `parse_linkedin_files()`.

Version 2 separates responsibilities into functions such as:

- `clean_linkedin_url()` for URL normalization and job-ID extraction.
- `read_html_file()` for reading HTML content.
- `extract_work_type()` for identifying remote, hybrid, or other work arrangements.
- `extract_jobs_from_html()` for extracting jobs from one HTML document.
- `process_folder()` for scanning files and combining results.
- `write_csv()` for generating the output file.
- `main()` for coordinating execution.

This makes the code easier to test, maintain, and extend.

### 2. Improved folder processing

Version 1 uses `os.listdir()` and processes matching files in the order returned by the operating system.

Version 2 uses `glob` with a configurable `FILE_PATTERN` and sorts the resulting file paths. This provides more predictable processing and makes the input pattern easier to change.

### 3. More robust HTML reading

Version 1 opens each file directly inside the parsing loop.

Version 2 centralizes file reading in `read_html_file()` and handles read failures per file. If a file cannot be read, the script reports the problem and continues processing the remaining files instead of stopping the overall run.

### 4. More flexible job-link detection

Version 1 requires the link to contain the classes `font-bold` and `text-md` in addition to `text-system-blue-50`.

Version 2 uses a more focused selector for the job-title link and validates the title and URL before adding a record. This reduces dependence on a particular combination of CSS classes, which can make the parser less fragile when LinkedIn changes its markup.

### 5. Improved company and location extraction

Version 1 reads the next table row and splits the text at the first middle dot (`·`).

Version 2 performs the same basic extraction but uses cleaner text normalization and explicit empty-string defaults for company and location. It also handles detail rows that do not contain the separator.

### 6. Additional cleanup of location text

Version 2 removes a trailing `Actively recruiting` badge when that text is accidentally included in the location/details line. This prevents badge text from being stored as part of the location.

### 7. Centralized work-type detection

Version 1 detects only `(Remote)` and `(Hybrid)` inline within the parsing loop. Otherwise it assigns `On-site/Unspecified`.

Version 2 moves this behavior into `extract_work_type()`. The logic is therefore reusable and easier to expand—for example, to support additional labels or alternate formatting. The extracted result is stored separately as `location` and `work_type`.

### 8. Better duplicate tracking and reporting

Both versions use the LinkedIn job ID as the primary de-duplication value. Version 2 moves de-duplication into `process_folder()` and reports both:

- The total number of postings found, including duplicates.
- The number of unique postings retained.

It also reports how many new jobs came from each file. This provides better visibility into the parsing results.

### 9. One extraction date per run

Version 1 calls `datetime.now()` for each job record.

Version 2 calculates the extraction date once at the beginning of folder processing and applies the same date to every job from that run. This is more consistent and avoids small timing differences if processing crosses midnight.

### 10. More controlled CSV output

Version 1 defines the CSV field order inside the writing section and writes the complete result list directly.

Version 2 defines a shared `CSV_FIELDS` configuration and writes each row using those fields. Missing values are safely replaced with empty strings, reducing the chance of key errors when a record lacks a field.

### 11. Cleaner program entry point and error handling

Version 2 adds a `main()` function that checks whether the source folder exists, displays the scan configuration, handles an empty result set, and writes the output only when jobs were extracted.

This creates a clearer execution flow and makes the script easier to invoke or later integrate into another program.

## Functional impact

The output remains a CSV containing job title, company, location, work type, URL, job ID, source file, and extraction date. The main user-visible improvements are cleaner location values, more predictable file processing, improved diagnostics, and greater resilience when individual files or HTML elements are malformed.
