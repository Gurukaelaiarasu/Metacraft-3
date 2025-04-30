import os
import json
import datetime
import numpy as np
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, Boolean, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Get the database connection string from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class SimulationConfig(Base):
    """
    Model to store simulation configurations.
    """
    __tablename__ = 'simulation_configs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    structure_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    parameters = Column(JSON, nullable=False)  # Store all parameters as JSON
    
    # Relationship with results
    results = relationship("SimulationResult", back_populates="config", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SimulationConfig(id={self.id}, name='{self.name}', structure_type='{self.structure_type}')>"

class SimulationResult(Base):
    """
    Model to store simulation results.
    """
    __tablename__ = 'simulation_results'
    
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey('simulation_configs.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    wavelength_min = Column(Float, nullable=False)
    wavelength_max = Column(Float, nullable=False)
    wavelength_steps = Column(Integer, nullable=False)
    
    # Store the main spectral results as arrays in JSON format
    reflectance = Column(Text, nullable=False)  # JSON serialized array
    transmittance = Column(Text, nullable=False)  # JSON serialized array
    absorption = Column(Text, nullable=False)  # JSON serialized array
    
    # Store metadata about field distributions and refractive index
    field_distributions_available = Column(Boolean, default=False)
    refractive_index_available = Column(Boolean, default=False)
    
    # Relationship with config
    config = relationship("SimulationConfig", back_populates="results")
    
    def __repr__(self):
        return f"<SimulationResult(id={self.id}, config_id={self.config_id})>"

# Create all tables
def setup_database():
    """Initialize the database tables."""
    Base.metadata.create_all(engine)

# Database operations for simulation configurations
def save_simulation_config(name, structure_params):
    """
    Save a simulation configuration to the database.
    
    Args:
        name (str): Name of the configuration
        structure_params (dict): Dictionary containing structure parameters
        
    Returns:
        SimulationConfig: The created configuration object
    """
    # Extract structure type
    structure_type = structure_params.get('structure_type', 'Unknown')
    
    # Create a new session
    session = Session()
    
    try:
        # Create a new simulation config
        config = SimulationConfig(
            name=name,
            structure_type=structure_type,
            parameters=structure_params
        )
        
        # Add to session and commit
        session.add(config)
        session.commit()
        
        return config
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_simulation_configs():
    """
    Get all saved simulation configurations.
    
    Returns:
        list: List of SimulationConfig objects
    """
    session = Session()
    try:
        configs = session.query(SimulationConfig).order_by(SimulationConfig.created_at.desc()).all()
        return configs
    finally:
        session.close()

def get_simulation_config(config_id):
    """
    Get a specific simulation configuration by ID.
    
    Args:
        config_id (int): ID of the configuration to retrieve
        
    Returns:
        SimulationConfig: The requested configuration or None if not found
    """
    session = Session()
    try:
        config = session.query(SimulationConfig).filter_by(id=config_id).first()
        return config
    finally:
        session.close()

def delete_simulation_config(config_id):
    """
    Delete a simulation configuration and its results.
    
    Args:
        config_id (int): ID of the configuration to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = Session()
    try:
        config = session.query(SimulationConfig).filter_by(id=config_id).first()
        if config:
            session.delete(config)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()

# Database operations for simulation results
def save_simulation_result(config_id, results, wavelength_range):
    """
    Save simulation results to the database.
    
    Args:
        config_id (int): ID of the associated configuration
        results (dict): Dictionary containing simulation results
        wavelength_range (np.ndarray): Array of wavelengths
        
    Returns:
        SimulationResult: The created result object
    """
    # Create a new session
    session = Session()
    
    try:
        # Convert numpy arrays to JSON serializable lists
        reflectance_json = json.dumps(results['reflectance'].tolist())
        transmittance_json = json.dumps(results['transmittance'].tolist())
        absorption_json = json.dumps(results['absorption'].tolist())
        
        # Create a new simulation result
        result = SimulationResult(
            config_id=config_id,
            wavelength_min=float(min(wavelength_range)),
            wavelength_max=float(max(wavelength_range)),
            wavelength_steps=len(wavelength_range),
            reflectance=reflectance_json,
            transmittance=transmittance_json,
            absorption=absorption_json,
            field_distributions_available='electric_field_2d' in results,
            refractive_index_available='refractive_index_real' in results
        )
        
        # Add to session and commit
        session.add(result)
        session.commit()
        
        return result
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_simulation_results(config_id):
    """
    Get all simulation results for a specific configuration.
    
    Args:
        config_id (int): ID of the configuration
        
    Returns:
        list: List of SimulationResult objects
    """
    session = Session()
    try:
        results = session.query(SimulationResult).filter_by(config_id=config_id).order_by(SimulationResult.created_at.desc()).all()
        return results
    finally:
        session.close()

def get_simulation_result(result_id):
    """
    Get a specific simulation result by ID.
    
    Args:
        result_id (int): ID of the result to retrieve
        
    Returns:
        SimulationResult: The requested result or None if not found
    """
    session = Session()
    try:
        result = session.query(SimulationResult).filter_by(id=result_id).first()
        return result
    finally:
        session.close()

def delete_simulation_result(result_id):
    """
    Delete a simulation result.
    
    Args:
        result_id (int): ID of the result to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = Session()
    try:
        result = session.query(SimulationResult).filter_by(id=result_id).first()
        if result:
            session.delete(result)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()

# Function to convert database result back to simulation format
def convert_result_to_simulation_format(result, wavelength_range=None):
    """
    Convert a database result back to the simulation format for visualization.
    
    Args:
        result (SimulationResult): The database result object
        wavelength_range (np.ndarray, optional): Array of wavelengths if different from stored range
        
    Returns:
        dict: Dictionary containing simulation results in the format expected by visualization functions
    """
    # If no wavelength range is provided, create one from the database values
    if wavelength_range is None:
        wavelength_range = np.linspace(result.wavelength_min, result.wavelength_max, result.wavelength_steps)
    
    # Convert JSON strings back to numpy arrays
    reflectance = np.array(json.loads(result.reflectance))
    transmittance = np.array(json.loads(result.transmittance))
    absorption = np.array(json.loads(result.absorption))
    
    # Create a minimal simulation result that works with visualization
    simulation_result = {
        'reflectance': reflectance,
        'transmittance': transmittance,
        'absorption': absorption,
        # Add placeholder values for other fields that might be used by visualization
        'refractive_index_real': np.ones_like(reflectance),
        'refractive_index_imag': np.ones_like(reflectance),
    }
    
    return simulation_result

# Initialize the database when this module is imported
setup_database()