"""
This file contains the core knowledge base for client and group mappings.
"""

# Static map of client names to their internal IDs
CLIENT_NAME_TO_ID = {
    "millennium": "cl_id_millennium",
    "citadel": "cl_id_citadel",
    "point 72": "cl_id_point72",
    "two sigma": "cl_id_twosigma",
    # ... add all other client names here
}

# Static map of client group names to a list of internal client IDs
CLIENT_GROUP_TO_IDS = {
    "systematic": ["cl_id_twosigma", "cl_id_citadel", "cl_id_some_other_quant"],
    "quant": ["cl_id_twosigma", "cl_id_some_other_quant"],
    "multi-manager": ["cl_id_millennium", "cl_id_point72"],
    "book": [],
    "all clients": []
}

CLIENT_MAPPING = {
    "names": {
        "millennium": "cl_id_millennium",
        "citadel": "cl_id_citadel",
        "point 72": "cl_id_point72",
        "two sigma": "cl_id_twosigma",
    },
    "groups": {
        "systematic client segment": ["cl_id_some_other_quant", "cl_id_twosigma", "cl_id_citadel"],
        "discretionary majors": ["cl_id_millennium", "cl_id_point72", "cl_id_citadel"],
        "all clients": [] # This will be populated dynamically
    }
}

CLIENT_URL_SKELETON = "https://my-internal-platform.com/clients/{client_id}"

VALID_BUSINESSES = ["Prime", "Equities Ex Prime", "FICC"]
VALID_SUBBUSINESSES = ["PB", "SPG", "Futures", "DCS", "One Delta", "Eq Deriv", "Credit", "Macro"] 