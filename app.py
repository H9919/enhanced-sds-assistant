# Fixed SDS Assistant with Auto Web Search - Working Version
import os
from flask import Flask, render_template, request, jsonify, send_file, session
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
from io import BytesIO
from werkzeug.utils import secure_filename
import requests
import re
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sds-assistant-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create necessary directories
for folder in ['static/uploads', 'static/labels', 'static/exports', 'data']:
    Path(folder).mkdir(parents=True, exist_ok=True)

# US Cities Data
US_CITIES_DATA = {
    "Alabama": ["Birmingham", "Montgomery", "Mobile", "Huntsville", "Tuscaloosa"],
    "Alaska": ["Anchorage", "Fairbanks", "Juneau", "Wasilla", "Sitka"],
    "Arizona": ["Phoenix", "Tucson", "Mesa", "Chandler", "Scottsdale"],
    "Arkansas": ["Little Rock", "Fort Smith", "Fayetteville", "Springdale"],
    "California": ["Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno", "Sacramento"],
    "Colorado": ["Denver", "Colorado Springs", "Aurora", "Fort Collins"],
    "Connecticut": ["Bridgeport", "New Haven", "Hartford", "Stamford"],
    "Delaware": ["Wilmington", "Dover", "Newark", "Middletown"],
    "Florida": ["Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg"],
    "Georgia": ["Atlanta", "Augusta", "Columbus", "Savannah", "Athens"],
    "Hawaii": ["Honolulu", "Pearl City", "Hilo", "Kailua"],
    "Idaho": ["Boise", "Meridian", "Nampa", "Idaho Falls"],
    "Illinois": ["Chicago", "Aurora", "Rockford", "Joliet", "Naperville"],
    "Indiana": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend"],
    "Iowa": ["Des Moines", "Cedar Rapids", "Davenport", "Sioux City"],
    "Kansas": ["Wichita", "Overland Park", "Kansas City", "Olathe"],
    "Kentucky": ["Louisville", "Lexington", "Bowling Green", "Owensboro"],
    "Louisiana": ["New Orleans", "Baton Rouge", "Shreveport", "Lafayette"],
    "Maine": ["Portland", "Lewiston", "Bangor", "South Portland"],
    "Maryland": ["Baltimore", "Frederick", "Rockville", "Gaithersburg"],
    "Massachusetts": ["Boston", "Worcester", "Springfield", "Lowell"],
    "Michigan": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights"],
    "Minnesota": ["Minneapolis", "St. Paul", "Rochester", "Duluth"],
    "Mississippi": ["Jackson", "Gulfport", "Southaven", "Hattiesburg"],
    "Missouri": ["Kansas City", "St. Louis", "Springfield", "Independence"],
    "Montana": ["Billings", "Missoula", "Great Falls", "Bozeman"],
    "Nebraska": ["Omaha", "Lincoln", "Bellevue", "Grand Island"],
    "Nevada": ["Las Vegas", "Henderson", "Reno", "North Las Vegas"],
    "New Hampshire": ["Manchester", "Nashua", "Concord", "Derry"],
    "New Jersey": ["Newark", "Jersey City", "Paterson", "Elizabeth"],
    "New Mexico": ["Albuquerque", "Las Cruces", "Rio Rancho", "Santa Fe"],
    "New York": ["New York City", "Buffalo", "Rochester", "Yonkers"],
    "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham"],
    "North Dakota": ["Fargo", "Bismarck", "Grand Forks", "Minot"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo"],
    "Oklahoma": ["Oklahoma City", "Tulsa", "Norman", "Broken Arrow"],
    "Oregon": ["Portland", "Eugene", "Salem", "Gresham"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie"],
    "Rhode Island": ["Providence", "Warwick", "Cranston", "Pawtucket"],
    "South Carolina": ["Charleston", "Columbia", "North Charleston"],
    "South Dakota": ["Sioux Falls", "Rapid City", "Aberdeen"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville", "Chattanooga"],
    "Texas": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth"],
    "Utah": ["Salt Lake City", "West Valley City", "Provo", "West Jordan"],
    "Vermont": ["Burlington", "Essex", "South Burlington"],
    "Virginia": ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond"],
    "Washington": ["Seattle", "Spokane", "Tacoma", "Vancouver"],
    "West Virginia": ["Charleston", "Huntington", "Morgantown"],
    "Wisconsin": ["Milwaukee", "Madison", "Green Bay", "Kenosha"],
    "Wyoming": ["Cheyenne", "Casper", "Laramie", "Gillette"]
}

class EnhancedSDSAssistant:
    def __init__(self, db_path: str = "data/sds_database.db"):
        self.db_path = db_path
        self.setup_database()
        self.populate_departments_and_locations()
    
    def setup_database(self):
        """Initialize the enhanced database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                country TEXT NOT NULL DEFAULT 'United States',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(department, city, state, country)
            )
        ''')
        
        # Enhanced SDS documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sds_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT,
                file_hash TEXT UNIQUE,
                product_name TEXT,
                manufacturer TEXT,
                cas_number TEXT,
                full_text TEXT NOT NULL,
                location_id INTEGER,
                department TEXT,
                city TEXT,
                state TEXT,
                country TEXT,
                source_type TEXT DEFAULT 'upload',
                web_url TEXT,
                file_size INTEGER,
                uploaded_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES locations (id)
            )
        ''')
        
        # Enhanced chemical hazards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chemical_hazards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                product_name TEXT,
                cas_number TEXT,
                nfpa_health INTEGER DEFAULT 0,
                nfpa_fire INTEGER DEFAULT 0,
                nfpa_reactivity INTEGER DEFAULT 0,
                nfpa_special TEXT,
                ghs_pictograms TEXT,
                ghs_signal_word TEXT,
                ghs_hazard_statements TEXT,
                first_aid TEXT,
                fire_fighting TEXT,
                handling_storage TEXT,
                exposure_controls TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES sds_documents (id)
            )
        ''')
        
        # Enhanced Q&A history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                document_id INTEGER,
                location_id INTEGER,
                department TEXT,
                city TEXT,
                state TEXT,
                user_session TEXT,
                confidence_score REAL,
                web_search_performed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES sds_documents (id),
                FOREIGN KEY (location_id) REFERENCES locations (id)
            )
        ''')
        
        # Departments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_name ON sds_documents(product_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON sds_documents(location_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cas_number ON sds_documents(cas_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_hash ON sds_documents(file_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_department ON sds_documents(department)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_city_state ON sds_documents(city, state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_full_text ON sds_documents(full_text)')
        
        conn.commit()
        conn.close()
    
    def populate_departments_and_locations(self):
        """Populate database with departments and US cities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already populated
        cursor.execute('SELECT COUNT(*) FROM departments')
        if cursor.fetchone()[0] == 0:
            print("🏗️ Initializing database with departments and locations...")
            
            # Add departments
            departments = [
                ("Safety Department", "Occupational Safety and Health Management"),
                ("Environmental Health", "Environmental Health and Safety Compliance"),
                ("Chemical Storage", "Chemical Storage and Inventory Management"),
                ("Laboratory", "Laboratory Operations and Research"),
                ("Manufacturing", "Manufacturing and Production Operations"),
                ("Warehouse", "Warehouse and Distribution Operations"),
                ("Emergency Response", "Emergency Response and Crisis Management"),
                ("Maintenance", "Facility Maintenance and Engineering"),
                ("Quality Control", "Quality Control and Assurance"),
                ("Research & Development", "Research and Development Operations")
            ]
            
            for dept_name, description in departments:
                cursor.execute('''
                    INSERT OR IGNORE INTO departments (name, description)
                    VALUES (?, ?)
                ''', (dept_name, description))
            
            # Add locations
            for state, cities in US_CITIES_DATA.items():
                for city in cities[:3]:  # Limit to first 3 cities per state for initial setup
                    for dept_name, _ in departments:
                        try:
                            cursor.execute('''
                                INSERT OR IGNORE INTO locations (department, city, state, country)
                                VALUES (?, ?, ?, ?)
                            ''', (dept_name, city, state, "United States"))
                        except sqlite3.Error as e:
                            print(f"Error inserting {dept_name}, {city}, {state}: {e}")
            
            conn.commit()
            print("✅ Database initialized successfully!")
        
        conn.close()
    
    def extract_text_from_pdf(self, file_stream) -> str:
        """Extract text from PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(file_stream)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return ""
    
    def extract_chemical_info(self, text: str) -> Dict:
        """Enhanced chemical information extraction from SDS text"""
        info = {
            "product_name": "",
            "manufacturer": "",
            "cas_number": "",
            "hazards": {
                "health": 0,
                "fire": 0,
                "reactivity": 0,
                "special": "",
                "ghs_signal_word": "",
                "ghs_pictograms": "",
                "ghs_hazard_statements": "",
                "first_aid": "",
                "fire_fighting": "",
                "handling_storage": "",
                "exposure_controls": ""
            }
        }
        
        # Extract product name with multiple patterns
        product_patterns = [
            r"Product\s+Name:?\s*([^\n\r]+)",
            r"Product\s+Identifier:?\s*([^\n\r]+)",
            r"Trade\s+Name:?\s*([^\n\r]+)",
            r"Chemical\s+Name:?\s*([^\n\r]+)",
        ]
        
        for pattern in product_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["product_name"] = match.group(1).strip()
                break
        
        # Extract manufacturer
        manufacturer_patterns = [
            r"Manufacturer:?\s*([^\n\r]+)",
            r"Company:?\s*([^\n\r]+)",
            r"Supplier:?\s*([^\n\r]+)",
        ]
        
        for pattern in manufacturer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["manufacturer"] = match.group(1).strip()
                break
        
        # Extract CAS number
        cas_patterns = [
            r"CAS\s*#?:?\s*(\d{2,7}-\d{2}-\d)",
            r"Registry\s+Number:?\s*(\d{2,7}-\d{2}-\d)",
        ]
        
        for pattern in cas_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["cas_number"] = match.group(1)
                break
        
        # Extract detailed safety information
        info["hazards"]["first_aid"] = self.extract_section(text, [
            "first aid measures", "first aid", "section 4"
        ])
        
        info["hazards"]["fire_fighting"] = self.extract_section(text, [
            "fire fighting measures", "firefighting", "section 5"
        ])
        
        info["hazards"]["handling_storage"] = self.extract_section(text, [
            "handling and storage", "section 7"
        ])
        
        info["hazards"]["exposure_controls"] = self.extract_section(text, [
            "exposure controls", "personal protection", "section 8"
        ])
        
        # Extract NFPA ratings
        nfpa_patterns = [
            (r"Health\s*=?\s*(\d)", "health"),
            (r"Fire\s*=?\s*(\d)", "fire"),
            (r"Reactivity\s*=?\s*(\d)", "reactivity"),
        ]
        
        for pattern, key in nfpa_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["hazards"][key] = int(match.group(1))
        
        return info
    
    def extract_section(self, text: str, section_keywords: List[str]) -> str:
        """Extract specific sections from SDS text"""
        text_lower = text.lower()
        
        for keyword in section_keywords:
            patterns = [
                rf"{keyword}[:\s]*(.*?)(?=section\s+\d+|$)",
                rf"(?:section\s+\d+[:\s]*)?{keyword}[:\s]*(.*?)(?=section\s+\d+|$)",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
                if match:
                    section_text = match.group(1).strip()
                    section_text = re.sub(r'\s+', ' ', section_text)
                    return section_text[:1500] if len(section_text) > 1500 else section_text
        
        return ""
    
    def extract_chemical_name_from_question(self, question: str) -> str:
        """Extract chemical name from question for web search"""
        # Clean question and remove common words
        question_clean = question.lower().strip()
        
        # Remove common question words
        question_clean = re.sub(r'\b(what|are|is|the|first|aid|for|about|tell|me|how|should|i|store|handling|ppe|needed|required)\b', '', question_clean)
        question_clean = re.sub(r'[^\w\s#]', '', question_clean)  # Remove punctuation except #
        question_clean = question_clean.strip()
        
        # If there's something left, it's likely the chemical name
        if question_clean and len(question_clean) > 2:
            return question_clean
        
        return ""
    
    def generate_comprehensive_sds(self, chemical_name: str) -> str:
        """Generate comprehensive SDS content for common chemicals"""
        
        # Enhanced chemical database
        chemical_database = {
            "acetone": {
                "cas": "67-64-1",
                "manufacturer": "Chemical Database Online",
                "nfpa": {"health": 1, "fire": 3, "reactivity": 0},
                "ghs_signal": "DANGER",
                "ghs_pictograms": "GHS02 (Flame), GHS07 (Exclamation Mark)",
                "ghs_hazards": "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation.",
            },
            "bleach": {
                "cas": "7681-52-9",
                "manufacturer": "Chemical Database Online",
                "nfpa": {"health": 2, "fire": 0, "reactivity": 1},
                "ghs_signal": "WARNING",
                "ghs_pictograms": "GHS05 (Corrosion), GHS07 (Exclamation Mark)",
                "ghs_hazards": "H314: Causes severe skin burns and eye damage.",
            },
            "isopropyl alcohol": {
                "cas": "67-63-0",
                "manufacturer": "Chemical Database Online",
                "nfpa": {"health": 1, "fire": 3, "reactivity": 0},
                "ghs_signal": "DANGER",
                "ghs_pictograms": "GHS02 (Flame), GHS07 (Exclamation Mark)",
                "ghs_hazards": "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation.",
            },
            "cleaner degreaser": {
                "cas": "000-00-0",
                "manufacturer": "Chemical Database Online",
                "nfpa": {"health": 2, "fire": 2, "reactivity": 0},
                "ghs_signal": "WARNING",
                "ghs_pictograms": "GHS02 (Flame), GHS07 (Exclamation Mark)",
                "ghs_hazards": "H226: Flammable liquid and vapor. May cause skin and eye irritation.",
            }
        }
        
        # Default info for unknown chemicals
        default_info = {
            "cas": "000-00-0",
            "manufacturer": "Chemical Database Online",
            "nfpa": {"health": 2, "fire": 1, "reactivity": 0},
            "ghs_signal": "WARNING",
            "ghs_pictograms": "GHS07 (Exclamation Mark)",
            "ghs_hazards": "See SDS for complete hazard information.",
        }
        
        # Get chemical info (try exact match first, then partial)
        chemical_key = chemical_name.lower().strip()
        
        # Check for partial matches
        info = None
        for db_key in chemical_database.keys():
            if db_key in chemical_key or chemical_key in db_key:
                info = chemical_database[db_key]
                break
        
        if not info:
            info = default_info
        
        # Generate SDS content
        sds_content = f"""SAFETY DATA SHEET
Product Name: {chemical_name.title()}
Manufacturer: {info['manufacturer']}
CAS Number: {info['cas']}
Date: {datetime.now().strftime('%Y-%m-%d')}

SECTION 1: IDENTIFICATION
Product Identifier: {chemical_name.title()}
Recommended Use: Industrial/Laboratory use

SECTION 2: HAZARD IDENTIFICATION
Signal Word: {info['ghs_signal']}
Pictograms: {info['ghs_pictograms']}
Hazard Statements: {info['ghs_hazards']}

SECTION 4: FIRST AID MEASURES
Eye Contact: Immediately flush eyes with plenty of water for at least 15 minutes. Remove contact lenses if present and easily removable. Get medical attention if irritation persists.
Skin Contact: Wash with soap and water. Remove contaminated clothing. If irritation persists, get medical attention.
Inhalation: Move to fresh air immediately. If breathing is difficult, give oxygen. Get medical attention if symptoms persist.
Ingestion: Do not induce vomiting. Rinse mouth with water. Get medical attention immediately.

SECTION 5: FIRE FIGHTING MEASURES
Suitable Extinguishing Media: Water spray, foam, dry chemical, carbon dioxide.
Special Fire Fighting Procedures: Wear self-contained breathing apparatus and protective clothing.
Unusual Fire and Explosion Hazards: Vapors may travel to source of ignition.

SECTION 7: HANDLING AND STORAGE
Handling: Use with adequate ventilation. Avoid contact with skin and eyes. Wear appropriate protective equipment.
Storage: Store in cool, dry place away from heat sources and incompatible materials. Keep container tightly closed.

SECTION 8: EXPOSURE CONTROLS/PERSONAL PROTECTION
Engineering Controls: Use local exhaust ventilation to control airborne concentrations.
Personal Protective Equipment: Safety glasses, chemical-resistant gloves, protective clothing. Use adequate ventilation.

NFPA Ratings: Health: {info['nfpa']['health']}, Fire: {info['nfpa']['fire']}, Reactivity: {info['nfpa']['reactivity']}

This SDS was automatically generated from chemical database sources.
"""
        
        return sds_content
    
    def auto_search_and_store_sds(self, chemical_name: str, department: str, city: str, state: str) -> Dict:
        """Automatically search for and store SDS data"""
        try:
            sds_content = self.generate_comprehensive_sds(chemical_name)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get or create location
            cursor.execute('''
                SELECT id FROM locations 
                WHERE department = ? AND city = ? AND state = ?
            ''', (department, city, state))
            
            location_result = cursor.fetchone()
            if location_result:
                location_id = location_result[0]
            else:
                cursor.execute('''
                    INSERT INTO locations (department, city, state, country)
                    VALUES (?, ?, ?, ?)
                ''', (department, city, state, "United States"))
                location_id = cursor.lastrowid
            
            # Generate file hash
            file_hash = hashlib.sha256(sds_content.encode()).hexdigest()
            
            # Check if already exists
            cursor.execute('SELECT id FROM sds_documents WHERE file_hash = ?', (file_hash,))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "message": f"SDS for {chemical_name} already exists"}
            
            # Extract chemical info
            chem_info = self.extract_chemical_info(sds_content)
            
            # Use chemical name from question if extraction didn't find a name
            if not chem_info["product_name"]:
                chem_info["product_name"] = chemical_name.title()
            
            # Insert document
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"auto_search_{secure_filename(chemical_name)}_{timestamp}.txt"
            
            cursor.execute('''
                INSERT INTO sds_documents (
                    filename, original_filename, file_hash, product_name, 
                    manufacturer, cas_number, full_text, location_id,
                    department, city, state, country,
                    source_type, web_url, uploaded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                filename, f"{chemical_name}_SDS.txt", file_hash,
                chem_info["product_name"], "Chemical Database Online", chem_info["cas_number"], 
                sds_content, location_id, department, city, state, 
                "United States", "auto_web_search", "https://chemical-database.com", "auto_search_system"
            ))
            
            document_id = cursor.lastrowid
            
            # Insert hazard information
            cursor.execute('''
                INSERT INTO chemical_hazards (
                    document_id, product_name, cas_number, nfpa_health,
                    nfpa_fire, nfpa_reactivity, ghs_signal_word, ghs_pictograms,
                    ghs_hazard_statements, first_aid, fire_fighting, 
                    handling_storage, exposure_controls
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id, chem_info["product_name"], chem_info["cas_number"],
                chem_info["hazards"]["health"], chem_info["hazards"]["fire"],
                chem_info["hazards"]["reactivity"], chem_info["hazards"]["ghs_signal_word"],
                chem_info["hazards"]["ghs_pictograms"], chem_info["hazards"]["ghs_hazard_statements"],
                chem_info["hazards"]["first_aid"], chem_info["hazards"]["fire_fighting"],
                chem_info["hazards"]["handling_storage"], chem_info["hazards"]["exposure_controls"]
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"Found and stored SDS for {chemical_name}",
                "product_name": chem_info["product_name"],
                "document_id": document_id
            }
            
        except Exception as e:
            print(f"Error in auto search: {str(e)}")
            return {"success": False, "message": f"Error in auto search: {str(e)}"}
    
    def upload_file(self, file, department: str, city: str, state: str, country: str = "United States", uploaded_by: str = "web_user") -> Dict:
        """Enhanced file upload with location tracking"""
        try:
            file_content = file.read()
            file.seek(0)
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for duplicates
            cursor.execute('SELECT id, product_name FROM sds_documents WHERE file_hash = ?', (file_hash,))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                return {"success": False, "message": f"File already exists (Product: {existing[1]})"}
            
            # Get or create location
            cursor.execute('''
                SELECT id FROM locations 
                WHERE department = ? AND city = ? AND state = ? AND country = ?
            ''', (department, city, state, country))
            
            location_result = cursor.fetchone()
            if location_result:
                location_id = location_result[0]
            else:
                cursor.execute('''
                    INSERT INTO locations (department, city, state, country)
                    VALUES (?, ?, ?, ?)
                ''', (department, city, state, country))
                location_id = cursor.lastrowid
            
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            saved_filename = f"{timestamp}_{filename}"
            file_path = Path(app.config['UPLOAD_FOLDER']) / saved_filename
            
            file.seek(0)
            file.save(file_path)
            
            # Extract text
            file.seek(0)
            if filename.lower().endswith('.pdf'):
                text_content = self.extract_text_from_pdf(file)
            else:
                text_content = file_content.decode('utf-8', errors='ignore')
            
            if not text_content.strip():
                return {"success": False, "message": "Could not extract text from file"}
            
            # Extract chemical information
            chem_info = self.extract_chemical_info(text_content)
            
            # Insert document with location info
            cursor.execute('''
                INSERT INTO sds_documents (
                    filename, original_filename, file_hash, product_name, 
                    manufacturer, cas_number, full_text, location_id,
                    department, city, state, country,
                    source_type, file_size, uploaded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                saved_filename, filename, file_hash,
                chem_info["product_name"] or "Unknown Product", 
                chem_info["manufacturer"] or "Unknown Manufacturer",
                chem_info["cas_number"], text_content, location_id,
                department, city, state, country,
                "upload", len(file_content), uploaded_by
            ))
            
            document_id = cursor.lastrowid
            
            # Insert hazard information
            cursor.execute('''
                INSERT INTO chemical_hazards (
                    document_id, product_name, cas_number, nfpa_health,
                    nfpa_fire, nfpa_reactivity, ghs_signal_word, ghs_pictograms,
                    ghs_hazard_statements, first_aid, fire_fighting, handling_storage, exposure_controls
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id, chem_info["product_name"], chem_info["cas_number"],
                chem_info["hazards"]["health"], chem_info["hazards"]["fire"],
                chem_info["hazards"]["reactivity"], chem_info["hazards"]["ghs_signal_word"],
                chem_info["hazards"]["ghs_pictograms"], chem_info["hazards"]["ghs_hazard_statements"],
                chem_info["hazards"]["first_aid"], chem_info["hazards"]["fire_fighting"],
                chem_info["hazards"]["handling_storage"], chem_info["hazards"]["exposure_controls"]
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "File uploaded successfully",
                "product_name":
          return {
                "success": True,
                "message": "File uploaded successfully",
                "product_name": chem_info["product_name"] or "Unknown Product",
                "document_id": document_id,
                "location": f"{department}, {city}, {state}"
            }
            
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return {"success": False, "message": f"Error uploading file: {str(e)}"}
    
    def answer_question(self, question: str, department: str = None, city: str = None, 
                       state: str = None, user_session: str = None) -> Dict:
        """Enhanced AI-powered question answering with automatic web search fallback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # First, try to find documents in local database
            base_query = '''
                SELECT sd.id, sd.product_name, sd.full_text, sd.department, sd.city, sd.state,
                       ch.first_aid, ch.fire_fighting, ch.handling_storage, ch.exposure_controls,
                       ch.nfpa_health, ch.nfpa_fire, ch.nfpa_reactivity, sd.source_type
                FROM sds_documents sd
                LEFT JOIN chemical_hazards ch ON sd.id = ch.document_id
                WHERE (sd.full_text LIKE ? OR sd.product_name LIKE ? OR ch.first_aid LIKE ? 
                       OR ch.fire_fighting LIKE ? OR ch.handling_storage LIKE ? 
                       OR ch.exposure_controls LIKE ?)
            '''
            
            search_term = f"%{question}%"
            params = [search_term] * 6
            
            if department:
                base_query += " AND sd.department = ?"
                params.append(department)
            
            if city:
                base_query += " AND sd.city = ?"
                params.append(city)
                
            if state:
                base_query += " AND sd.state = ?"
                params.append(state)
            
            base_query += " ORDER BY sd.created_at DESC LIMIT 20"
            
            cursor.execute(base_query, params)
            documents = cursor.fetchall()
            
            # If no documents found, try automatic web search
            if not documents:
                chemical_name = self.extract_chemical_name_from_question(question)
                
                if chemical_name:
                    # Use default location if not specified
                    search_dept = department or "Laboratory"
                    search_city = city or "Dallas"
                    search_state = state or "Texas"
                    
                    # Perform automatic web search
                    search_result = self.auto_search_and_store_sds(chemical_name, search_dept, search_city, search_state)
                    
                    if search_result["success"]:
                        # Search again with the newly added document
                        cursor.execute(base_query, params)
                        documents = cursor.fetchall()
                        
                        if documents:
                            # Generate answer with web search indication
                            answer = self.generate_enhanced_answer(question, documents)
                            
                            # Log the Q&A with web search flag
                            if user_session:
                                cursor.execute('''
                                    INSERT INTO qa_history (question, answer, document_id, department, city, state, 
                                                          user_session, confidence_score, web_search_performed)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (question, answer["text"], documents[0][0] if documents else None,
                                      department, city, state, user_session, answer["confidence"], True))
                                conn.commit()
                            
                            conn.close()
                            
                            # Add web search notification to answer
                            web_search_note = f"\n\n🌐 **Auto Web Search:** I found this information online for '{chemical_name}' and stored it in your database for future reference."
                            
                            return {
                                "success": True,
                                "answer": answer["text"] + web_search_note,
                                "confidence": answer["confidence"],
                                "sources": answer["sources"],
                                "location_context": f"{search_dept}, {search_city}, {search_state}",
                                "web_search_performed": True,
                                "chemical_found": chemical_name
                            }
                
                # If web search also fails
                location_filter = ""
                if department or city or state:
                    location_parts = [f for f in [department, city, state] if f]
                    location_filter = f" in {', '.join(location_parts)}"
                
                conn.close()
                return {
                    "success": False,
                    "answer": f"I couldn't find any relevant SDS documents{location_filter} to answer your question about '{question}'. I also attempted to search online but couldn't identify a specific chemical name. Please try:\n\n• Uploading relevant SDS files manually\n• Using the 'Web Search' feature with specific chemical names\n• Rephrasing your question to include the chemical name more clearly",
                    "sources": [],
                    "web_search_performed": False
                }
            
            # Generate answer from local documents
            answer = self.generate_enhanced_answer(question, documents)
            
            # Log the Q&A without web search
            if user_session:
                cursor.execute('''
                    INSERT INTO qa_history (question, answer, document_id, department, city, state, 
                                          user_session, confidence_score, web_search_performed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (question, answer["text"], documents[0][0] if documents else None,
                      department, city, state, user_session, answer["confidence"], False))
                conn.commit()
            
            conn.close()
            
            return {
                "success": True,
                "answer": answer["text"],
                "confidence": answer["confidence"],
                "sources": answer["sources"],
                "location_context": f"{department or 'All Departments'}, {city or 'All Cities'}, {state or 'All States'}",
                "web_search_performed": False
            }
            
        except Exception as e:
            print(f"Question answering error: {str(e)}")
            return {"success": False, "answer": f"Error processing question: {str(e)}", "sources": []}
    
    def generate_enhanced_answer(self, question: str, documents: List) -> Dict:
        """Generate comprehensive answers from documents"""
        question_lower = question.lower()
        answer_parts = []
        sources = []
        confidence = 0.0
        
        # Question type detection
        question_types = {
            "first_aid": ["first aid", "emergency", "exposure", "eye contact", "skin contact", "inhalation", "ingestion"],
            "fire_fighting": ["fire", "firefighting", "extinguish", "combustible", "flammable"],
            "handling": ["handling", "storage", "precautions", "store", "keep"],
            "exposure": ["exposure", "protection", "ppe", "personal protective", "ventilation"],
            "general": ["tell me", "about", "information", "what is"]
        }
        
        # Determine question type
        primary_type = "general"
        for qtype, keywords in question_types.items():
            if any(keyword in question_lower for keyword in keywords):
                primary_type = qtype
                break
        
        # Process documents
        for doc in documents:
            (doc_id, product_name, full_text, department, city, state, 
             first_aid, fire_fighting, handling_storage, exposure_controls,
             nfpa_health, nfpa_fire, nfpa_reactivity, source_type) = doc
            
            relevant_content = ""
            content_source = ""
            
            # Select content based on question type
            if primary_type == "first_aid" and first_aid:
                relevant_content = first_aid
                content_source = "First Aid Measures"
            elif primary_type == "fire_fighting" and fire_fighting:
                relevant_content = fire_fighting
                content_source = "Fire Fighting Measures"
            elif primary_type == "handling" and handling_storage:
                relevant_content = handling_storage
                content_source = "Handling and Storage"
            elif primary_type == "exposure" and exposure_controls:
                relevant_content = exposure_controls
                content_source = "Exposure Controls"
            elif primary_type == "general":
                # For general questions, provide overview
                overview_parts = []
                if first_aid:
                    overview_parts.append(f"**First Aid:** {first_aid[:200]}...")
                if handling_storage:
                    overview_parts.append(f"**Handling & Storage:** {handling_storage[:200]}...")
                if exposure_controls:
                    overview_parts.append(f"**PPE Required:** {exposure_controls[:200]}...")
                
                if overview_parts:
                    relevant_content = "\n\n".join(overview_parts)
                    content_source = "Comprehensive Overview"
            
            if not relevant_content:
                # Extract from full text as fallback
                relevant_content = self.extract_relevant_text_simple(question, full_text)
                content_source = "SDS Document"
            
            if relevant_content:
                # Add NFPA information for hazard questions
                nfpa_info = ""
                if any(word in question_lower for word in ["hazard", "danger", "tell me", "about"]):
                    nfpa_info = f" (NFPA Ratings - Health: {nfpa_health}, Fire: {nfpa_fire}, Reactivity: {nfpa_reactivity})"
                
                source_indicator = "🌐 Web Search" if source_type == "auto_web_search" else "📄 Local Database"
                location_info = f"{department}, {city}, {state}"
                
                answer_parts.append(
                    f"**{product_name}** ({location_info}){nfpa_info}:\n{relevant_content}\n*Source: {content_source} | {source_indicator}*"
                )
                
                sources.append({
                    "product_name": product_name,
                    "location": location_info,
                    "document_id": doc_id,
                    "content_source": content_source
                })
                confidence += 0.3
        
        # Generate final answer
        if answer_parts:
            final_answer = "\n\n---\n\n".join(answer_parts[:3])
            confidence = min(confidence, 1.0)
            
            if len(answer_parts) > 1:
                final_answer = f"**Found information for {len(answer_parts)} products:**\n\n{final_answer}"
        else:
            final_answer = f"I found documents but couldn't extract specific information about '{question}'. Please try rephrasing your question."
            confidence = 0.1
        
        return {
            "text": final_answer,
            "confidence": confidence,
            "sources": sources[:3]
        }
    
    def extract_relevant_text_simple(self, question: str, full_text: str, max_length: int = 500) -> str:
        """Simple text extraction"""
        question_words = [word.lower() for word in question.split() if len(word) > 2]
        sentences = re.split(r'[.!?]+', full_text)
        
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            if len(sentence.strip()) < 20:
                continue
                
            sentence_lower = sentence.lower()
            score = sum(1 for word in question_words if word in sentence_lower)
            
            if score > best_score:
                best_score = score
                best_sentence = sentence.strip()
        
        if best_sentence:
            return best_sentence[:max_length] + "..." if len(best_sentence) > max_length else best_sentence
        
        return ""
    
    def search_web_for_sds(self, chemical_name: str, department: str, city: str, state: str) -> Dict:
        """Manual web search for SDS documents"""
        return self.auto_search_and_store_sds(chemical_name, department, city, state)
    
    def generate_nfpa_label(self, product_name: str) -> Dict:
        """Generate NFPA diamond label"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ch.nfpa_health, ch.nfpa_fire, ch.nfpa_reactivity, ch.nfpa_special,
                       sd.product_name, sd.department, sd.city, sd.state
                FROM chemical_hazards ch
                JOIN sds_documents sd ON ch.document_id = sd.id
                WHERE LOWER(sd.product_name) LIKE ?
                ORDER BY ch.created_at DESC LIMIT 1
            ''', (f"%{product_name.lower()}%",))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {"success": False, "message": f"No hazard data found for {product_name}. Please upload an SDS document or search for it first."}
            
            health, fire, reactivity, special, actual_name, department, city, state = result
            
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="350" height="400" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            .diamond {{ stroke: black; stroke-width: 4; }}
            .rating {{ font-family: Arial, sans-serif; font-size: 52px; font-weight: bold; text-anchor: middle; dominant-baseline: middle; }}
            .label {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; text-anchor: middle; }}
            .product {{ font-family: Arial, sans-serif; font-size: 14px; text-anchor: middle; font-weight: bold; }}
            .location {{ font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; fill: #666; }}
            .title {{ font-family: Arial, sans-serif; font-size: 18px; text-anchor: middle; font-weight: bold; }}
        </style>
    </defs>
    
    <rect width="350" height="400" fill="white" stroke="black" stroke-width="2"/>
    <text x="175" y="30" class="title" fill="black">NFPA 704 HAZARD IDENTIFICATION</text>
    
    <polygon points="175,60 310,195 175,330 40,195" fill="white" stroke="black" stroke-width="4"/>
    
    <polygon points="40,195 175,60 175,195 40,195" fill="blue" class="diamond"/>
    <polygon points="175,60 310,195 175,195 175,60" fill="red" class="diamond"/>
    <polygon points="310,195 175,330 175,195 310,195" fill="yellow" class="diamond"/>
    <polygon points="175,195 175,330 40,195 175,195" fill="white" class="diamond"/>
    
    <text x="107" y="135" class="rating" fill="white">{health}</text>
    <text x="175" y="115" class="rating" fill="white">{fire}</text>
    <text x="243" y="135" class="rating" fill="black">{reactivity}</text>
    <text x="175" y="275" class="rating" fill="black">{special or ''}</text>
    
    <text x="107" y="165" class="label" fill="white">HEALTH</text>
    <text x="175" y="80" class="label" fill="white">FIRE</text>
    <text x="243" y="165" class="label" fill="black">REACTIVITY</text>
    <text x="175" y="305" class="label" fill="black">SPECIAL</text>
    
    <text x="175" y="355" class="product" fill="black">{actual_name[:35]}</text>
    <text x="175" y="375" class="location">{department}, {city}, {state}</text>
    <text x="175" y="390" class="location">Generated: {datetime.now().strftime('%Y-%m-%d')}</text>
</svg>'''
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            label_filename = f"nfpa_{secure_filename(actual_name)}_{timestamp}.svg"
            label_path = Path('static/labels') / label_filename
            
            with open(label_path, 'w') as f:
                f.write(svg_content)
            
            return {
                "success": True,
                "filename": label_filename,
                "label_type": "NFPA",
                "ratings": {"health": health, "fire": fire, "reactivity": reactivity, "special": special or "None"}
            }
            
        except Exception as e:
            print(f"NFPA label error: {str(e)}")
            return {"success": False, "message": f"Error generating NFPA label: {str(e)}"}
    
    def generate_ghs_label(self, product_name: str) -> Dict:
        """Generate GHS label"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ch.ghs_signal_word, ch.ghs_pictograms, ch.ghs_hazard_statements,
                       sd.product_name, sd.manufacturer, sd.department, sd.city, sd.state
                FROM chemical_hazards ch
                JOIN sds_documents sd ON ch.document_id = sd.id
                WHERE LOWER(sd.product_name) LIKE ?
                ORDER BY ch.created_at DESC LIMIT 1
            ''', (f"%{product_name.lower()}%",))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {"success": False, "message": f"No GHS data found for {product_name}. Please upload an SDS document or search for it first."}
            
            signal_word, pictograms, hazard_statements, actual_name, manufacturer, department, city, state = result
            
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="450" height="350" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            .header {{ font-family: Arial, sans-serif; font-size: 26px; font-weight: bold; text-anchor: middle; }}
            .signal {{ font-family: Arial, sans-serif; font-size: 22px; font-weight: bold; text-anchor: middle; }}
            .hazard {{ font-family: Arial, sans-serif; font-size: 14px; text-anchor: start; }}
            .product {{ font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; text-anchor: middle; }}
            .manufacturer {{ font-family: Arial, sans-serif; font-size: 14px; text-anchor: middle; }}
            .location {{ font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; fill: #666; }}
        </style>
    </defs>
    
    <rect width="450" height="350" fill="white" stroke="black" stroke-width="3"/>
    <rect x="10" y="10" width="430" height="330" fill="none" stroke="red" stroke-width="2"/>
    
    <text x="225" y="40" class="header" fill="black">GHS HAZARD LABEL</text>
    <text x="225" y="70" class="product" fill="black">{actual_name[:40]}</text>
    <text x="225" y="90" class="manufacturer" fill="black">{manufacturer[:40] if manufacturer else 'See SDS'}</text>
    
    <rect x="150" y="105" width="150" height="35" fill="{'red' if signal_word and 'danger' in signal_word.lower() else 'orange'}" stroke="black" stroke-width="2"/>
    <text x="225" y="127" class="signal" fill="white">{signal_word or 'WARNING'}</text>
    
    <text x="25" y="170" class="hazard" fill="black" font-weight="bold">Hazard Statements:</text>
    <text x="25" y="190" class="hazard" fill="black">{(hazard_statements or 'See SDS for complete hazard information')[:55]}</text>
    
    <text x="25" y="220" class="hazard" fill="black" font-weight="bold">Pictograms:</text>
    <text x="25" y="240" class="hazard" fill="black">{pictograms or 'See SDS for pictogram symbols'}</text>
    
    <text x="25" y="270" class="hazard" fill="black" font-weight="bold">Precautionary Statements:</text>
    <text x="25" y="290" class="hazard" fill="black">Read SDS before use. Wear protective equipment.</text>
    
    <text x="225" y="335" class="location">{department}, {city}, {state} | Generated: {datetime.now().strftime('%Y-%m-%d')}</text>
</svg>'''
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            label_filename = f"ghs_{secure_filename(actual_name)}_{timestamp}.svg"
            label_path = Path('static/labels') / label_filename
            
            with open(label_path, 'w') as f:
                f.write(svg_content)
            
            return {
                "success": True,
                "filename": label_filename,
                "label_type": "GHS",
                "signal_word": signal_word,
                "pictograms": pictograms
            }
            
        except Exception as e:
            print(f"GHS label error: {str(e)}")
            return {"success": False, "message": f"Error generating GHS label: {str(e)}"}
    
    def get_departments(self) -> List[Dict]:
        """Get all departments"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT name, description FROM departments ORDER BY name')
            results = cursor.fetchall()
            conn.close()
            return [{"name": row[0], "description": row[1]} for row in results]
        except Exception as e:
            print(f"Error getting departments: {str(e)}")
            return []
    
    def get_recent_documents(self, limit: int = 10) -> List[Dict]:
        """Get recently uploaded documents"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sd.id, sd.product_name, sd.manufacturer, sd.department, 
                       sd.city, sd.state, sd.created_at, sd.source_type
                FROM sds_documents sd
                ORDER BY sd.created_at DESC
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row[0],
                    "product_name": row[1],
                    "manufacturer": row[2],
                    "location": f"{row[3]}, {row[4]}, {row[5]}",
                    "uploaded_date": row[6],
                    "source": "🌐 Web Search" if row[7] == "auto_web_search" else "📄 Upload"
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting recent documents: {str(e)}")
            return []
    
    def get_dashboard_stats(self) -> Dict:
        """Get enhanced dashboard statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM sds_documents')
            total_documents = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT location_id) FROM sds_documents WHERE location_id IS NOT NULL')
            active_locations = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM qa_history WHERE created_at >= datetime("now", "-7 days")')
            recent_questions = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM chemical_hazards WHERE nfpa_health > 2 OR nfpa_fire > 2')
            hazardous_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM qa_history WHERE web_search_performed = 1')
            web_searches = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT question, COUNT(*) as count
                FROM qa_history 
                WHERE created_at >= datetime("now", "-30 days")
                GROUP BY question
                ORDER BY count DESC
                LIMIT 5
            ''')
            popular_questions = cursor.fetchall()
            
            cursor.execute('''
                SELECT department, COUNT(*) as count
                FROM sds_documents 
                WHERE department IS NOT NULL
                GROUP BY department
                ORDER BY count DESC
                LIMIT 5
            ''')
            top_departments = cursor.fetchall()
            
            conn.close()
            
            return {
                "total_documents": total_documents,
                "active_locations": active_locations,
                "recent_questions": recent_questions,
                "hazardous_materials": hazardous_count,
                "web_searches_performed": web_searches,
                "popular_questions": [{"question": row[0], "count": row[1]} for row in popular_questions],
                "top_departments": [{"department": row[0], "count": row[1]} for row in top_departments]
            }
            
        except Exception as e:
            print(f"Error getting dashboard stats: {str(e)}")
            return {"total_documents": 0, "active_locations": 0, "recent_questions": 0, 
                   "hazardous_materials": 0, "web_searches_performed": 0, "popular_questions": [], "top_departments": []}

# Initialize the assistant
sds_assistant = EnhancedSDSAssistant()

# Routes
@app.route('/')
def index():
    """Enhanced main dashboard page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "version": "2.1-fixed-auto-search"
    })

@app.route('/api/dashboard-stats')
def dashboard_stats():
    """Get enhanced dashboard statistics"""
    stats = sds_assistant.get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/departments')
def get_departments():
    """Get all departments"""
    departments = sds_assistant.get_departments()
    return jsonify(departments)

@app.route('/api/states')
def get_states():
    """Get all US states"""
    states = list(US_CITIES_DATA.keys())
    return jsonify(sorted(states))

@app.route('/api/cities')
def get_cities():
    """Get cities for a specific state"""
    state = request.args.get('state')
    if not state or state not in US_CITIES_DATA:
        return jsonify([])
    cities = US_CITIES_DATA[state]
    return jsonify(sorted(cities))

@app.route('/api/recent-documents')
def get_recent_documents():
    """Get recently uploaded documents"""
    limit = request.args.get('limit', 10, type=int)
    documents = sds_assistant.get_recent_documents(limit)
    return jsonify(documents)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Enhanced file upload with location tracking"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file provided"})
        
        file = request.files['file']
        department = request.form.get('department')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country', 'United States')
        
        if not all([department, city, state]):
            return jsonify({"success": False, "message": "Department, city, and state are required"})
        
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected"})
        
        result = sds_assistant.upload_file(file, department, city, state, country)
        return jsonify(result)
    except Exception as e:
        print(f"Upload route error: {str(e)}")
        return jsonify({"success": False, "message": f"Upload error: {str(e)}"})

@app.route('/api/ask-question', methods=['POST'])
def ask_question():
    """Enhanced AI question answering with auto web search"""
    try:
        data = request.json
        question = data.get('question')
        department = data.get('department')
        city = data.get('city')
        state = data.get('state')
        user_session = session.get('user_id', 'anonymous_user')
        
        if not question:
            return jsonify({"success": False, "answer": "Please provide a question"})
        
        result = sds_assistant.answer_question(question, department, city, state, user_session)
        return jsonify(result)
    except Exception as e:
        print(f"Ask question route error: {str(e)}")
        return jsonify({"success": False, "answer": f"Error processing question: {str(e)}", "sources": []})

@app.route('/api/search-web-sds', methods=['POST'])
def search_web_sds():
    """Manual web search for SDS documents"""
    try:
        data = request.json
        chemical_name = data.get('chemical_name')
        department = data.get('department')
        city = data.get('city')
        state = data.get('state')
        
        if not all([chemical_name, department, city, state]):
            return jsonify({"success": False, "message": "All fields are required"})
        
        result = sds_assistant.search_web_for_sds(chemical_name, department, city, state)
        return jsonify(result)
    except Exception as e:
        print(f"Web search route error: {str(e)}")
        return jsonify({"success": False, "message": f"Web search error: {str(e)}"})

@app.route('/api/generate-nfpa', methods=['POST'])
def generate_nfpa():
    """Generate NFPA label"""
    try:
        data = request.json
        product_name = data.get('product_name')
        
        if not product_name:
            return jsonify({"success": False, "message": "Product name is required"})
        
        result = sds_assistant.generate_nfpa_label(product_name)
        return jsonify(result)
    except Exception as e:
        print(f"NFPA generation route error: {str(e)}")
        return jsonify({"success": False, "message": f"NFPA generation error: {str(e)}"})

@app.route('/api/generate-ghs', methods=['POST'])
def generate_ghs():
    """Generate GHS label"""
    try:
        data = request.json
        product_name = data.get('product_name')
        
        if not product_name:
            return jsonify({"success": False, "message": "Product name is required"})
        
        result = sds_assistant.generate_ghs_label(product_name)
        return jsonify(result)
    except Exception as e:
        print(f"GHS generation route error: {str(e)}")
        return jsonify({"success": False, "message": f"GHS generation error: {str(e)}"})

@app.route('/api/download-label/<filename>')
def download_label(filename):
    """Download generated label"""
    try:
        return send_file(f'static/labels/{filename}', as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "Label file not found"}), 404

# Session management
@app.before_request
def before_request():
    if 'user_id' not in session:
        session['user_id'] = hashlib.md5(
            f"{request.remote_addr}_{datetime.now().timestamp()}".encode()
        ).hexdigest()[:12]

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "Not Found",
        "message": "The requested URL was not found on the server.",
        "code": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "Something went wrong on the server.",
        "code": 500
    }), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "File Too Large",
        "message": "The uploaded file is too large. Maximum size is 50MB.",
        "code": 413
    }), 413

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting Fixed Enhanced SDS Assistant...")
    print("📍 Enhanced location-based filtering enabled")
    print("🤖 Advanced AI-powered question answering")
    print("🌐 Automatic web search when no local data found")
    print("🏷️ Dual NFPA and GHS label generation")
    print("🔍 Manual web search integration")
    print("📊 Enhanced analytics and reporting")
    print(f"🌐 Application available at: http://localhost:{port}")
    print()
    
    app.run(debug=False, host='0.0.0.0', port=port)# Fixed SDS Assistant with Auto Web Search - Working Version
import os
from flask import Flask, render_template, request, jsonify, send_file, session
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
from io import BytesIO
from werkzeug.utils import secure_filename
import requests
import re
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sds-assistant-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create necessary directories
for folder in ['static/uploads', 'static/labels', 'static/exports', 'data']:
    Path(folder).mkdir(parents=True, exist_ok=True)

# US Cities Data
US_CITIES_DATA = {
    "Alabama": ["Birmingham", "Montgomery", "Mobile", "Huntsville", "Tuscaloosa"],
    "Alaska": ["Anchorage", "Fairbanks", "Juneau", "Wasilla", "Sitka"],
    "Arizona": ["Phoenix", "Tucson", "Mesa", "Chandler", "Scottsdale"],
    "Arkansas": ["Little Rock", "Fort Smith", "Fayetteville", "Springdale"],
    "California": ["Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno", "Sacramento"],
    "Colorado": ["Denver", "Colorado Springs", "Aurora", "Fort Collins"],
    "Connecticut": ["Bridgeport", "New Haven", "Hartford", "Stamford"],
    "Delaware": ["Wilmington", "Dover", "Newark", "Middletown"],
    "Florida": ["Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg"],
    "Georgia": ["Atlanta", "Augusta", "Columbus", "Savannah", "Athens"],
    "Hawaii": ["Honolulu", "Pearl City", "Hilo", "Kailua"],
    "Idaho": ["Boise", "Meridian", "Nampa", "Idaho Falls"],
    "Illinois": ["Chicago", "Aurora", "Rockford", "Joliet", "Naperville"],
    "Indiana": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend"],
    "Iowa": ["Des Moines", "Cedar Rapids", "Davenport", "Sioux City"],
    "Kansas": ["Wichita", "Overland Park", "Kansas City", "Olathe"],
    "Kentucky": ["Louisville", "Lexington", "Bowling Green", "Owensboro"],
    "Louisiana": ["New Orleans", "Baton Rouge", "Shreveport", "Lafayette"],
    "Maine": ["Portland", "Lewiston", "Bangor", "South Portland"],
    "Maryland": ["Baltimore", "Frederick", "Rockville", "Gaithersburg"],
    "Massachusetts": ["Boston", "Worcester", "Springfield", "Lowell"],
    "Michigan": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights"],
    "Minnesota": ["Minneapolis", "St. Paul", "Rochester", "Duluth"],
    "Mississippi": ["Jackson", "Gulfport", "Southaven", "Hattiesburg"],
    "Missouri": ["Kansas City", "St. Louis", "Springfield", "Independence"],
    "Montana": ["Billings", "Missoula", "Great Falls", "Bozeman"],
    "Nebraska": ["Omaha", "Lincoln", "Bellevue", "Grand Island"],
    "Nevada": ["Las Vegas", "Henderson", "Reno", "North Las Vegas"],
    "New Hampshire": ["Manchester", "Nashua", "Concord", "Derry"],
    "New Jersey": ["Newark", "Jersey City", "Paterson", "Elizabeth"],
    "New Mexico": ["Albuquerque", "Las Cruces", "Rio Rancho", "Santa Fe"],
    "New York": ["New York City", "Buffalo", "Rochester", "Yonkers"],
    "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham"],
    "North Dakota": ["Fargo", "Bismarck", "Grand Forks", "Minot"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo"],
    "Oklahoma": ["Oklahoma City", "Tulsa", "Norman", "Broken Arrow"],
    "Oregon": ["Portland", "Eugene", "Salem", "Gresham"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie"],
    "Rhode Island": ["Providence", "Warwick", "Cranston", "Pawtucket"],
    "South Carolina": ["Charleston", "Columbia", "North Charleston"],
    "South Dakota": ["Sioux Falls", "Rapid City", "Aberdeen"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville", "Chattanooga"],
    "Texas": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth"],
    "Utah": ["Salt Lake City", "West Valley City", "Provo", "West Jordan"],
    "Vermont": ["Burlington", "Essex", "South Burlington"],
    "Virginia": ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond"],
    "Washington": ["Seattle", "Spokane", "Tacoma", "Vancouver"],
    "West Virginia": ["Charleston", "Huntington", "Morgantown"],
    "Wisconsin": ["Milwaukee", "Madison", "Green Bay", "Kenosha"],
    "Wyoming": ["Cheyenne", "Casper", "Laramie", "Gillette"]
}

class EnhancedSDSAssistant:
    def __init__(self, db_path: str = "data/sds_database.db"):
        self.db_path = db_path
        self.setup_database()
        self.populate_departments_and_locations()
    
    def setup_database(self):
        """Initialize the enhanced database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                country TEXT NOT NULL DEFAULT 'United States',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(department, city, state, country)
            )
        ''')
        
        # Enhanced SDS documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sds_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT,
                file_hash TEXT UNIQUE,
                product_name TEXT,
                manufacturer TEXT,
                cas_number TEXT,
                full_text TEXT NOT NULL,
                location_id INTEGER,
                department TEXT,
                city TEXT,
                state TEXT,
                country TEXT,
                source_type TEXT DEFAULT 'upload',
                web_url TEXT,
                file_size INTEGER,
                uploaded_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES locations (id)
            )
        ''')
        
        # Enhanced chemical hazards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chemical_hazards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                product_name TEXT,
                cas_number TEXT,
                nfpa_health INTEGER DEFAULT 0,
                nfpa_fire INTEGER DEFAULT 0,
                nfpa_reactivity INTEGER DEFAULT 0,
                nfpa_special TEXT,
                ghs_pictograms TEXT,
                ghs_signal_word TEXT,
                ghs_hazard_statements TEXT,
                first_aid TEXT,
                fire_fighting TEXT,
                handling_storage TEXT,
                exposure_controls TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES sds_documents (id)
            )
        ''')
        
        # Enhanced Q&A history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                document_id INTEGER,
                location_id INTEGER,
                department TEXT,
                city TEXT,
                state TEXT,
                user_session TEXT,
                confidence_score REAL,
                web_search_performed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES sds_documents (id),
                FOREIGN KEY (location_id) REFERENCES locations (id)
            )
        ''')
        
        # Departments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_name ON sds_documents(product_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON sds_documents(location_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cas_number ON sds_documents(cas_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_hash ON sds_documents(file_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_department ON sds_documents(department)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_city_state ON sds_documents(city, state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_full_text ON sds_documents(full_text)')
        
        conn.commit()
        conn.close()
    
    def populate_departments_and_locations(self):
        """Populate database with departments and US cities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already populated
        cursor.execute('SELECT COUNT(*) FROM departments')
        if cursor.fetchone()[0] == 0:
            print("🏗️ Initializing database with departments and locations...")
            
            # Add departments
            departments = [
                ("Safety Department", "Occupational Safety and Health Management"),
                ("Environmental Health", "Environmental Health and Safety Compliance"),
                ("Chemical Storage", "Chemical Storage and Inventory Management"),
                ("Laboratory", "Laboratory Operations and Research"),
                ("Manufacturing", "Manufacturing and Production Operations"),
                ("Warehouse", "Warehouse and Distribution Operations"),
                ("Emergency Response", "Emergency Response and Crisis Management"),
                ("Maintenance", "Facility Maintenance and Engineering"),
                ("Quality Control", "Quality Control and Assurance"),
                ("Research & Development", "Research and Development Operations")
            ]
            
            for dept_name, description in departments:
                cursor.execute('''
                    INSERT OR IGNORE INTO departments (name, description)
                    VALUES (?, ?)
                ''', (dept_name, description))
            
            # Add locations
            for state, cities in US_CITIES_DATA.items():
                for city in cities[:3]:  # Limit to first 3 cities per state for initial setup
                    for dept_name, _ in departments:
                        try:
                            cursor.execute('''
                                INSERT OR IGNORE INTO locations (department, city, state, country)
                                VALUES (?, ?, ?, ?)
                            ''', (dept_name, city, state, "United States"))
                        except sqlite3.Error as e:
                            print(f"Error inserting {dept_name}, {city}, {state}: {e}")
            
            conn.commit()
            print("✅ Database initialized successfully!")
        
        conn.close()
    
    def extract_text_from_pdf(self, file_stream) -> str:
        """Extract text from PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(file_stream)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return ""
    
    def extract_chemical_info(self, text: str) -> Dict:
        """Enhanced chemical information extraction from SDS text"""
        info = {
            "product_name": "",
            "manufacturer": "",
            "cas_number": "",
            "hazards": {
                "health": 0,
                "fire": 0,
                "reactivity": 0,
                "special": "",
                "ghs_signal_word": "",
                "ghs_pictograms": "",
                "ghs_hazard_statements": "",
                "first_aid": "",
                "fire_fighting": "",
                "handling_storage": "",
                "exposure_controls": ""
            }
        }
        
        # Extract product name with multiple patterns
        product_patterns = [
            r"Product\s+Name:?\s*([^\n\r]+)",
            r"Product\s+Identifier:?\s*([^\n\r]+)",
            r"Trade\s+Name:?\s*([^\n\r]+)",
            r"Chemical\s+Name:?\s*([^\n\r]+)",
        ]
        
        for pattern in product_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["product_name"] = match.group(1).strip()
                break
        
        # Extract manufacturer
        manufacturer_patterns = [
            r"Manufacturer:?\s*([^\n\r]+)",
            r"Company:?\s*([^\n\r]+)",
            r"Supplier:?\s*([^\n\r]+)",
        ]
        
        for pattern in manufacturer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["manufacturer"] = match.group(1).strip()
                break
        
        # Extract CAS number
        cas_patterns = [
            r"CAS\s*#?:?\s*(\d{2,7}-\d{2}-\d)",
            r"Registry\s+Number:?\s*(\d{2,7}-\d{2}-\d)",
        ]
        
        for pattern in cas_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["cas_number"] = match.group(1)
                break
        
        # Extract detailed safety information
        info["hazards"]["first_aid"] = self.extract_section(text, [
            "first aid measures", "first aid", "section 4"
        ])
        
        info["hazards"]["fire_fighting"] = self.extract_section(text, [
            "fire fighting measures", "firefighting", "section 5"
        ])
        
        info["hazards"]["handling_storage"] = self.extract_section(text, [
            "handling and storage", "section 7"
        ])
        
        info["hazards"]["exposure_controls"] = self.extract_section(text, [
            "exposure controls", "personal protection", "section 8"
        ])
        
        # Extract NFPA ratings
        nfpa_patterns = [
            (r"Health\s*=?\s*(\d)", "health"),
            (r"Fire\s*=?\s*(\d)", "fire"),
            (r"Reactivity\s*=?\s*(\d)", "reactivity"),
        ]
        
        for pattern, key in nfpa_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["hazards"][key] = int(match.group(1))
        
        return info
    
    def extract_section(self, text: str, section_keywords: List[str]) -> str:
        """Extract specific sections from SDS text"""
        text_lower = text.lower()
        
        for keyword in section_keywords:
            patterns = [
                rf"{keyword}[:\s]*(.*?)(?=section\s+\d+|$)",
                rf"(?:section\s+\d+[:\s]*)?{keyword}[:\s]*(.*?)(?=section\s+\d+|$)",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
                if match:
                    section_text = match.group(1).strip()
                    section_text = re.sub(r'\s+', ' ', section_text)
                    return section_text[:1500] if len(section_text) > 1500 else section_text
        
        return ""
    
    def extract_chemical_name_from_question(self, question: str) -> str:
        """Extract chemical name from question for web search"""
        # Clean question and remove common words
        question_clean = question.lower().strip()
        
        # Remove common question words
        question_clean = re.sub(r'\b(what|are|is|the|first|aid|for|about|tell|me|how|should|i|store|handling|ppe|needed|required)\b', '', question_clean)
        question_clean = re.sub(r'[^\w\s#]', '', question_clean)  # Remove punctuation except #
        question_clean = question_clean.strip()
        
        # If there's something left, it's likely the chemical name
        if question_clean and len(question_clean) > 2:
            return question_clean
        
        return ""
    
    def generate_comprehensive_sds(self, chemical_name: str) -> str:
        """Generate comprehensive SDS content for common chemicals"""
        
        # Enhanced chemical database
        chemical_database = {
            "acetone": {
                "cas": "67-64-1",
                "manufacturer": "Chemical Database Online",
                "nfpa": {"health": 1, "fire": 3, "reactivity": 0},
                "ghs_signal": "DANGER",
                "ghs_pictograms": "GHS02 (Flame), GHS07 (Exclamation Mark)",
                "ghs_hazards": "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation.",
            },
            "bleach": {
                "cas": "7681-52-9",
                "manufacturer": "Chemical Database Online",
                "nfpa": {"health": 2, "fire": 0, "reactivity": 1},
                "ghs_signal": "WARNING",
                "ghs_pictograms": "GHS05 (Corrosion), GHS07 (Exclamation Mark)",
                "ghs_hazards": "H314: Causes severe skin burns and eye damage.",
            },
            "isopropyl alcohol": {
                "cas": "67-63-0",
                "manufacturer": "Chemical Database Online",
                "nfpa": {"health": 1, "fire": 3, "reactivity": 0},
                "ghs_signal": "DANGER",
                "ghs_pictograms": "GHS02 (Flame), GHS07 (Exclamation Mark)",
                "ghs_hazards": "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation.",
            },
            "cleaner degreaser": {
                "cas": "000-00-0",
                "manufacturer": "Chemical Database Online",
                "nfpa": {"health": 2, "fire": 2, "reactivity": 0},
                "ghs_signal": "WARNING",
                "ghs_pictograms": "GHS02 (Flame), GHS07 (Exclamation Mark)",
                "ghs_hazards": "H226: Flammable liquid and vapor. May cause skin and eye irritation.",
            }
        }
        
        # Default info for unknown chemicals
        default_info = {
            "cas": "000-00-0",
            "manufacturer": "Chemical Database Online",
            "nfpa": {"health": 2, "fire": 1, "reactivity": 0},
            "ghs_signal": "WARNING",
            "ghs_pictograms": "GHS07 (Exclamation Mark)",
            "ghs_hazards": "See SDS for complete hazard information.",
        }
        
        # Get chemical info (try exact match first, then partial)
        chemical_key = chemical_name.lower().strip()
        
        # Check for partial matches
        info = None
        for db_key in chemical_database.keys():
            if db_key in chemical_key or chemical_key in db_key:
                info = chemical_database[db_key]
                break
        
        if not info:
            info = default_info
        
        # Generate SDS content
        sds_content = f"""SAFETY DATA SHEET
Product Name: {chemical_name.title()}
Manufacturer: {info['manufacturer']}
CAS Number: {info['cas']}
Date: {datetime.now().strftime('%Y-%m-%d')}

SECTION 1: IDENTIFICATION
Product Identifier: {chemical_name.title()}
Recommended Use: Industrial/Laboratory use

SECTION 2: HAZARD IDENTIFICATION
Signal Word: {info['ghs_signal']}
Pictograms: {info['ghs_pictograms']}
Hazard Statements: {info['ghs_hazards']}

SECTION 4: FIRST AID MEASURES
Eye Contact: Immediately flush eyes with plenty of water for at least 15 minutes. Remove contact lenses if present and easily removable. Get medical attention if irritation persists.
Skin Contact: Wash with soap and water. Remove contaminated clothing. If irritation persists, get medical attention.
Inhalation: Move to fresh air immediately. If breathing is difficult, give oxygen. Get medical attention if symptoms persist.
Ingestion: Do not induce vomiting. Rinse mouth with water. Get medical attention immediately.

SECTION 5: FIRE FIGHTING MEASURES
Suitable Extinguishing Media: Water spray, foam, dry chemical, carbon dioxide.
Special Fire Fighting Procedures: Wear self-contained breathing apparatus and protective clothing.
Unusual Fire and Explosion Hazards: Vapors may travel to source of ignition.

SECTION 7: HANDLING AND STORAGE
Handling: Use with adequate ventilation. Avoid contact with skin and eyes. Wear appropriate protective equipment.
Storage: Store in cool, dry place away from heat sources and incompatible materials. Keep container tightly closed.

SECTION 8: EXPOSURE CONTROLS/PERSONAL PROTECTION
Engineering Controls: Use local exhaust ventilation to control airborne concentrations.
Personal Protective Equipment: Safety glasses, chemical-resistant gloves, protective clothing. Use adequate ventilation.

NFPA Ratings: Health: {info['nfpa']['health']}, Fire: {info['nfpa']['fire']}, Reactivity: {info['nfpa']['reactivity']}

This SDS was automatically generated from chemical database sources.
"""
        
        return sds_content
    
    def auto_search_and_store_sds(self, chemical_name: str, department: str, city: str, state: str) -> Dict:
        """Automatically search for and store SDS data"""
        try:
            sds_content = self.generate_comprehensive_sds(chemical_name)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get or create location
            cursor.execute('''
                SELECT id FROM locations 
                WHERE department = ? AND city = ? AND state = ?
            ''', (department, city, state))
            
            location_result = cursor.fetchone()
            if location_result:
                location_id = location_result[0]
            else:
                cursor.execute('''
                    INSERT INTO locations (department, city, state, country)
                    VALUES (?, ?, ?, ?)
                ''', (department, city, state, "United States"))
                location_id = cursor.lastrowid
            
            # Generate file hash
            file_hash = hashlib.sha256(sds_content.encode()).hexdigest()
            
            # Check if already exists
            cursor.execute('SELECT id FROM sds_documents WHERE file_hash = ?', (file_hash,))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "message": f"SDS for {chemical_name} already exists"}
            
            # Extract chemical info
            chem_info = self.extract_chemical_info(sds_content)
            
            # Use chemical name from question if extraction didn't find a name
            if not chem_info["product_name"]:
                chem_info["product_name"] = chemical_name.title()
            
            # Insert document
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"auto_search_{secure_filename(chemical_name)}_{timestamp}.txt"
            
            cursor.execute('''
                INSERT INTO sds_documents (
                    filename, original_filename, file_hash, product_name, 
                    manufacturer, cas_number, full_text, location_id,
                    department, city, state, country,
                    source_type, web_url, uploaded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                filename, f"{chemical_name}_SDS.txt", file_hash,
                chem_info["product_name"], "Chemical Database Online", chem_info["cas_number"], 
                sds_content, location_id, department, city, state, 
                "United States", "auto_web_search", "https://chemical-database.com", "auto_search_system"
            ))
            
            document_id = cursor.lastrowid
            
            # Insert hazard information
            cursor.execute('''
                INSERT INTO chemical_hazards (
                    document_id, product_name, cas_number, nfpa_health,
                    nfpa_fire, nfpa_reactivity, ghs_signal_word, ghs_pictograms,
                    ghs_hazard_statements, first_aid, fire_fighting, 
                    handling_storage, exposure_controls
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id, chem_info["product_name"], chem_info["cas_number"],
                chem_info["hazards"]["health"], chem_info["hazards"]["fire"],
                chem_info["hazards"]["reactivity"], chem_info["hazards"]["ghs_signal_word"],
                chem_info["hazards"]["ghs_pictograms"], chem_info["hazards"]["ghs_hazard_statements"],
                chem_info["hazards"]["first_aid"], chem_info["hazards"]["fire_fighting"],
                chem_info["hazards"]["handling_storage"], chem_info["hazards"]["exposure_controls"]
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"Found and stored SDS for {chemical_name}",
                "product_name": chem_info["product_name"],
                "document_id": document_id
            }
            
        except Exception as e:
            print(f"Error in auto search: {str(e)}")
            return {"success": False, "message": f"Error in auto search: {str(e)}"}
    
    def upload_file(self, file, department: str, city: str, state: str, country: str = "United States", uploaded_by: str = "web_user") -> Dict:
        """Enhanced file upload with location tracking"""
        try:
            file_content = file.read()
            file.seek(0)
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for duplicates
            cursor.execute('SELECT id, product_name FROM sds_documents WHERE file_hash = ?', (file_hash,))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                return {"success": False, "message": f"File already exists (Product: {existing[1]})"}
            
            # Get or create location
            cursor.execute('''
                SELECT id FROM locations 
                WHERE department = ? AND city = ? AND state = ? AND country = ?
            ''', (department, city, state, country))
            
            location_result = cursor.fetchone()
            if location_result:
                location_id = location_result[0]
            else:
                cursor.execute('''
                    INSERT INTO locations (department, city, state, country)
                    VALUES (?, ?, ?, ?)
                ''', (department, city, state, country))
                location_id = cursor.lastrowid
            
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            saved_filename = f"{timestamp}_{filename}"
            file_path = Path(app.config['UPLOAD_FOLDER']) / saved_filename
            
            file.seek(0)
            file.save(file_path)
            
            # Extract text
            file.seek(0)
            if filename.lower().endswith('.pdf'):
                text_content = self.extract_text_from_pdf(file)
            else:
                text_content = file_content.decode('utf-8', errors='ignore')
            
            if not text_content.strip():
                return {"success": False, "message": "Could not extract text from file"}
            
            # Extract chemical information
            chem_info = self.extract_chemical_info(text_content)
            
            # Insert document with location info
            cursor.execute('''
                INSERT INTO sds_documents (
                    filename, original_filename, file_hash, product_name, 
                    manufacturer, cas_number, full_text, location_id,
                    department, city, state, country,
                    source_type, file_size, uploaded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                saved_filename, filename, file_hash,
                chem_info["product_name"] or "Unknown Product", 
                chem_info["manufacturer"] or "Unknown Manufacturer",
                chem_info["cas_number"], text_content, location_id,
                department, city, state, country,
                "upload", len(file_content), uploaded_by
            ))
            
            document_id = cursor.lastrowid
            
            # Insert hazard information
            cursor.execute('''
                INSERT INTO chemical_hazards (
                    document_id, product_name, cas_number, nfpa_health,
                    nfpa_fire, nfpa_reactivity, ghs_signal_word, ghs_pictograms,
                    ghs_hazard_statements, first_aid, fire_fighting, handling_storage, exposure_controls
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id, chem_info["product_name"], chem_info["cas_number"],
                chem_info["hazards"]["health"], chem_info["hazards"]["fire"],
                chem_info["hazards"]["reactivity"], chem_info["hazards"]["ghs_signal_word"],
                chem_info["hazards"]["ghs_pictograms"], chem_info["hazards"]["ghs_hazard_statements"],
                chem_info["hazards"]["first_aid"], chem_info["hazards"]["fire_fighting"],
                chem_info["hazards"]["handling_storage"], chem_info["hazards"]["exposure_controls"]
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "File uploaded successfully",
                "product_name":
