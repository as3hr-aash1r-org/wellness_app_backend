import phonenumbers
from phonenumbers import geocoder, country_code_for_region

def get_country_details(phone_number: str):
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        country_name = geocoder.description_for_number(parsed_number, "en")
        country_code = f"+{parsed_number.country_code}"
        return country_name, country_code
    except Exception as e:
        print(f"Failed to parse phone number {phone_number}: {e}")
        return None, None
