#!/usr/bin/env python3
"""
generate_id_ner_faker.py

Faker-based ID NER data generator with infinite diversity.
Uses Faker library to generate realistic names, cities, dates from 50+ locales.

Advantages:
- Infinite unique combinations
- 50+ language/locale support
- Realistic name distributions
- No API limits, works offline
- 100% position accuracy guaranteed
"""
import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

from faker import Faker


class FakerIDGenerator:
    """Generate ID NER data using Faker library."""
    
    # Supported locales for diverse name generation
    AVAILABLE_LOCALES = {
        'fr_FR': 'French',
        'ar_EG': 'Arabic (Egypt)',
        'ar_SA': 'Arabic (Saudi Arabia)',
        'pt_BR': 'Portuguese (Brazil)',
        'pt_PT': 'Portuguese (Portugal)',
        'es_ES': 'Spanish',
        'zh_CN': 'Chinese',
        'vi_VN': 'Vietnamese',
        'de_DE': 'German',
        'it_IT': 'Italian',
        'en_US': 'English (US)',
        'en_GB': 'English (UK)',
        'ja_JP': 'Japanese',
        'ko_KR': 'Korean',
        'ru_RU': 'Russian',
        'nl_NL': 'Dutch',
        'pl_PL': 'Polish',
        'tr_TR': 'Turkish',
        'sv_SE': 'Swedish',
        'no_NO': 'Norwegian'
    }
    
    def __init__(self, config_path: Path = None, noise_level: str = None, locales: List[str] = None):
        """Initialize with Faker providers for multiple locales."""
        
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        # Load noise settings
        self._load_noise_settings(noise_level)
        
        # Initialize Faker instances for different locales
        self.locales = locales or ['fr_FR', 'ar_EG', 'pt_PT', 'zh_CN', 'es_ES']
        self.fakers = {locale: Faker(locale) for locale in self.locales}
        
        # Legacy config data
        self.word_replacements = self.config.get("word_replacements", {})
        self.spacing_errors = self.config.get("spacing_errors", {})
        self.char_subs = self.config.get("character_substitutions", {})
        self.extra_chars = self.config.get("extra_chars_pool", [" ", ".", ",", "-"])
        self.field_typos = self.config.get("field_typos", {})
        
        # Field generation probabilities
        self.field_probs = self.config.get("field_generation_probabilities", {})
        
        # Extract simple format probabilities with backward compatibility
        simple_format = self.field_probs.get("simple_format", {})
        self.simple_probs = {}
        for key, value in simple_format.items():
            if key == "comment":
                continue
            if isinstance(value, dict) and "probability" in value:
                self.simple_probs[key] = value["probability"]
            else:
                self.simple_probs[key] = value
        
        # Extract bilingual format probabilities with backward compatibility  
        bilingual_format = self.field_probs.get("bilingual_format", {})
        self.bilingual_probs = {}
        for key, value in bilingual_format.items():
            if key == "comment":
                continue
            if isinstance(value, dict) and "probability" in value:
                self.bilingual_probs[key] = value["probability"]
            else:
                self.bilingual_probs[key] = value
        
        # Extract signature noise patterns with backward compatibility
        signature_patterns = self.field_probs.get("signature_noise_patterns", {})
        self.signature_noise = {}
        for format_type, patterns in signature_patterns.items():
            if format_type == "comment":
                continue
            self.signature_noise[format_type] = {}
            for pattern, config in patterns.items():
                if pattern == "comment":
                    continue
                if isinstance(config, dict) and "weight" in config:
                    self.signature_noise[format_type][pattern] = config["weight"]
                else:
                    self.signature_noise[format_type][pattern] = config
        
        print(f"🌍 Using {len(self.fakers)} locales: {', '.join(self.locales)}")
    
    def _weighted_choice(self, choices_dict: Dict[str, float]) -> str:
        """Make a weighted random choice from a dictionary of {option: probability}."""
        rand_val = random.random()
        cumulative = 0.0
        for choice, weight in choices_dict.items():
            cumulative += weight
            if rand_val <= cumulative:
                return choice
        # Fallback to last choice if rounding errors
        return list(choices_dict.keys())[-1]
    
    def _load_noise_settings(self, noise_level: str = None):
        """Load noise probabilities from config."""
        if noise_level and noise_level != "config":
            presets = self.config.get("noise_presets", {})
            if noise_level in presets:
                settings = presets[noise_level]
                self.noise_enabled = settings.get("enabled", True) if noise_level != "clean" else False
                if noise_level == "clean":
                    self._set_zero_noise()
                else:
                    self.global_prob = settings.get("global_probability", 0.15)
                    self.word_noise_prob = settings.get("word_noise", 0.10)
                    self.spacing_noise_prob = settings.get("spacing_noise", 0.08)
                    self.char_sub_prob = settings.get("char_substitution", 0.05)
                    self.extra_char_prob = settings.get("char_extra", 0.02)
                    self.missing_char_prob = settings.get("char_missing", 0.015)
                    self.double_char_prob = settings.get("char_double", 0.02)
                print(f"📝 Using noise preset: {noise_level} ({settings.get('description', '')})")
            else:
                self._load_from_config()
        else:
            self._load_from_config()
    
    def _load_from_config(self):
        """Load noise settings from config file."""
        custom = self.config.get("custom_settings", {})
        
        if custom.get("use_custom", False):
            self.noise_enabled = True
            self.global_prob = custom.get("global_probability", 0.15)
            self.word_noise_prob = custom.get("word_noise_probability", 0.10)
            self.spacing_noise_prob = custom.get("spacing_noise_probability", 0.08)
            self.char_sub_prob = custom.get("character_substitution_probability", 0.05)
            self.extra_char_prob = custom.get("extra_char_probability", 0.02)
            self.missing_char_prob = custom.get("missing_char_probability", 0.015)
            self.double_char_prob = custom.get("double_char_probability", 0.02)
            print("📝 Using custom noise settings from config.json")
        else:
            presets = self.config.get("noise_presets", {})
            for name, settings in presets.items():
                if settings.get("enabled", False):
                    if name == "clean":
                        self._set_zero_noise()
                    else:
                        self.noise_enabled = True
                        self.global_prob = settings.get("global_probability", 0.15)
                        self.word_noise_prob = settings.get("word_noise", 0.10)
                        self.spacing_noise_prob = settings.get("spacing_noise", 0.08)
                        self.char_sub_prob = settings.get("char_substitution", 0.05)
                        self.extra_char_prob = settings.get("char_extra", 0.02)
                        self.missing_char_prob = settings.get("char_missing", 0.015)
                        self.double_char_prob = settings.get("char_double", 0.02)
                    print(f"📝 Using preset from config: {name} ({settings.get('description', '')})")
                    return
            
            # Default to medium
            self.noise_enabled = True
            self.global_prob = 0.15
            self.word_noise_prob = 0.10
            self.spacing_noise_prob = 0.08
            self.char_sub_prob = 0.05
            self.extra_char_prob = 0.02
            self.missing_char_prob = 0.015
            self.double_char_prob = 0.02
            print("📝 Using default medium noise")
    
    def _set_zero_noise(self):
        """Disable all noise."""
        self.noise_enabled = False
        self.global_prob = 0.0
        self.word_noise_prob = 0.0
        self.spacing_noise_prob = 0.0
        self.char_sub_prob = 0.0
        self.extra_char_prob = 0.0
        self.missing_char_prob = 0.0
        self.double_char_prob = 0.0
        print("📝 Using clean mode (no noise)")
    
    def apply_noise(self, text: str, allow_noise: bool = True) -> str:
        """Apply OCR-style noise to text."""
        if not self.noise_enabled or not allow_noise or random.random() > self.global_prob:
            return text
        
        # Word-level replacements
        if random.random() < self.word_noise_prob:
            for original, variants in self.word_replacements.items():
                if original in text:
                    text = text.replace(original, random.choice(variants))
        
        # Spacing errors
        if random.random() < self.spacing_noise_prob:
            for original, variants in self.spacing_errors.items():
                if original in text:
                    text = text.replace(original, random.choice(variants))
        
        # Character-level noise
        if random.random() < (self.char_sub_prob + self.extra_char_prob + self.missing_char_prob):
            text = self._apply_character_noise(text)
        
        return text
    
    def _apply_character_noise(self, text: str) -> str:
        """Apply character-level OCR noise."""
        result = []
        
        for char in text:
            # Skip character (missing)
            if random.random() < self.missing_char_prob:
                continue
            
            # Character substitution
            if char in self.char_subs and random.random() < self.char_sub_prob:
                result.append(self.char_subs[char])
            else:
                result.append(char)
            
            # Duplicate character
            if random.random() < self.double_char_prob:
                result.append(char)
            
            # Insert extra character
            if random.random() < self.extra_char_prob:
                result.append(random.choice(self.extra_chars))
        
        return "".join(result)
    
    def apply_field_typo(self, field_text: str) -> str:
        """
        Apply field-specific typos (e.g., 'Surname' -> 'Sumame').
        This adds realistic OCR errors specific to form field labels.
        """
        # Check if this exact field has typo variants
        if field_text in self.field_typos:
            return random.choice(self.field_typos[field_text])
        
        # Check for partial matches (e.g., field contains the word)
        for original, variants in self.field_typos.items():
            if original in field_text:
                return field_text.replace(original, random.choice(variants))
        
        # If no specific typo defined, apply general noise
        return self.apply_noise(field_text, allow_noise=True)
    
    def generate_name(self) -> str:
        """Generate surname using random locale."""
        faker = random.choice(list(self.fakers.values()))
        return faker.last_name().upper()
    
    def generate_given_names(self, count: int = None) -> List[str]:
        """Generate 1-3 given names using random locales."""
        if count is None:
            count = random.randint(1, 3)
        
        names = []
        for _ in range(count):
            faker = random.choice(list(self.fakers.values()))
            name = faker.first_name().upper()
            names.append(name)
        
        return names
    
    def generate_city(self) -> str:
        """Generate city name using random locale."""
        faker = random.choice(list(self.fakers.values()))
        city = faker.city().upper()
        
        # Clean up city names (remove common prefixes/suffixes)
        city = city.replace("VILLE", "").replace("CITY", "").replace("SAN ", "").strip()
        
        return city[:20]  # Limit length
    
    def generate_id_number(self) -> str:
        """Generate random ID number."""
        format_type = random.choice(["numeric", "date_based", "alphanumeric"])
        
        if format_type == "numeric":
            return "".join([str(random.randint(0, 9)) for _ in range(12)])
        
        elif format_type == "date_based":
            year = random.randint(50, 99)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            suffix = "".join([str(random.randint(0, 9)) for _ in range(5)])
            return f"{year:02d}{month:02d}{day:02d}T{suffix}"
        
        else:
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            nums = "0123456789"
            return (random.choice(letters) + random.choice(nums) +
                   "".join([random.choice(letters) for _ in range(3)]) +
                   "".join([random.choice(nums) for _ in range(2)]) +
                   random.choice(letters) + random.choice(nums))
    
    def generate_date(self) -> str:
        """Generate birth date using Faker."""
        faker = random.choice(list(self.fakers.values()))
        date = faker.date_of_birth(minimum_age=18, maximum_age=80)
        
        format_type = random.choice(["dots", "spaces"])
        
        if format_type == "dots":
            return f"{date.day:02d}.{date.month:02d}.{date.year}"
        else:
            return f"{date.day:02d} {date.month:02d} {date.year}"
    
    def generate_height(self) -> str:
        """Generate height in meters."""
        meters = random.randint(1, 2)
        cm = random.randint(50, 99)
        separator = random.choice([" ", ""])
        unit = random.choice(["m", "M"])
        return f"{meters}{separator}{cm}{unit}"
    
    def generate_support_number(self) -> str:
        """Generate support number (6-digit numeric only)."""
        return f"{random.randint(100000, 999999)}"
    
    def generate_expiry_date(self, birth_year: int) -> str:
        """Generate expiry date."""
        issue_year = birth_year + random.randint(18, 50)
        expiry_year = issue_year + 15
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{day:02d} {month:02d} {expiry_year}"
    
    def generate_simple_format(self) -> Tuple[str, List]:
        """Generate simple format (70% probability)."""
        parts = []
        entities = []
        pos = 0
        
        # Header variations with Country entity
        header_variants = [
            "RÉPUBLIQUE FRANÇAISE",
            "FRANÇAISE RÉPUBLIQUE",
            "RÉPUBLIQUEFRANÇAISE"
        ]
        header = random.choice(header_variants)
        header_noisy = self.apply_noise(header, allow_noise=True)
        country_start = pos
        parts.append(header_noisy + " ")
        pos += len(header_noisy) + 1
        entities.append([country_start, country_start + len(header_noisy), "Country", header_noisy])
        
        # Document type
        doc_type = "CARTE NATIONALE D'IDENTITÉ"
        doc_type_noisy = self.apply_noise(doc_type, allow_noise=True)
        doc_start = pos
        parts.append(doc_type_noisy)
        pos += len(doc_type_noisy)
        entities.append([doc_start, pos, "DOC_TYPE", doc_type_noisy])
        
        # ID Number
        id_label = " N° : "
        id_label_noisy = self.apply_noise(id_label, allow_noise=True)
        parts.append(id_label_noisy)
        pos += len(id_label_noisy)
        
        id_num = self.generate_id_number()
        id_start = pos
        parts.append(id_num)
        pos += len(id_num)
        entities.append([id_start, pos, "DNI", id_num])
        
        # Nationality (label)
        nat_label = " Nationalité "
        nat_label_noisy = self.apply_field_typo(nat_label)
        parts.append(nat_label_noisy)
        pos += len(nat_label_noisy)
        
        # Nationality value (annotated entity)
        nationality = "Française"
        nat_start = pos
        parts.append(nationality + " ")
        pos += len(nationality) + 1
        entities.append([nat_start, pos - 1, "Nationality", nationality])

        # Pre-generate names to calculate 2-letter code
        surname = self.generate_name()
        given_names_list = self.generate_given_names()

        # Dynamic 2-letter code based on first letters of surname and first given name
        code_prob = self.simple_probs.get("two_letter_code", 0.5)
        if random.random() < code_prob:
            first_letter_surname = surname[0] if surname else "A"
            first_letter_given = given_names_list[0][0] if given_names_list else "A"
            code = first_letter_surname + first_letter_given
            parts.append(code + " ")
            pos += len(code + " ")

        # Signature noise (before NOM like in bilingual format)
        noise_prob = self.simple_probs.get("signature_noise_before_nom", 0.2)
        if random.random() < noise_prob:
            simple_noise_patterns = self.signature_noise.get("simple_format", {
                "RF ": 0.3, "3F ": 0.2, "RERE ": 0.1, "none": 0.4
            })
            chosen_noise = self._weighted_choice(simple_noise_patterns)
            if chosen_noise != "none":
                parts.append(chosen_noise)
                pos += len(chosen_noise)

        # Name (using Faker)
        name_label = "Nom : "
        name_label_noisy = self.apply_noise(name_label, allow_noise=True)
        parts.append(name_label_noisy)
        pos += len(name_label_noisy)
        
        name_start = pos
        parts.append(surname)
        pos += len(surname)
        entities.append([name_start, pos, "Name", surname])

        # Optional social status fields (Epouse, Veuve, Nom d'usage)
        social_status_prob = self.simple_probs.get("social_status_fields", 0.3)
        if random.random() < social_status_prob:
            social_status_types = [
                "Epouse: ",
                "Veuve: ", 
                "Nom d'usage: "
            ]
            social_label = random.choice(social_status_types)
            social_label_noisy = self.apply_field_typo(social_label)
            parts.append(" " + social_label_noisy)
            pos += len(" " + social_label_noisy)
            
            alt_name = self.generate_name()
            alt_start = pos
            # Handle hyphenated names like "BERTAU- PETE"
            hyphen_prob = self.simple_probs.get("hyphenated_alt_names", 0.3)
            if random.random() < hyphen_prob:
                alt_name = alt_name + "- " + self.generate_name()
            parts.append(alt_name)
            pos += len(alt_name)
            entities.append([alt_start, pos, "Alt_name", alt_name])

        # Given names (using pre-generated list)
        prenom_label = "Prénom(s)"
        prenom_label_noisy = self.apply_field_typo(prenom_label)
        prenom_full = f" {prenom_label_noisy}: "
        parts.append(prenom_full)
        pos += len(prenom_full)
        
        for i, gname in enumerate(given_names_list):
            if i > 0:
                parts.append(", ")
                pos += 2
            
            gname_start = pos
            parts.append(gname)
            pos += len(gname)
            entities.append([gname_start, pos, f"Surname_{i+1}", gname])
        
        # Gender
        sex_label = " Sexe : "
        sex_label_noisy = self.apply_field_typo(sex_label)
        parts.append(sex_label_noisy)
        pos += len(sex_label_noisy)
        
        gender = random.choice(["M", "F"])
        gender_start = pos
        parts.append(gender)
        pos += 1
        entities.append([gender_start, pos, "Gender", gender])
        
        # Birth date (using Faker)
        ne_label = "Né(e)"
        ne_label_noisy = self.apply_field_typo(ne_label)
        ne_full = f" {ne_label_noisy} le : "
        parts.append(ne_full)
        pos += len(ne_full)
        
        birth_date = self.generate_date()
        birth_date_start = pos
        parts.append(birth_date)
        pos += len(birth_date)
        entities.append([birth_date_start, pos, "Date of birthday", birth_date])
        
        # Birth place (using Faker)
        birth_place_prob = self.simple_probs.get("birth_place", 0.8)
        if random.random() < birth_place_prob:
            a_label = " à "
            parts.append(a_label)
            pos += len(a_label)
            
            city = self.generate_city()
            city_start = pos
            parts.append(city)
            pos += len(city)
            entities.append([city_start, pos, "Birth_place", city])
        
        # Height
        height_prob = self.simple_probs.get("height", 0.6)
        if random.random() < height_prob:
            taille_label = "Taille"
            taille_label_noisy = self.apply_noise(taille_label, allow_noise=True)
            taille_full = f" {taille_label_noisy} : "
            parts.append(taille_full)
            pos += len(taille_full)
            
            height = self.generate_height()
            height_start = pos
            parts.append(height)
            pos += len(height)
            entities.append([height_start, pos, "Height", height])
        
        # Optional signature
        signature_prob = self.simple_probs.get("optional_signature", 0.4)
        if random.random() < signature_prob:
            sig_label = "Signature du titulaire"
            sig_label_noisy = self.apply_noise(sig_label, allow_noise=True)
            sig_full = f" {sig_label_noisy} :"
            parts.append(sig_full)
            pos += len(sig_full)
        
        text = "".join(parts)
        return text, entities
    
    def generate_bilingual_format(self) -> Tuple[str, List]:
        parts = []
        entities = []
        pos = 0
        
        # Header with Country entity - with variations like simple format
        header_variants = [
            "RÉPUBLIQUE FRANÇAISE",
            "FRANÇAISE RÉPUBLIQUE",
            "RÉPUBLIQUEFRANÇAISE"
        ]
        header = random.choice(header_variants)
        header_noisy = self.apply_noise(header, allow_noise=True)
        country_start = pos
        parts.append(header_noisy)
        pos += len(header_noisy)
        entities.append([country_start, pos, "Country", header_noisy])
        
        # Add " FR " after country
        parts.append(" FR ")
        pos += 4
        
        # Document type
        doc_type = "CARTE NATIONALE D'IDENTITÉ / IDENTITY CARD"
        doc_type_noisy = self.apply_noise(doc_type, allow_noise=True)
        doc_start = pos
        parts.append(doc_type_noisy)
        pos += len(doc_type_noisy)
        entities.append([doc_start, pos, "DOC_TYPE", doc_type_noisy])
        
        # Name (using Faker) - default to "Sumame" (most common OCR error)
        # Will occasionally change to "Surname" or other variants when noise is applied
        field_label = self.apply_field_typo(" NOM/Sumame ")
        parts.append(field_label)
        pos += len(field_label)
        surname = self.generate_name()
        name_start = pos
        parts.append(surname)
        pos += len(surname)
        entities.append([name_start, pos, "Name", surname])
        
        # Given names
        given_label = self.apply_field_typo(" Prénoms / Given names ")
        parts.append(given_label)
        pos += len(given_label)
        
        given_names_list = self.generate_given_names(random.randint(1, 2))
        
        for i, gname in enumerate(given_names_list):
            if i > 0:
                parts.append(", ")
                pos += 2
            
            gname_start = pos
            parts.append(gname)
            pos += len(gname)
            entities.append([gname_start, pos, f"Surname_{i+1}", gname])
        
        # Gender label (without value - value comes after birth date)
        gender_label = self.apply_field_typo(" SEXE /Sex ")
        parts.append(gender_label)
        pos += len(gender_label)
        
        # Nationality label (but value comes later after date)
        nat_label = self.apply_field_typo(" NATIONALITÉ / Nationality ")
        parts.append(nat_label)
        pos += len(nat_label)
        
        # Birth date label
        date_label = "DATE DE NAISS. / Date of birth "
        parts.append(date_label)
        pos += len(date_label)
        
        # Gender value (appears before nationality value)
        gender = random.choice(["M", "F"])
        gender_start = pos
        parts.append(gender + " ")
        pos += 2
        entities.append([gender_start, gender_start + 1, "Gender", gender])
        
        # Nationality value (appears after gender, before the date)
        nationality = random.choice(["FRA", "ESP", "PRT", "ITA", "BEL", "MAR", "TUN", "DZA"])
        nat_start = pos
        parts.append(nationality + " ")
        pos += len(nationality) + 1
        entities.append([nat_start, pos - 1, "Nationality", nationality])
        
        # Birth date value
        birth_date = self.generate_date()
        birth_date_start = pos
        parts.append(birth_date)
        pos += len(birth_date)
        entities.append([birth_date_start, pos, "Date of birthday", birth_date])
        
        # Birth place (using Faker)
        birth_place_prob = self.bilingual_probs.get("birth_place", 0.9)
        if random.random() < birth_place_prob:
            birth_place_label = " LIEU DE NAISSANCE / Place of birth "
            parts.append(birth_place_label)
            pos += len(birth_place_label)
            
            city = self.generate_city()
            city_start = pos
            parts.append(city)
            pos += len(city)
            entities.append([city_start, pos, "Birth_place", city])
        
        # Guardian name (married name) - appears randomly for married individuals
        alt_name_prob = self.bilingual_probs.get("alt_name_married", 0.3)
        if random.random() < alt_name_prob:
            guardian_label = " NOM D'USAGE / Alternate name ép. "
            guardian_label_noisy = self.apply_field_typo(guardian_label)
            parts.append(guardian_label_noisy)
            pos += len(guardian_label_noisy)
            
            guardian_name = self.generate_name()
            guardian_start = pos
            parts.append(guardian_name)
            pos += len(guardian_name)
            entities.append([guardian_start, pos, "Alt_name", guardian_name])
        
        # Document number
        doc_num_label = " N° DU DOCUMENT / Document No "
        parts.append(doc_num_label)
        pos += len(doc_num_label)
        id_num = self.generate_id_number()
        id_start = pos
        parts.append(id_num)
        pos += len(id_num)
        entities.append([id_start, pos, "DNI", id_num])
        
        # Expiry date
        expiry_prob = self.bilingual_probs.get("expiry_date", 0.8)
        if random.random() < expiry_prob:
            expiry_label = " DATE D'EXPIR. / Expiry date "
            parts.append(expiry_label)
            pos += len(expiry_label)
            
            expiry = self.generate_expiry_date(1980)
            expiry_start = pos
            parts.append(expiry)
            pos += len(expiry)
            entities.append([expiry_start, pos, "Validity_date", expiry])
        
        # Support number with optional signature noise
        support_prob = self.bilingual_probs.get("support_number", 0.4)
        if random.random() < support_prob:
            parts.append(" ")
            pos += 1
            
            # Random signature noise (sometimes appears before support number)
            # This simulates OCR misreading signatures as characters
            bilingual_noise_patterns = self.signature_noise.get("bilingual_format", {
                "MA ": 0.3, "random_2letter": 0.2, "random_digits": 0.1, "none": 0.4
            })
            chosen_noise = self._weighted_choice(bilingual_noise_patterns)
            
            if chosen_noise == "MA ":
                parts.append("MA ")
                pos += 3
            elif chosen_noise == "random_2letter":
                noise = random.choice(["AB ", "BA ", "CA ", "DA ", "KA ", "RA ", "SA "])
                parts.append(noise)
                pos += 3
            elif chosen_noise == "random_digits":
                noise_len = random.choice([2, 3])
                noise = "".join([str(random.randint(0, 9)) for _ in range(noise_len)]) + " "
                parts.append(noise)
                pos += len(noise)
            # else: no noise (none option)
            
            support = self.generate_support_number()
            support_start = pos
            parts.append(support)
            pos += len(support)
            entities.append([support_start, pos, "Support_number", support])

        
        text = "".join(parts)
        return text, entities
    
    def generate_one(self) -> Dict:
        """Generate one complete ID with entities."""
        if random.random() < 0.7:
            text, entities = self.generate_simple_format()
        else:
            text, entities = self.generate_bilingual_format()
        
        return {
            "text": text,
            "entities": entities
        }
    
    def generate_batch(self, count: int) -> List[Dict]:
        """Generate multiple IDs."""
        return [self.generate_one() for _ in range(count)]


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic ID NER data using Faker library"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output JSON file path"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=100,
        help="Number of IDs to generate (default: 100)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.json (default: ./config.json)"
    )
    parser.add_argument(
        "--noise-level",
        choices=["clean", "light", "medium", "heavy", "config"],
        default="config",
        help="Noise level preset (default: config)"
    )
    parser.add_argument(
        "--locales",
        type=str,
        default="fr_FR,es_ES,it_IT",
        help="Comma-separated list of locales (default: fr_FR,es_ES,it_IT)"
    )
    parser.add_argument(
        "--all-locales",
        action="store_true",
        help="Use all 20 available locales for maximum diversity"
    )
    parser.add_argument(
        "--list-locales",
        action="store_true",
        help="List available locales and exit"
    )
    
    args = parser.parse_args()
    
    # List locales and exit
    if args.list_locales:
        print("\n🌍 Available Locales:")
        print("=" * 60)
        for code, name in sorted(FakerIDGenerator.AVAILABLE_LOCALES.items()):
            print(f"  {code:10s} - {name}")
        print("\nUsage: --locales fr_FR,ar_EG,zh_CN")
        print("   Or: --all-locales")
        return
    
    # Determine locales
    if args.all_locales:
        locales = list(FakerIDGenerator.AVAILABLE_LOCALES.keys())
    else:
        locales = [loc.strip() for loc in args.locales.split(",")]
        # Validate locales
        invalid = [loc for loc in locales if loc not in FakerIDGenerator.AVAILABLE_LOCALES]
        if invalid:
            print(f"❌ Invalid locales: {', '.join(invalid)}")
            print(f"Use --list-locales to see available options")
            return 1
    
    print(f"\n🎲 Generating {args.count} synthetic ID cards with Faker")
    
    # Initialize generator
    generator = FakerIDGenerator(
        config_path=args.config,
        noise_level=args.noise_level if args.noise_level != "config" else None,
        locales=locales
    )
    
    print("-" * 70)
    
    # Generate data
    results = generator.generate_batch(args.count)
    
    # Save results
    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Statistics
    total_entities = sum(len(item["entities"]) for item in results)
    avg_entities = total_entities / len(results) if results else 0
    
    print("-" * 70)
    print(f"✅ Successfully generated {len(results)} ID cards")
    print(f"📊 Total entities: {total_entities}")
    print(f"📈 Average entities per card: {avg_entities:.1f}")
    print(f"💾 Saved to: {output_path}")
    print(f"\n🔍 Validate with: python verify_positions.py {args.output}")


if __name__ == "__main__":
    main()
