"""
Core data models for Near-Earth Objects and Close Approaches.

This module defines the fundamental data structures used throughout the NEO Explorer
application, with improved type safety, validation, and error handling.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
import math
from dataclasses import dataclass, field
from enum import Enum


class HazardLevel(Enum):
    """Enumeration for NEO hazard levels."""
    SAFE = "safe"
    POTENTIALLY_HAZARDOUS = "hazardous"
    UNKNOWN = "unknown"


@dataclass
class NearEarthObject:
    """    
    An NEO encapsulates semantic and physical parameters about the object, such
    as its primary designation (required, unique), IAU name (optional), diameter
    in kilometers (optional), and whether it's marked as potentially hazardous.
    
    Attributes:
        designation: The primary designation of the NEO (required, unique)
        name: The IAU name of the NEO (optional)
        diameter: The NEO's diameter in kilometers (optional)
        hazardous: Whether the NEO is potentially hazardous
        approaches: Collection of close approaches (populated by database)
    """
    
    designation: str
    name: Optional[str] = None
    diameter: Optional[float] = None
    hazardous: bool = False
    approaches: List['CloseApproach'] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate the NEO data after initialization."""
        if not self.designation or not self.designation.strip():
            raise ValueError("NEO designation cannot be empty")
        
        self.designation = self.designation.strip().upper()
        
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                self.name = None
        
        if self.diameter is not None:
            if self.diameter < 0:
                raise ValueError("NEO diameter cannot be negative")
            if math.isnan(self.diameter):
                self.diameter = None
    
    @property
    def fullname(self) -> str:
        """Return a representation of the full name of this NEO."""
        if self.name:
            return f"{self.designation} ({self.name})"
        return self.designation
    
    @property
    def hazard_level(self) -> HazardLevel:
        """Return the hazard level of this NEO."""
        if self.hazardous:
            return HazardLevel.POTENTIALLY_HAZARDOUS
        return HazardLevel.SAFE
    
    @property
    def has_diameter(self) -> bool:
        """Check if this NEO has a known diameter."""
        return self.diameter is not None and not math.isnan(self.diameter)
    
    def __str__(self) -> str:
        """Return a human-readable string representation."""
        if self.has_diameter:
            return (f"NEO {self.fullname} has a diameter of {self.diameter:.3f} km "
                   f"and {'is' if self.hazardous else 'is not'} potentially hazardous.")
        return f"NEO {self.fullname} {'is' if self.hazardous else 'is not'} potentially hazardous."
    
    def __repr__(self) -> str:
        """Return a computer-readable string representation."""
        return (f"NearEarthObject(designation={self.designation!r}, "
                f"name={self.name!r}, diameter={self.diameter}, "
                f"hazardous={self.hazardous!r})")
    
    def serialize(self) -> Dict[str, Any]:
        """Return a dictionary representation for serialization."""
        return {
            "designation": self.designation,
            "name": self.name,
            "diameter_km": self.diameter,
            "potentially_hazardous": self.hazardous,
            "hazard_level": self.hazard_level.value
        }


@dataclass
class CloseApproach:
    """    
    A Close Approach encapsulates information about the NEO's close approach to
    Earth, such as the date and time (in UTC) of closest approach, the nominal
    approach distance in astronomical units, and the relative approach velocity
    in kilometers per second.
    
    Attributes:
        designation: The primary designation of the NEO
        time: The datetime of closest approach
        distance: The approach distance in astronomical units
        velocity: The relative approach velocity in km/s
        neo: Reference to the associated NEO (set by database)
    """
    
    designation: str
    time: datetime
    distance: float
    velocity: float
    neo: Optional[NearEarthObject] = None
    
    def __post_init__(self):
        """Validate the close approach data after initialization."""
        if not self.designation or not self.designation.strip():
            raise ValueError("Close approach designation cannot be empty")
        
        self.designation = self.designation.strip().upper()
        
        if not isinstance(self.time, datetime):
            raise TypeError("Time must be a datetime object")
        
        if not isinstance(self.distance, (int, float)) or math.isnan(self.distance):
            raise ValueError("Distance must be a valid number")
        
        if not isinstance(self.velocity, (int, float)) or math.isnan(self.velocity):
            raise ValueError("Velocity must be a valid number")
    
    @property
    def time_str(self) -> str:
        """Return a formatted string representation of the approach time."""
        return self.time.strftime("%Y-%m-%d %H:%M")
    
    @property
    def date(self) -> date:
        """Return the date of the close approach."""
        return self.time.date()
    
    @property
    def distance_au(self) -> float:
        """Return the approach distance in astronomical units."""
        return self.distance
    
    @property
    def velocity_km_s(self) -> float:
        """Return the approach velocity in kilometers per second."""
        return self.velocity
    
    def __str__(self) -> str:
        """Return a human-readable string representation."""
        neo_name = self.neo.fullname if self.neo else f"'{self.designation}'"
        return (f"At {self.time_str}, {neo_name} approaches Earth at a distance of "
                f"{self.distance:.2f} au and a velocity of {self.velocity:.2f} km/s.")
    
    def __repr__(self) -> str:
        """Return a computer-readable string representation."""
        return (f"CloseApproach(time={self.time_str!r}, distance={self.distance:.2f}, "
                f"velocity={self.velocity:.2f}, neo={self.neo!r})")
    
    def serialize(self) -> Dict[str, Any]:
        """Return a dictionary representation for serialization."""
        return {
            "datetime_utc": self.time_str,
            "distance_au": self.distance,
            "velocity_km_s": self.velocity,
            "neo_designation": self.designation,
            "neo_name": self.neo.name if self.neo else None,
            "neo_diameter_km": self.neo.diameter if self.neo else None,
            "neo_potentially_hazardous": self.neo.hazardous if self.neo else None
        } 