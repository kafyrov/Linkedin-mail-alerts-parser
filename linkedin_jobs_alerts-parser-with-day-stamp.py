#!/usr/bin/env python3
"""
LinkedIn Job Alert Email Parser vibecoded with claude.ai at September 1 2026
=======================================================

Parses saved LinkedIn daily job alert HTML emails and extracts structured
job posting data into a single, de-duplicated CSV file.

Handles HTML files saved by different mail programs (e.g. Outlook saving as
UTF-16 with a BOM, other clients saving as plain UTF-8), and decodes Outlook
"Safe Links" (safelinks.protection.outlook.com) wrappers back to clean
LinkedIn job URLs, stripping tracking parameters.

Usage:
    python linkedin_jobs_enhanced-with-day-stamp-v.2.py

Just edit the CONFIGURATION section below and run the script.

You may have different final results if your Linked-In account is not binded to Hotmail/Outlook email address! no (SafeLinks)

"""

import csv
import glob
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote

from bs4 import BeautifulSoup

# --- Configuration ---------------------------------------------------------
# Folder containing the saved LinkedIn job alert .html email files.
SOURCE_FOLDER = r'C:\SavedEmails\Linkedin-parser'

# Dynamic filename with current date.
current_date = datetime.now().strftime('%Y-%m-%d')
OUTPUT_FILE = f'linkedin_jobs_enhanced-list-{current_date}.csv'

# Glob pattern used to find email files inside SOURCE_FOLDER.
FILE_PATTERN = '*.html'

# CSV column order.
CSV_FIELDS = [
    'job_title',
    'company',
    'location',
    'work_type',
    'url',
    'job_id',
    'source_file',
    'extracted_date',
]
# ---------------------------------------------------------------------------


def read_html_file(filepath):
    """
    Read an HTML email file, auto-detecting its encoding.

    LinkedIn job alert emails saved from different mail clients show up with
    different encodings - most commonly UTF-16 (with a BOM) when saved from
    Outlook, or UTF-8 when saved from other mail programs/browsers.
    """
    with open(filepath, 'rb') as f:
        raw = f.read()

    # BOM-based detection first (most reliable).
    if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
        return raw.decode('utf-16')
    if raw.startswith(b'\xef\xbb\xbf'):
        return raw.decode('utf-8-sig')

    # No BOM: try UTF-8, then fall back to a couple of common encodings.
    for encoding in ('utf-8', 'cp1252', 'latin-1'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    # Last resort: decode with replacement so the script never crashes.
    return raw.decode('utf-8', errors='replace')


def unwrap_outlook_safelink(url):
    """
    Decode an Outlook Safe Links URL (safelinks.protection.outlook.com) back
    to the original destination URL. If the URL is not a Safe Link, it is
    returned unchanged.
    """
    if not url:
        return url

    if 'safelinks.protection.outlook.com' not in url:
        return url

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    inner = qs.get('url')
    if inner:
        return unquote(inner[0])
    return url


def clean_linkedin_url(raw_url):
    """
    Given a (possibly Safe-Links-wrapped, possibly tracking-parameter-laden)
    LinkedIn job URL, return a clean canonical job URL of the form:

        https://www.linkedin.com/jobs/view/<job_id>/

    and the extracted job_id. Returns (clean_url, job_id) or (None, None)
    if no job id could be found.
    """
    if not raw_url:
        return None, None

    url = unwrap_outlook_safelink(raw_url)

    # LinkedIn sometimes double-encodes query strings inside Safe Links.
    url = unquote(url)

    match = re.search(r'/jobs/view/(\d+)', url)
    if not match:
        return None, None

    job_id = match.group(1)
    clean_url = f'https://www.linkedin.com/jobs/view/{job_id}/'
    return clean_url, job_id


def extract_work_type(location_text):
    """
    Split a "City, ST (Remote)" style string into (location, work_type).
    work_type is one of: 'Remote', 'Hybrid', 'On-site/Unspecified'.
    """
    if not location_text:
        return location_text, 'On-site/Unspecified'

    match = re.search(r'\((Remote|Hybrid|On-site)\)\s*$', location_text, re.IGNORECASE)
    if match:
        work_type = match.group(1).title()
        location = location_text[:match.start()].strip()
        return location, work_type

    return location_text.strip(), 'On-site/Unspecified'


def find_job_anchor_groups(soup):
    """
    Find LinkedIn job anchors in the parsed HTML and group them by job id.

    Each job card in the email typically renders 2-3 <a> tags that all point
    to the same job (a company-logo link, a whole-card link, and a
    title-only link). We collect them all per job id so we can later pick
    the one with the cleanest title text.
    """
    groups = {}

    # LinkedIn keeps an un-wrapped copy of the destination URL in the
    # "originalsrc" attribute (used by some mail clients for link previews).
    # Prefer that; fall back to decoding the (possibly Safe-Links-wrapped)
    # href attribute otherwise.
    anchors = soup.find_all('a', href=True)

    for a in anchors:
        candidate_url = a.get('originalsrc') or a.get('href')
        clean_url, job_id = clean_linkedin_url(candidate_url)
        if not job_id:
            continue
        groups.setdefault(job_id, {'url': clean_url, 'anchors': []})
        groups[job_id]['anchors'].append(a)

    return groups


def extract_jobs_from_html(html_text, source_filename):
    """
    Parse a single LinkedIn job-alert email (already decoded to str) and
    return a list of job dicts (without job_id/url/source_file/extracted_date
    de-duplication applied - that happens at the caller level).
    """
    soup = BeautifulSoup(html_text, 'html.parser')
    job_groups = find_job_anchor_groups(soup)

    jobs = []

    for job_id, info in job_groups.items():
        anchors = info['anchors']

        # Among the (usually 2-3) anchors pointing at this job, the one with
        # the shortest non-empty text is the clean job-title-only link; the
        # others tend to wrap the whole card (title + company + badges).
        texts = [(len(a.get_text(strip=True)), a.get_text(strip=True), a)
                 for a in anchors if a.get_text(strip=True)]
        if not texts:
            continue
        texts.sort(key=lambda t: t[0])
        _, job_title, title_anchor = texts[0]

        # The company/location line lives in the following table row's <p>.
        company = ''
        location_raw = ''
        tr = title_anchor.find_parent('tr')
        sib = tr.find_next_sibling('tr') if tr else None
        if sib:
            detail_text = sib.get_text(' ', strip=True)
            if '\u00b7' in detail_text:  # '·' middle dot separator
                parts = detail_text.split('\u00b7', 1)
                company = parts[0].strip()
                location_raw = parts[1].strip()
            else:
                location_raw = detail_text.strip()

        # Strip trailing badge text like "Actively recruiting" that can
        # sometimes bleed into the detail line's text.
        location_raw = re.sub(r'\s*Actively recruiting\s*$', '', location_raw,
                               flags=re.IGNORECASE).strip()

        location, work_type = extract_work_type(location_raw)

        jobs.append({
            'job_title': job_title.strip(),
            'company': company.strip(),
            'location': location.strip(),
            'work_type': work_type,
            'url': info['url'],
            'job_id': job_id,
            'source_file': source_filename,
        })

    return jobs


def process_folder(source_folder, file_pattern):
    """
    Process every HTML file in source_folder, extracting and de-duplicating
    job postings (de-duplication key: job_id).
    """
    pattern = os.path.join(source_folder, file_pattern)
    filepaths = sorted(glob.glob(pattern))

    if not filepaths:
        print(f'No files matching "{file_pattern}" found in: {source_folder}')
        return []

    extracted_date = datetime.now().strftime('%Y-%m-%d')
    seen_job_ids = set()
    all_jobs = []
    total_found = 0

    for filepath in filepaths:
        filename = os.path.basename(filepath)
        try:
            html_text = read_html_file(filepath)
        except Exception as exc:
            print(f'  [!] Could not read {filename}: {exc}')
            continue

        jobs = extract_jobs_from_html(html_text, filename)
        total_found += len(jobs)

        new_in_file = 0
        for job in jobs:
            if job['job_id'] in seen_job_ids:
                continue
            seen_job_ids.add(job['job_id'])
            job['extracted_date'] = extracted_date
            all_jobs.append(job)
            new_in_file += 1

        print(f'  {filename}: {len(jobs)} job(s) found, {new_in_file} new')

    print(f'\nTotal job postings found (with duplicates): {total_found}')
    print(f'Unique job postings after de-duplication:    {len(all_jobs)}')

    return all_jobs


def write_csv(jobs, output_file):
    """Write extracted jobs to a CSV file using the configured column order."""
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for job in jobs:
            writer.writerow({field: job.get(field, '') for field in CSV_FIELDS})


def main():
    print(f'Scanning folder: {SOURCE_FOLDER}')
    print(f'Looking for files matching: {FILE_PATTERN}\n')

    if not os.path.isdir(SOURCE_FOLDER):
        print(f'ERROR: Source folder does not exist: {SOURCE_FOLDER}')
        sys.exit(1)

    jobs = process_folder(SOURCE_FOLDER, FILE_PATTERN)

    if not jobs:
        print('\nNo jobs extracted. CSV file was not created.')
        sys.exit(0)

    write_csv(jobs, OUTPUT_FILE)
    print(f'\nSaved {len(jobs)} unique job postings to: {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
