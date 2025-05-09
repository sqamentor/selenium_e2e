from faker import Faker
import random
import json
import yaml
from pathlib import Path

fake = Faker()
OUTPUT_DIR = Path(__file__).resolve().parent
payer_list = ["Aetna Health", "Blue Cross Blue Shield", "UnitedHealthcare", "Cigna", "Humana"]

def generate_custom_email():
    username = fake.user_name()
    domain = random.choice(["mailinator.com", "yopmail.com"])
    return f"{username}@{domain}"

def generate_bookslot_payload():
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": generate_custom_email(),            # Random from allowed domains
        "phone_number": "1234567890",                # Static
        #"zip": fake.zipcode_in_state("MD"),          # Or fixed "20678"
        "zip": ("20678"),          # Or fixed "20678"
        #"contact_method": random.choice(["Text", "Email", "Call"]),
        "contact_method": random.choice(["Text"]),
        "verification_code": "123456",               # Static
        "zip_distance": random.choice(["25", "50", "75", "100"]),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=85).strftime("%m/%d/%Y"),
        # New Insurance Fields
        "MemberName": fake.name(),
        "idNumber": f"INS-{random.randint(10000,99999)}",
        "GroupNumber": f"GRP-{random.randint(1000,9999)}",
        "PayerName": random.choice(payer_list)
    }

def generate_and_save_bookslot_data(count=5):
    data_list = [generate_bookslot_payload() for _ in range(count)]

    # Save to JSON
    json_path = OUTPUT_DIR / "bookslot_data.json"
    with open(json_path, "w") as jf:
        json.dump(data_list, jf, indent=4)
    print(f"✅ Bookslot JSON saved to: {json_path}")

    # Save to YAML
    yaml_path = OUTPUT_DIR / "bookslot_data.yaml"
    with open(yaml_path, "w") as yf:
        yaml.dump(data_list, yf, default_flow_style=False)
    print(f"✅ Bookslot YAML saved to: {yaml_path}")

    return data_list

if __name__ == "__main__":
    generate_and_save_bookslot_data(5)
