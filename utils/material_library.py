import numpy as np

def get_material_library():
    """
    Returns the list of available materials in the database.
    
    Returns:
        list: A list of material names available for selection
    """
    return [
        "Gold",
        "Silver",
        "Aluminum",
        "Copper",
        "Platinum",
        "Silicon",
        "Silicon Dioxide",
        "Titanium Dioxide",
        "Aluminum Oxide",
        "Indium Tin Oxide",
        "Gallium Arsenide",
        "Zinc Oxide",
        "Hafnium Oxide",
        "Zirconium Oxide",
        "Silicon Nitride",
        "Gallium Nitride",
        "Glass (BK7)",
        "Fused Silica",
        "Water",
        "Air"
    ]

def get_material_properties(material_name, wavelength_nm):
    """
    Returns the optical properties of the specified material at the given wavelength.
    
    Args:
        material_name (str): Name of the material
        wavelength_nm (float or np.ndarray): Wavelength in nanometers
        
    Returns:
        dict: Dictionary containing the material properties including:
            - n: Refractive index (real part)
            - k: Extinction coefficient (imaginary part)
            - eps_r: Real part of the permittivity
            - eps_i: Imaginary part of the permittivity
    """
    # Convert input to numpy array if it isn't already
    if not isinstance(wavelength_nm, np.ndarray):
        wavelength_nm = np.array([wavelength_nm])
    
    # For demonstration purposes, we'll use simplified models
    # In a real implementation, this would access a database of material properties
    if material_name == "Gold":
        # Simplified Drude model for gold
        plasma_freq = 2175  # THz
        collision_freq = 6.5  # THz
        
        # Convert wavelength nm to frequency THz
        freq = 3e5 / wavelength_nm  # THz
        
        eps_r = 1 - (plasma_freq**2) / (freq**2 + collision_freq**2)
        eps_i = (plasma_freq**2 * collision_freq) / (freq**3 + freq * collision_freq**2)
        
        # Calculate n and k from eps
        n = np.sqrt((np.sqrt(eps_r**2 + eps_i**2) + eps_r) / 2)
        k = np.sqrt((np.sqrt(eps_r**2 + eps_i**2) - eps_r) / 2)
        
    elif material_name == "Silver":
        # Simplified model for silver
        plasma_freq = 2175  # THz
        collision_freq = 4.35  # THz
        
        freq = 3e5 / wavelength_nm  # THz
        
        eps_r = 1 - (plasma_freq**2) / (freq**2 + collision_freq**2)
        eps_i = (plasma_freq**2 * collision_freq) / (freq**3 + freq * collision_freq**2)
        
        n = np.sqrt((np.sqrt(eps_r**2 + eps_i**2) + eps_r) / 2)
        k = np.sqrt((np.sqrt(eps_r**2 + eps_i**2) - eps_r) / 2)
        
    elif material_name == "Silicon":
        # Simplified model for silicon
        n = 3.5 + 0.1 * np.exp(-(wavelength_nm - 500)**2 / 10000)
        k = 0.01 + 0.1 * np.exp(-(wavelength_nm - 400)**2 / 5000)
        eps_r = n**2 - k**2
        eps_i = 2 * n * k
        
    elif material_name == "Silicon Dioxide" or material_name == "Fused Silica":
        # Simplified model for SiO2
        n = 1.45 + 0.01 * np.exp(-(wavelength_nm - 300)**2 / 10000)
        k = 1e-6 + 1e-5 * np.exp(-(wavelength_nm - 250)**2 / 2500)
        eps_r = n**2 - k**2
        eps_i = 2 * n * k
        
    elif material_name == "Titanium Dioxide":
        # Simplified model for TiO2
        n = 2.5 + 0.1 * np.exp(-(wavelength_nm - 400)**2 / 10000)
        k = 1e-4 + 1e-3 * np.exp(-(wavelength_nm - 300)**2 / 5000)
        eps_r = n**2 - k**2
        eps_i = 2 * n * k
        
    elif material_name == "Aluminum":
        # Simplified model for aluminum
        plasma_freq = 3570  # THz
        collision_freq = 19.4  # THz
        
        freq = 3e5 / wavelength_nm  # THz
        
        eps_r = 1 - (plasma_freq**2) / (freq**2 + collision_freq**2)
        eps_i = (plasma_freq**2 * collision_freq) / (freq**3 + freq * collision_freq**2)
        
        n = np.sqrt((np.sqrt(eps_r**2 + eps_i**2) + eps_r) / 2)
        k = np.sqrt((np.sqrt(eps_r**2 + eps_i**2) - eps_r) / 2)
        
    elif material_name == "Air":
        n = np.ones_like(wavelength_nm)
        k = np.zeros_like(wavelength_nm)
        eps_r = n**2
        eps_i = np.zeros_like(wavelength_nm)
        
    elif material_name == "Water":
        n = 1.33 + 0.01 * np.exp(-(wavelength_nm - 300)**2 / 10000)
        k = 1e-4 + 1e-3 * np.exp(-(wavelength_nm - 750)**2 / 10000)
        eps_r = n**2 - k**2
        eps_i = 2 * n * k
        
    # Add more materials as needed...
    else:
        # Default generic dielectric
        n = 1.5 * np.ones_like(wavelength_nm)
        k = 1e-4 * np.ones_like(wavelength_nm)
        eps_r = n**2 - k**2
        eps_i = 2 * n * k
    
    return {
        "n": n,
        "k": k,
        "eps_r": eps_r,
        "eps_i": eps_i
    }
