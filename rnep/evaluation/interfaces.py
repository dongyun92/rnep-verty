"""
Algorithm interfaces for evaluation modules

This module defines abstract base classes that all evaluation algorithms
must implement. Actual implementations will be provided by external organizations
(UNIST, Konkuk University, etc.) and integrated via adapters.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel


class AlgorithmMetadata(BaseModel):
    """Metadata about an algorithm"""
    name: str
    version: str
    organization: str
    description: str
    supported_evaluation_types: List[str]
    required_inputs: List[str]
    optional_inputs: List[str]


class EvaluationInput(BaseModel):
    """Standard input format for evaluation algorithms"""
    scenario_id: str
    flight_date: datetime
    waypoints_with_eta: List[Dict[str, Any]]
    aircraft_data: Dict[str, Any]
    environment_data: Optional[Dict[str, Any]] = None
    additional_params: Optional[Dict[str, Any]] = None


class EvaluationOutput(BaseModel):
    """Standard output format for evaluation algorithms"""
    evaluation_type: str
    algorithm_metadata: AlgorithmMetadata
    summary: Dict[str, Any]
    detailed_results: Dict[str, Any]
    output_files: List[Dict[str, str]]  # {"type": "shapefile", "path": "/path/to/file"}
    processing_time: float  # seconds
    timestamp: datetime


class AlgorithmInterface(ABC):
    """
    Abstract base class for all evaluation algorithms.
    
    All evaluation algorithms (risk assessment, noise evaluation, etc.)
    must implement this interface to be compatible with RNEP.
    """
    
    @abstractmethod
    def get_metadata(self) -> AlgorithmMetadata:
        """
        Get algorithm metadata including version, requirements, etc.
        
        Returns:
            AlgorithmMetadata: Algorithm metadata
        """
        pass
    
    @abstractmethod
    def validate_input(self, data: EvaluationInput) -> bool:
        """
        Validate that input data meets algorithm requirements.
        
        Args:
            data: Input data to validate
            
        Returns:
            bool: True if valid, raises exception if invalid
            
        Raises:
            ValueError: If input data is invalid
        """
        pass
    
    @abstractmethod
    def execute(self, data: EvaluationInput) -> EvaluationOutput:
        """
        Execute the evaluation algorithm.
        
        Args:
            data: Input data for evaluation
            
        Returns:
            EvaluationOutput: Evaluation results
            
        Raises:
            Exception: If evaluation fails
        """
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get the schema for output data.
        
        This helps RNEP understand what kind of output to expect
        and how to process it for QGIS visualization.
        
        Returns:
            Dict: JSON Schema for output data
        """
        pass


class RiskAssessmentInterface(AlgorithmInterface):
    """Specific interface for risk assessment algorithms"""
    
    @abstractmethod
    def calculate_ground_risk(self, data: EvaluationInput) -> Dict[str, Any]:
        """Calculate ground risk for the flight scenario"""
        pass
    
    @abstractmethod
    def calculate_air_risk(self, data: EvaluationInput) -> Dict[str, Any]:
        """Calculate air risk for the flight scenario"""
        pass


class NoiseAssessmentInterface(AlgorithmInterface):
    """Specific interface for noise assessment algorithms"""
    
    @abstractmethod
    def calculate_noise_contours(self, data: EvaluationInput, 
                               levels: List[float]) -> Dict[str, Any]:
        """Calculate noise contours for specified dB levels"""
        pass
    
    @abstractmethod
    def calculate_noise_impact(self, data: EvaluationInput) -> Dict[str, Any]:
        """Calculate overall noise impact metrics"""
        pass


# Example of how external organizations would implement these interfaces:
"""
class UNISTGroundRiskAdapter(RiskAssessmentInterface):
    # UNIST would implement this
    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="UNIST Ground Risk Assessment",
            version="1.0.0",
            organization="UNIST",
            description="Ground risk assessment for UAM operations",
            supported_evaluation_types=["ground_risk"],
            required_inputs=["waypoints", "aircraft_data", "population_density"],
            optional_inputs=["weather_data", "building_data"]
        )
    
    def execute(self, data: EvaluationInput) -> EvaluationOutput:
        # Actual implementation would go here
        pass

class KonkukNoiseAdapter(NoiseAssessmentInterface):
    # Konkuk University would implement this
    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="Konkuk Noise Assessment",
            version="1.0.0",
            organization="Konkuk University",
            description="Noise assessment for UAM operations",
            supported_evaluation_types=["noise"],
            required_inputs=["waypoints", "aircraft_noise_profile"],
            optional_inputs=["weather_data", "terrain_data"]
        )
    
    def execute(self, data: EvaluationInput) -> EvaluationOutput:
        # Actual implementation would go here
        pass
"""