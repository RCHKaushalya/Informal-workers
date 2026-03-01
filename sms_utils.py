def send_sms(phone_number: str, message: str):
    # Placeholder function to simulate sending an SMS
    print(f"Sending SMS to {phone_number}: {message}")

def receive_sms():
    # Placeholder function to simulate receiving an SMS
    received = input("Enter received SMS: (job_id|worker_id|responce) ")

    job_id, worker_id, resp = received.split('|')
    response = 'liked' if resp == '1' else 'rejected'

    return int(job_id), int(worker_id), response
