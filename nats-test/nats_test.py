import asyncio
import os
from nats.aio.client import Client as NATS

def load_env_vars():
    env_vars = {
        "NATS_SERVER": os.environ.get("NATS_SERVER") or "nats://localhost:4222",
        "NATS_SUBJECT": os.environ.get("NATS_SUBJECT") or "test"
    }
    
    missing_vars = [key for key, value in env_vars.items() if key not in ["NATS_SERVER", "NATS_SUBJECT"] and not value]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return env_vars


async def run():
    env_vars = load_env_vars()
    nats_server = env_vars["NATS_SERVER"]
    nats_subject = env_vars["NATS_SUBJECT"]

    nc = NATS()

    try:
        # Connect to the NATS server
        await nc.connect(servers=[nats_server])
        print(f"Connected to NATS server: {nats_server}")

        # Define a message handler
        async def message_handler(msg):
            print(f"Received a message on '{msg.subject}': {msg.data.decode()}")

        # Subscribe to the subject
        await nc.subscribe(nats_subject, cb=message_handler)
        print(f"Subscribed to subject: {nats_subject}")

        # Publish a message
        message = "Hello, NATS!"
        await nc.publish(nats_subject, message.encode())
        print(f"Published message to '{nats_subject}': {message}")

        # Give some time to process the message
        await asyncio.sleep(1)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        await nc.close()
        print("Connection to NATS server closed.")

if __name__ == "__main__":
    asyncio.run(run())