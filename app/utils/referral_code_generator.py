from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.user import User


class ReferralCodeGenerator:
    """
    Generates unique referral codes in the format: [COUNTRY]AAA000 -> [COUNTRY]AAA001 -> [COUNTRY]AAA999 -> [COUNTRY]AAB000
    Pattern: Country Code + 3 letters + 3 digits
    """
    
    DEFAULT_PREFIX = "XX"  # Default for unknown countries
    LETTER_START = "AAA"
    NUMBER_START = "000"
    
    @staticmethod
    def _increment_letters(letters: str) -> str:
        """Increment the 3-letter part (AAA -> AAB -> ... -> AAZ -> ABA -> ...)"""
        letters_list = list(letters)
        
        # Start from the rightmost letter
        for i in range(len(letters_list) - 1, -1, -1):
            if letters_list[i] < 'Z':
                letters_list[i] = chr(ord(letters_list[i]) + 1)
                break
            else:
                letters_list[i] = 'A'
                # Continue to next position (carry over)
        
        return ''.join(letters_list)
    
    @staticmethod
    def _increment_numbers(numbers: str) -> tuple[str, bool]:
        """
        Increment the 3-digit part (000 -> 001 -> ... -> 999)
        Returns (new_numbers, overflow) where overflow indicates if we need to increment letters
        """
        num = int(numbers)
        num += 1
        
        if num > 999:
            return "000", True  # Overflow, reset to 000 and increment letters
        
        return f"{num:03d}", False  # Format as 3-digit string with leading zeros
    
    @classmethod
    def get_country_prefix(cls, country: str) -> str:
        """
        Get the country prefix for referral code generation.
        Expects a 2-letter ISO code or a country name.
        """
        if not country or country == "Unknown":
            return cls.DEFAULT_PREFIX
        
        # If it's already a 2-letter code, return it
        if len(country) == 2 and country.isalpha():
            return country.upper()
            
        # If it's a full name, try to look it up (fallback)
        # Note: We now enforce strict 2-letter codes in the schema, so this is just a safety net
        try:
            import pycountry
            country_obj = pycountry.countries.lookup(country)
            if country_obj:
                return country_obj.alpha_2
        except (ImportError, LookupError):
            pass
        
        return cls.DEFAULT_PREFIX

    @classmethod
    def _parse_referral_code(cls, code: str, prefix: str) -> tuple[str, str]:
        """Parse referral code into letters and numbers parts"""
        if not code.startswith(prefix) or len(code) != len(prefix) + 6:
            raise ValueError(f"Invalid referral code format: {code}")
        
        letters = code[len(prefix):len(prefix)+3]  # 3 letters after prefix
        numbers = code[len(prefix)+3:len(prefix)+6]  # 3 digits after letters
        
        return letters, numbers
    
    @classmethod
    def generate_next_code(cls, db: Session, country: str = None) -> str:
        """Generate the next available referral code for the given country"""
        prefix = cls.get_country_prefix(country)
        
        # Get the latest referral code from database for this country prefix
        query = select(User.referral_code).where(
            User.referral_code.isnot(None),
            User.referral_code.like(f"{prefix}%")
        ).order_by(User.referral_code.desc()).limit(1)
        
        result = db.execute(query)
        latest_code = result.scalar_one_or_none()
        
        if not latest_code:
            # First referral code for this country
            return f"{prefix}{cls.LETTER_START}{cls.NUMBER_START}"
        
        try:
            letters, numbers = cls._parse_referral_code(latest_code, prefix)
            
            # Increment numbers first
            new_numbers, overflow = cls._increment_numbers(numbers)
            
            if overflow:
                # Need to increment letters and reset numbers
                new_letters = cls._increment_letters(letters)
                new_numbers = cls.NUMBER_START
            else:
                new_letters = letters
            
            new_code = f"{prefix}{new_letters}{new_numbers}"
            
            # Verify the code doesn't already exist (safety check)
            existing_query = select(User.id).where(User.referral_code == new_code)
            existing = db.execute(existing_query).scalar_one_or_none()
            
            if existing:
                # This shouldn't happen, but if it does, recursively try next code
                # Create a temporary user with this code to trigger next generation
                temp_user = User(referral_code=new_code)
                db.add(temp_user)
                db.flush()  # Don't commit, just flush to get the effect
                next_code = cls.generate_next_code(db, country)
                db.rollback()  # Rollback the temp user
                return next_code
            
            return new_code
            
        except ValueError as e:
            # If parsing fails, start fresh
            return f"{prefix}{cls.LETTER_START}{cls.NUMBER_START}"
    
    @classmethod
    def is_valid_referral_code(cls, code: str) -> bool:
        """Validate if a referral code has the correct format"""
        if not code or len(code) < 6:
            return False
        
        # Check if it starts with a valid country prefix
        valid_prefix = False
        prefix_used = None
        
        for prefix in cls.COUNTRY_PREFIX_MAP.values():
            if code.startswith(prefix):
                valid_prefix = True
                prefix_used = prefix
                break
        
        if code.startswith(cls.DEFAULT_PREFIX):
            valid_prefix = True
            prefix_used = cls.DEFAULT_PREFIX
        
        if not valid_prefix:
            return False
        
        if len(code) != len(prefix_used) + 6:
            return False
        
        letters = code[len(prefix_used):len(prefix_used)+3]
        numbers = code[len(prefix_used)+3:len(prefix_used)+6]
        
        # Check if letters are all uppercase A-Z
        if not letters.isalpha() or not letters.isupper():
            return False
        
        # Check if numbers are all digits
        if not numbers.isdigit():
            return False
        
        return True


def generate_referral_code(db: Session, country: str = None) -> str:
    """Generate a new unique referral code"""
    return ReferralCodeGenerator.generate_next_code(db, country)


def validate_referral_code(code: str) -> bool:
    """Validate referral code format"""
    return ReferralCodeGenerator.is_valid_referral_code(code)
