import os
import csv
import urllib.parse
import re
from datetime import datetime
from bs4 import BeautifulSoup

# This script processes HTML files containing LinkedIn job alerts, extracts job details,
# --- Configuration ---
SOURCE_FOLDER = r'C:\SavedEmails\Linkedin-parser'

# Dynamic filename with current date
current_date = datetime.now().strftime('%Y-%m-%d')
OUTPUT_FILE = f'linkedin_jobs_enhanced-list-{current_date}.csv'

def clean_linkedin_url(url):
    """
    Decodes Outlook Safe Links, removes tracking parameters, 
    and extracts the Job ID.
    """
    # 1. Decode Outlook Safe Link
    if 'safelinks.protection.outlook.com' in url:
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(parsed.query)
        if 'url' in query:
            url = query['url'][0]
    
    # 2. Parse the inner LinkedIn URL
    parsed_inner = urllib.parse.urlparse(url)
    
    # 3. Extract Job ID for deduplication
    # URL structure is usually /comm/jobs/view/123456789 or /jobs/view/123456789
    job_id = "unknown"
    path_parts = parsed_inner.path.strip('/').split('/')
    if 'view' in path_parts:
        try:
            view_index = path_parts.index('view')
            if view_index + 1 < len(path_parts):
                job_id = path_parts[view_index + 1]
        except ValueError:
            pass

    # 4. Rebuild clean URL
    clean_url = f"{parsed_inner.scheme}://{parsed_inner.netloc}{parsed_inner.path}"
    
    return clean_url, job_id

def parse_linkedin_files():
    results = []
    seen_job_ids = set() # To track duplicates
    
    if not os.path.exists(SOURCE_FOLDER):
        print(f"Error: The folder '{SOURCE_FOLDER}' does not exist.")
        return

    files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith(('.html', '.htm'))]
    print(f"Found {len(files)} HTML files. Processing...")

    for filename in files:
        file_path = os.path.join(SOURCE_FOLDER, filename)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'html.parser')
                job_links = soup.find_all('a', class_='text-system-blue-50')

                for link in job_links:
                    classes = link.get('class', [])
                    if 'font-bold' in classes and 'text-md' in classes:
                        title = link.get_text(strip=True)
                        raw_href = link.get('href', '')
                        
                        # --- Enhanced Extraction ---
                        company_name = "Unknown"
                        location = "Unknown"
                        work_type = "On-site/Unspecified" # Default
                        
                        try:
                            # Navigate to the next row for details
                            title_row = link.find_parent('tr')
                            if title_row:
                                company_row = title_row.find_next_sibling('tr')
                                if company_row:
                                    full_text = company_row.get_text(strip=True)
                                    
                                    # Split "Company · Location"
                                    if '·' in full_text:
                                        parts = full_text.split('·', 1)
                                        company_name = parts[0].strip()
                                        location_text = parts[1].strip()
                                        
                                        # Detect Work Type (Remote/Hybrid)
                                        if '(Remote)' in location_text:
                                            work_type = "Remote"
                                            location = location_text.replace('(Remote)', '').strip()
                                        elif '(Hybrid)' in location_text:
                                            work_type = "Hybrid"
                                            location = location_text.replace('(Hybrid)', '').strip()
                                        else:
                                            location = location_text
                                    else:
                                        company_name = full_text
                        except Exception:
                            pass 

                        if title and raw_href:
                            final_url, job_id = clean_linkedin_url(raw_href)
                            
                            # --- Deduplication Logic ---
                            if job_id != "unknown" and job_id in seen_job_ids:
                                continue # Skip duplicate
                            seen_job_ids.add(job_id)
                            
                            results.append({
                                'job_title': title,
                                'company': company_name,
                                'location': location,
                                'work_type': work_type,
                                'job_id': job_id,
                                'url': final_url,
                                'source_file': filename,
                                'extracted_date': datetime.now().strftime('%Y-%m-%d')
                            })
                            
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    # Save to CSV
    if results:
        try:
            with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
                # Reordered fields for better readability
                fieldnames = ['job_title', 'company', 'location', 'work_type', 'url', 'job_id', 'source_file', 'extracted_date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(results)
            print(f"Success! Extracted {len(results)} unique jobs to '{OUTPUT_FILE}'.")
            print(f"Columns added: Location, Work Type, Job ID")
        except PermissionError:
            print(f"Error: Could not write to '{OUTPUT_FILE}'. Close the file if it is open.")
    else:
        print("No job titles found.")

if __name__ == "__main__":
    parse_linkedin_files()
