import random

from app.models.cerohumano import CeroHumanoCupDescription


SEASONS = (
    'winter',
    'spring',
    'summer',
    'fall',
)
DAYTIMES = (
    'early morning',
    'dawn',
    'twilight',
    'sunrise',
    'morning',
    'midday',
    'noon',
    'afternoon',
    'evening',
    'golden hour',
    'sunset',
    'dusk',
    'night',
    'midnight',
)
LIGHTINGS = (
    'contrast lighting',
    'soft lighting',
    'normal lighting',
    'lit light',
    'dim light',
    'high key',
    'low key',
    'dramatic lighting',
)
IN_OUT_DOORS = (
    'indoor',
    'outdoor',
)
CLOTHES = (
    'casual outfit',
    'luxury',
    'avant garde',
    'editorial',
    'haute couture',
    'runway',
    'cyberpunk luxury',
    'techwear',
    'hypebeast',
    'oversized',
    'y2k streetwear',
    'athleisure',
    'skatecore',
    'goth',
    'cyberpunk',
    'whimsigoth',
    'grunge',
    'punk glam',
    'e girl',
    'dark academia',
    'coquette',
    'soft girl',
    'cottagecore',
    'kawaii',
    'fairycore',
    'pastel aesthetic',
    'y2k',
    '90s grunge',
    '70s retro',
    'vintage glam',
    'pin up',
    'old money',
    'clubwear',
    'baddie',
    'metallic',
    'bodycon',
    'euphoria high',
    'glitter glam',
    'boudoir',
    'minimalist lingerie',
    'loungewear',
    'sheer',
    'micro knit',
    'silk aesthetic',
)
MOODS = (
    'sensual',
    'mysterious',
    'playful',
    'confident',
    'dreamy',
    'edgy',
    'cozy',
    'provocative',
    'nostalgic',
    'energetic',
    'glamorous',
    'dominant',
    'rebellious',
    'elegant',
    'chill',
    'flirtatious',
    'melancholic',
    'bold',
    'innocent',
    'futuristic',
)
ENVIRONMENT_SETTINGS = (
    'bedroom',
    'school',
    'street',
    'home',
    'luxury hotel suite',
    'neon lit alleyway',
    'minimalist living room',
    'rooftop at sunset',
    'sunlit garden',
    'mirrored dressing room',
    'industrial warehouse',
    'beachfront balcony',
    'vintage diner',
    'dimly lit lounge',
    'cozy coffee shop',
    'futuristic studio',
    'swimming pool edge',
    'underground parking',
    'coastal cliffside',
    'private jet interior',
    'art gallery',
    'urban tennis court',
    'marble bathroom',
)
PLACES = (
    'los angeles',
    'miami beach',
    'tokyo shibuya',
    'paris cafe',
    'ibiza beach club',
    'london underground',
    'new york rooftop',
    'milan fashion week',
    'las vegas strip',
    'bali resort',
    'seoul neon district',
    'berlin night club',
    'amalfi coast',
    'dubai marina',
    'amsterdam canals',
    'icelandic black beach',
    'kyoto bamboo forest',
    'monaco harbor',
    'rio de janeiro',
    'santorini caldera',
    'maldives',
)
CAMERA_ANGLES = (
    ('eye-level', 70),
    ('low-angle', 15),
    ('high-angle', 15),
)
PHOTO_TYPES = (
    'photo',
    'shot',
    'selfie',
)
CROPS = (
    'close-up',
    'bust shot',
    'midshot',
    'full body shot',
)
LOOKING_DIRECTION = (
    ('looking in camera', 70),
    ('not looking in camera', 30),
)
POSITIONS = (
    'staying',
    'sitting',
    'lying',
)
BODY_SHAPES = (
    'slim, slender, thin',
    'fit, toned, shaped',
    'voluptuous',
)

CUP_PERCENTAGES = (20, 15, 11, 8, 6, 5)

POST_CATEGORIES = (
    # ('clothes', CLOTHES),
    ('daytime', DAYTIMES),
    ('environment', ENVIRONMENT_SETTINGS),
    ('location', IN_OUT_DOORS),
    ('lighting', LIGHTINGS),
    ('mood', MOODS),
    ('place', PLACES),
    ('season', SEASONS),
)


def pick_random_settings():
    # 1. picking categories
    categories_amount = random.randint(5, len(POST_CATEGORIES))
    categories = random.sample(POST_CATEGORIES, categories_amount)

    # 2. picking one token from each chosen categories
    return {k: random.choice(v) for k, v in categories}

def pick_random_clothes():
    return random.choice(CLOTHES)

def pick_random_camera_angle():
    options, percentages = zip(*CAMERA_ANGLES)
    return random.choices(options, weights=percentages, k=1)[0]

def pick_random_photo_type():
    return random.choice(PHOTO_TYPES)

def pick_random_crop():
    return random.choice(CROPS)

def pick_random_looking_direction():
    options, percentages = zip(*LOOKING_DIRECTION)
    return random.choices(options, weights=percentages, k=1)[0]

def pick_random_position():
    return random.choice(POSITIONS)

def pick_random_seed():
    return random.randint(0, 2**32 - 1)

def pick_random_cup(min_cup: CeroHumanoCupDescription):
    larger_cups = [None, *[m for m in CeroHumanoCupDescription if min_cup is None or m >= min_cup]]
    percentages = [*CUP_PERCENTAGES[:len(larger_cups) - 1]]
    percentages.insert(0, 100 - sum(percentages))

    return random.choices(larger_cups, weights=percentages, k=1)[0]

def pick_random_body_shape():
    return random.choice(BODY_SHAPES)
