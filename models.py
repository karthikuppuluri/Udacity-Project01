"""
Models for representing Near-Earth Objects and Close Approaches.

This module defines the core data structures used throughout the NEO Explorer
application.
"""

from typing import Optional, List
from datetime import datetime, date
import math


class NearEarthObject:
    """
    A NearEarthObject encapsulates semantic and physical parameters about the object, such
    as its primary designation (required, unique), IAU name (optional), diameter
    in kilometers (optional), and whether it's marked as potentially hazardous.
    
    Attributes:
        designation: The primary designation of the NEO (required, unique)
        name: The IAU name of the NEO (optional)
        diameter: The NEO's diameter in kilometers (optional)
        hazardous: Whether the NEO is potentially hazardous
        approaches: A collection of this NEO's close approaches to Earth
    """
    
    def __init__(self, designation, name=None, diameter=None, hazardous=False):
        """
        Create a new NearEarthObject.
        
        Args:
            designation: The primary designation of the NEO
            name: The IAU name of the NEO (optional)
            diameter: The NEO's diameter in kilometers (optional)
            hazardous: Whether the NEO is potentially hazardous
        """
        self.designation = designation
        self.name = name
        self.diameter = diameter
        self.hazardous = hazardous
        self.approaches = []
        
        # Handle missing diameter
        if self.diameter is None:
            self.diameter = float('nan')
    
    @property
    def fullname(self):
        """Return a representation of the full name of this NEO."""
        if self.name:
            return f"{self.designation} ({self.name})"
        return self.designation
    
    def __str__(self):
        """Return a human-readable string representation."""
        if self.diameter is not None and not math.isnan(self.diameter):
            return (f"NEO {self.fullname} has a diameter of {self.diameter:.3f} km "
                   f"and {'is' if self.hazardous else 'is not'} potentially hazardous.")
        return f"NEO {self.fullname} {'is' if self.hazardous else 'is not'} potentially hazardous."
    
    def __repr__(self):
        """Return a computer-readable string representation."""
        return (f"NearEarthObject(designation={self.designation!r}, "
                f"name={self.name!r}, diameter={self.diameter}, "
                f"hazardous={self.hazardous!r})")
    
    def serialize(self):
        """Return a dictionary representation for serialization."""
        return {
            'designation': self.designation,
            'name': self.name,
            'diameter_km': self.diameter,
            'potentially_hazardous': self.hazardous
        }


class CloseApproach:
    """
    A CloseApproach encapsulates information about the NEO's close approach to
    Earth, such as the date and time (in UTC) of closest approach, the nominal
    approach distance in astronomical units, and the relative approach velocity
    in kilometers per second.
    
    Attributes:
        time: The date and time, in UTC, at which the NEO passes closest to Earth
        distance: The nominal approach distance, in astronomical units, of the NEO to Earth
        velocity: The velocity, in kilometers per second, of the NEO relative to Earth
        neo: The NearEarthObject that is making a close approach to Earth
        _designation: The primary designation of the close approach's NEO
    """
    
    def __init__(self, time, distance, velocity, designation, neo=None):
        """
        Create a new CloseApproach.
        
        Args:
            time: The datetime of closest approach
            distance: The approach distance in astronomical units
            velocity: The relative approach velocity in km/s
            designation: The primary designation of the NEO
            neo: The NearEarthObject (optional, will be set by database)
        """
        self.time = time
        self.distance = distance
        self.velocity = velocity
        self._designation = designation
        self.neo = neo
    
    @property
    def time_str(self):
        """Return a formatted string representation of the approach time."""
        return self.time.strftime("%Y-%m-%d %H:%M")
    
    @property
    def date(self):
        """Return the date of the close approach."""
        return self.time.date()
    
    def __str__(self):
        """Return a human-readable string representation."""
        neo_name = self.neo.fullname if self.neo else f"'{self._designation}'"
        return (f"On {self.time_str}, {neo_name} approaches Earth at a distance of "
                f"{self.distance:.2f} au and a velocity of {self.velocity:.2f} km/s.")
    
    def __repr__(self):
        """Return a computer-readable string representation."""
        return (f"CloseApproach(time={self.time_str!r}, distance={self.distance:.2f}, "
                f"velocity={self.velocity:.2f}, neo={self.neo!r})")
    
    def serialize(self):
        """Return a dictionary representation for serialization."""
        return {
            'datetime_utc': self.time_str,
            'distance_au': self.distance,
            'velocity_km_s': self.velocity
        } 