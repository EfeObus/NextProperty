# Comprehensive list of Canadian cities organized by province
# This includes all major cities, towns, and metropolitan areas across Canada

CANADIAN_CITIES = {
    'ON': [  # Ontario
        'Toronto', 'Ottawa', 'Hamilton', 'London', 'Markham', 'Vaughan', 'Kitchener', 
        'Windsor', 'Richmond Hill', 'Oakville', 'Burlington', 'Oshawa', 'Barrie', 
        'Sudbury', 'Kingston', 'Guelph', 'Cambridge', 'Whitby', 'Ajax', 'Thunder Bay',
        'Waterloo', 'Brantford', 'Mississauga', 'Brampton', 'St. Catharines', 
        'Niagara Falls', 'Peterborough', 'Belleville', 'Sarnia', 'Welland', 
        'North Bay', 'Cornwall', 'Chatham', 'Georgetown', 'Milton', 'Newmarket',
        'Aurora', 'Bradford', 'Collingwood', 'Orangeville', 'Orillia', 'Owen Sound',
        'Cobourg', 'Port Hope', 'Lindsay', 'Woodstock', 'Tillsonburg', 'Ingersoll',
        'Simcoe', 'Delhi', 'Stratford', 'St. Thomas', 'Leamington', 'Tecumseh',
        'LaSalle', 'Amherstburg', 'Essex', 'Kingsville', 'Pickering', 'Stouffville',
        'Uxbridge', 'Port Perry', 'Bowmanville', 'Clarington', 'Courtice', 'Newcastle'
    ],
    'QC': [  # Quebec
        'Montreal', 'Quebec City', 'Laval', 'Gatineau', 'Longueuil', 'Sherbrooke',
        'Saguenay', 'Levis', 'Trois-Rivieres', 'Terrebonne', 'Saint-Jean-sur-Richelieu',
        'Repentigny', 'Boucherville', 'Saint-Jerome', 'Granby', 'Blainville',
        'Saint-Hyacinthe', 'Shawinigan', 'Dollard-des-Ormeaux', 'Rimouski',
        'Sorel-Tracy', 'Victoriaville', 'Saint-Eustache', 'Saint-Bruno-de-Montarville',
        'Drummondville', 'Saint-Constant', 'Candiac', 'Beloeil', 'Mascouche',
        'Chateauguay', 'Mirabel', 'La Prairie', 'Brossard', 'Sainte-Julie',
        'Vaudreuil-Dorion', 'Val-d\'Or', 'Alma', 'Rouyn-Noranda', 'Sept-Iles',
        'Thetford Mines', 'Saint-Georges', 'Magog', 'Chambly', 'Sainte-Therese',
        'Varennes', 'Mont-Royal', 'Westmount', 'Cote Saint-Luc', 'Pointe-Claire',
        'Kirkland', 'Dorval', 'Beaconsfield', 'Baie-Comeau', 'Joliette'
    ],
    'BC': [  # British Columbia
        'Vancouver', 'Surrey', 'Burnaby', 'Richmond', 'Abbotsford', 'Coquitlam',
        'Langley', 'Saanich', 'Delta', 'North Vancouver', 'Kelowna', 'Kamloops',
        'Nanaimo', 'Victoria', 'Chilliwack', 'Prince George', 'Vernon', 'Courtenay',
        'Campbell River', 'Penticton', 'Port Coquitlam', 'North Vancouver District',
        'Mission', 'Maple Ridge', 'New Westminster', 'West Vancouver', 'Port Moody',
        'Cranbrook', 'Fort St. John', 'Dawson Creek', 'Terrace', 'Prince Rupert',
        'Quesnel', 'Williams Lake', 'Powell River', 'Squamish', 'Whistler',
        'White Rock', 'Burnaby Heights', 'Metrotown', 'Brentwood', 'Lougheed',
        'Edmonds', 'Highgate', 'Deer Lake', 'Sperling', 'Lake City', 'Production Way',
        'Lougheed Town Centre', 'Brentwood Town Centre', 'Holdom', 'Sapperton',
        'Columbia', 'Scott Road', 'Gateway', 'Surrey Central', 'King George'
    ],
    'AB': [  # Alberta
        'Calgary', 'Edmonton', 'Red Deer', 'Lethbridge', 'St. Albert', 'Medicine Hat',
        'Grande Prairie', 'Airdrie', 'Spruce Grove', 'Okotoks', 'Lloydminster',
        'Fort McMurray', 'Camrose', 'Beaumont', 'Wetaskiwin', 'Canmore', 'Jasper',
        'Banff', 'Cochrane', 'High River', 'Strathmore', 'Chestermere', 'Leduc',
        'Fort Saskatchewan', 'Sherwood Park', 'St. Albert', 'Stony Plain',
        'Morinville', 'Legal', 'Bon Accord', 'Gibbons', 'Redwater', 'Lamont',
        'Mundare', 'Vegreville', 'Two Hills', 'Vermilion', 'Wainwright', 'Provost',
        'Innisfree', 'Willingdon', 'Andrew', 'Smoky Lake', 'Vilna', 'Holden',
        'Ryley', 'Tofield', 'Viking', 'Hardisty', 'Sedgewick', 'Killam'
    ],
    'MB': [  # Manitoba
        'Winnipeg', 'Brandon', 'Steinbach', 'Thompson', 'Portage la Prairie',
        'Winkler', 'Selkirk', 'Morden', 'Dauphin', 'The Pas', 'Flin Flon',
        'Swan River', 'Neepawa', 'Carman', 'Stonewall', 'Beausejour', 'Gimli',
        'Niverville', 'Altona', 'Virden', 'Souris', 'Boissevain', 'Killarney',
        'Deloraine', 'Melita', 'Pilot Mound', 'Crystal City', 'Manitou',
        'La Broquerie', 'Taché', 'Hanover', 'Ritchot', 'MacDonald', 'Morris',
        'Emerson', 'Gretna', 'Roseau River', 'Piney', 'Stuartburn', 'Reynolds',
        'Whitemouth', 'Lac du Bonnet', 'Pinawa', 'Powerview-Pine Falls',
        'Teulon', 'Oakbank', 'Lorette', 'Ile des Chenes', 'Landmark'
    ],
    'SK': [  # Saskatchewan
        'Saskatoon', 'Regina', 'Prince Albert', 'Moose Jaw', 'Swift Current',
        'Yorkton', 'North Battleford', 'Estevan', 'Weyburn', 'Lloydminster',
        'Melfort', 'Humboldt', 'Kindersley', 'Warman', 'Martensville', 'Meadow Lake',
        'La Ronge', 'Melville', 'Tisdale', 'Nipawin', 'Rosetown', 'Unity',
        'Maple Creek', 'Outlook', 'Watrous', 'Lanigan', 'Foam Lake', 'Wynyard',
        'Kamsack', 'Canora', 'Preeceville', 'Wadena', 'Quill Lake', 'Watson',
        'Naicam', 'Spalding', 'Star City', 'Carrot River', 'Hudson Bay',
        'Porcupine Plain', 'Arborfield', 'Zenon Park', 'Smeaton', 'Love',
        'Weekes', 'Birch Hills', 'Prince Albert National Park', 'Christopher Lake'
    ],
    'NS': [  # Nova Scotia
        'Halifax', 'Dartmouth', 'Sydney', 'Truro', 'New Glasgow', 'Glace Bay',
        'Yarmouth', 'Kentville', 'Amherst', 'Bridgewater', 'Antigonish',
        'Wolfville', 'Windsor', 'Stellarton', 'Westville', 'Pictou', 'Oxford',
        'Springhill', 'Parrsboro', 'Digby', 'Annapolis Royal', 'Middleton',
        'Berwick', 'Hantsport', 'Mahone Bay', 'Lunenburg', 'Liverpool',
        'Shelburne', 'Lockeport', 'Barrington', 'Clark\'s Harbour', 'Pubnico',
        'Meteghan', 'Church Point', 'Weymouth', 'Bear River', 'Lawrencetown',
        'Musquodoboit Harbour', 'Sheet Harbour', 'Sherbrooke', 'Canso',
        'Guysborough', 'Mulgrave', 'Port Hawkesbury', 'Baddeck', 'Ingonish'
    ],
    'NB': [  # New Brunswick
        'Saint John', 'Moncton', 'Fredericton', 'Dieppe', 'Riverview', 'Miramichi',
        'Edmundston', 'Campbellton', 'Bathurst', 'Sackville', 'Caraquet',
        'Sussex', 'Oromocto', 'Woodstock', 'Grand Falls', 'Dalhousie',
        'Shippagan', 'Lamèque', 'Tracadie', 'Richibucto', 'Bouctouche',
        'Shediac', 'Port Elgin', 'Sackville', 'Dorchester', 'Petitcodiac',
        'Hillsborough', 'Alma', 'Hopewell Cape', 'Harvey', 'McAdam',
        'Nackawic', 'Canterbury', 'Meductic', 'Hartland', 'Florenceville-Bristol',
        'Perth-Andover', 'Plaster Rock', 'Tobique First Nation', 'Saint-Léonard',
        'Baker Brook', 'Saint-François', 'Clair', 'Fort Kent', 'Madawaska'
    ],
    'NL': [  # Newfoundland and Labrador
        'St. John\'s', 'Mount Pearl', 'Corner Brook', 'Conception Bay South',
        'Paradise', 'Grand Falls-Windsor', 'Gander', 'Happy Valley-Goose Bay',
        'Labrador City', 'Stephenville', 'Bay Roberts', 'Carbonear', 'Placentia',
        'Clarenville', 'Trinity', 'Bonavista', 'Twillingate', 'Fogo Island',
        'Change Islands', 'Greenspond', 'Wesleyville', 'Lumsden', 'Musgrave Harbour',
        'Carmanville', 'Deer Lake', 'Pasadena', 'Steady Brook', 'Humber Arm South',
        'Cox\'s Cove', 'Lark Harbour', 'York Harbour', 'Benoit\'s Cove',
        'Meadows', 'Reidville', 'Hughes Brook', 'Irishtown-Summerside',
        'Massey Drive', 'Springdale', 'King\'s Point', 'Baie Verte', 'Fleur de Lys'
    ],
    'PE': [  # Prince Edward Island
        'Charlottetown', 'Summerside', 'Stratford', 'Cornwall', 'Montague',
        'Souris', 'Kensington', 'Alberton', 'Georgetown', 'Tignish', 'O\'Leary',
        'Borden-Carleton', 'Cavendish', 'North Rustico', 'Brackley Beach',
        'Hunter River', 'New London', 'Park Corner', 'Malpeque', 'Tyne Valley',
        'Lennox Island', 'Miscouche', 'Wellington', 'Bloomfield', 'Crapaud',
        'Bonshaw', 'Victoria', 'Clyde River', 'Alexandra', 'Warren Grove',
        'Belle River', 'Wood Islands', 'Murray River', 'Murray Harbour',
        'Little Pond', 'Red Point', 'Cardigan', 'Launching', 'Pooles Corner',
        'Rollo Bay', 'St. Peters', 'Morell', 'Mount Stewart', 'Tracadie'
    ],
    'NT': [  # Northwest Territories
        'Yellowknife', 'Hay River', 'Inuvik', 'Fort Smith', 'Behchokò',
        'Iqaluit', 'Norman Wells', 'Fort Simpson', 'Fort McPherson', 'Tuktoyaktuk',
        'Aklavik', 'Tsiigehtchic', 'Fort Good Hope', 'Colville Lake', 'Tulita',
        'Déline', 'Wrigley', 'Nahanni Butte', 'Trout Lake', 'Jean Marie River',
        'Fort Liard', 'Sambaa K\'e', 'Whatì', 'Gamètì', 'Wekweètì',
        'Łutselk\'e', 'Fort Resolution', 'Reliance', 'Enterprise', 'Kakisa'
    ],
    'YT': [  # Yukon
        'Whitehorse', 'Dawson City', 'Watson Lake', 'Haines Junction',
        'Mayo', 'Faro', 'Carmacks', 'Pelly Crossing', 'Beaver Creek',
        'Destruction Bay', 'Burwash Landing', 'Champagne', 'Teslin',
        'Carcross', 'Tagish', 'Marsh Lake', 'Ibex Valley', 'Deep Creek',
        'Mendenhall', 'Gravel Lake', 'Little Salmon', 'Ross River',
        'Old Crow', 'Eagle Plains', 'Inuvik'
    ],
    'NU': [  # Nunavut
        'Iqaluit', 'Rankin Inlet', 'Arviat', 'Baker Lake', 'Cambridge Bay',
        'Igloolik', 'Pangnirtung', 'Pond Inlet', 'Kugluktuk', 'Cape Dorset',
        'Gjoa Haven', 'Taloyoak', 'Coral Harbour', 'Repulse Bay', 'Hall Beach',
        'Clyde River', 'Arctic Bay', 'Resolute', 'Grise Fiord', 'Sanikiluaq',
        'Chesterfield Inlet', 'Whale Cove', 'Naujaat', 'Kimmirut', 'Qikiqtarjuaq'
    ]
}

def get_all_canadian_cities():
    """Get a flat list of all Canadian cities sorted alphabetically."""
    cities = []
    for province_cities in CANADIAN_CITIES.values():
        cities.extend(province_cities)
    return sorted(set(cities))  # Remove duplicates and sort

def get_cities_by_province(province_code):
    """Get cities for a specific province."""
    return CANADIAN_CITIES.get(province_code, [])

def get_major_cities():
    """Get list of major Canadian cities (population > 100,000)."""
    major_cities = [
        # Ontario
        'Toronto', 'Ottawa', 'Hamilton', 'London', 'Markham', 'Vaughan', 'Kitchener',
        'Windsor', 'Richmond Hill', 'Oakville', 'Burlington', 'Oshawa', 'Barrie',
        'Sudbury', 'Kingston', 'Guelph', 'Cambridge', 'Whitby', 'Ajax', 'Thunder Bay',
        'Waterloo', 'Brantford', 'Mississauga', 'Brampton', 'St. Catharines',
        
        # Quebec
        'Montreal', 'Quebec City', 'Laval', 'Gatineau', 'Longueuil', 'Sherbrooke',
        'Saguenay', 'Levis', 'Trois-Rivieres', 'Terrebonne',
        
        # British Columbia
        'Vancouver', 'Surrey', 'Burnaby', 'Richmond', 'Abbotsford', 'Coquitlam',
        'Langley', 'Saanich', 'Delta', 'North Vancouver', 'Kelowna', 'Kamloops',
        'Nanaimo', 'Victoria', 'Chilliwack', 'Prince George',
        
        # Alberta
        'Calgary', 'Edmonton', 'Red Deer', 'Lethbridge', 'St. Albert', 'Medicine Hat',
        'Grande Prairie', 'Airdrie', 'Spruce Grove',
        
        # Manitoba
        'Winnipeg', 'Brandon', 'Steinbach',
        
        # Saskatchewan
        'Saskatoon', 'Regina', 'Prince Albert', 'Moose Jaw',
        
        # Nova Scotia
        'Halifax', 'Dartmouth', 'Sydney',
        
        # New Brunswick
        'Saint John', 'Moncton', 'Fredericton',
        
        # Newfoundland and Labrador
        'St. John\'s',
        
        # Prince Edward Island
        'Charlottetown',
        
        # Northwest Territories
        'Yellowknife',
        
        # Yukon
        'Whitehorse',
        
        # Nunavut
        'Iqaluit'
    ]
    return sorted(major_cities)
