import re
import quopri
import glob
import os
import asyncio
from nats.aio.client import Client as NATS
from dotenv import load_dotenv

load_dotenv()

def load_env_vars():
    env_vars = {
        "NATS_SERVER": os.environ.get("NATS_SERVER") or "nats://localhost:4222",
        "NATS_SUBJECT": os.environ.get("NATS_SUBJECT") or "jobs",
        "FILE_PATH": os.environ.get("FILE_PATH") or "/var/tmp/mail/mail*",
        "ENVIRONMENT": os.environ.get("ENVIRONMENT") or "production"
    }
    return env_vars

def extract_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

            delivery_date = extract_value(text, r"Delivery-date:\s(.+)")
            mail_content = extract_text_plain_with_regex(text, "Diesen Job melden")
            job_description_link = extract_value(mail_content, r"Die vollständige Stellenbeschreibung findest du hier\s+(https://\S+)")

            job = {
                "delivery_date": delivery_date,
                "text": mail_content,
                "job_description_link": job_description_link
            }

        return job

    except FileNotFoundError:
        return "The file was not found."
    except Exception as e:
        return f"An error occurred: {e}"

def extract_value(text, pattern):
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def extract_text_plain_with_regex(raw_email, endstring):
    try:
        # Normalize line endings
        raw_email = raw_email.replace("\r\n", "\n").replace("\r", "\n")
        
        # Regex to find the text/plain content
        text_plain_pattern = re.compile(
            r"Content-Transfer-Encoding:\s*quoted-printable\s*"
            r"Content-Type:\s*text/plain;\s*charset=['\"]?UTF-8['\"]?\s*"
            r"(.*?)"  # Text nach Content-Type
            rf"(?=\s*{re.escape(endstring)}|\Z|\nContent-Type:)",  # Stoppe bei endstring oder nächstem Block
            re.DOTALL | re.IGNORECASE
        )
        
        # Search and find all matches
        matches = text_plain_pattern.findall(raw_email)
        
        if not matches:
            return "No text/plain content found."
        
        extracted_content = ""
        for content in matches:
            decoded_content = quopri.decodestring(content).decode('utf-8', errors='replace')
            extracted_content += decoded_content.strip() + "\n"
        
        return extracted_content.strip()
    
    except Exception as e:
        return f"An error occurred: {e}"


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

async def publish_to_nats(nats_server, nats_subject, job_data):
    try:
        nc = NATS()
        await nc.connect(servers=[nats_server])

        # Convert job data to string (or JSON) for publishing
        message = str(job_data)
        await nc.publish(nats_subject, message.encode('utf-8'))
        # print(f"Published job to NATS subject '{nats_subject}': {message}")
        await nc.close()

    except Exception as e:
        print(f"Error publishing to NATS: {e}")

async def process_file(file_path, env_vars):
    job_data = extract_content(file_path)
    if isinstance(job_data, dict):
        await publish_to_nats(env_vars["NATS_SERVER"],env_vars["NATS_SUBJECT"], job_data)

        if env_vars["ENVIRONMENT"] != "development":
            delete_file(file_path)

        return job_data
    else:
        print(f"Error processing file {file_path}: {job_data}")
        return None

async def process_all_files():
    env_vars = load_env_vars()
    all_jobs = []
    for file_path in glob.glob(env_vars["FILE_PATH"]):
        job_data = await process_file(file_path, env_vars)
        if job_data:
            all_jobs.append(job_data)
    
    return all_jobs

# Main entry point
if __name__ == "__main__":
    try:
        asyncio.run(process_all_files())
    except EnvironmentError as e:
        print(e)
        exit(1)