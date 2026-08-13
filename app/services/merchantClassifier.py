from rapidfuzz import process, fuzz
from app.models.transaction import Transaction

'''This file will be responsible for categorizing each transaction'''

merchants = {
    "Groceries & Supermarkets": [
        "walmart", "target", "kroger", "whole foods", "trader joe", "safeway",
        "publix", "aldi", "heb", "heb grocery", "costco", "sam's club", "sams club",
        "instacart", "food lion", "giant eagle", "stop and shop", "sprouts", "wegmans"
    ],
    
    "Coffee, Dining & Food Delivery": [
        "starbucks", "dunkin", "dunkin donuts", "mcdonalds", "mcdonald's",
        "doordash", "uber eats", "grubhub", "chipotle", "subway", "chick-fil-a",
        "chick fil a", "panera", "wendys", "dominos", "taco bell", "sweetgreen",
        "shake shack", "dutch bros", "peet's coffee"
    ],
    
    "Transportation & Gas": [
        "uber", "lyft", "chevron", "shell", "bp", "exxon", "exxonmobil",
        "7-eleven", "7 eleven", "circle k", "speedway", "texaco", "marathon petroleum",
        "mta", "clipper", "amtrak", "bird app", "lime app"
    ],
    
    "Subscriptions & Streaming": [
        "netflix", "spotify", "hulu", "apple.com/bill", "apple com bill",
        "disney+", "disney plus", "amazon prime", "youtube premium", "max",
        "hbo max", "playstation", "xbox", "nintendo", "patreon", "nytimes"
    ],
    
    "Retail & E-Commerce": [
        "amazon", "amzn", "ebay", "etsy", "best buy", "apple store",
        "home depot", "lowes", "lowe's", "ikea", "nike", "zara", "marshalls",
        "tj maxx", "nordstrom", "ross stores", "sephora", "ultabeauty"
    ],
    
    "Utilities & Telecom": [
        "at&t", "att", "verizon", "t-mobile", "tmobile", "xfinity", "comcast",
        "spectrum", "charter spectrum", "duke energy", "pg&e", "pge",
        "con edison", "waste management"
    ],
    
    "Travel & Lodging": [
        "airbnb", "vrbo", "delta", "delta air", "united airlines", "american airlines",
        "southwest", "expedia", "booking.com", "marriott", "hilton", "hertz", "enterprise"
    ],
    
    "Pharmacy & Health": [
        "cvs", "cvs pharmacy", "walgreens", "rite aid", "planet fitness",
        "equinox", "quest diagnostics", "goodrx"
    ],
    
    "P2P & Financial Services": [
        "venmo", "zelle", "cash app", "paypal", "coinbase", "robinhood",
        "fidelity", "vanguard", "charles schwab"
    ]
}

MAX_THRESHOLD = 85

FLATTENED_MERCHANTS = {}
for category, merchant_names in merchants.items():
    for merchant in merchant_names:
        FLATTENED_MERCHANTS[merchant] = category


def normalize_description(pre_normalized_description):
    stripped_description = pre_normalized_description.lower().strip()
    words = stripped_description.split()
    normalize = " ".join(words)
    return normalize


def classify_merchant(flattened_merchants, transaction):
    described = normalize_description(transaction.description)
    return process.extractOne(described, flattened_merchants.keys(), fuzz.WRatio)
   
def classify_transaction(transaction):
    match_matrix = classify_merchant(FLATTENED_MERCHANTS, transaction)
    score = match_matrix[1]
    matched_category = FLATTENED_MERCHANTS[match_matrix[0]]
    if score < 85:
        transaction.category = "unclassified"
    else:
        transaction.category = matched_category
    return transaction
    




     




