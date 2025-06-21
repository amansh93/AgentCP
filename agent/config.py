"""
Central configuration for LLM model names.
This allows for easy swapping of models without changing the core logic.
"""

# The primary model used by the MultiStepPlanner for creating complex plans.
# Recommended: A powerful model like GPT-4 Turbo.
PLANNER_MODEL = "gpt-4-turbo"

# A cheaper, faster model used for simpler, single-shot tasks like parsing dates.
# Recommended: A model like GPT-3.5 Turbo.
DATE_PARSER_MODEL = "gpt-3.5-turbo" 