"""Behave-Django environment hooks for the movie theater booking app."""

from __future__ import annotations

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_theater_booking.settings")
django.setup()


def before_scenario(context, scenario):
    """Require every feature scenario to be explicitly tagged as integration."""
    scenario_tags = {tag.lower() for tag in getattr(scenario, "tags", [])}
    feature_tags = {
        tag.lower()
        for tag in getattr(getattr(context, "feature", None), "tags", [])
    }
    if "integration" not in scenario_tags | feature_tags:
        raise AssertionError(
            f"Scenario '{scenario.name}' must include @integration."
        )
