# Probability System Documentation

## Overview

The ID generator uses a **layered probability system** that controls when and how often different elements appear in the generated identity cards. **Fields do NOT appear all the time** - each field has its own probability that determines if it will be included in a specific ID card.

## Key Concept: Probabilities Are Per-Card, Not Global

🎯 **Important**: Each time an ID is generated, the system rolls the dice for each optional field independently. A probability of 0.3 (30%) means that field appears in roughly 3 out of every 10 cards generated.

## Format Selection (First Decision)

```
70% chance → Simple Format
30% chance → Bilingual Format
```

This is determined first, then the appropriate probabilities are used for that format.

---

## Simple Format Field Probabilities

### Core Fields (Always Present)
- **Country header**: 100% (RÉPUBLIQUE FRANÇAISE, etc.)
- **Document type**: 100% (CARTE NATIONALE D'IDENTITÉ)
- **ID number**: 100% 
- **Nationality**: 100% (Française)
- **Surname**: 100% (Nom : SURNAME)
- **Given names**: 100% (Prénom(s): NAMES)
- **Gender**: 100% (Sexe : M/F)
- **Birth date**: 100% (Né(e) le : DATE)

### Optional Fields (Probability-Based)

#### 1. Two-Letter Code (50% chance)
```json
"two_letter_code": {
  "probability": 0.5,
  "description": "Dynamic 2-letter code based on first letters of surname + first given name"
}
```

**How it works**:
- **IF** `random.random() < 0.5` → Code appears (e.g., "MM" from MARTIN + MARIE)
- **ELSE** → No code
- **Position**: After nationality, before signature noise
- **Example**: `Nationalité Française MM Nom : MARTIN`

#### 2. Signature Noise Before Nom (20% chance)
```json
"signature_noise_before_nom": {
  "probability": 0.2,
  "description": "OCR noise patterns (RF, 3F, RERE) that appear before the 'Nom :' field"
}
```

**How it works**:
- **First check**: `random.random() < 0.2` → Signature noise will appear
- **IF YES**: Weighted selection from patterns:
  - RF (30% of noise cases) → Most likely
  - 3F (20% of noise cases) 
  - RERE (10% of noise cases)
  - none (40% of noise cases) → Clean
- **Position**: Right before "Nom :"
- **Example**: `Française RF Nom : GARCIA`

#### 3. Social Status Fields (30% chance)
```json
"social_status_fields": {
  "probability": 0.3,
  "description": "Social status fields like 'Epouse: SURNAME', 'Veuve: SURNAME', 'Nom d'usage: SURNAME'"
}
```

**How it works**:
- **IF** `random.random() < 0.3` → Social status will appear
- **THEN**: Random choice from ["Epouse: ", "Veuve: ", "Nom d'usage: "]
- **Position**: After main surname
- **Example**: `Nom : MARTIN Epouse: BERNARD Prénom(s): MARIE`

#### 4. Hyphenated Alt Names (30% chance | only when social status appears)
```json
"hyphenated_alt_names": {
  "probability": 0.3,
  "description": "When social status fields appear, chance for hyphenated format"
}
```

**How it works**:
- **Only triggers IF** social status field is already appearing
- **IF** `random.random() < 0.3` → Use hyphenated format
- **Example**: `Epouse: BERTAU- PETE` instead of `Epouse: BERTAU`

#### 5. Birth Place (80% chance)
```json
"birth_place": {
  "probability": 0.8,
  "description": "City/location after birth date"
}
```

**How it works**:
- **IF** `random.random() < 0.8` → Birth place appears
- **Position**: After birth date
- **Example**: `Né(e) le : 15.03.1980 à PARIS`

#### 6. Height (60% chance)
```json
"height": {
  "probability": 0.6,
  "description": "Height field in meters format"
}
```

**How it works**:
- **IF** `random.random() < 0.6` → Height appears
- **Position**: After birth place (if present) or birth date
- **Example**: `Taille : 1 75m`

#### 7. Optional Signature (40% chance)
```json
"optional_signature": {
  "probability": 0.4,
  "description": "Signature section label at the end"
}
```

**How it works**:
- **IF** `random.random() < 0.4` → Signature label appears
- **Position**: End of card
- **Example**: `Signature du titulaire :`

---

## Bilingual Format Field Probabilities

### Core Fields (Always Present)
- All the same core fields as simple format
- Plus bilingual labels (French/English)

### Optional Fields (Probability-Based)

#### 1. Birth Place (90% chance)
```json
"birth_place": {
  "probability": 0.9,
  "description": "Birth location field 'LIEU DE NAISSANCE / Place of birth'"
}
```

**Higher probability than simple format** - bilingual cards more commonly include birth location.

#### 2. Alt Name Married (30% chance)
```json
"alt_name_married": {
  "probability": 0.3,
  "description": "Married/alternate name field for married individuals"
}
```

**How it works**:
- **IF** `random.random() < 0.3` → Married name appears
- **Format**: `NOM D'USAGE / Alternate name ép. SURNAME`

#### 3. Support Number (40% chance)
```json
"support_number": {
  "probability": 0.4,
  "description": "6-digit support number at end of bilingual cards"
}
```

**How it works**:
- **IF** `random.random() < 0.4` → Support number appears
- **May include signature noise before it** (see signature noise section)

#### 4. Expiry Date (80% chance)
```json
"expiry_date": {
  "probability": 0.8,
  "description": "Expiry date field in bilingual format"
}
```

**High probability** - most bilingual cards include expiry dates.

---

## Signature Noise Patterns (Weighted Selection)

### Simple Format Signature Noise
When signature noise is triggered (20% chance), weighted selection:

```json
"RF ": {"weight": 0.3},     // 30% of noise cases → Most common
"3F ": {"weight": 0.2},     // 20% of noise cases
"RERE ": {"weight": 0.1},   // 10% of noise cases  
"none": {"weight": 0.4}     // 40% of noise cases → No noise
```

**Weighted Selection Algorithm**:
```python
# Generate random number 0.0 to 1.0
rand_val = random.random()

# Check cumulative weights
if rand_val <= 0.3:        # 0.0 to 0.3 → RF
    chosen = "RF "
elif rand_val <= 0.5:      # 0.3 to 0.5 → 3F  
    chosen = "3F "
elif rand_val <= 0.6:      # 0.5 to 0.6 → RERE
    chosen = "RERE "
else:                      # 0.6 to 1.0 → none
    chosen = "none"
```

### Bilingual Format Signature Noise
When support number appears (40% chance), weighted selection for noise before it:

```json
"MA ": {"weight": 0.1},            // 10% of support cases
"random_2letter": {"weight": 0.2}, // 20% of support cases → AB, BA, CA, etc.
"random_digits": {"weight": 0.1},  // 10% of support cases → 2-3 digits
"none": {"weight": 0.4}            // 60% of support cases → Clean
```

---

## Real-World Examples

### Example 1: Simple Format Generation
1. **Format selection**: 70% roll → Simple format chosen
2. **Core fields**: All appear (100%)
3. **Two-letter code**: 50% roll → **NO** (unlucky roll)
4. **Signature noise**: 20% roll → **YES** (lucky roll)
   - Weighted selection → "3F " chosen
5. **Social status**: 30% roll → **YES** 
   - Random choice → "Epouse: " selected
   - Hyphenated: 30% roll → **NO**
6. **Birth place**: 80% roll → **YES**
7. **Height**: 60% roll → **NO**
8. **Signature**: 40% roll → **YES**

**Result**: 
```
RÉPUBLIQUE FRANÇAISE CARTE NATIONALE D'IDENTITÉ N° : 123456789 
Nationalité Française 3F Nom : MARTIN Epouse: BERNARD 
Prénom(s): MARIE Sexe : F Né(e) le : 15.03.1980 à PARIS 
Signature du titulaire :
```

### Example 2: Bilingual Format Generation
1. **Format selection**: 30% roll → Bilingual format chosen
2. **Core fields**: All appear (100%)
3. **Birth place**: 90% roll → **YES**
4. **Alt name**: 30% roll → **NO**
5. **Support number**: 40% roll → **YES**
   - Signature noise: Weighted → "MA " chosen
6. **Expiry date**: 80% roll → **YES**

**Result**:
```
RÉPUBLIQUE FRANÇAISE FR CARTE NATIONALE D'IDENTITÉ / IDENTITY CARD 
NOM/Surname GARCIA Prénoms / Given names MARIA SEXE /Sex F 
NATIONALITÉ / Nationality FRA DATE DE NAISS. / Date of birth 15.03.1980 
LIEU DE NAISSANCE / Place of birth MADRID N° DU DOCUMENT / Document No 987654321 
DATE D'EXPIR. / Expiry date 15 03 2025 MA 123456
```

---

## Summary: Why Fields Don't Always Appear

- **Probabilities create realistic variation** - real ID cards don't all have identical fields
- **Each card is independently generated** - 30% probability means roughly 30% of generated cards will have that field
- **Layered system** - some probabilities are conditional (e.g., hyphenated names only when social status appears)
- **Weighted selection** ensures realistic distribution of noise patterns

**Key takeaway**: The system generates diverse, realistic ID cards where optional fields appear at frequencies matching real-world French identity documents.