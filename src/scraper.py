import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

DATA_DIR = os.path.join("data")

URLS = {
    "INPC": "https://www.aasp.org.br/produtos-servicos/indices-economicos/mensal/inpc-ibge/",
    "IPC-FIPE": "https://www.aasp.org.br/produtos-servicos/indices-economicos/mensal/ipc-fipe/",
    "IPCA": "https://www.aasp.org.br/produtos-servicos/indices-economicos/mensal/ipca-ibge/",
    "SELIC": "https://www.aasp.org.br/produtos-servicos/indices-economicos/mensal/selic/"
}

FILES = {
    "INPC": os.path.join(DATA_DIR, "indices_inpc.csv"),
    "IPC-FIPE": os.path.join(DATA_DIR, "indices_ipc_fipe.csv"),
    "IPCA": os.path.join(DATA_DIR, "indices_ipca.csv"),
    "SELIC": os.path.join(DATA_DIR, "selic.csv")
}

def fetch_indices(index_name):
    """
    Fetches the specified index table from AASP and saves it to CSV.
    """
    url = URLS.get(index_name)
    if not url:
        print(f"URL for {index_name} not found.")
        return False

    try:
        print(f"Fetching {index_name} from {url}...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # The table usually has class 'has-fixed-layout' or similar. 
        # We'll look for the first table in the content.
        table = soup.find('table', class_='has-fixed-layout')
        if not table:
            table = soup.find('table') # Fallback
        
        if not table:
            print(f"No table found for {index_name}")
            with open(f"debug_{index_name}.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            return False

        # Parse table
        data = []
        rows = table.find_all('tr')
        
        # Skip header if it exists (usually first row has years, or months)
        # AASP tables usually have Year in first col, then Jan, Feb... Dec.
        # Let's inspect the first row to see if it's header
        
        # We need to handle the structure: Year | Jan | Feb ...
        # We want to flatten this to: Date (01/Month/Year), Value
        
        months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
        
        for row in rows:
            cols = row.find_all('td')
            if not cols:
                continue
            
            # Assuming first col is Year
            try:
                year_text = cols[0].get_text(strip=True)
                if not year_text.isdigit():
                    continue # Skip header row if first col is not a year
                
                year = int(year_text)
                
                # Iterate over months (cols 1 to 12)
                for i, month in enumerate(months):
                    if i + 1 < len(cols):
                        val_text = cols[i+1].get_text(strip=True)
                        if val_text and val_text != "-":
                            # Clean value: remove %, handle (-), replace comma
                            val_text = val_text.replace('%', '').strip()
                            val_text = val_text.replace('(-)', '-').strip()
                            val_text = val_text.replace(',', '.')
                            
                            try:
                                val = float(val_text)
                                date_str = f"01/{month}/{year}"
                                data.append({"data": date_str, "valor": val})
                            except ValueError:
                                print(f"Could not parse value: {val_text}")
                                continue
            except Exception as e:
                print(f"Error parsing row: {e}")
                continue

        if data:
            df = pd.DataFrame(data)
            # Sort by date? Need to convert to datetime to sort correctly
            df['date_obj'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
            df = df.sort_values('date_obj', ascending=False)
            df = df.drop(columns=['date_obj'])
            
            save_path = FILES[index_name]
            df.to_csv(save_path, index=False)
            print(f"Saved {len(df)} records to {save_path}")
            return True
        else:
            print(f"No data extracted for {index_name}")
            with open(f"debug_{index_name}_empty.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            return False

    except Exception as e:
        print(f"Error fetching {index_name}: {e}")
        return False

def update_all_indices():
    """Updates all configured indices."""
    results = {}
    for name in URLS.keys():
        results[name] = fetch_indices(name)
    return results

if __name__ == "__main__":
    update_all_indices()
