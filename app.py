import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import datetime
from utils.material_library import get_material_library, get_material_properties
from utils.deep_learning_models import predict_optical_properties
from utils.visualization import (
    plot_reflectance_transmittance_absorption,
    plot_field_distribution,
    plot_refractive_index,
    plot_power_distribution,
    plot_3d_structure
)
from utils.simulation import generate_structure_parameters
from utils.database import (
    save_simulation_config,
    save_simulation_result,
    get_simulation_configs,
    get_simulation_config,
    get_simulation_results,
    get_simulation_result,
    delete_simulation_config,
    delete_simulation_result,
    convert_result_to_simulation_format
)

# Page configuration
st.set_page_config(
    page_title="Photonic & Plasmonic Structure Analyzer",
    page_icon="🔬",
    layout="wide",
)

# Title and introduction
st.title("Deep Learning-Based Photonic & Plasmonic Structure Analyzer")
st.markdown("""
    Design and analyze various plasmonic and photonic structures with comprehensive visualization 
    of optical and electromagnetic properties using deep learning models.
""")

# Sidebar for structure and material selection
st.sidebar.header("Structure Configuration")

# Structure type selection
structure_type = st.sidebar.selectbox(
    "Select Structure Type",
    [
        "Metamaterial Thin Film",
        "Photonic Crystal",
        "Metal-Insulator-Metal (MIM)",
        "Insulator-Metal-Insulator (IMI)",
        "2D Pattern",
        "3D Pattern",
        "Nanoparticle"
    ]
)

# Environment settings
st.sidebar.subheader("Environment")
environment_material = st.sidebar.selectbox(
    "Environment Material",
    ["Air", "Water", "Glass", "Oil", "Custom"]
)

if environment_material == "Custom":
    env_refractive_index = st.sidebar.number_input(
        "Custom Environment Refractive Index",
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.01
    )
else:
    env_refractive_index = None  # Will be fetched from material library

# Material selection
st.sidebar.subheader("Material Selection")
material_library = get_material_library()

# Different material selections based on structure type
if structure_type in ["Metamaterial Thin Film", "Photonic Crystal"]:
    primary_material = st.sidebar.selectbox("Primary Material", material_library)
    secondary_material = st.sidebar.selectbox("Secondary Material", material_library, index=1)
    
elif structure_type in ["Metal-Insulator-Metal (MIM)", "Insulator-Metal-Insulator (IMI)"]:
    metal_material = st.sidebar.selectbox("Metal Material", [m for m in material_library if m in ["Gold", "Silver", "Aluminum", "Copper", "Platinum"]])
    insulator_material = st.sidebar.selectbox("Insulator Material", [m for m in material_library if m not in ["Gold", "Silver", "Aluminum", "Copper", "Platinum"]])
    
elif "Pattern" in structure_type:
    substrate_material = st.sidebar.selectbox("Substrate Material", material_library)
    pattern_material = st.sidebar.selectbox("Pattern Material", material_library, index=1)
    
elif structure_type == "Nanoparticle":
    particle_material = st.sidebar.selectbox("Particle Material", material_library)
    include_substrate = st.sidebar.checkbox("Include Substrate")
    if include_substrate:
        substrate_material = st.sidebar.selectbox("Substrate Material", material_library, index=1)
    else:
        substrate_material = None

# Wavelength range
st.sidebar.subheader("Wavelength Settings")
wavelength_min = st.sidebar.slider("Minimum Wavelength (nm)", 300, 1000, 400)
wavelength_max = st.sidebar.slider("Maximum Wavelength (nm)", wavelength_min + 100, 2500, 800)
wavelength_steps = st.sidebar.number_input("Number of Wavelength Steps", 10, 500, 100)
wavelength_range = np.linspace(wavelength_min, wavelength_max, int(wavelength_steps))

# Main content area
st.header(f"{structure_type} Design")

# Structure-specific parameters
with st.expander("Structure Parameters", expanded=True):
    if structure_type == "Metamaterial Thin Film":
        num_layers = st.number_input("Number of Layers", 1, 20, 5)
        layer_thickness = st.slider("Layer Thickness (nm)", 5, 500, 50)
        
        layers = []
        for i in range(num_layers):
            col1, col2 = st.columns(2)
            with col1:
                material = st.selectbox(f"Layer {i+1} Material", [primary_material, secondary_material], index=i % 2)
            with col2:
                thickness = st.number_input(f"Layer {i+1} Thickness (nm)", 5, 500, layer_thickness)
            layers.append({"material": material, "thickness": thickness})
            
    elif structure_type == "Photonic Crystal":
        crystal_dimension = st.radio("Crystal Dimension", ["1D", "2D", "3D"])
        
        if crystal_dimension == "1D":
            periodicity = st.slider("Periodicity (nm)", 100, 1000, 300)
            duty_cycle = st.slider("Duty Cycle", 0.1, 0.9, 0.5)
            num_periods = st.number_input("Number of Periods", 1, 50, 10)
            
        elif crystal_dimension == "2D":
            lattice_type = st.selectbox("Lattice Type", ["Square", "Hexagonal", "Triangular"])
            lattice_constant = st.slider("Lattice Constant (nm)", 100, 1000, 300)
            hole_radius = st.slider("Hole Radius (nm)", 10, 400, 100)
            
        else:  # 3D
            crystal_type = st.selectbox("3D Crystal Type", ["FCC", "BCC", "Diamond", "Woodpile"])
            lattice_constant = st.slider("Lattice Constant (nm)", 100, 1000, 300)
            
    elif structure_type in ["Metal-Insulator-Metal (MIM)", "Insulator-Metal-Insulator (IMI)"]:
        is_mim = structure_type == "Metal-Insulator-Metal (MIM)"
        
        if is_mim:
            top_layer_thickness = st.slider("Top Metal Layer (nm)", 5, 200, 20)
            middle_layer_thickness = st.slider("Insulator Layer (nm)", 5, 500, 100)
            bottom_layer_thickness = st.slider("Bottom Metal Layer (nm)", 5, 200, 20)
        else:  # IMI
            top_layer_thickness = st.slider("Top Insulator Layer (nm)", 5, 500, 100)
            middle_layer_thickness = st.slider("Metal Layer (nm)", 5, 200, 20)
            bottom_layer_thickness = st.slider("Bottom Insulator Layer (nm)", 5, 500, 100)
        
        include_patterns = st.checkbox("Include Patterns")
        if include_patterns:
            pattern_type = st.selectbox("Pattern Type", ["Hole Array", "Slit Array", "Disk Array", "Custom"])
            pattern_period = st.slider("Pattern Period (nm)", 50, 1000, 200)
            pattern_size = st.slider("Pattern Size (nm)", 10, 500, 100)
            
    elif "Pattern" in structure_type:
        dimension = "3D" if structure_type == "3D Pattern" else "2D"
        
        pattern_type = st.selectbox(
            f"Pattern Type ({dimension})", 
            ["Hole Array", "Pillar Array", "Grating", "Split Ring", "Bowtie", "Custom"] if dimension == "2D" else 
            ["Cubic", "Spherical", "Pyramid", "Rod", "Custom"]
        )
        
        substrate_thickness = st.slider("Substrate Thickness (nm)", 10, 1000, 200)
        pattern_periodicity = st.slider("Pattern Periodicity (nm)", 50, 1000, 200)
        
        if dimension == "2D":
            pattern_height = st.slider("Pattern Height (nm)", 10, 500, 100)
            pattern_width = st.slider("Pattern Width (nm)", 10, 500, 100)
        else:  # 3D
            pattern_height = st.slider("Pattern Height (nm)", 10, 500, 100)
            pattern_width = st.slider("Pattern Width (nm)", 10, 500, 100)
            pattern_depth = st.slider("Pattern Depth (nm)", 10, 500, 100)
            
    elif structure_type == "Nanoparticle":
        particle_shape = st.selectbox("Particle Shape", ["Sphere", "Cube", "Rod", "Disk", "Core-Shell", "Custom"])
        
        if particle_shape == "Sphere":
            particle_radius = st.slider("Particle Radius (nm)", 5, 500, 50)
        elif particle_shape == "Cube":
            particle_side = st.slider("Cube Side Length (nm)", 5, 500, 50)
        elif particle_shape == "Rod":
            particle_length = st.slider("Rod Length (nm)", 10, 1000, 100)
            particle_diameter = st.slider("Rod Diameter (nm)", 5, 500, 30)
        elif particle_shape == "Disk":
            particle_radius = st.slider("Disk Radius (nm)", 5, 500, 50)
            particle_height = st.slider("Disk Height (nm)", 1, 100, 20)
        elif particle_shape == "Core-Shell":
            core_material = st.selectbox("Core Material", material_library)
            shell_material = st.selectbox("Shell Material", material_library, index=1)
            core_radius = st.slider("Core Radius (nm)", 5, 300, 30)
            shell_thickness = st.slider("Shell Thickness (nm)", 1, 100, 10)
        elif particle_shape == "Custom":
            st.warning("Custom particle shape requires additional parameters")
            
        if include_substrate:
            substrate_thickness = st.slider("Substrate Thickness (nm)", 10, 1000, 200)

# Button to run the simulation
run_simulation = st.button("Run Deep Learning Simulation")

# Main content display
if run_simulation:
    with st.spinner("Running simulation using deep learning models..."):
        # Prepare the structure parameters based on the selected structure type
        local_vars = {k: v for k, v in locals().items() if k not in ['st', 'run_simulation', 'wavelength_range', 'structure_type']}
        structure_params = generate_structure_parameters(
            structure_type=structure_type,
            wavelength_range=wavelength_range,
            **local_vars
        )
        
        # Run prediction with deep learning model
        results = predict_optical_properties(structure_params)
        
        # Display the results in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Optical Spectra",
            "Field Distributions",
            "Refractive Index",
            "Power Distribution",
            "Structure Visualization"
        ])
        
        with tab1:
            st.subheader("Reflectance, Transmittance, and Absorption Spectra")
            fig_rta = plot_reflectance_transmittance_absorption(results, wavelength_range)
            st.plotly_chart(fig_rta, use_container_width=True)
            
            # Add a wavelength slider to view specific wavelength results
            selected_wavelength = st.slider(
                "Select wavelength (nm)",
                float(wavelength_min),
                float(wavelength_max),
                float((wavelength_min + wavelength_max) / 2)
            )
            
            # Find the closest wavelength in our data
            closest_idx = np.abs(wavelength_range - selected_wavelength).argmin()
            closest_wavelength = wavelength_range[closest_idx]
            
            # Display values at the selected wavelength
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Reflectance", f"{results['reflectance'][closest_idx]:.3f}")
            with col2:
                st.metric("Transmittance", f"{results['transmittance'][closest_idx]:.3f}")
            with col3:
                st.metric("Absorption", f"{results['absorption'][closest_idx]:.3f}")
                
        with tab2:
            st.subheader("Electric and Magnetic Field Distributions")
            
            field_type = st.radio("Field Type", ["Electric Field", "Magnetic Field"])
            view_dimension = st.radio("View Dimension", ["2D Cross-section", "3D Volume"])
            
            # Display the appropriate field distribution
            field_fig = plot_field_distribution(
                results, 
                wavelength_range,
                selected_wavelength,
                field_type,
                view_dimension
            )
            st.plotly_chart(field_fig, use_container_width=True)
            
            # Add explanation
            st.markdown(f"""
                Field distribution at λ = {selected_wavelength:.1f} nm. 
                The color intensity represents the field magnitude.
            """)
            
        with tab3:
            st.subheader("Refractive Index Analysis")
            
            # Plot refractive index vs wavelength
            ri_fig = plot_refractive_index(results, wavelength_range)
            st.plotly_chart(ri_fig, use_container_width=True)
            
            # Display effective refractive index at selected wavelength
            closest_idx = np.abs(wavelength_range - selected_wavelength).argmin()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Real Part (n)", f"{results['refractive_index_real'][closest_idx]:.3f}")
            with col2:
                st.metric("Imaginary Part (k)", f"{results['refractive_index_imag'][closest_idx]:.3f}")
                
        with tab4:
            st.subheader("Power Vector Distribution")
            
            power_view = st.radio("Power View", ["Poynting Vector", "Power Flow", "Energy Density"])
            power_dimension = st.radio("View Dimension", ["2D Cross-section", "3D Volume"], key="power_dim")
            
            # Display power distribution
            power_fig = plot_power_distribution(
                results,
                wavelength_range,
                selected_wavelength,
                power_view,
                power_dimension
            )
            st.plotly_chart(power_fig, use_container_width=True)
            
        with tab5:
            st.subheader("Structure Visualization")
            
            # Display 3D visualization of the structure
            structure_fig = plot_3d_structure(structure_params)
            st.plotly_chart(structure_fig, use_container_width=True)
            
            # Display a table with structure parameters
            st.subheader("Structure Parameters")
            
            # Extract parameters to display in a more readable format
            display_params = {}
            
            if structure_type == "Metamaterial Thin Film":
                display_params["Total Thickness"] = f"{sum(layer['thickness'] for layer in layers)} nm"
                display_params["Number of Layers"] = num_layers
                for i, layer in enumerate(layers):
                    display_params[f"Layer {i+1}"] = f"{layer['material']} ({layer['thickness']} nm)"
            
            elif structure_type == "Photonic Crystal":
                display_params["Crystal Dimension"] = crystal_dimension
                if crystal_dimension == "1D":
                    display_params["Periodicity"] = f"{periodicity} nm"
                    display_params["Duty Cycle"] = duty_cycle
                    display_params["Number of Periods"] = num_periods
                elif crystal_dimension == "2D":
                    display_params["Lattice Type"] = lattice_type
                    display_params["Lattice Constant"] = f"{lattice_constant} nm"
                    display_params["Hole Radius"] = f"{hole_radius} nm"
                else:  # 3D
                    display_params["Crystal Type"] = crystal_type
                    display_params["Lattice Constant"] = f"{lattice_constant} nm"
                    
            # More parameter displays for other structure types...
            elif structure_type in ["Metal-Insulator-Metal (MIM)", "Insulator-Metal-Insulator (IMI)"]:
                if structure_type == "Metal-Insulator-Metal (MIM)":
                    display_params["Top Layer"] = f"{metal_material} ({top_layer_thickness} nm)"
                    display_params["Middle Layer"] = f"{insulator_material} ({middle_layer_thickness} nm)"
                    display_params["Bottom Layer"] = f"{metal_material} ({bottom_layer_thickness} nm)"
                else:
                    display_params["Top Layer"] = f"{insulator_material} ({top_layer_thickness} nm)"
                    display_params["Middle Layer"] = f"{metal_material} ({middle_layer_thickness} nm)"
                    display_params["Bottom Layer"] = f"{insulator_material} ({bottom_layer_thickness} nm)"
                
                if include_patterns:
                    display_params["Pattern Type"] = pattern_type
                    display_params["Pattern Period"] = f"{pattern_period} nm"
                    display_params["Pattern Size"] = f"{pattern_size} nm"
                    
            # Display parameters as a DataFrame
            st.dataframe(pd.DataFrame(display_params.items(), columns=["Parameter", "Value"]))
            
        # Add database save option
        st.header("Save Simulation")
        simulation_name = st.text_input("Simulation Name", value=f"{structure_type} - {datetime.datetime.now().strftime('%Y-%m-%d')}")
        
        if st.button("Save to Database"):
            try:
                # Save the configuration
                config = save_simulation_config(simulation_name, structure_params)
                
                # Save the results
                result = save_simulation_result(config.id, results, wavelength_range)
                st.success(f"Simulation saved to database with ID: {config.id}")
            except Exception as e:
                st.error(f"Error saving to database: {str(e)}")
        
        # Add export options
        st.header("Export Results")
        export_format = st.selectbox("Export Format", ["CSV", "Excel", "JSON", "PNG"])
        
        if st.button("Export Data"):
            st.success(f"Results exported in {export_format} format (simulation only)")
            # In a real implementation, this would generate and provide a download link for the data
            # Since we're simulating, we'll just show a success message

else:
    # Add a section to load simulations from the database
    with st.expander("Load Saved Simulations", expanded=True):
        st.subheader("Previously Saved Simulations")
        
        # Get all saved configurations
        try:
            saved_configs = get_simulation_configs()
            
            if saved_configs:
                # Create a DataFrame to display the configurations
                config_data = []
                for config in saved_configs:
                    config_data.append({
                        "ID": config.id,
                        "Name": config.name,
                        "Structure Type": config.structure_type,
                        "Created At": config.created_at.strftime("%Y-%m-%d %H:%M"),
                    })
                
                # Display the configurations
                st.dataframe(pd.DataFrame(config_data))
                
                # Add a selectbox to choose a configuration
                selected_config_id = st.selectbox(
                    "Select a saved simulation to load",
                    options=[c["ID"] for c in config_data],
                    format_func=lambda x: next((c["Name"] for c in config_data if c["ID"] == x), "")
                )
                
                if st.button("Load Selected Simulation"):
                    with st.spinner("Loading simulation results..."):
                        # Get the configuration
                        config = get_simulation_config(selected_config_id)
                        structure_params = config.parameters
                        
                        # Get the simulation results
                        sim_results = get_simulation_results(selected_config_id)
                        
                        if sim_results:
                            # Take the most recent result
                            result_obj = sim_results[0]
                            
                            # Create wavelength range from the saved values
                            wavelength_range = np.linspace(
                                result_obj.wavelength_min,
                                result_obj.wavelength_max,
                                result_obj.wavelength_steps
                            )
                            
                            # Convert to simulation format
                            results = convert_result_to_simulation_format(result_obj, wavelength_range)
                            
                            # Display the results
                            st.success(f"Loaded simulation: {config.name}")
                            
                            # Display the structure parameters
                            st.subheader("Structure Parameters")
                            
                            # Extract and display key parameters
                            display_params = {
                                "Structure Type": config.structure_type,
                                "Created At": config.created_at.strftime("%Y-%m-%d %H:%M"),
                            }
                            
                            # Add more details based on the structure type
                            for key, value in structure_params.items():
                                if key not in ["wavelength_range", "structure_type"] and not key.startswith("_"):
                                    # Format the value for display
                                    if isinstance(value, float):
                                        display_params[key] = f"{value:.2f}"
                                    elif isinstance(value, list) and len(value) > 5:
                                        display_params[key] = f"List with {len(value)} items"
                                    else:
                                        display_params[key] = str(value)
                            
                            # Display parameters as a DataFrame
                            st.dataframe(pd.DataFrame(display_params.items(), columns=["Parameter", "Value"]))
                            
                            # Display the simulation results in tabs
                            tab1, tab2, tab3 = st.tabs([
                                "Optical Spectra",
                                "Refractive Index",
                                "Structure Visualization"
                            ])
                            
                            with tab1:
                                st.subheader("Reflectance, Transmittance, and Absorption Spectra")
                                fig_rta = plot_reflectance_transmittance_absorption(results, wavelength_range)
                                st.plotly_chart(fig_rta, use_container_width=True)
                            
                            with tab2:
                                st.subheader("Refractive Index")
                                fig_ri = plot_refractive_index(results, wavelength_range)
                                st.plotly_chart(fig_ri, use_container_width=True)
                            
                            with tab3:
                                st.subheader("Structure Visualization")
                                fig_struct = plot_3d_structure(structure_params)
                                st.plotly_chart(fig_struct, use_container_width=True)
                                
                            # Add option to delete this simulation
                            if st.button("Delete This Simulation"):
                                delete_simulation_config(selected_config_id)
                                st.success("Simulation deleted successfully")
                                st.rerun()
                        else:
                            st.warning("No results found for this configuration")
            else:
                st.info("No saved simulations found. Run a simulation and save it to see it here.")
        except Exception as e:
            st.error(f"Error loading simulations from database: {str(e)}")
    
    # Display placeholder visualization when no simulation has been run yet
    st.info("Configure your structure parameters and click 'Run Deep Learning Simulation' to see results.")
    
    # Show a sample structure visualization to guide the user
    st.subheader("Sample Structure Visualization")
    # Create a static sample image instead of loading an external URL
    import matplotlib.pyplot as plt
    import io
    from PIL import Image
    
    # Create a simple sample image
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, 'Structure Visualization Preview', ha='center', va='center', fontsize=20)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Convert matplotlib figure to image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    sample_image = Image.open(buf)
    
    # Display the image
    st.image(sample_image, caption="This is a placeholder. Run the simulation to see your actual structure.")
