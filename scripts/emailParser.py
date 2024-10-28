import re
import quopri

def extract_content(file_path):
    try:
        with open(file_path, 'r') as file:
            text = file.read().strip()

            delivery_date = extract_value(text,r"Delivery-date:\s(.+)")
            mail_content = extract_text_between(text, 'Content-Type: text/plain; charset="UTF-8"', "Diesen Job melden")
            decoded_mail_content = decode_quoted_printable(mail_content)
            job_description_link = extract_value(decoded_mail_content,r"Die vollständige Stellenbeschreibung findest du hier\s+(https://\S+)")

            job = {
                "delivery_date": delivery_date,
                "text": decoded_mail_content,
                "job_description_link" : job_description_link
            }

        return job
    
    except FileNotFoundError:
        return "The file was not found."
    except Exception as e:
        return f"An error occurred: {e}"


    
def extract_value(text, pattern):
    match = re.search(pattern, text)
    
    if match:
        return  match.group(1)
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
    

file_path = './mail/mail20241028_110904_722922619'
result = extract_content(file_path)
print(result["text"])
