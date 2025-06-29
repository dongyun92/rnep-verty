"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create PostGIS extension if not exists
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create aircraft table
    op.create_table('aircraft',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('manufacturer', sa.String(255), nullable=False),
        sa.Column('cruise_speed', sa.Float(), nullable=False),
        sa.Column('max_speed', sa.Float(), nullable=False),
        sa.Column('climb_rate', sa.Float(), nullable=False),
        sa.Column('descent_rate', sa.Float(), nullable=False),
        sa.Column('max_altitude', sa.Float(), nullable=True),
        sa.Column('range', sa.Float(), nullable=True),
        sa.Column('noise_profile', sa.JSON(), nullable=True),
        sa.Column('risk_parameters', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create flight_paths table
    op.create_table('flight_paths',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('source_file', sa.String(500), nullable=True),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326), nullable=False),
        sa.Column('waypoints', sa.JSON(), nullable=False),
        sa.Column('total_distance', sa.Float(), nullable=False),
        sa.Column('imported_at', sa.DateTime(), nullable=True),
        sa.Column('imported_by', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_flight_paths_geometry', 'flight_paths', ['geometry'], postgresql_using='gist')
    
    # Create flight_scenarios table
    op.create_table('flight_scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('flight_date', sa.Date(), nullable=False),
        sa.Column('departure_time', sa.Time(), nullable=False),
        sa.Column('aircraft_id', sa.String(50), nullable=False),
        sa.Column('flight_path_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('waypoints_with_eta', sa.JSON(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'ready', 'evaluating', 'completed', name='scenariostatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['aircraft_id'], ['aircraft.id'], ),
        sa.ForeignKeyConstraint(['flight_path_id'], ['flight_paths.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scenarios_flight_date', 'flight_scenarios', ['flight_date'])
    op.create_index('idx_scenarios_status', 'flight_scenarios', ['status'])
    
    # Create evaluation_requests table
    op.create_table('evaluation_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_types', sa.JSON(), nullable=False),
        sa.Column('requested_at', sa.DateTime(), nullable=True),
        sa.Column('requested_by', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['scenario_id'], ['flight_scenarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_requests_scenario', 'evaluation_requests', ['scenario_id'])
    op.create_index('idx_requests_status', 'evaluation_requests', ['status'])
    
    # Create evaluation_results table
    op.create_table('evaluation_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_type', sa.String(20), nullable=False),
        sa.Column('algorithm_version', sa.String(50), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['evaluation_request_id'], ['evaluation_requests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_results_request', 'evaluation_results', ['evaluation_request_id'])
    op.create_index('idx_results_type', 'evaluation_results', ['evaluation_type'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_results_type', table_name='evaluation_results')
    op.drop_index('idx_results_request', table_name='evaluation_results')
    op.drop_table('evaluation_results')
    
    op.drop_index('idx_requests_status', table_name='evaluation_requests')
    op.drop_index('idx_requests_scenario', table_name='evaluation_requests')
    op.drop_table('evaluation_requests')
    
    op.drop_index('idx_scenarios_status', table_name='flight_scenarios')
    op.drop_index('idx_scenarios_flight_date', table_name='flight_scenarios')
    op.drop_table('flight_scenarios')
    
    op.drop_index('idx_flight_paths_geometry', table_name='flight_paths', postgresql_using='gist')
    op.drop_table('flight_paths')
    
    op.drop_table('aircraft')
    
    # Drop enum
    op.execute('DROP TYPE IF EXISTS scenariostatus')