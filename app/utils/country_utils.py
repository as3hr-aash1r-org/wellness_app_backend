import pycountry
import phonenumbers
from phonenumbers import NumberParseException

class CountryValidator:
    """
    Utility to validate consistency between country name, country code, and phone data.
    """
    
    @staticmethod
    def validate_consistency(country_name: str, country_code: str, phone_code: str, phone_number: str) -> None:
        """
        Validates that all country-related fields are consistent with each other.
        Raises ValueError if any inconsistency is found.
        """
        # 1. Validate Country Code (ISO) against Country Name
        try:
            # Look up country by alpha_2 code
            country_obj = pycountry.countries.get(alpha_2=country_code.upper())
            if not country_obj:
                raise ValueError(f"Invalid country code: {country_code}")
            
            # Check if name matches (fuzzy match or exact)
            # We'll check if the provided name is contained in the official name or common name
            # or if the official name is contained in the provided name (for flexibility)
            official_name = getattr(country_obj, 'name', '').lower()
            common_name = getattr(country_obj, 'common_name', '').lower()
            provided_name = country_name.lower()
            
            if provided_name not in official_name and provided_name not in common_name and \
               official_name not in provided_name:
                raise ValueError(f"Country name '{country_name}' does not match country code '{country_code}' ({country_obj.name})")
                
        except KeyError:
             raise ValueError(f"Invalid country code: {country_code}")

        # 2. Validate Phone Code against Country Code
        try:
            # phonenumbers.country_code_for_region returns the integer calling code (e.g. 92 for PK)
            expected_calling_code = phonenumbers.country_code_for_region(country_code.upper())
            
            # Strip '+' from input phone_code
            provided_calling_code_str = phone_code.replace('+', '').strip()
            
            if not provided_calling_code_str.isdigit():
                 raise ValueError(f"Invalid phone code format: {phone_code}")
                 
            provided_calling_code = int(provided_calling_code_str)
            
            if provided_calling_code != expected_calling_code:
                raise ValueError(f"Phone code '{phone_code}' does not match country code '{country_code}' (Expected +{expected_calling_code})")
                
        except Exception as e:
            raise ValueError(f"Error validating phone code: {str(e)}")

        # 3. Validate Phone Number against Country Code
        try:
            # Parse the phone number
            # If phone_number doesn't start with +, add the phone_code
            full_number = phone_number
            if not full_number.startswith('+'):
                if not full_number.startswith(phone_code):
                     full_number = f"{phone_code}{full_number}"
                else:
                     full_number = f"+{full_number}" # Ensure it starts with + if it has the code
            
            parsed_number = phonenumbers.parse(full_number, country_code.upper())
            
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError(f"Phone number '{phone_number}' is not valid for region '{country_code}'")
                
        except NumberParseException:
            raise ValueError(f"Could not parse phone number '{phone_number}'")
