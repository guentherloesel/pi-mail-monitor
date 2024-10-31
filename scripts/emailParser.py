import re
import quopri
import glob
import os

def extract_content(file_path):
    try:
        with open(file_path, 'r') as file:
            text = file.read().strip()

            delivery_date = extract_value(text, r"Delivery-date:\s(.+)")
            mail_content = extract_text_between(text, 'Content-Type: text/plain; charset="UTF-8"', "Diesen Job melden")
            decoded_mail_content = decode_quoted_printable(mail_content)
            job_description_link = extract_value(decoded_mail_content, r"Die vollständige Stellenbeschreibung findest du hier\s+(https://\S+)")

            job = {
                "delivery_date": delivery_date,
                "text": decoded_mail_content,
                "job_description_link": job_description_link
            }

        return job

    except FileNotFoundError:
        return "The file was not found."
    except Exception as e:
        return f"An error occurred: {e}"

def extract_value(text, pattern):
    match = re.search(pattern, text)
    
    if match:
        return match.group(1)
    else:
        return ""      

def extract_text_between(text, start_string, end_string):
    pattern = re.escape(start_string) + r"(.*?)" + re.escape(end_string)
    match = re.search(pattern, text, re.DOTALL)

    if match:
        extracted_text = match.group(1).strip()
        return extracted_text
    else:
        return ""
    
def decode_quoted_printable(encoded_text):
    decoded_text = quopri.decodestring(encoded_text).decode('utf-8')
    return decoded_text

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

def process_all_files():
    all_jobs = []
    for file_path in glob.glob('./mail/mail*'):
        job_data = extract_content(file_path)
        
        if isinstance(job_data, dict):
            all_jobs.append(job_data)
            delete_file(file_path)
        else:
            print(f"Error processing file {file_path}: {job_data}")
    
    return all_jobs

# Start
all_jobs_result = process_all_files()
for job in all_jobs_result:
    print(job["job_description_link"])

print("Anzahl der verarbeiteten Dateien: ", len(all_jobs_result))