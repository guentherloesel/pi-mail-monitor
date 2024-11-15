import asyncio
from nats.aio.client import Client as NATS

async def run():
    nats_server = "nats"
    subject = "test"

    nc = NATS()

    try:
        # Connect to the NATS server
        await nc.connect(servers=[nats_server])
        print(f"Connected to NATS server: {nats_server}")

        # Define a message handler
        async def message_handler(msg):
            print(f"Received a message on '{msg.subject}': {msg.data.decode()}")

        # Subscribe to the subject
        await nc.subscribe(subject, cb=message_handler)
        print(f"Subscribed to subject: {subject}")

        # Publish a message
        message = "Hello, NATS!"
        await nc.publish(subject, message.encode())
        print(f"Published message to '{subject}': {message}")

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