"""
Extract data from structured files into Python objects.

This module provides functions to load NEO and close approach data from CSV and JSON files.
"""

import csv
import json
from pathlib import Path
from typing import List

from models import NearEarthObject, CloseApproach
from helpers import cd_to_datetime


def load_neos(neo_csv_path):
    """
    Load near-Earth object data from a CSV file.
    
    Args:
        neo_csv_path: Path to the CSV file containing NEO data.
    
    Returns:
        A collection of NearEarthObject instances.
    """
    neos = []
    
    with open(neo_csv_path, 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Extract data from CSV row
            designation = row.get('pdes', '').strip()
            name = row.get('name', '').strip()
            diameter_str = row.get('diameter', '').strip()
            hazardous_str = row.get('pha', '').strip()
            
            # Handle missing or empty values
            if not designation:
                continue
                
            if not name:
                name = None
                
            # Parse diameter
            diameter = None
            if diameter_str and diameter_str != '':
                try:
                    diameter = float(diameter_str)
                except ValueError:
                    diameter = None
            
            # Parse hazardous flag
            hazardous = hazardous_str.lower() == 'y'
            
            # Create NEO object
            neo = NearEarthObject(
                designation=designation,
                name=name,
                diameter=diameter,
                hazardous=hazardous
            )
            
            neos.append(neo)
    
    return neos


def load_approaches(cad_json_path):
    """
    Load close approach data from a JSON file.
    
    Args:
        cad_json_path: Path to the JSON file containing close approach data.
    
    Returns:
        A collection of CloseApproach instances.
    """
    approaches = []
    
    with open(cad_json_path, 'r') as file:
        data = json.load(file)
        
        for item in data['data']:
            # Extract data from JSON item
            designation = item[0].strip()
            time_str = item[3].strip()
            distance_str = item[4].strip()
            velocity_str = item[7].strip()
            
            # Handle missing or empty values
            if not designation or not time_str or not distance_str or not velocity_str:
                continue
            
            try:
                # Parse datetime
                time = cd_to_datetime(time_str)
                
                # Parse distance and velocity
                distance = float(distance_str)
                velocity = float(velocity_str)
                
                # Create close approach object
                approach = CloseApproach(
                    time=time,
                    distance=distance,
                    velocity=velocity,
                    designation=designation
                )
                
                approaches.append(approach)
                
            except (ValueError, TypeError) as e:
                # Skip invalid entries
                continue
    
    return approaches 