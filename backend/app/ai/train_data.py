"""
Synthetic-but-representative training corpus for the incident classification
models. Each tuple is (free_text_report, incident_type, severity).

This stands in for a real historical 911/112 transcript dataset. Because it's
generated in-code, the whole project trains and runs fully offline with no
external dataset download required, while still exercising a genuine
TF-IDF + Naive Bayes / Logistic Regression pipeline (see classifier.py).
"""

TRAINING_SAMPLES = [
    # --- FIRE ---
    ("Building is on fire, heavy smoke coming from the second floor", "fire", "critical"),
    ("Kitchen fire spreading fast, family trapped inside apartment", "fire", "critical"),
    ("Small electrical fire in the garage, contained with extinguisher", "fire", "low"),
    ("Warehouse fully engulfed in flames, explosion risk nearby", "fire", "critical"),
    ("Smell of smoke from neighbor's house, not sure if fire", "fire", "moderate"),
    ("Wildfire approaching residential area, evacuation needed", "fire", "critical"),
    ("Car engine caught fire on the highway shoulder", "fire", "moderate"),
    ("Trash bin fire behind restaurant, spreading to fence", "fire", "low"),
    ("Apartment complex fire, multiple units affected, people on balconies", "fire", "critical"),
    ("Faint burning smell in office building, investigating", "fire", "low"),
    ("Gas leak caused explosion and fire at residential home", "fire", "critical"),
    ("Bonfire got out of control near dry grass field", "fire", "moderate"),

    # --- MEDICAL ---
    ("Man collapsed on the street, not breathing, need ambulance now", "medical", "critical"),
    ("Elderly woman having chest pain and difficulty breathing", "medical", "critical"),
    ("Child fell off bike, has a small cut on knee", "medical", "low"),
    ("Person having seizure at the mall food court", "medical", "high"),
    ("Someone choking on food at the restaurant, turning blue", "medical", "critical"),
    ("Diabetic patient unconscious, low blood sugar suspected", "medical", "high"),
    ("Minor allergic reaction, mild rash after eating peanuts", "medical", "moderate"),
    ("Woman in labor, contractions two minutes apart", "medical", "high"),
    ("Worker fell from ladder, possible broken leg, conscious", "medical", "high"),
    ("Headache and dizziness, requesting non emergency medical advice", "medical", "low"),
    ("Overdose suspected, patient unresponsive and pale", "medical", "critical"),
    ("Stroke symptoms, face drooping and slurred speech", "medical", "critical"),

    # --- CRIME ---
    ("Armed robbery in progress at the corner store", "crime", "critical"),
    ("Break in reported, suspect fled the house", "crime", "moderate"),
    ("Fight breaking out between two groups outside the bar", "crime", "high"),
    ("Someone is following me, I feel unsafe walking home", "crime", "moderate"),
    ("Shots fired reported near the park, people running", "crime", "critical"),
    ("Car window smashed, laptop stolen from the vehicle", "crime", "low"),
    ("Domestic disturbance next door, yelling and banging heard", "crime", "high"),
    ("Shoplifting suspect detained by store security", "crime", "low"),
    ("Kidnapping attempt reported near the school gate", "crime", "critical"),
    ("Vandalism, graffiti sprayed on the community center wall", "crime", "low"),
    ("Suspicious person trying door handles on parked cars", "crime", "moderate"),
    ("Hostage situation reported inside the bank branch", "crime", "critical"),

    # --- ACCIDENT ---
    ("Multi car pileup on the freeway, injuries reported", "accident", "critical"),
    ("Motorcycle collided with a car, rider on the ground", "accident", "high"),
    ("Fender bender in the parking lot, no injuries", "accident", "low"),
    ("Pedestrian hit by a car at the crosswalk", "accident", "critical"),
    ("Truck overturned on the highway, cargo spilled", "accident", "high"),
    ("Bicycle accident, rider has a scraped arm", "accident", "low"),
    ("School bus involved in a collision, children on board", "accident", "critical"),
    ("Two vehicles collided at the intersection, minor damage", "accident", "moderate"),
    ("Boat capsized on the lake, two people in the water", "accident", "critical"),
    ("Ladder fell from a truck onto the road", "accident", "moderate"),
    ("Train derailment reported near the station", "accident", "critical"),
    ("Slip and fall on wet floor at the supermarket", "accident", "low"),

    # --- NATURAL DISASTER ---
    ("Building collapsed after the earthquake, people trapped", "natural_disaster", "critical"),
    ("Flash flooding, water rising fast in the neighborhood", "natural_disaster", "critical"),
    ("Tornado spotted approaching the town from the west", "natural_disaster", "critical"),
    ("Landslide blocking the mountain road after heavy rain", "natural_disaster", "high"),
    ("Minor tremor felt, no visible damage so far", "natural_disaster", "low"),
    ("Hurricane making landfall, storm surge flooding coastline", "natural_disaster", "critical"),
    ("Sinkhole opened up on the residential street", "natural_disaster", "high"),
    ("Heavy hail storm damaging car roofs and windows", "natural_disaster", "moderate"),

    # --- HAZMAT ---
    ("Chemical spill at the factory, strong toxic odor", "hazmat", "critical"),
    ("Gas leak smell reported inside the apartment building", "hazmat", "high"),
    ("Tanker truck leaking unknown liquid on the highway", "hazmat", "critical"),
    ("Carbon monoxide alarm going off, family feeling dizzy", "hazmat", "critical"),
    ("Mild chlorine smell near the swimming pool area", "hazmat", "low"),
    ("Industrial container leaking fumes near the school", "hazmat", "critical"),

    # --- OTHER ---
    ("Cat stuck in a tree, owner requesting assistance", "other", "low"),
    ("Power outage across the block, no immediate danger", "other", "low"),
    ("Noise complaint, loud party next door after midnight", "other", "low"),
    ("Stray dog acting aggressively near the playground", "other", "moderate"),
    ("Water main burst flooding the street, no injuries", "other", "moderate"),
    ("Elevator stuck between floors, two people inside calm", "other", "moderate"),
]


def get_texts_labels_severity():
    texts = [t for t, _, _ in TRAINING_SAMPLES]
    types = [ty for _, ty, _ in TRAINING_SAMPLES]
    sevs = [s for _, _, s in TRAINING_SAMPLES]
    return texts, types, sevs
