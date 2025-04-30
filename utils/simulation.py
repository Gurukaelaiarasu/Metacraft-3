import numpy as np

def generate_structure_parameters(structure_type, wavelength_range, **kwargs):
    """
    Organize structure parameters for simulation.
    
    Args:
        structure_type (str): Type of the structure to be simulated
        wavelength_range (np.ndarray): Array of wavelengths in nm
        **kwargs: Additional structure-specific parameters
        
    Returns:
        dict: Dictionary containing all structure parameters in a standardized format
    """
    # Start with the basic parameters that all structures have
    structure_params = {
        'structure_type': structure_type,
        'wavelength_range': wavelength_range,
    }
    
    # Add environment parameters
    environment_material = kwargs.get('environment_material', 'Air')
    structure_params['environment_material'] = environment_material
    
    if environment_material == 'Custom':
        env_refractive_index = kwargs.get('env_refractive_index', 1.0)
        structure_params['env_refractive_index'] = env_refractive_index
    
    # Add structure-specific parameters
    if structure_type == "Metamaterial Thin Film":
        structure_params.update({
            'num_layers': kwargs.get('num_layers', 5),
            'layer_thickness': kwargs.get('layer_thickness', 50),
            'primary_material': kwargs.get('primary_material', 'Gold'),
            'secondary_material': kwargs.get('secondary_material', 'Titanium Dioxide'),
            'layers': kwargs.get('layers', [])
        })
    
    elif structure_type == "Photonic Crystal":
        structure_params['crystal_dimension'] = kwargs.get('crystal_dimension', '1D')
        
        if structure_params['crystal_dimension'] == '1D':
            structure_params.update({
                'periodicity': kwargs.get('periodicity', 300),
                'duty_cycle': kwargs.get('duty_cycle', 0.5),
                'num_periods': kwargs.get('num_periods', 10),
                'primary_material': kwargs.get('primary_material', 'Silicon'),
                'secondary_material': kwargs.get('secondary_material', 'Silicon Dioxide')
            })
        
        elif structure_params['crystal_dimension'] == '2D':
            structure_params.update({
                'lattice_type': kwargs.get('lattice_type', 'Square'),
                'lattice_constant': kwargs.get('lattice_constant', 300),
                'hole_radius': kwargs.get('hole_radius', 100),
                'primary_material': kwargs.get('primary_material', 'Silicon'),
                'secondary_material': kwargs.get('secondary_material', 'Air')
            })
        
        else:  # 3D
            structure_params.update({
                'crystal_type': kwargs.get('crystal_type', 'FCC'),
                'lattice_constant': kwargs.get('lattice_constant', 300),
                'primary_material': kwargs.get('primary_material', 'Silicon'),
                'secondary_material': kwargs.get('secondary_material', 'Air')
            })
    
    elif structure_type in ["Metal-Insulator-Metal (MIM)", "Insulator-Metal-Insulator (IMI)"]:
        structure_params.update({
            'top_layer_thickness': kwargs.get('top_layer_thickness', 20),
            'middle_layer_thickness': kwargs.get('middle_layer_thickness', 100),
            'bottom_layer_thickness': kwargs.get('bottom_layer_thickness', 20),
            'metal_material': kwargs.get('metal_material', 'Gold'),
            'insulator_material': kwargs.get('insulator_material', 'Silicon Dioxide'),
            'include_patterns': kwargs.get('include_patterns', False)
        })
        
        if structure_params['include_patterns']:
            structure_params.update({
                'pattern_type': kwargs.get('pattern_type', 'Hole Array'),
                'pattern_period': kwargs.get('pattern_period', 200),
                'pattern_size': kwargs.get('pattern_size', 100)
            })
    
    elif "Pattern" in structure_type:
        structure_params.update({
            'dimension': '3D' if structure_type == "3D Pattern" else '2D',
            'pattern_type': kwargs.get('pattern_type', 'Hole Array' if structure_type == "2D Pattern" else 'Cubic'),
            'substrate_thickness': kwargs.get('substrate_thickness', 200),
            'pattern_periodicity': kwargs.get('pattern_periodicity', 200),
            'pattern_height': kwargs.get('pattern_height', 100),
            'pattern_width': kwargs.get('pattern_width', 100),
            'substrate_material': kwargs.get('substrate_material', 'Silicon'),
            'pattern_material': kwargs.get('pattern_material', 'Gold')
        })
        
        if structure_params['dimension'] == '3D':
            structure_params['pattern_depth'] = kwargs.get('pattern_depth', 100)
    
    elif structure_type == "Nanoparticle":
        structure_params.update({
            'particle_shape': kwargs.get('particle_shape', 'Sphere'),
            'particle_material': kwargs.get('particle_material', 'Gold'),
            'include_substrate': kwargs.get('include_substrate', False)
        })
        
        if structure_params['particle_shape'] == 'Sphere':
            structure_params['particle_radius'] = kwargs.get('particle_radius', 50)
        
        elif structure_params['particle_shape'] == 'Cube':
            structure_params['particle_side'] = kwargs.get('particle_side', 50)
        
        elif structure_params['particle_shape'] == 'Rod':
            structure_params.update({
                'particle_length': kwargs.get('particle_length', 100),
                'particle_diameter': kwargs.get('particle_diameter', 30)
            })
        
        elif structure_params['particle_shape'] == 'Disk':
            structure_params.update({
                'particle_radius': kwargs.get('particle_radius', 50),
                'particle_height': kwargs.get('particle_height', 20)
            })
        
        elif structure_params['particle_shape'] == 'Core-Shell':
            structure_params.update({
                'core_material': kwargs.get('core_material', 'Gold'),
                'shell_material': kwargs.get('shell_material', 'Silicon Dioxide'),
                'core_radius': kwargs.get('core_radius', 30),
                'shell_thickness': kwargs.get('shell_thickness', 10)
            })
        
        if structure_params['include_substrate']:
            structure_params.update({
                'substrate_thickness': kwargs.get('substrate_thickness', 200),
                'substrate_material': kwargs.get('substrate_material', 'Silicon Dioxide')
            })
    
    return structure_params
