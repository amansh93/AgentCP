"""
Central configuration for LLM model names.
This allows for easy swapping of models without changing the core logic.
"""

import os

# Get the directory where the current script is located
_current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the data file
CLIENT_DATA_PATH = os.path.join(_current_dir, '..', 'knowledge_base', 'client_data.py')

# The primary model used by the MultiStepPlanner for creating complex plans.
# Recommended: A powerful model like GPT-4 Turbo.
PLANNER_MODEL = "gpt-4o-mini"

# A cheaper, faster model used for simpler, single-shot tasks like parsing dates.
# Recommended: A model like GPT-3.5 Turbo.
DATE_PARSER_MODEL = "gpt-3.5-turbo"

# A new model used for synthesizing responses
SYNTHESIZER_MODEL = "gpt-4o-mini" 