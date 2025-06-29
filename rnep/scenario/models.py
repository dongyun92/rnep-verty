"""
Data models for flight scenarios and paths
"""
from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator
from geojson_pydantic import LineString, Point


class ScenarioStatus(str, Enum):
    """Status of a flight scenario"""
    DRAFT = "draft"
    READY = "ready"
    EVALUATING = "evaluating"
    COMPLETED = "completed"


class Position(BaseModel):
    """3D position with latitude, longitude, and altitude"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    alt: float = Field(..., ge=0, le=10000, description="Altitude in meters")


class Waypoint(BaseModel):
    """Waypoint in a flight path"""
    id: str = Field(..., description="Unique waypoint identifier")
    sequence: int = Field(..., ge=0, description="Order in the flight path")
    position: Position
    distance_from_previous: float = Field(
        default=0.0, 
        ge=0, 
        description="Distance from previous waypoint in kilometers"
    )


class WaypointWithETA(Waypoint):
    """Waypoint with estimated time of arrival"""
    estimated_arrival_time: datetime
    speed: float = Field(default=0.0, ge=0, description="Speed in km/h")


class FlightPath(BaseModel):
    """Flight path imported from SHP file"""
    id: UUID = Field(default_factory=uuid4)
    name: str
    source_file: Optional[str] = None
    geometry: LineString
    waypoints: List[Waypoint]
    total_distance: float = Field(..., ge=0, description="Total distance in kilometers")
    imported_at: datetime = Field(default_factory=datetime.now)
    
    @validator("waypoints")
    def validate_waypoints(cls, v):
        """Ensure at least 2 waypoints exist"""
        if len(v) < 2:
            raise ValueError("Flight path must have at least 2 waypoints")
        return v


class FlightScenario(BaseModel):
    """Flight scenario combining date, time, aircraft, and path"""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    flight_date: date
    departure_time: time
    aircraft_type: str
    flight_path_id: UUID
    waypoints_with_eta: List[WaypointWithETA]
    status: ScenarioStatus = ScenarioStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator("flight_date")
    def validate_flight_date(cls, v):
        """Ensure flight date is not in the past"""
        if v < date.today():
            raise ValueError("Flight date cannot be in the past")
        return v
    
    @validator("waypoints_with_eta")
    def validate_eta_sequence(cls, v):
        """Ensure ETAs are in chronological order"""
        if len(v) < 2:
            return v
        
        for i in range(1, len(v)):
            if v[i].estimated_arrival_time <= v[i-1].estimated_arrival_time:
                raise ValueError("ETAs must be in chronological order")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class Aircraft(BaseModel):
    """Aircraft information"""
    id: str = Field(..., description="Aircraft model identifier")
    name: str
    manufacturer: str
    cruise_speed: float = Field(..., gt=0, description="Cruise speed in km/h")
    max_speed: float = Field(..., gt=0, description="Maximum speed in km/h")
    climb_rate: float = Field(..., gt=0, description="Climb rate in m/min")
    descent_rate: float = Field(..., gt=0, description="Descent rate in m/min")
    max_altitude: float = Field(..., gt=0, description="Maximum altitude in meters")
    range: float = Field(..., gt=0, description="Range in kilometers")
    noise_profile: Dict[str, float] = Field(
        default_factory=dict,
        description="Noise levels for different flight phases"
    )
    risk_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Risk-related parameters"
    )
    
    @validator("max_speed")
    def validate_speeds(cls, v, values):
        """Ensure max speed is greater than cruise speed"""
        if "cruise_speed" in values and v <= values["cruise_speed"]:
            raise ValueError("Max speed must be greater than cruise speed")
        return v


# Create/Update schemas for API
class FlightScenarioCreate(BaseModel):
    """Schema for creating a flight scenario"""
    name: str
    description: Optional[str] = None
    flight_date: date
    departure_time: time
    aircraft_type: str
    flight_path_id: UUID


class FlightScenarioUpdate(BaseModel):
    """Schema for updating a flight scenario"""
    name: Optional[str] = None
    description: Optional[str] = None
    flight_date: Optional[date] = None
    departure_time: Optional[time] = None
    aircraft_type: Optional[str] = None
    status: Optional[ScenarioStatus] = None