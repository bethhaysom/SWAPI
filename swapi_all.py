import os
import pandas as pd
import requests

# Helper function to extract integer ID from a URL string
def extract_id(url):
    if isinstance(url, str):
        return int(url.rstrip('/').split('/')[-1])
    return None

output_dir = r"G:\My Drive\12. Python\SWAPI"
os.makedirs(output_dir, exist_ok=True)


# Fetch all tables
endpoints = ["films", "vehicles", "people", "planets", "species", "starships"]
tables = {}

for endpoint in endpoints:
    data = requests.get(f"https://swapi.info/api/{endpoint}").json()
    df = pd.DataFrame(data)
    
    # Create dynamic primary key (e.g., film_id, person_id, vehicle_id)
    pk_name = "person_id" if endpoint == "people" else f"{endpoint[:-1]}_id"
    df[pk_name] = df["url"].apply(extract_id)
    
    tables[endpoint] = df

# Access individual tables using tables['films'], tables['people'], etc.


# Dictionary to store generated junction DataFrames
junction_tables = {}

# Configuration list:
# (Source Table Key, Source PK, List Column Name, Target PK, Junction Key, CSV Filename)
junction_config = [
    ("vehicles", "vehicle_id", "films",    "film_id",    "vehicles_films", "junction_veh_fil.csv"),
    ("people",   "person_id",  "films",    "film_id",    "people_films",   "junction_peo_fil.csv"),
    ("people",   "person_id",  "vehicles", "vehicle_id", "people_vehicles", "junction_peo_veh.csv"),
    ("starships", "starship_id", "films", "film_id", "starships_films", "junction_sta_fil.csv"),
    ("starships", "starship_id", "pilots", "person_id", "starships_people", "junction_sta_peo.csv"),
    ("planets", "planet_id", "films", "film_id", "planets_films", "junction_pla_fil.csv"),
    ("people", "person_id", "species", "specie_id", "people_species", "junction_peo_spe.csv"),
    ("species", "specie_id", "films", "film_id", "species_films", "junction_spe_fil.csv")
]

for source_key, source_pk, list_col, target_pk, j_key, csv_filename in junction_config:
    # 1. Pull the DataFrame directly from your 'tables' dictionary
    source_df = tables[source_key]
    
    # 2. Explode the list column and extract the target ID
    j_df = source_df[[source_pk, list_col]].explode(list_col).dropna()
    j_df[target_pk] = j_df[list_col].apply(extract_id)
    j_df = j_df[[source_pk, target_pk]].drop_duplicates().astype(int)
    
    # 3. Store in the junction_tables dictionary
    junction_tables[j_key] = j_df
    
    # 4. Export to CSV
    j_df.to_csv(os.path.join(output_dir, csv_filename), index=False)

# Can access any junction table using junction_tables['people_films'], etc.



# Clean columns and export to CSV for each table
table_columns = {
    "films": ['film_id', 'title', 'episode_id', 'director', 'release_date'],
    "vehicles": [
        'vehicle_id', 'name', 'model', 'manufacturer', 
        'cost_in_credits', 'length', 'max_atmosphering_speed', 'crew', 
        'passengers', 'cargo_capacity', 'consumables', 'vehicle_class'
    ],
    "people": [
        'person_id', 'name', 'height', 'mass', 
        'hair_color', 'skin_color', 'eye_color', 'birth_year', 
        'gender', 'homeworld'
    ],
    "starships": [
        'starship_id', 'name', 'model', 'manufacturer',
        'cost_in_credits', 'length', 'max_atmosphering_speed', 'crew',
        'passengers', 'cargo_capacity', 'consumables', 'hyperdrive_rating',
        'MGLT', 'starship_class'
    ],
    "planets": [
        'planet_id', 'name', 'rotation_period', 'orbital_period',
        'diameter', 'climate', 'gravity', 'terrain', 'surface_water',
        'population'
    ],
    "species": [
        'specie_id', 'name', 'classification', 'designation',
        'average_height', 'skin_colors', 'hair_colors', 
        'average_lifespan', 'homeworld', 'language'
    ]
}

# Export each entity table to CSV
for table_key, cols in table_columns.items():
    csv_path = os.path.join(output_dir, f"{table_key}.csv")
    tables[table_key][cols].to_csv(csv_path, index=False)

print(f"Exported all tables CSVs to: {output_dir}")
