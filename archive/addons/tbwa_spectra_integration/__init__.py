# -*- coding: utf-8 -*-
from . import models, wizards


def post_init_hook(env):
    """
    Post-installation hook to create standard tag vocabulary.
    Creates common expense categories for GL mapping.
    """
    TagVocabulary = env["tbwa.tag.vocabulary"]

    # Check if tags already exist (avoid duplicates on upgrade)
    existing = TagVocabulary.search([])
    if existing:
        return  # Tags already created, skip

    # Standard expense category tags
    standard_tags = [
        {
            "name": "Travel",
            "tag_category": "travel",
            "tag_color": 1,  # Red
            "description": "Travel and transportation expenses",
        },
        {
            "name": "Meals",
            "tag_category": "meals",
            "tag_color": 3,  # Yellow
            "description": "Meals and entertainment",
        },
        {
            "name": "Accommodation",
            "tag_category": "accommodation",
            "tag_color": 2,  # Orange
            "description": "Hotel and lodging",
        },
        {
            "name": "Office Supplies",
            "tag_category": "office",
            "tag_color": 4,  # Blue
            "description": "Office supplies and materials",
        },
        {
            "name": "Professional Fees",
            "tag_category": "professional",
            "tag_color": 9,  # Purple
            "description": "Professional services and consulting",
        },
        {
            "name": "Rent",
            "tag_category": "rent",
            "tag_color": 6,  # Green
            "description": "Office rent and lease",
        },
        {
            "name": "Utilities",
            "tag_category": "utilities",
            "tag_color": 5,  # Pink
            "description": "Electricity, water, utilities",
        },
        {
            "name": "Communication",
            "tag_category": "communication",
            "tag_color": 7,  # Cyan
            "description": "Phone, internet, telecommunications",
        },
        {
            "name": "Equipment",
            "tag_category": "equipment",
            "tag_color": 8,  # Gray
            "description": "Equipment purchase and repairs",
        },
        {
            "name": "Miscellaneous",
            "tag_category": "miscellaneous",
            "tag_color": 0,  # Default
            "description": "Other business expenses",
        },
    ]

    # Create tags
    for tag_data in standard_tags:
        TagVocabulary.create(tag_data)
