import requests

def get_address_from_viacep(cep):
    """
    Fetches address information from ViaCEP API.
    Returns a dict with address fields or None if not found/error.
    """
    clean_cep = "".join(filter(str.isdigit, cep))
    
    if len(clean_cep) != 8:
        return None
        
    try:
        url = f"https://viacep.com.br/ws/{clean_cep}/json/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "erro" in data:
            return None
            
        return {
            "street": data.get("logradouro", ""),
            "neighborhood": data.get("bairro", ""),
            "city": data.get("localidade", ""),
            "state": data.get("uf", "")
        }
    except Exception as e:
        print(f"Error fetching CEP: {e}")
        return None

def update_all_indices():
    """
    Simulates updating financial indices.
    In a real scenario, this would fetch data from an API (e.g. BCB).
    """
    import time
    time.sleep(2) # Simulate network request
    return True
