"""
Write close approach data to CSV or JSON files.

This module provides functions for serializing close approach data
to structured files.
"""

import csv
import json


def write_to_csv(results, filename):
    """
    Write close approach data to a CSV file.

    Args:
        results: An iterable of CloseApproach objects
        filename: Path to the output CSV file
    """
    fieldnames = (
        "datetime_utc",
        "distance_au",
        "velocity_km_s",
        "designation",
        "name",
        "diameter_km",
        "potentially_hazardous",
    )

    with open(filename, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for approach in results:
            # Get NEO data
            neo = approach.neo
            if neo:
                designation = neo.designation
                name = neo.name
                diameter = neo.diameter
                hazardous = neo.hazardous
            else:
                designation = approach.designation
                name = ""
                diameter = float("nan")
                hazardous = False

            # Write row
            writer.writerow({
                "datetime_utc": approach.time_str,
                "distance_au": approach.distance,
                "velocity_km_s": approach.velocity,
                "designation": designation,
                "name": name or "",
                "diameter_km": diameter,
                "potentially_hazardous": hazardous,
            })


def write_to_json(results, filename):
    """
    Write close approach data to a JSON file.

    Args:
        results: An iterable of CloseApproach objects
        filename: Path to the output JSON file
    """
    # Convert results to serializable format
    data = []
    for approach in results:
        # Get approach data
        approach_data = approach.serialize()

        # Get NEO data
        neo = approach.neo
        if neo:
            approach_data["neo"] = neo.serialize()
        else:
            # Create minimal NEO data if not linked
            approach_data["neo"] = {
                "designation": approach.designation,
                "name": "",
                "diameter_km": float("nan"),
                "potentially_hazardous": False,
            }

        data.append(approach_data)

    # Write to file
    with open(filename, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2)
