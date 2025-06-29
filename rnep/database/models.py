"""
SQLAlchemy database models
"""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Date, Time, 
    Text, JSON, Enum, ForeignKey, Boolean, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from rnep.database.base import Base
from rnep.scenario.models import ScenarioStatus


class Aircraft(Base):
    """Aircraft model"""
    __tablename__ = "aircraft"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    manufacturer = Column(String(255), nullable=False)
    cruise_speed = Column(Float, nullable=False)
    max_speed = Column(Float, nullable=False)
    climb_rate = Column(Float, nullable=False)
    descent_rate = Column(Float, nullable=False)
    max_altitude = Column(Float)
    range = Column(Float)
    noise_profile = Column(JSON, default={})
    risk_parameters = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scenarios = relationship("FlightScenario", back_populates="aircraft")


class FlightPath(Base):
    """Flight path model"""
    __tablename__ = "flight_paths"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    source_file = Column(String(500))
    geometry = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    waypoints = Column(JSON, nullable=False)
    total_distance = Column(Float, nullable=False)
    imported_at = Column(DateTime, default=datetime.utcnow)
    imported_by = Column(String(255))
    
    # Indexes
    __table_args__ = (
        Index('idx_flight_paths_geometry', 'geometry', postgresql_using='gist'),
    )
    
    # Relationships
    scenarios = relationship("FlightScenario", back_populates="flight_path")


class FlightScenario(Base):
    """Flight scenario model"""
    __tablename__ = "flight_scenarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    flight_date = Column(Date, nullable=False)
    departure_time = Column(Time, nullable=False)
    aircraft_id = Column(String(50), ForeignKey("aircraft.id"), nullable=False)
    flight_path_id = Column(UUID(as_uuid=True), ForeignKey("flight_paths.id"), nullable=False)
    waypoints_with_eta = Column(JSON, nullable=False)
    status = Column(Enum(ScenarioStatus), default=ScenarioStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Indexes
    __table_args__ = (
        Index('idx_scenarios_status', 'status'),
        Index('idx_scenarios_flight_date', 'flight_date'),
    )
    
    # Relationships
    aircraft = relationship("Aircraft", back_populates="scenarios")
    flight_path = relationship("FlightPath", back_populates="scenarios")
    evaluation_requests = relationship("EvaluationRequest", back_populates="scenario")


class EvaluationRequest(Base):
    """Evaluation request model"""
    __tablename__ = "evaluation_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("flight_scenarios.id"), nullable=False)
    evaluation_types = Column(JSON, nullable=False)  # ["ground_risk", "air_risk", "noise"]
    requested_at = Column(DateTime, default=datetime.utcnow)
    requested_by = Column(String(255))
    status = Column(String(20), default="pending", nullable=False)
    progress = Column(Integer, default=0)
    results = Column(JSON, default={})
    error_message = Column(Text)
    completed_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_requests_status', 'status'),
        Index('idx_requests_scenario', 'scenario_id'),
    )
    
    # Relationships
    scenario = relationship("FlightScenario", back_populates="evaluation_requests")
    evaluation_results = relationship("EvaluationResult", back_populates="request")


class EvaluationResult(Base):
    """Evaluation result model"""
    __tablename__ = "evaluation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    evaluation_request_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("evaluation_requests.id"), 
        nullable=False
    )
    evaluation_type = Column(String(20), nullable=False)
    algorithm_version = Column(String(50))
    input_data = Column(JSON)
    output_data = Column(JSON, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_results_request', 'evaluation_request_id'),
        Index('idx_results_type', 'evaluation_type'),
    )
    
    # Relationships
    request = relationship("EvaluationRequest", back_populates="evaluation_results")


# Import all models to ensure they are registered with Base
__all__ = [
    "Aircraft",
    "FlightPath", 
    "FlightScenario",
    "EvaluationRequest",
    "EvaluationResult"
]