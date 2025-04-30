import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_reflectance_transmittance_absorption(results, wavelength_range):
    """
    Plot reflectance, transmittance, and absorption spectra.
    
    Args:
        results (dict): Dictionary containing simulation results
        wavelength_range (np.ndarray): Array of wavelengths in nm
        
    Returns:
        go.Figure: Plotly figure object containing the spectra
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=wavelength_range,
        y=results['reflectance'],
        mode='lines',
        name='Reflectance',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=wavelength_range,
        y=results['transmittance'],
        mode='lines',
        name='Transmittance',
        line=dict(color='green', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=wavelength_range,
        y=results['absorption'],
        mode='lines',
        name='Absorption',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title="Optical Spectra",
        xaxis_title="Wavelength (nm)",
        yaxis_title="Intensity",
        legend_title="Spectrum",
        template="plotly_white",
        yaxis=dict(range=[0, 1])
    )
    
    return fig

def plot_field_distribution(results, wavelength_range, selected_wavelength, field_type, view_dimension):
    """
    Plot electric or magnetic field distribution.
    
    Args:
        results (dict): Dictionary containing simulation results
        wavelength_range (np.ndarray): Array of wavelengths in nm
        selected_wavelength (float): Selected wavelength for visualization
        field_type (str): Either "Electric Field" or "Magnetic Field"
        view_dimension (str): Either "2D Cross-section" or "3D Volume"
        
    Returns:
        go.Figure: Plotly figure object containing the field distribution
    """
    # Find the closest wavelength in our data
    closest_idx = np.abs(wavelength_range - selected_wavelength).argmin()
    closest_wavelength = wavelength_range[closest_idx]
    
    # Select the appropriate field data
    if field_type == "Electric Field":
        if view_dimension == "2D Cross-section":
            field_key = 'electric_field_2d'
        else:  # 3D Volume
            field_key = 'electric_field_3d'
    else:  # Magnetic Field
        if view_dimension == "2D Cross-section":
            field_key = 'magnetic_field_2d'
        else:  # 3D Volume
            field_key = 'magnetic_field_3d'
    
    # Get the field data for the selected wavelength
    # We might not have data for every wavelength in our simulation
    available_wavelengths = list(results[field_key].keys())
    closest_available = min(available_wavelengths, key=lambda x: abs(x - selected_wavelength))
    field_data = results[field_key][closest_available]
    
    # For 2D visualization
    if view_dimension == "2D Cross-section":
        # Create a heatmap
        fig = go.Figure(data=go.Heatmap(
            z=field_data,
            x=results['x_grid'],
            y=results['y_grid'],
            colorscale='Viridis',
            colorbar=dict(title="Field Intensity")
        ))
        
        fig.update_layout(
            title=f"{field_type} Distribution at λ = {closest_available:.1f} nm",
            xaxis_title="x (μm)",
            yaxis_title="y (μm)",
            template="plotly_white"
        )
        
    else:  # 3D Volume
        # We'll use a slice to visualize the 3D volume
        # In a real implementation, this could be more sophisticated
        z_slice_idx = field_data.shape[2] // 2  # Middle slice
        
        fig = go.Figure(data=go.Surface(
            z=z_slice_idx * np.ones_like(field_data[:, :, z_slice_idx]),
            x=np.tile(results['x_grid'], (len(results['y_grid']), 1)),
            y=np.tile(results['y_grid'], (len(results['x_grid']), 1)).T,
            surfacecolor=field_data[:, :, z_slice_idx],
            colorscale='Viridis',
            colorbar=dict(title="Field Intensity")
        ))
        
        fig.update_layout(
            title=f"3D {field_type} Distribution at λ = {closest_available:.1f} nm (z-slice)",
            scene=dict(
                xaxis_title="x (μm)",
                yaxis_title="y (μm)",
                zaxis_title="z (μm)"
            ),
            template="plotly_white"
        )
    
    return fig

def plot_refractive_index(results, wavelength_range):
    """
    Plot real and imaginary parts of the effective refractive index.
    
    Args:
        results (dict): Dictionary containing simulation results
        wavelength_range (np.ndarray): Array of wavelengths in nm
        
    Returns:
        go.Figure: Plotly figure object containing the refractive index plot
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=wavelength_range,
            y=results['refractive_index_real'],
            mode='lines',
            name='Real Part (n)',
            line=dict(color='blue', width=2)
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=wavelength_range,
            y=results['refractive_index_imag'],
            mode='lines',
            name='Imaginary Part (k)',
            line=dict(color='red', width=2)
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title="Effective Refractive Index",
        template="plotly_white",
        legend=dict(x=0, y=1, orientation='h')
    )
    
    fig.update_xaxes(title_text="Wavelength (nm)")
    fig.update_yaxes(title_text="Real Part (n)", secondary_y=False)
    fig.update_yaxes(title_text="Imaginary Part (k)", secondary_y=True)
    
    return fig

def plot_power_distribution(results, wavelength_range, selected_wavelength, power_view, power_dimension):
    """
    Plot power distribution (Poynting vector, power flow, energy density).
    
    Args:
        results (dict): Dictionary containing simulation results
        wavelength_range (np.ndarray): Array of wavelengths in nm
        selected_wavelength (float): Selected wavelength for visualization
        power_view (str): Type of power visualization
        power_dimension (str): Either "2D Cross-section" or "3D Volume"
        
    Returns:
        go.Figure: Plotly figure object containing the power distribution
    """
    # In a real implementation, the power calculations would be more sophisticated
    # For this simulation, we'll use the power_distribution data as a proxy
    
    # Find the closest wavelength in our data
    available_wavelengths = list(results['power_distribution_2d'].keys())
    closest_available = min(available_wavelengths, key=lambda x: abs(x - selected_wavelength))
    
    if power_dimension == "2D Cross-section":
        power_data = results['power_distribution_2d'][closest_available]
        
        # For vector visualization (Poynting or power flow)
        if power_view in ["Poynting Vector", "Power Flow"]:
            # Create vector components for visualization
            # In a real implementation, these would be calculated from E and H fields
            u = np.gradient(power_data, axis=0)
            v = np.gradient(power_data, axis=1)
            
            # Normalize for better visualization
            magnitude = np.sqrt(u**2 + v**2)
            u = u / (magnitude + 1e-10)
            v = v / (magnitude + 1e-10)
            
            # Subsample for cleaner visualization
            skip = 2
            x_grid = results['x_grid']
            y_grid = results['y_grid']
            X, Y = np.meshgrid(x_grid, y_grid)
            
            fig = go.Figure()
            
            # Add the vector field - use scatter with markers instead of quiver
            # since quiver is not directly available in plotly.graph_objects
            x_points = X[::skip, ::skip].flatten()
            y_points = Y[::skip, ::skip].flatten()
            u_points = u[::skip, ::skip].flatten()
            v_points = v[::skip, ::skip].flatten()
            
            # Normalize vectors for visualization
            norm = np.sqrt(u_points**2 + v_points**2)
            u_norm = u_points / (norm + 1e-10)
            v_norm = v_points / (norm + 1e-10)
            
            # Add arrow markers
            fig.add_trace(go.Scatter(
                x=x_points,
                y=y_points,
                mode='markers',
                marker=dict(
                    symbol='arrow',
                    size=12,
                    angle=np.arctan2(v_norm, u_norm) * 180 / np.pi,
                    color=norm,
                    colorscale='Viridis',
                    colorbar=dict(title="Vector Magnitude"),
                ),
                name='Power Flow'
            ))
            
            # Add the background heatmap
            fig.add_trace(go.Heatmap(
                z=power_data,
                x=x_grid,
                y=y_grid,
                colorscale='Viridis',
                opacity=0.8,
                showscale=True,
                colorbar=dict(title="Power Intensity"),
                name='Power Magnitude'
            ))
            
            title = f"{power_view} at λ = {closest_available:.1f} nm"
            
        else:  # Energy Density
            fig = go.Figure(data=go.Heatmap(
                z=power_data**2,  # Square for energy density
                x=results['x_grid'],
                y=results['y_grid'],
                colorscale='Viridis',
                colorbar=dict(title="Energy Density")
            ))
            
            title = f"Energy Density at λ = {closest_available:.1f} nm"
        
        fig.update_layout(
            title=title,
            xaxis_title="x (μm)",
            yaxis_title="y (μm)",
            template="plotly_white"
        )
        
    else:  # 3D Volume
        power_data = results['power_distribution_3d'][closest_available]
        
        # We'll use a slice to visualize the 3D volume
        z_slice_idx = power_data.shape[2] // 2  # Middle slice
        
        if power_view in ["Poynting Vector", "Power Flow"]:
            # For 3D vector visualization, we'll show a slice with vectors
            # In a real implementation, this would be a more sophisticated 3D vector field
            u = np.gradient(power_data[:, :, z_slice_idx], axis=0)
            v = np.gradient(power_data[:, :, z_slice_idx], axis=1)
            
            # Normalize
            magnitude = np.sqrt(u**2 + v**2)
            u = u / (magnitude + 1e-10)
            v = v / (magnitude + 1e-10)
            
            # Subsample
            skip = 2
            x_grid = results['x_grid']
            y_grid = results['y_grid']
            X, Y = np.meshgrid(x_grid, y_grid)
            
            fig = go.Figure()
            
            # Add the surface
            fig.add_trace(go.Surface(
                z=z_slice_idx * np.ones_like(power_data[:, :, z_slice_idx]),
                x=np.tile(x_grid, (len(y_grid), 1)),
                y=np.tile(y_grid, (len(x_grid), 1)).T,
                surfacecolor=power_data[:, :, z_slice_idx],
                colorscale='Viridis',
                colorbar=dict(title="Power Intensity"),
                opacity=0.8
            ))
            
            # Add arrows to indicate flow direction
            for i in range(0, len(x_grid), skip):
                for j in range(0, len(y_grid), skip):
                    fig.add_trace(go.Cone(
                        x=[x_grid[i]],
                        y=[y_grid[j]],
                        z=[results['z_grid'][z_slice_idx]],
                        u=[u[j, i]],
                        v=[v[j, i]],
                        w=[0],  # No z component for simplicity
                        sizemode="absolute",
                        sizeref=0.1,
                        showscale=False
                    ))
            
            title = f"3D {power_view} at λ = {closest_available:.1f} nm (z-slice)"
            
        else:  # Energy Density
            fig = go.Figure(data=go.Volume(
                x=results['x_grid'],
                y=results['y_grid'],
                z=results['z_grid'],
                value=power_data.flatten(),
                opacity=0.2,
                surface_count=20,
                colorscale='Viridis',
                colorbar=dict(title="Energy Density")
            ))
            
            title = f"3D Energy Density at λ = {closest_available:.1f} nm"
        
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title="x (μm)",
                yaxis_title="y (μm)",
                zaxis_title="z (μm)"
            ),
            template="plotly_white"
        )
    
    return fig

def plot_3d_structure(structure_params):
    """
    Create a 3D visualization of the designed structure.
    
    Args:
        structure_params (dict): Dictionary containing structure parameters
        
    Returns:
        go.Figure: Plotly figure object containing the 3D structure visualization
    """
    structure_type = structure_params['structure_type']
    
    fig = go.Figure()
    
    # Generate different structure visualizations based on the type
    if structure_type == "Metamaterial Thin Film":
        # Create a layered structure
        layers = structure_params.get('layers', [])
        total_thickness = sum(layer['thickness'] for layer in layers) if layers else 500
        
        # Base dimensions
        width = 500
        depth = 500
        
        current_height = 0
        for i, layer in enumerate(layers):
            thickness = layer['thickness']
            material = layer['material']
            
            # Assign a color based on the material
            if 'Gold' in material or 'Silver' in material or 'Copper' in material:
                color = 'goldenrod' if 'Gold' in material else 'silver' if 'Silver' in material else 'peru'
            elif 'Silicon' in material:
                color = 'blue'
            elif 'Oxide' in material:
                color = 'lightblue'
            else:
                color = f'hsl({(i * 30) % 360}, 70%, 60%)'
            
            # Add the layer as a box
            fig.add_trace(go.Mesh3d(
                x=[0, width, width, 0, 0, width, width, 0],
                y=[0, 0, depth, depth, 0, 0, depth, depth],
                z=[current_height, current_height, current_height, current_height, 
                   current_height + thickness, current_height + thickness, 
                   current_height + thickness, current_height + thickness],
                i=[0, 0, 0, 1, 4, 4],
                j=[1, 2, 4, 5, 5, 6],
                k=[2, 3, 7, 6, 6, 7],
                opacity=0.8,
                color=color,
                name=f"Layer {i+1}: {material} ({thickness} nm)"
            ))
            
            current_height += thickness
    
    elif structure_type == "Photonic Crystal":
        crystal_dimension = structure_params.get('crystal_dimension', '2D')
        
        if crystal_dimension == '1D':
            # 1D photonic crystal - alternating layers
            periodicity = structure_params.get('periodicity', 300)
            duty_cycle = structure_params.get('duty_cycle', 0.5)
            num_periods = structure_params.get('num_periods', 10)
            
            # Base dimensions
            width = 500
            depth = 500
            primary_thickness = periodicity * duty_cycle
            secondary_thickness = periodicity * (1 - duty_cycle)
            total_thickness = num_periods * periodicity
            
            for i in range(num_periods):
                # Primary material layer
                primary_start = i * periodicity
                fig.add_trace(go.Mesh3d(
                    x=[0, width, width, 0, 0, width, width, 0],
                    y=[0, 0, depth, depth, 0, 0, depth, depth],
                    z=[primary_start, primary_start, primary_start, primary_start, 
                       primary_start + primary_thickness, primary_start + primary_thickness, 
                       primary_start + primary_thickness, primary_start + primary_thickness],
                    i=[0, 0, 0, 1, 4, 4],
                    j=[1, 2, 4, 5, 5, 6],
                    k=[2, 3, 7, 6, 6, 7],
                    opacity=0.8,
                    color='blue',
                    name=f"Primary Material Layer {i+1}"
                ))
                
                # Secondary material layer
                secondary_start = primary_start + primary_thickness
                fig.add_trace(go.Mesh3d(
                    x=[0, width, width, 0, 0, width, width, 0],
                    y=[0, 0, depth, depth, 0, 0, depth, depth],
                    z=[secondary_start, secondary_start, secondary_start, secondary_start, 
                       secondary_start + secondary_thickness, secondary_start + secondary_thickness, 
                       secondary_start + secondary_thickness, secondary_start + secondary_thickness],
                    i=[0, 0, 0, 1, 4, 4],
                    j=[1, 2, 4, 5, 5, 6],
                    k=[2, 3, 7, 6, 6, 7],
                    opacity=0.8,
                    color='red',
                    name=f"Secondary Material Layer {i+1}"
                ))
                
        elif crystal_dimension == '2D':
            # 2D photonic crystal - substrate with holes/pillars
            lattice_type = structure_params.get('lattice_type', 'Square')
            lattice_constant = structure_params.get('lattice_constant', 300)
            hole_radius = structure_params.get('hole_radius', 100)
            
            # Base dimensions
            width = 1500
            depth = 1500
            thickness = 300
            
            # Add the substrate
            fig.add_trace(go.Mesh3d(
                x=[0, width, width, 0, 0, width, width, 0],
                y=[0, 0, depth, depth, 0, 0, depth, depth],
                z=[0, 0, 0, 0, thickness, thickness, thickness, thickness],
                i=[0, 0, 0, 1, 4, 4],
                j=[1, 2, 4, 5, 5, 6],
                k=[2, 3, 7, 6, 6, 7],
                opacity=0.5,
                color='blue',
                name="Substrate"
            ))
            
            # Add holes or pillars based on the lattice type
            if lattice_type == 'Square':
                for x in range(int(hole_radius), int(width - hole_radius), int(lattice_constant)):
                    for y in range(int(hole_radius), int(depth - hole_radius), int(lattice_constant)):
                        # Create cylinder for holes
                        theta = np.linspace(0, 2*np.pi, 20)
                        x_circle = hole_radius * np.cos(theta) + x
                        y_circle = hole_radius * np.sin(theta) + y
                        z_bottom = np.zeros_like(theta)
                        z_top = thickness * np.ones_like(theta)
                        
                        fig.add_trace(go.Mesh3d(
                            x=np.concatenate([x_circle, x_circle]),
                            y=np.concatenate([y_circle, y_circle]),
                            z=np.concatenate([z_bottom, z_top]),
                            i=list(range(19)) + list(range(20, 39)),
                            j=list(range(1, 20)) + list(range(21, 40)),
                            k=list(range(20, 39)) + list(range(1, 20)),
                            opacity=1.0,
                            color='white',
                            name=f"Hole at ({x}, {y})"
                        ))
            
            # Hexagonal and Triangular lattices would be implemented similarly
            
        else:  # 3D
            # For 3D photonic crystal, we'll show a simplified visualization
            crystal_type = structure_params.get('crystal_type', 'FCC')
            lattice_constant = structure_params.get('lattice_constant', 300)
            
            # Create a simple unit cell visualization based on crystal type
            if crystal_type == 'FCC':
                # Create an FCC unit cell
                fig.add_trace(go.Scatter3d(
                    x=[0, lattice_constant, lattice_constant, 0, 0, lattice_constant, lattice_constant, 0, 
                       lattice_constant/2, lattice_constant/2, lattice_constant/2, lattice_constant/2, 
                       lattice_constant/2, lattice_constant/2],
                    y=[0, 0, lattice_constant, lattice_constant, 0, 0, lattice_constant, lattice_constant, 
                       lattice_constant/2, lattice_constant/2, 0, lattice_constant, lattice_constant/2, lattice_constant/2],
                    z=[0, 0, 0, 0, lattice_constant, lattice_constant, lattice_constant, lattice_constant, 
                       0, lattice_constant, lattice_constant/2, lattice_constant/2, lattice_constant/2, lattice_constant/2],
                    mode='markers',
                    marker=dict(size=20, color='blue'),
                    name='FCC Lattice Points'
                ))
    
    elif structure_type in ["Metal-Insulator-Metal (MIM)", "Insulator-Metal-Insulator (IMI)"]:
        is_mim = structure_type == "Metal-Insulator-Metal (MIM)"
        
        top_layer_thickness = structure_params.get('top_layer_thickness', 20)
        middle_layer_thickness = structure_params.get('middle_layer_thickness', 100)
        bottom_layer_thickness = structure_params.get('bottom_layer_thickness', 20)
        
        # Base dimensions
        width = 500
        depth = 500
        
        # Bottom layer
        fig.add_trace(go.Mesh3d(
            x=[0, width, width, 0, 0, width, width, 0],
            y=[0, 0, depth, depth, 0, 0, depth, depth],
            z=[0, 0, 0, 0, bottom_layer_thickness, bottom_layer_thickness, bottom_layer_thickness, bottom_layer_thickness],
            i=[0, 0, 0, 1, 4, 4],
            j=[1, 2, 4, 5, 5, 6],
            k=[2, 3, 7, 6, 6, 7],
            opacity=0.8,
            color='goldenrod' if is_mim else 'lightblue',
            name="Bottom Layer"
        ))
        
        # Middle layer
        middle_start = bottom_layer_thickness
        fig.add_trace(go.Mesh3d(
            x=[0, width, width, 0, 0, width, width, 0],
            y=[0, 0, depth, depth, 0, 0, depth, depth],
            z=[middle_start, middle_start, middle_start, middle_start, 
               middle_start + middle_layer_thickness, middle_start + middle_layer_thickness, 
               middle_start + middle_layer_thickness, middle_start + middle_layer_thickness],
            i=[0, 0, 0, 1, 4, 4],
            j=[1, 2, 4, 5, 5, 6],
            k=[2, 3, 7, 6, 6, 7],
            opacity=0.8,
            color='lightblue' if is_mim else 'goldenrod',
            name="Middle Layer"
        ))
        
        # Top layer
        top_start = middle_start + middle_layer_thickness
        fig.add_trace(go.Mesh3d(
            x=[0, width, width, 0, 0, width, width, 0],
            y=[0, 0, depth, depth, 0, 0, depth, depth],
            z=[top_start, top_start, top_start, top_start, 
               top_start + top_layer_thickness, top_start + top_layer_thickness, 
               top_start + top_layer_thickness, top_start + top_layer_thickness],
            i=[0, 0, 0, 1, 4, 4],
            j=[1, 2, 4, 5, 5, 6],
            k=[2, 3, 7, 6, 6, 7],
            opacity=0.8,
            color='goldenrod' if is_mim else 'lightblue',
            name="Top Layer"
        ))
        
        # Add patterns if specified
        include_patterns = structure_params.get('include_patterns', False)
        if include_patterns:
            pattern_type = structure_params.get('pattern_type', 'Hole Array')
            pattern_period = structure_params.get('pattern_period', 200)
            pattern_size = structure_params.get('pattern_size', 100)
            
            if pattern_type == 'Hole Array':
                for x in range(int(pattern_size), int(width - pattern_size), int(pattern_period)):
                    for y in range(int(pattern_size), int(depth - pattern_size), int(pattern_period)):
                        # Create cylinder for holes through the top layer only
                        theta = np.linspace(0, 2*np.pi, 20)
                        x_circle = pattern_size/2 * np.cos(theta) + x
                        y_circle = pattern_size/2 * np.sin(theta) + y
                        z_bottom = top_start * np.ones_like(theta)
                        z_top = (top_start + top_layer_thickness) * np.ones_like(theta)
                        
                        fig.add_trace(go.Mesh3d(
                            x=np.concatenate([x_circle, x_circle]),
                            y=np.concatenate([y_circle, y_circle]),
                            z=np.concatenate([z_bottom, z_top]),
                            i=list(range(19)) + list(range(20, 39)),
                            j=list(range(1, 20)) + list(range(21, 40)),
                            k=list(range(20, 39)) + list(range(1, 20)),
                            opacity=1.0,
                            color='white',
                            name=f"Hole at ({x}, {y})"
                        ))
    
    elif "Pattern" in structure_type:
        dimension = "3D" if structure_type == "3D Pattern" else "2D"
        
        pattern_type = structure_params.get('pattern_type', 'Hole Array' if dimension == '2D' else 'Cubic')
        substrate_thickness = structure_params.get('substrate_thickness', 200)
        pattern_periodicity = structure_params.get('pattern_periodicity', 200)
        pattern_height = structure_params.get('pattern_height', 100)
        pattern_width = structure_params.get('pattern_width', 100)
        
        # Base dimensions
        width = 1000
        depth = 1000
        
        # Add the substrate
        fig.add_trace(go.Mesh3d(
            x=[0, width, width, 0, 0, width, width, 0],
            y=[0, 0, depth, depth, 0, 0, depth, depth],
            z=[0, 0, 0, 0, substrate_thickness, substrate_thickness, substrate_thickness, substrate_thickness],
            i=[0, 0, 0, 1, 4, 4],
            j=[1, 2, 4, 5, 5, 6],
            k=[2, 3, 7, 6, 6, 7],
            opacity=0.5,
            color='lightblue',
            name="Substrate"
        ))
        
        # Add patterns
        if dimension == '2D':
            if pattern_type == 'Hole Array':
                for x in range(int(pattern_width/2), int(width - pattern_width/2), int(pattern_periodicity)):
                    for y in range(int(pattern_width/2), int(depth - pattern_width/2), int(pattern_periodicity)):
                        # Create cylinder for holes
                        theta = np.linspace(0, 2*np.pi, 20)
                        x_circle = pattern_width/2 * np.cos(theta) + x
                        y_circle = pattern_width/2 * np.sin(theta) + y
                        z_bottom = 0 * np.ones_like(theta)
                        z_top = substrate_thickness * np.ones_like(theta)
                        
                        fig.add_trace(go.Mesh3d(
                            x=np.concatenate([x_circle, x_circle]),
                            y=np.concatenate([y_circle, y_circle]),
                            z=np.concatenate([z_bottom, z_top]),
                            i=list(range(19)) + list(range(20, 39)),
                            j=list(range(1, 20)) + list(range(21, 40)),
                            k=list(range(20, 39)) + list(range(1, 20)),
                            opacity=1.0,
                            color='white',
                            name=f"Hole at ({x}, {y})"
                        ))
            
            elif pattern_type == 'Pillar Array':
                for x in range(int(pattern_width/2), int(width - pattern_width/2), int(pattern_periodicity)):
                    for y in range(int(pattern_width/2), int(depth - pattern_width/2), int(pattern_periodicity)):
                        # Create cylinder for pillars
                        theta = np.linspace(0, 2*np.pi, 20)
                        x_circle = pattern_width/2 * np.cos(theta) + x
                        y_circle = pattern_width/2 * np.sin(theta) + y
                        z_bottom = substrate_thickness * np.ones_like(theta)
                        z_top = (substrate_thickness + pattern_height) * np.ones_like(theta)
                        
                        fig.add_trace(go.Mesh3d(
                            x=np.concatenate([x_circle, x_circle]),
                            y=np.concatenate([y_circle, y_circle]),
                            z=np.concatenate([z_bottom, z_top]),
                            i=list(range(19)) + list(range(20, 39)),
                            j=list(range(1, 20)) + list(range(21, 40)),
                            k=list(range(20, 39)) + list(range(1, 20)),
                            opacity=0.8,
                            color='goldenrod',
                            name=f"Pillar at ({x}, {y})"
                        ))
        
        else:  # 3D Pattern
            pattern_depth = structure_params.get('pattern_depth', 100)
            
            if pattern_type == 'Cubic':
                for x in range(int(pattern_width/2), int(width - pattern_width/2), int(pattern_periodicity)):
                    for y in range(int(pattern_width/2), int(depth - pattern_width/2), int(pattern_periodicity)):
                        # Create a cube
                        fig.add_trace(go.Mesh3d(
                            x=[x-pattern_width/2, x+pattern_width/2, x+pattern_width/2, x-pattern_width/2, 
                               x-pattern_width/2, x+pattern_width/2, x+pattern_width/2, x-pattern_width/2],
                            y=[y-pattern_width/2, y-pattern_width/2, y+pattern_width/2, y+pattern_width/2, 
                               y-pattern_width/2, y-pattern_width/2, y+pattern_width/2, y+pattern_width/2],
                            z=[substrate_thickness, substrate_thickness, substrate_thickness, substrate_thickness, 
                               substrate_thickness+pattern_height, substrate_thickness+pattern_height, 
                               substrate_thickness+pattern_height, substrate_thickness+pattern_height],
                            i=[0, 0, 0, 1, 4, 4],
                            j=[1, 2, 4, 5, 5, 6],
                            k=[2, 3, 7, 6, 6, 7],
                            opacity=0.8,
                            color='goldenrod',
                            name=f"Cube at ({x}, {y})"
                        ))
    
    elif structure_type == "Nanoparticle":
        particle_shape = structure_params.get('particle_shape', 'Sphere')
        include_substrate = structure_params.get('include_substrate', False)
        
        # Add substrate if requested
        if include_substrate:
            substrate_thickness = structure_params.get('substrate_thickness', 200)
            
            # Base dimensions
            width = 500
            depth = 500
            
            fig.add_trace(go.Mesh3d(
                x=[0, width, width, 0, 0, width, width, 0],
                y=[0, 0, depth, depth, 0, 0, depth, depth],
                z=[0, 0, 0, 0, substrate_thickness, substrate_thickness, substrate_thickness, substrate_thickness],
                i=[0, 0, 0, 1, 4, 4],
                j=[1, 2, 4, 5, 5, 6],
                k=[2, 3, 7, 6, 6, 7],
                opacity=0.5,
                color='lightblue',
                name="Substrate"
            ))
            
            z_offset = substrate_thickness
        else:
            z_offset = 0
            
        # Add the nanoparticle based on its shape
        if particle_shape == 'Sphere':
            particle_radius = structure_params.get('particle_radius', 50)
            
            # Create a sphere
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            x = particle_radius * np.outer(np.cos(u), np.sin(v)) + 250
            y = particle_radius * np.outer(np.sin(u), np.sin(v)) + 250
            z = particle_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + z_offset + particle_radius
            
            fig.add_trace(go.Surface(
                x=x,
                y=y,
                z=z,
                colorscale=[[0, 'goldenrod'], [1, 'goldenrod']],
                showscale=False,
                name="Spherical Nanoparticle"
            ))
            
        elif particle_shape == 'Cube':
            particle_side = structure_params.get('particle_side', 50)
            
            # Create a cube
            fig.add_trace(go.Mesh3d(
                x=[250-particle_side/2, 250+particle_side/2, 250+particle_side/2, 250-particle_side/2, 
                   250-particle_side/2, 250+particle_side/2, 250+particle_side/2, 250-particle_side/2],
                y=[250-particle_side/2, 250-particle_side/2, 250+particle_side/2, 250+particle_side/2, 
                   250-particle_side/2, 250-particle_side/2, 250+particle_side/2, 250+particle_side/2],
                z=[z_offset, z_offset, z_offset, z_offset, 
                   z_offset+particle_side, z_offset+particle_side, z_offset+particle_side, z_offset+particle_side],
                i=[0, 0, 0, 1, 4, 4],
                j=[1, 2, 4, 5, 5, 6],
                k=[2, 3, 7, 6, 6, 7],
                opacity=0.8,
                color='goldenrod',
                name="Cubic Nanoparticle"
            ))
            
        elif particle_shape == 'Rod':
            particle_length = structure_params.get('particle_length', 100)
            particle_diameter = structure_params.get('particle_diameter', 30)
            
            # Create a rod (cylinder)
            theta = np.linspace(0, 2*np.pi, 20)
            x_circle1 = particle_diameter/2 * np.cos(theta) + 250 - particle_length/2
            y_circle1 = particle_diameter/2 * np.sin(theta) + 250
            z_circle1 = z_offset + particle_diameter/2 * np.ones_like(theta)
            
            x_circle2 = particle_diameter/2 * np.cos(theta) + 250 + particle_length/2
            y_circle2 = particle_diameter/2 * np.sin(theta) + 250
            z_circle2 = z_offset + particle_diameter/2 * np.ones_like(theta)
            
            fig.add_trace(go.Mesh3d(
                x=np.concatenate([x_circle1, x_circle2]),
                y=np.concatenate([y_circle1, y_circle2]),
                z=np.concatenate([z_circle1, z_circle2]),
                i=list(range(19)) + list(range(20, 39)),
                j=list(range(1, 20)) + list(range(21, 40)),
                k=list(range(20, 39)) + list(range(1, 20)),
                opacity=0.8,
                color='goldenrod',
                name="Rod Nanoparticle"
            ))
            
        elif particle_shape == 'Core-Shell':
            core_radius = structure_params.get('core_radius', 30)
            shell_thickness = structure_params.get('shell_thickness', 10)
            
            # Create the core
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            x = core_radius * np.outer(np.cos(u), np.sin(v)) + 250
            y = core_radius * np.outer(np.sin(u), np.sin(v)) + 250
            z = core_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + z_offset + core_radius
            
            fig.add_trace(go.Surface(
                x=x,
                y=y,
                z=z,
                colorscale=[[0, 'red'], [1, 'red']],
                showscale=False,
                opacity=0.8,
                name="Core"
            ))
            
            # Create the shell
            shell_radius = core_radius + shell_thickness
            x = shell_radius * np.outer(np.cos(u), np.sin(v)) + 250
            y = shell_radius * np.outer(np.sin(u), np.sin(v)) + 250
            z = shell_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + z_offset + core_radius
            
            fig.add_trace(go.Surface(
                x=x,
                y=y,
                z=z,
                colorscale=[[0, 'goldenrod'], [1, 'goldenrod']],
                showscale=False,
                opacity=0.5,
                name="Shell"
            ))
    
    # Configure layout with appropriate camera settings
    fig.update_layout(
        title=f"3D Visualization of {structure_type}",
        scene=dict(
            xaxis_title="x (nm)",
            yaxis_title="y (nm)",
            zaxis_title="z (nm)",
            aspectmode='data'
        ),
        template="plotly_white"
    )
    
    return fig
