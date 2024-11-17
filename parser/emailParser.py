import re
import quopri
import glob
import os
import couchdb
import asyncio
from nats.aio.client import Client as NATS

def load_env_vars():
    env_vars = {
        "DB_USER": os.environ.get("DB_USER"),
        "DB_PASS": os.environ.get("DB_PASS"),
        "DB_NAME": os.environ.get("DB_NAME"),
        "DB_SERVICE": os.environ.get("DB_SERVICE"),
        "DB_PORT": os.environ.get("DB_PORT") or "5984",
        "NATS_SERVER": os.environ.get("NATS_SERVER") or "nats://localhost:4222",
        "NATS_SUBJECT": os.environ.get("NATS_SUBJECT") or "jobs"
    }
    
    missing_vars = [key for key, value in env_vars.items() if key not in ["DB_PORT", "NATS_SERVER", "NATS_SUBJECT"] and not value]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return env_vars

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
    return match.group(1) if match else ""

def extract_text_between(text, start_string, end_string):
    pattern = re.escape(start_string) + r"(.*?)" + re.escape(end_string)
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""
    
def decode_quoted_printable(encoded_text):
    return quopri.decodestring(encoded_text).decode('utf-8')

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

def save_to_couchdb(env_vars, job_data):
    try:
        db_user = env_vars["DB_USER"]
        db_pass = env_vars["DB_PASS"]
        db_name = env_vars["DB_NAME"]
        db_service = env_vars["DB_SERVICE"]
        db_port = env_vars["DB_PORT"]

        couch = couchdb.Server(f"http://{db_user}:{db_pass}@{db_service}:{db_port}/")
        
        if db_name not in couch:
            db = couch.create(db_name)
        else:
            db = couch[db_name]
        
        db.save(job_data)
        print("Job data saved to CouchDB.")
        return True
    
    except Exception as e:
        print(f"Error saving to CouchDB: {e}")
        return False

async def publish_to_nats(nats_server, nats_subject, job_data):
    try:
        nc = NATS()
        await nc.connect(servers=[nats_server])

        # Convert job data to string (or JSON) for publishing
        message = str(job_data)
        await nc.publish(nats_subject, message.encode('utf-8'))
        print(f"Published job to NATS subject '{nats_subject}': {message}")
        await nc.close()

    except Exception as e:
        print(f"Error publishing to NATS: {e}")

async def process_file(file_path, env_vars):
    job_data = extract_content(file_path)
    if isinstance(job_data, dict):
        if save_to_couchdb(env_vars, job_data):
            await publish_to_nats(env_vars["NATS_SERVER"],env_vars["NATS_SUBJECT"], job_data)
            delete_file(file_path)
        return job_data
    else:
        print(f"Error processing file {file_path}: {job_data}")
        return None

async def process_all_files():
    env_vars = load_env_vars()
    all_jobs = []
    for file_path in glob.glob('/var/tmp/mail/mail*'):
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