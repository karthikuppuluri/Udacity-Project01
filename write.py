"""
Write results to files.

This module provides functions to write close approach results to CSV and JSON files.
"""

import csv
import json
from pathlib import Path
from typing import Iterator

from models import CloseApproach
from helpers import datetime_to_str


def write_to_csv(results, filename):
    """
    Write a stream of CloseApproach objects to a CSV file.
    
    Args:
        results: A stream of CloseApproach objects
        filename: The name of the output CSV file
    """
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        
        # Write header
        writer.writerow([
            'datetime_utc',
            'distance_au',
            'velocity_km_s',
            'designation',
            'name',
            'diameter_km',
            'potentially_hazardous'
        ])
        
        # Write data rows
        for approach in results:
            # Use serialize method for consistent handling of edge cases
            approach_data = approach.serialize()
            neo_data = approach.neo.serialize() if approach.neo else {
                'designation': approach._designation,
                'name': '',
                'diameter_km': '',
                'potentially_hazardous': False
            }
            
            writer.writerow([
                approach_data['datetime_utc'],
                approach_data['distance_au'],
                approach_data['velocity_km_s'],
                neo_data['designation'],
                neo_data['name'],
                neo_data['diameter_km'],
                neo_data['potentially_hazardous']
            ])


def write_to_json(results, filename):
    """
    Write a stream of CloseApproach objects to a JSON file.
    
    Args:
        results: A stream of CloseApproach objects
        filename: The name of the output JSON file
    """
    data = []
    
    for approach in results:
        # Use serialize method for consistent handling of edge cases
        approach_data = approach.serialize()
        neo_data = approach.neo.serialize() if approach.neo else {
            'designation': approach._designation,
            'name': '',
            'diameter_km': float('nan'),
            'potentially_hazardous': False
        }
        
        entry = {
            "datetime_utc": approach_data['datetime_utc'],
            "distance_au": approach_data['distance_au'],
            "velocity_km_s": approach_data['velocity_km_s'],
            "neo": neo_data
        }
        
        data.append(entry)
    
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2) 