# Complete Enhanced SDS Assistant - Ready for GitHub and Render Deployment
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

# US Cities Data (Complete dataset)
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
            r"Commercial\s+Product\s+Name:?\s*([^\n\r]+)"
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
            r"Prepared\s+by:?\s*([^\n\r]+)"
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
            r"CAS\s+No\.?:?\s*(\d{2,7}-\d{2}-\d)"
        ]
        
        for pattern in cas_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["cas_number"] = match.group(1)
                break
        
        # Extract detailed safety information
        info["hazards"]["first_aid"] = self.extract_section(text, [
            "first aid measures", "first aid", "section 4", "emergency procedures"
        ])
        
        info["hazards"]["fire_fighting"] = self.extract_section(text, [
            "fire fighting measures", "firefighting", "fire-fighting", "section 5", "fire and explosion"
        ])
        
        info["hazards"]["handling_storage"] = self.extract_section(text, [
            "handling and storage", "handling", "storage", "section 7", "precautions"
        ])
        
        info["hazards"]["exposure_controls"] = self.extract_section(text, [
            "exposure controls", "personal protection", "section 8", "protective equipment"
        ])
        
        # Extract NFPA ratings with better patterns
        nfpa_patterns = [
            (r"Health\s*=?\s*(\d)", "health"),
            (r"Fire\s*=?\s*(\d)", "fire"),
            (r"Reactivity\s*=?\s*(\d)", "reactivity"),
            (r"NFPA\s+Health\s*:?\s*(\d)", "health"),
            (r"NFPA\s+Fire\s*:?\s*(\d)", "fire"),
            (r"NFPA\s+Reactivity\s*:?\s*(\d)", "reactivity"),
            (r"NFPA\s+(\d)\s*-\s*(\d)\s*-\s*(\d)", "combined")
        ]
        
        for pattern, key in nfpa_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if key == "combined":
                    info["hazards"]["health"] = int(match.group(1))
                    info["hazards"]["fire"] = int(match.group(2))
                    info["hazards"]["reactivity"] = int(match.group(3))
                    break
                else:
                    info["hazards"][key] = int(match.group(1))
        
        return info
    
    def extract_section(self, text: str, section_keywords: List[str]) -> str:
        """Extract specific sections from SDS text with better context"""
        text_lower = text.lower()
        
        for keyword in section_keywords:
            # Look for section headers with various formats
            patterns = [
                rf"{keyword}[:\s]*(.*?)(?=section\s+\d+|#{3,}|$)",
                rf"(?:section\s+\d+[:\s]*)?{keyword}[:\s]*(.*?)(?=section\s+\d+|#{3,}|$)",
                rf"\d+\.\s*{keyword}[:\s]*(.*?)(?=\d+\.|section\s+\d+|$)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
                if match:
                    section_text = match.group(1).strip()
                    # Clean up and limit length
                    section_text = re.sub(r'\s+', ' ', section_text)
                    return section_text[:2000] if len(section_text) > 2000 else section_text
        
        return ""
    
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
                    nfpa_fire, nfpa_reactivity, ghs_signal_word,
                    first_aid, fire_fighting, handling_storage, exposure_controls
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id, chem_info["product_name"], chem_info["cas_number"],
                chem_info["hazards"]["health"], chem_info["hazards"]["fire"],
                chem_info["hazards"]["reactivity"], chem_info["hazards"]["ghs_signal_word"],
                chem_info["hazards"]["first_aid"], chem_info["hazards"]["fire_fighting"],
                chem_info["hazards"]["handling_storage"], chem_info["hazards"]["exposure_controls"]
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "File uploaded successfully",
                "product_name": chem_info["product_name"] or "Unknown Product",
                "document_id": document_id,
                "location": f"{department}, {city}, {state}"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error uploading file: {str(e)}"}
    
    def answer_question(self, question: str, department: str = None, city: str = None, 
                       state: str = None, user_session: str = None) -> Dict:
        """Enhanced AI-powered question answering with location filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build dynamic query based on location filters
            base_query = '''
                SELECT sd.id, sd.product_name, sd.full_text, sd.department, sd.city, sd.state,
                       ch.first_aid, ch.fire_fighting, ch.handling_storage, ch.exposure_controls,
                       ch.nfpa_health, ch.nfpa_fire, ch.nfpa_reactivity
                FROM sds_documents sd
                LEFT JOIN chemical_hazards ch ON sd.id = ch.document_id
                WHERE (sd.full_text LIKE ? OR sd.product_name LIKE ? OR ch.first_aid LIKE ? 
                       OR ch.fire_fighting LIKE ? OR ch.handling_storage LIKE ? 
                       OR ch.exposure_controls LIKE ?)
            '''
            
            # Add location filters
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
            
            if not documents:
                location_filter = ""
                if department or city or state:
                    location_parts = [f for f in [department, city, state] if f]
                    location_filter = f" in {', '.join(location_parts)}"
                
                return {
                    "success": False,
                    "answer": f"I couldn't find any relevant SDS documents{location_filter} to answer your question about '{question}'. Please try uploading relevant SDS files or adjusting your location filters.",
                    "sources": []
                }
            
            # Generate enhanced answer
            answer = self.generate_enhanced_answer(question, documents)
            
            # Log the Q&A with location context
            if user_session:
                cursor.execute('''
                    INSERT INTO qa_history (question, answer, document_id, department, city, state, 
                                          user_session, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (question, answer["text"], documents[0][0] if documents else None,
                      department, city, state, user_session, answer["confidence"]))
                conn.commit()
            
            conn.close()
            
            return {
                "success": True,
                "answer": answer["text"],
                "confidence": answer["confidence"],
                "sources": answer["sources"],
                "location_context": f"{department or 'All Departments'}, {city or 'All Cities'}, {state or 'All States'}"
            }
            
        except Exception as e:
            return {"success": False, "answer": f"Error processing question: {str(e)}", "sources": []}
    
    def generate_enhanced_answer(self, question: str, documents: List) -> Dict:
        """Generate comprehensive answers from documents using advanced keyword matching"""
        question_lower = question.lower()
        answer_parts = []
        sources = []
        confidence = 0.0
        
        # Enhanced question type detection
        question_types = {
            "first_aid": {
                "keywords": ["first aid", "emergency", "exposure", "eye contact", "skin contact", 
                           "inhalation", "ingestion", "swallowed", "inhaled", "spilled"],
                "weight": 1.0
            },
            "fire_fighting": {
                "keywords": ["fire", "firefighting", "extinguish", "combustible", "flammable", 
                           "burning", "flame", "ignition"],
                "weight": 1.0
            },
            "handling": {
                "keywords": ["handling", "storage", "precautions", "handling precautions", 
                           "store", "keep", "avoid"],
                "weight": 1.0
            },
            "exposure": {
                "keywords": ["exposure", "protection", "ppe", "personal protective", 
                           "ventilation", "gloves", "mask", "respirator"],
                "weight": 1.0
            },
            "hazards": {
                "keywords": ["hazard", "danger", "toxic", "corrosive", "irritant", 
                           "harmful", "warning", "caution"],
                "weight": 0.9
            }
        }
        
        # Determine question type and priority
        detected_types = []
        for qtype, config in question_types.items():
            score = sum(1 for keyword in config["keywords"] if keyword in question_lower)
            if score > 0:
                detected_types.append((qtype, score * config["weight"]))
        
        detected_types.sort(key=lambda x: x[1], reverse=True)
        primary_type = detected_types[0][0] if detected_types else "general"
        
        # Process documents with intelligent content selection
        for doc in documents:
            (doc_id, product_name, full_text, department, city, state, 
             first_aid, fire_fighting, handling_storage, exposure_controls,
             nfpa_health, nfpa_fire, nfpa_reactivity) = doc
            
            relevant_content = ""
            content_source = ""
            
            # Select most relevant content based on question type
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
                content_source = "Exposure Controls/Personal Protection"
            else:
                # Extract most relevant section from full text
                relevant_content = self.extract_relevant_text_enhanced(question, full_text)
                content_source = "SDS Document"
            
            if relevant_content:
                # Add NFPA information for hazard-related questions
                nfpa_info = ""
                if any(word in question_lower for word in ["hazard", "danger", "risk", "rating"]):
                    nfpa_info = f" (NFPA Ratings - Health: {nfpa_health}, Fire: {nfpa_fire}, Reactivity: {nfpa_reactivity})"
                
                location_info = f"{department}, {city}, {state}"
                answer_parts.append(
                    f"**{product_name}** ({location_info}){nfpa_info}:\n{relevant_content}\n*Source: {content_source}*"
                )
                
                sources.append({
                    "product_name": product_name,
                    "location": location_info,
                    "document_id": doc_id,
                    "content_source": content_source
                })
                confidence += 0.25
        
        # Generate final answer
        if answer_parts:
            final_answer = "\n\n---\n\n".join(answer_parts[:3])  # Limit to top 3 results
            confidence = min(confidence, 1.0)
            
            # Add summary if multiple products found
            if len(answer_parts) > 1:
                final_answer = f"**Found information for {len(answer_parts)} products:**\n\n{final_answer}"
        else:
            final_answer = f"I found documents that might be relevant, but couldn't extract specific information about '{question}'. Please try rephrasing your question or check the documents directly."
            confidence = 0.1
        
        return {
            "text": final_answer,
            "confidence": confidence,
            "sources": sources[:3]
        }
    
    def extract_relevant_text_enhanced(self, question: str, full_text: str, max_length: int = 800) -> str:
        """Enhanced text extraction with better context understanding"""
        question_words = [word.lower() for word in question.split() if len(word) > 2]
        sentences = re.split(r'[.!?]+', full_text)
        
        # Score sentences based on keyword relevance
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 20:
                continue
                
            sentence_lower = sentence.lower()
            score = 0
            
            # Direct keyword matches
            for word in question_words:
                if word in sentence_lower:
                    score += 2
                    
            # Bonus for sentences with multiple keywords
            keyword_count = sum(1 for word in question_words if word in sentence_lower)
            if keyword_count > 1:
                score += keyword_count
                
            # Bonus for sentences that appear to be instructions or procedures
            if any(indicator in sentence_lower for indicator in ['should', 'must', 'avoid', 'use', 'wear', 'ensure']):
                score += 1
                
            scored_sentences.append((score, i, sentence.strip()))
        
        # Sort by score and get best sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        
        if scored_sentences and scored_sentences[0][0] > 0:
            # Take best sentence and add context
            best_score, best_index, best_sentence = scored_sentences[0]
            
            # Add surrounding sentences for context
            context_sentences = []
            start_idx = max(0, best_index - 1)
            end_idx = min(len(sentences), best_index + 3)
            
            for i in range(start_idx, end_idx):
                if i < len(sentences) and sentences[i].strip():
                    context_sentences.append(sentences[i].strip())
            
            context = '. '.join(context_sentences)
            return context[:max_length] + "..." if len(context) > max_length else context
        
        return ""
    
    def search_web_for_sds(self, chemical_name: str, department: str, city: str, state: str) -> Dict:
        """Enhanced web search for SDS documents with database storage"""
        try:
            # Simulate finding an SDS document online
            simulated_sds_content = f"""
SAFETY DATA SHEET
Product Name: {chemical_name}
Manufacturer: Chemical Database Online
CAS Number: 000-00-0

SECTION 4: FIRST AID MEASURES
Eye Contact: Immediately flush eyes with plenty of water for at least 15 minutes. Remove contact lenses if present and easily removable. Continue rinsing. Get medical attention immediately.
Skin Contact: Wash with soap and water. Remove contaminated clothing. If skin irritation occurs, get medical attention.
Inhalation: Move to fresh air immediately. If breathing is difficult, give oxygen. Get medical attention.
Ingestion: Do not induce vomiting. Rinse mouth with water. Get medical attention immediately.

SECTION 5: FIRE FIGHTING MEASURES
Suitable Extinguishing Media: Water spray, foam, dry chemical, carbon dioxide.
Unsuitable Extinguishing Media: High volume water jet.
Special Fire Fighting Procedures: Wear self-contained breathing apparatus and protective clothing.
Unusual Fire and Explosion Hazards: May release toxic gases when heated.

SECTION 7: HANDLING AND STORAGE
Handling: Use with adequate ventilation. Avoid contact with skin and eyes. Wear appropriate protective equipment.
Storage: Store in cool, dry place away from incompatible materials. Keep container tightly closed.

SECTION 8: EXPOSURE CONTROLS/PERSONAL PROTECTION
Engineering Controls: Use local exhaust ventilation to control airborne concentrations.
Personal Protective Equipment: Safety glasses, chemical-resistant gloves, protective clothing.
Respiratory Protection: Use NIOSH-approved respirator when airborne exposure limits may be exceeded.
"""
            
            # Store in database as if it was found online
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
            file_hash = hashlib.sha256(simulated_sds_content.encode()).hexdigest()
            
            # Check if already exists
            cursor.execute('SELECT id FROM sds_documents WHERE file_hash = ?', (file_hash,))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "message": f"SDS for {chemical_name} already exists in database"}
            
            # Extract chemical info
            chem_info = self.extract_chemical_info(simulated_sds_content)
            
            # Insert document
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"web_search_{secure_filename(chemical_name)}_{timestamp}.txt"
            
            cursor.execute('''
                INSERT INTO sds_documents (
                    filename, original_filename, file_hash, product_name, 
                    manufacturer, cas_number, full_text, location_id,
                    department, city, state, country,
                    source_type, web_url, uploaded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                filename, f"{chemical_name}_SDS.txt", file_hash,
                chemical_name, "Chemical Database Online", chem_info["cas_number"], 
                simulated_sds_content, location_id, department, city, state, 
                "United States", "web_search", "https://example-sds-database.com", "web_crawler"
            ))
            
            document_id = cursor.lastrowid
            
            # Insert hazard information
            cursor.execute('''
                INSERT INTO chemical_hazards (
                    document_id, product_name, cas_number, nfpa_health,
                    nfpa_fire, nfpa_reactivity, first_aid, fire_fighting, 
                    handling_storage, exposure_controls
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id, chemical_name, chem_info["cas_number"],
                2, 1, 0,  # Default NFPA ratings for demo
                chem_info["hazards"]["first_aid"],
                chem_info["hazards"]["fire_fighting"], 
                chem_info["hazards"]["handling_storage"],
                chem_info["hazards"]["exposure_controls"]
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"Found and stored SDS for {chemical_name}",
                "product_name": chemical_name,
                "document_id": document_id,
                "source": "Web Search"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error searching for SDS: {str(e)}"}
    
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
                return {"success": False, "message": f"No hazard data found for {product_name}"}
            
            health, fire, reactivity, special, actual_name, department, city, state = result
            
            # Enhanced SVG with better styling
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
    
    <!-- Background -->
    <rect width="350" height="400" fill="white" stroke="black" stroke-width="2"/>
    
    <!-- Title -->
    <text x="175" y="30" class="title" fill="black">NFPA 704 HAZARD IDENTIFICATION</text>
    
    <!-- Diamond -->
    <polygon points="175,60 310,195 175,330 40,195" fill="white" stroke="black" stroke-width="4"/>
    
    <!-- Colored sections -->
    <polygon points="40,195 175,60 175,195 40,195" fill="blue" class="diamond"/>
    <polygon points="175,60 310,195 175,195 175,60" fill="red" class="diamond"/>
    <polygon points="310,195 175,330 175,195 310,195" fill="yellow" class="diamond"/>
    <polygon points="175,195 175,330 40,195 175,195" fill="white" class="diamond"/>
    
    <!-- Ratings -->
    <text x="107" y="135" class="rating" fill="white">{health}</text>
    <text x="175" y="115" class="rating" fill="white">{fire}</text>
    <text x="243" y="135" class="rating" fill="black">{reactivity}</text>
    <text x="175" y="275" class="rating" fill="black">{special or ''}</text>
    
    <!-- Labels -->
    <text x="107" y="165" class="label" fill="white">HEALTH</text>
    <text x="175" y="80" class="label" fill="white">FIRE</text>
    <text x="243" y="165" class="label" fill="black">REACTIVITY</text>
    <text x="175" y="305" class="label" fill="black">SPECIAL</text>
    
    <!-- Product information -->
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
                "ratings": {"health": health, "fire": fire, "reactivity": reactivity, "special": special or "None"},
                "location": f"{department}, {city}, {state}"
            }
            
        except Exception as e:
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
                return {"success": False, "message": f"No GHS data found for {product_name}"}
            
            signal_word, pictograms, hazard_statements, actual_name, manufacturer, department, city, state = result
            
            # Enhanced GHS label with proper formatting
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
    
    <!-- Background -->
    <rect width="450" height="350" fill="white" stroke="black" stroke-width="3"/>
    <rect x="10" y="10" width="430" height="330" fill="none" stroke="red" stroke-width="2"/>
    
    <!-- Header -->
    <text x="225" y="40" class="header" fill="black">GHS HAZARD LABEL</text>
    
    <!-- Product Name -->
    <text x="225" y="70" class="product" fill="black">{actual_name[:40]}</text>
    <text x="225" y="90" class="manufacturer" fill="black">{manufacturer[:40] if manufacturer else 'See SDS'}</text>
    
    <!-- Signal Word -->
    <rect x="150" y="105" width="150" height="35" fill="{'red' if signal_word and 'danger' in signal_word.lower() else 'orange'}" stroke="black" stroke-width="2"/>
    <text x="225" y="127" class="signal" fill="white">{signal_word or 'WARNING'}</text>
    
    <!-- Hazard Information -->
    <text x="25" y="170" class="hazard" fill="black" font-weight="bold">Hazard Statements:</text>
    <text x="25" y="190" class="hazard" fill="black">{(hazard_statements or 'See SDS for complete hazard information')[:55]}</text>
    
    <!-- Pictograms -->
    <text x="25" y="220" class="hazard" fill="black" font-weight="bold">Pictograms:</text>
    <text x="25" y="240" class="hazard" fill="black">{pictograms or 'See SDS for pictogram symbols'}</text>
    
    <!-- Precautionary Statements -->
    <text x="25" y="270" class="hazard" fill="black" font-weight="bold">Precautionary Statements:</text>
    <text x="25" y="290" class="hazard" fill="black">Read SDS before use. Obtain special instructions before use.</text>
    <text x="25" y="310" class="hazard" fill="black">Wear protective gloves/protective clothing/eye protection.</text>
    
    <!-- Location and Date -->
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
                "pictograms": pictograms,
                "hazard_statements": hazard_statements,
                "location": f"{department}, {city}, {state}"
            }
            
        except Exception as e:
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
                    "source": row[7]
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
                "popular_questions": [{"question": row[0], "count": row[1]} for row in popular_questions],
                "top_departments": [{"department": row[0], "count": row[1]} for row in top_departments]
            }
            
        except Exception as e:
            print(f"Error getting dashboard stats: {str(e)}")
            return {"total_documents": 0, "active_locations": 0, "recent_questions": 0, 
                   "hazardous_materials": 0, "popular_questions": [], "top_departments": []}

# Initialize the enhanced assistant
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
        "version": "2.0-enhanced"
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

@app.route('/api/ask-question', methods=['POST'])
def ask_question():
    """Enhanced AI question answering with location filtering"""
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

@app.route('/api/search-web-sds', methods=['POST'])
def search_web_sds():
    """Enhanced web search for SDS documents"""
    data = request.json
    chemical_name = data.get('chemical_name')
    department = data.get('department')
    city = data.get('city')
    state = data.get('state')
    
    if not all([chemical_name, department, city, state]):
        return jsonify({"success": False, "message": "All fields are required"})
    
    result = sds_assistant.search_web_for_sds(chemical_name, department, city, state)
    return jsonify(result)

@app.route('/api/generate-nfpa', methods=['POST'])
def generate_nfpa():
    """Generate NFPA label"""
    data = request.json
    product_name = data.get('product_name')
    
    if not product_name:
        return jsonify({"success": False, "message": "Product name is required"})
    
    result = sds_assistant.generate_nfpa_label(product_name)
    return jsonify(result)

@app.route('/api/generate-ghs', methods=['POST'])
def generate_ghs():
    """Generate GHS label"""
    data = request.json
    product_name = data.get('product_name')
    
    if not product_name:
        return jsonify({"success": False, "message": "Product name is required"})
    
    result = sds_assistant.generate_ghs_label(product_name)
    return jsonify(result)

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
    print("🚀 Starting Enhanced SDS Assistant...")
    print("📍 Enhanced location-based filtering enabled")
    print("🤖 Advanced AI-powered question answering")
    print("🏷️ NFPA and GHS label generation")
    print("🔍 Web search integration for SDS documents")
    print("📊 Enhanced analytics and reporting")
    print(f"🌐 Application available at: http://localhost:{port}")
    print()
    
    app.run(debug=False, host='0.0.0.0', port=port)

<button id="webSearchBtn" class="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition">
                        <i class="fas fa-globe mr-2"></i>Web Search
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- Enhanced Dashboard Stats -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6 card-hover">
                <div class="flex items-center">
                    <div class="p-3 rounded-full bg-blue-100 text-blue-600">
                        <i class="fas fa-file-alt text-2xl"></i>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">Total Documents</p>
                        <p id="totalDocs" class="text-2xl font-bold text-gray-900">0</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow p-6 card-hover">
                <div class="flex items-center">
                    <div class="p-3 rounded-full bg-green-100 text-green-600">
                        <i class="fas fa-map-marker-alt text-2xl"></i>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">Active Locations</p>
                        <p id="activeLocations" class="text-2xl font-bold text-gray-900">0</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow p-6 card-hover">
                <div class="flex items-center">
                    <div class="p-3 rounded-full bg-purple-100 text-purple-600">
                        <i class="fas fa-question-circle text-2xl"></i>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">Questions Answered</p>
                        <p id="recentQuestions" class="text-2xl font-bold text-gray-900">0</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow p-6 card-hover">
                <div class="flex items-center">
                    <div class="p-3 rounded-full bg-red-100 text-red-600">
                        <i class="fas fa-exclamation-triangle text-2xl"></i>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">High Hazard Materials</p>
                        <p id="hazardousMaterials" class="text-2xl font-bold text-gray-900">0</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Content Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Enhanced AI Question Answering -->
            <div class="lg:col-span-2 bg-white rounded-lg shadow">
                <div class="p-6">
                    <h2 class="text-2xl font-bold text-gray-900 mb-4">
                        <i class="fas fa-robot mr-2"></i>Ask AI About SDS Documents
                    </h2>
                    
                    <!-- Location Filters -->
                    <div class="filter-section p-4 rounded-lg mb-4">
                        <h4 class="font-semibold text-gray-700 mb-3">Filter by Location</h4>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                            <select id="departmentFilter" class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                <option value="">All Departments</option>
                            </select>
                            <select id="cityFilter" class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                <option value="">All Cities</option>
                            </select>
                            <select id="stateFilter" class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                <option value="">All States</option>
                            </select>
                        </div>
                    </div>
                    
                    <!-- Chat Container -->
                    <div id="chatContainer" class="chat-container border rounded-lg p-4 mb-4 bg-gray-50">
                        <div class="message ai-message p-3 rounded-lg">
                            <p><strong>AI Assistant:</strong> Hello! I can help you find information in your SDS documents. Ask me questions like:</p>
                            <ul class="mt-2 ml-4 list-disc text-sm">
                                <li>"What are the first aid measures for cleaner degreaser?"</li>
                                <li>"How should I store acetone in the laboratory?"</li>
                                <li>"What PPE is needed for handling sulfuric acid in manufacturing?"</li>
                                <li>"What are the fire fighting measures for methanol?"</li>
                            </ul>
                        </div>
                    </div>
                    
                    <!-- Question Input -->
                    <div class="flex space-x-2 mb-4">
                        <input 
                            type="text" 
                            id="questionInput" 
                            placeholder="Ask a question about your SDS documents (e.g., 'What is the first aid for cleaner degreaser?')"
                            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        >
                        <button id="askBtn" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                    
                    <!-- Quick Questions -->
                    <div class="mb-4">
                        <h4 class="font-semibold text-gray-700 mb-2">Quick Questions:</h4>
                        <div class="flex flex-wrap gap-2">
                            <button class="quick-question bg-blue-100 hover:bg-blue-200 px-3 py-1 rounded-full text-sm transition" data-question="What are the first aid measures for this chemical?">
                                First Aid
                            </button>
                            <button class="quick-question bg-green-100 hover:bg-green-200 px-3 py-1 rounded-full text-sm transition" data-question="How should this chemical be stored?">
                                Storage Requirements
                            </button>
                            <button class="quick-question bg-orange-100 hover:bg-orange-200 px-3 py-1 rounded-full text-sm transition" data-question="What PPE is required for handling this chemical?">
                                PPE Requirements
                            </button>
                            <button class="quick-question bg-red-100 hover:bg-red-200 px-3 py-1 rounded-full text-sm transition" data-question="What are the fire fighting measures for this chemical?">
                                Fire Fighting
                            </button>
                            <button class="quick-question bg-purple-100 hover:bg-purple-200 px-3 py-1 rounded-full text-sm transition" data-question="What are the hazards of this chemical?">
                                Hazards
                            </button>
                        </div>
                    </div>
                    
                    <!-- Answer Confidence Indicator -->
                    <div id="confidenceIndicator" class="hidden mb-4">
                        <div class="flex items-center justify-between text-sm text-gray-600 mb-1">
                            <span>Answer Confidence</span>
                            <span id="confidenceText">0%</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div id="confidenceBar" class="confidence-bar bg-gradient-to-r from-red-400 via-yellow-400 to-green-400" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Enhanced File Management & Recent Documents -->
            <div class="bg-white rounded-lg shadow">
                <div class="p-6">
                    <h2 class="text-xl font-bold text-gray-900 mb-4">
                        <i class="fas fa-file-upload mr-2"></i>Document Management
                    </h2>
                    
                    <!-- Action Buttons -->
                    <div class="grid grid-cols-1 gap-3 mb-6">
                        <button id="uploadDocBtn" class="bg-blue-100 hover:bg-blue-200 p-4 rounded-lg transition text-center">
                            <i class="fas fa-upload text-blue-600 text-xl mb-2"></i>
                            <h3 class="font-semibold text-blue-600">Upload SDS File</h3>
                            <p class="text-xs text-gray-600">PDF, TXT, DOC files</p>
                        </button>
                        
                        <button id="webSearchDocBtn" class="bg-purple-100 hover:bg-purple-200 p-4 rounded-lg transition text-center">
                            <i class="fas fa-globe text-purple-600 text-xl mb-2"></i>
                            <h3 class="font-semibold text-purple-600">Search Web for SDS</h3>
                            <p class="text-xs text-gray-600">Find SDS online</p>
                        </button>
                        
                        <button id="generateLabelsBtn" class="bg-orange-100 hover:bg-orange-200 p-4 rounded-lg transition text-center">
                            <i class="fas fa-tags text-orange-600 text-xl mb-2"></i>
                            <h3 class="font-semibold text-orange-600">Generate Labels</h3>
                            <p class="text-xs text-gray-600">NFPA & GHS labels</p>
                        </button>
                    </div>
                    
                    <!-- Recent Documents -->
                    <div>
                        <h4 class="font-semibold text-gray-700 mb-3">Recent Documents</h4>
                        <div id="recentDocumentsList" class="space-y-2 max-h-64 overflow-y-auto">
                            <p class="text-gray-500 text-center py-4">No documents uploaded yet</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Enhanced Analytics Section -->
        <div class="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Popular Questions -->
            <div class="bg-white rounded-lg shadow">
                <div class="p-6">
                    <h3 class="text-xl font-bold text-gray-900 mb-4">
                        <i class="fas fa-chart-line mr-2"></i>Popular Questions
                    </h3>
                    <div id="popularQuestions" class="space-y-3">
                        <p class="text-gray-500 text-center py-4">No questions asked yet</p>
                    </div>
                </div>
            </div>
            
            <!-- Top Departments -->
            <div class="bg-white rounded-lg shadow">
                <div class="p-6">
                    <h3 class="text-xl font-bold text-gray-900 mb-4">
                        <i class="fas fa-building mr-2"></i>Top Departments
                    </h3>
                    <div id="topDepartments" class="space-y-3">
                        <p class="text-gray-500 text-center py-4">No data available yet</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Enhanced Upload Modal -->
    <div id="uploadModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 hidden z-50">
        <div class="flex items-center justify-center min-h-screen p-4">
            <div class="bg-white rounded-lg shadow-xl max-w-lg w-full">
                <div class="p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-bold text-gray-900">Upload SDS Document</h3>
                        <button id="closeUploadModal" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <form id="uploadForm" enctype="multipart/form-data">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Department</label>
                                <select id="uploadDepartmentSelect" name="department" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" required>
                                    <option value="">Choose a department...</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">State</label>
                                <select id="uploadStateSelect" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" required>
                                    <option value="">Choose a state...</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">City</label>
                                <select id="uploadCitySelect" name="city" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" required>
                                    <option value="">Choose a city...</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Country</label>
                                <select name="country" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" required>
                                    <option value="United States">United States</option>
                                    <option value="Canada">Canada</option>
                                    <option value="Mexico">Mexico</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">SDS File</label>
                            <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-gray-400 transition">
                                <div class="space-y-1 text-center">
                                    <i class="fas fa-cloud-upload-alt text-3xl text-gray-400"></i>
                                    <div class="flex text-sm text-gray-600">
                                        <label for="file-upload" class="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500">
                                            <span>Upload a file</span>
                                            <input id="file-upload" name="file" type="file" class="sr-only" accept=".pdf,.txt,.doc,.docx" required>
                                        </label>
                                        <p class="pl-1">or drag and drop</p>
                                    </div>
                                    <p class="text-xs text-gray-500">PDF, TXT, DOC up to 50MB</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="flex justify-end space-x-3">
                            <button type="button" id="cancelUpload" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition">
                                Cancel
                            </button>
                            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                                <i class="fas fa-upload mr-2"></i>Upload
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Web Search Modal -->
    <div id="webSearchModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 hidden z-50">
        <div class="flex items-center justify-center min-h-screen p-4">
            <div class="bg-white rounded-lg shadow-xl max-w-lg w-full">
                <div class="p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-bold text-gray-900">Search Web for SDS</h3>
                        <button id="closeWebSearchModal" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <form id="webSearchForm">
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Chemical/Product Name</label>
                            <input type="text" id="searchChemicalName" name="chemical_name" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="e.g., Acetone, Bleach, Isopropyl Alcohol" required>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Department</label>
                                <select id="searchDepartmentSelect" name="department" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" required>
                                    <option value="">Choose department...</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">City</label>
                                <select id="searchCitySelect" name="city" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" required>
                                    <option value="">Choose city...</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">State</label>
                                <select id="searchStateSelect" name="state" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" required>
                                    <option value="">Choose state...</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="flex justify-end space-x-3">
                            <button type="button" id="cancelWebSearch" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition">
                                Cancel
                            </button>
                            <button type="submit" class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                                <i class="fas fa-search mr-2"></i>Search & Download
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Label Generation Modal -->
    <div id="labelModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 hidden z-50">
        <div class="flex items-center justify-center min-h-screen p-4">
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
                <div class="p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-bold text-gray-900">Generate Safety Labels</h3>
                        <button id="closeLabelModal" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="mb-4">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Product Name</label>
                        <input type="text" id="labelProductName" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Enter product name...">
                    </div>
                    
                    <div class="flex justify-end space-x-3">
                        <button type="button" id="cancelLabel" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition">
                            Cancel
                        </button>
                        <button id="generateNFPA" type="button" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
                            <i class="fas fa-diamond mr-2"></i>NFPA Label
                        </button>
                        <button id="generateGHS" type="button" class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition">
                            <i class="fas fa-exclamation-triangle mr-2"></i>GHS Label
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notifications -->
    <div id="toast" class="fixed top-4 right-4 z-50 hidden">
        <div class="bg-white rounded-lg shadow-lg border-l-4 p-4 max-w-sm">
            <div class="flex">
                <div class="flex-shrink-0">
                    <i id="toastIcon" class="text-xl"></i>
                </div>
                <div class="ml-3">
                    <p id="toastMessage" class="text-sm font-medium text-gray-900"></p>
                </div>
                <div class="ml-auto pl-3">
                    <button id="closeToast" class="text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let currentConversation = [];
        
        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardStats();
            loadDepartments();
            loadStates();
            loadRecentDocuments();
            setupEventListeners();
        });
        
        // Setup enhanced event listeners
        function setupEventListeners() {
            // Question answering
            document.getElementById('askBtn').addEventListener('click', askQuestion);
            document.getElementById('questionInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') askQuestion();
            });
            
            // Quick questions
            document.querySelectorAll('.quick-question').forEach(btn => {
                btn.addEventListener('click', function() {
                    document.getElementById('questionInput').value = this.dataset.question;
                    askQuestion();
                });
            });
            
            // File upload
            document.getElementById('uploadBtn').addEventListener('click', () => showModal('uploadModal'));
            document.getElementById('uploadDocBtn').addEventListener('click', () => showModal('uploadModal'));
            document.getElementById('closeUploadModal').addEventListener('click', () => hideModal('uploadModal'));
            document.getElementById('cancelUpload').addEventListener('click', () => hideModal('uploadModal'));
            document.getElementById('uploadForm').addEventListener('submit', handleFileUpload);
            
            // Web search
            document.getElementById('webSearchBtn').addEventListener('click', () => showModal('webSearchModal'));
            document.getElementById('webSearchDocBtn').addEventListener('click', () => showModal('webSearchModal'));
            document.getElementById('closeWebSearchModal').addEventListener('click', () => hideModal('webSearchModal'));
            document.getElementById('cancelWebSearch').addEventListener('click', () => hideModal('webSearchModal'));
            document.getElementById('webSearchForm').addEventListener('submit', handleWebSearch);
            
            // Label generation
            document.getElementById('generateLabelBtn').addEventListener('click', () => showModal('labelModal'));
            document.getElementById('generateLabelsBtn').addEventListener('click', () => showModal('labelModal'));
            document.getElementById('closeLabelModal').addEventListener('click', () => hideModal('labelModal'));
            document.getElementById('cancelLabel').addEventListener('click', () => hideModal('labelModal'));
            document.getElementById('generateNFPA').addEventListener('click', () => generateLabel('nfpa'));
            document.getElementById('generateGHS').addEventListener('click', () => generateLabel('ghs'));
            
            // Enhanced dropdowns
            document.getElementById('uploadStateSelect').addEventListener('change', function() {
                loadCitiesByState(this.value, 'uploadCitySelect');
            });
            
            document.getElementById('searchStateSelect').addEventListener('change', function() {
                loadCitiesByState(this.value, 'searchCitySelect');
            });
            
            document.getElementById('stateFilter').addEventListener('change', updateLocationFilters);
            
            // Toast close
            document.getElementById('closeToast').addEventListener('click', hideToast);
        }
        
        // Load enhanced dashboard statistics
        async function loadDashboardStats() {
            try {
                const response = await fetch('/api/dashboard-stats');
                const stats = await response.json();
                
                document.getElementById('totalDocs').textContent = stats.total_documents;
                document.getElementById('activeLocations').textContent = stats.active_locations;
                document.getElementById('recentQuestions').textContent = stats.recent_questions;
                document.getElementById('hazardousMaterials').textContent = stats.hazardous_materials;
                
                updatePopularQuestions(stats.popular_questions);
                updateTopDepartments(stats.top_departments);
                
            } catch (error) {
                console.error('Error loading dashboard stats:', error);
            }
        }
        
        // Load departments
        async function loadDepartments() {
            try {
                const response = await fetch('/api/departments');
                const departments = await response.json();
                
                const selects = ['uploadDepartmentSelect', 'searchDepartmentSelect', 'departmentFilter'];
                selects.forEach(selectId => {
                    const select = document.getElementById(selectId);
                    if (select) {
                        departments.forEach(dept => {
                            const option = document.createElement('option');
                            option.value = dept.name;
                            option.textContent = dept.name;
                            select.appendChild(option);
                        });
                    }
                });
                
            } catch (error) {
                console.error('Error loading departments:', error);
            }
        }
        
        // Load states
        async function loadStates() {
            try {
                const response = await fetch('/api/states');
                const states = await response.json();
                
                const selects = ['uploadStateSelect', 'searchStateSelect', 'stateFilter'];
                selects.forEach(selectId => {
                    const select = document.getElementById(selectId);
                    if (select) {
                        states.forEach(state => {
                            const option = document.createElement('option');
                            option.value = state;
                            option.textContent = state;
                            select.appendChild(option);
                        });
                    }
                });
                
            } catch (error) {
                console.error('Error loading states:', error);
            }
        }
        
        // Load cities by state
        async function loadCitiesByState(state, selectId) {
            if (!state) {
                document.getElementById(selectId).innerHTML = '<option value="">Choose a city...</option>';
                return;
            }
            
            try {
                const response = await fetch(`/api/cities?state=${encodeURIComponent(state)}`);
                const cities = await response.json();
                
                const select = document.getElementById(selectId);
                select.innerHTML = '<option value="">Choose a city...</option>';
                
                cities.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city;
                    option.textContent = city;
                    select.appendChild(option);
                });
                
            } catch (error) {
                console.error('Error loading cities:', error);
            }
        }
        
        // Load recent documents
        async function loadRecentDocuments() {
            try {
                const response = await fetch('/api/recent-documents');
                const documents = await response.json();
                
                const container = document.getElementById('recentDocumentsList');
                container.innerHTML = '';
                
                if (documents.length === 0) {
                    container.innerHTML = '<p class="text-gray-500 text-center py-4">No documents uploaded yet</p>';
                    return;
                }
                
                documents.forEach(doc => {
                    const div = document.createElement('div');
                    div.className = 'p-3 border rounded-lg hover:bg-gray-50 transition cursor-pointer';
                    div.innerHTML = `
                        <h4 class="font-medium text-sm">${doc.product_name}</h4>
                        <p class="text-xs text-gray-500">${doc.location}</p>
                        <p class="text-xs text-gray-400">${new Date(doc.uploaded_date).toLocaleDateString()}</p>
                    `;
                    div.addEventListener('click', () => {
                        document.getElementById('questionInput').value = `Tell me about ${doc.product_name}`;
                        askQuestion();
                    });
                    container.appendChild(div);
                });
                
            } catch (error) {
                console.error('Error loading recent documents:', error);
            }
        }
        
        // Enhanced question asking with location filtering
        async function askQuestion() {
            const question = document.getElementById('questionInput').value.trim();
            const department = document.getElementById('departmentFilter')?.value;
            const city = document.getElementById('cityFilter')?.value;
            const state = document.getElementById('stateFilter')?.value;
            
            if (!question) {
                showToast('Please enter a question', 'warning');
                return;
            }
            
            // Add user message to chat
            addMessageToChat(question, 'user');
            document.getElementById('questionInput').value = '';
            
            // Show loading
            const loadingDiv = addMessageToChat('Analyzing SDS documents...', 'ai', true);
            
            try {
                const response = await fetch('/api/ask-question', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        question: question,
                        department: department || null,
                        city: city || null,
                        state: state || null
                    })
                });
                
                const result = await response.json();
                
                // Remove loading message
                loadingDiv.remove();
                
                if (result.success) {
                    let answer = result.answer;
                    
                    // Add location context if applicable
                    if (result.location_context) {
                        answer += `\n\n*Filtered by: ${result.location_context}*`;
                    }
                    
                    // Add sources information
                    if (result.sources && result.sources.length > 0) {
                        answer += "\n\n**Sources:**\n" + result.sources.map(s => 
                            `• ${s.product_name} (${s.location}) - ${s.content_source}`
                        ).join('\n');
                    }
                    
                    addMessageToChat(answer, 'ai');
                    
                    // Show confidence indicator
                    if (result.confidence !== undefined) {
                        showConfidence(result.confidence);
                    }
                } else {
                    addMessageToChat(result.answer || 'Sorry, I couldn\'t find an answer to your question.', 'ai');
                }
                
                // Refresh stats after question
                loadDashboardStats();
                
            } catch (error) {
                loadingDiv.remove();
                addMessageToChat('Sorry, there was an error processing your question.', 'ai');
                console.error('Error asking question:', error);
            }
        }
        
        // Show confidence indicator
        function showConfidence(confidence) {
            const indicator = document.getElementById('confidenceIndicator');
            const bar = document.getElementById('confidenceBar');
            const text = document.getElementById('confidenceText');
            
            const percentage = Math.round(confidence * 100);
            text.textContent = `${percentage}%`;
            bar.style.width = `${percentage}%`;
            
            indicator.classList.remove('hidden');
            
            // Hide after 5 seconds
            setTimeout(() => {
                indicator.classList.add('hidden');
            }, 5000);
        }
        
        // Enhanced message adding with better formatting
        function addMessageToChat(message, sender, isLoading = false) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message p-3 rounded-lg ${isLoading ? 'opacity-50' : ''}`;
            
            const senderLabel = sender === 'user' ? 'You' : 'AI Assistant';
            
            // Convert markdown-style formatting to HTML
            const formattedMessage = message
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n/g, '<br>');
            
            messageDiv.innerHTML = `<p><strong>${senderLabel}:</strong> ${formattedMessage}</p>`;
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            return messageDiv;
        }
        
        // Handle enhanced file upload
        async function handleFileUpload(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const fileInput = document.getElementById('file-upload');
            const department = document.getElementById('uploadDepartmentSelect').value;
            const city = document.getElementById('uploadCitySelect').value;
            const state = document.getElementById('uploadStateSelect').value;
            const country = e.target.country.value;
            
            if (!fileInput.files[0] || !department || !city || !state) {
                showToast('Please fill in all required fields', 'warning');
                return;
            }
            
            formData.append('file', fileInput.files[0]);
            formData.append('department', department);
            formData.append('city', city);
            formData.append('state', state);
            formData.append('country', country);
            
            const uploadBtn = e.target.querySelector('button[type="submit"]');
            
            // Show loading state
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Uploading...';
            uploadBtn.disabled = true;
            
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(`File uploaded successfully: ${result.product_name}`, 'success');
                    hideModal('uploadModal');
                    e.target.reset();
                    loadDashboardStats();
                    loadRecentDocuments();
                } else {
                    showToast(result.message, 'error');
                }
                
            } catch (error) {
                console.error('Error uploading file:', error);
                showToast('Error uploading file', 'error');
            } finally {
                uploadBtn.innerHTML = '<i class="fas fa-upload mr-2"></i>Upload';
                uploadBtn.disabled = false;
            }
        }
        
        // Handle web search for SDS
        async function handleWebSearch(e) {
            e.preventDefault();
            
            const chemicalName = document.getElementById('searchChemicalName').value.trim();
            const department = document.getElementById('searchDepartmentSelect').value;
            const city = document.getElementById('searchCitySelect').value;
            const state = document.getElementById('searchStateSelect').value;
            
            if (!chemicalName || !department || !city || !state) {
                showToast('Please fill in all required fields', 'warning');
                return;
            }
            
            const searchBtn = e.target.querySelector('button[type="submit"]');
            
            // Show loading state
            searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Searching...';
            searchBtn.disabled = true;
            
            try {
                const response = await fetch('/api/search-web-sds', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        chemical_name: chemicalName,
                        department: department,
                        city: city,
                        state: state
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(`Found and stored SDS for ${result.product_name}`, 'success');
                    hideModal('webSearchModal');
                    e.target.reset();
                    loadDashboardStats();
                    loadRecentDocuments();
                } else {
                    showToast(result.message, 'error');
                }
                
            } catch (error) {
                console.error('Error searching for SDS:', error);
                showToast('Error searching for SDS', 'error');
            } finally {
                searchBtn.innerHTML = '<i class="fas fa-search mr-2"></i>Search & Download';
                searchBtn.disabled = false;
            }
        }
        
        // Generate label (renamed from sticker)
        async function generateLabel(type) {
            const productName = document.getElementById('labelProductName').value.trim();
            
            if (!productName) {
                showToast('Please enter a product name', 'warning');
                return;
            }
            
            try {
                const endpoint = type === 'nfpa' ? '/api/generate-nfpa' : '/api/generate-ghs';
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ product_name: productName })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(`${result.label_type} label generated successfully`, 'success');
                    hideModal('labelModal');
                    
                    // Create download link
                    const link = document.createElement('a');
                    link.href = `/api/download-label/${result.filename}`;
                    link.download = result.filename;
                    link.click();
                } else {
                    showToast(result.message, 'error');
                }
                
            } catch (error) {
                console.error('Error generating label:', error);
                showToast('Error generating label', 'error');
            }
        }
        
        // Update location filters based on selection
        function updateLocationFilters() {
            const state = document.getElementById('stateFilter').value;
            if (state) {
                loadCitiesByState(state, 'cityFilter');
            } else {
                document.getElementById('cityFilter').innerHTML = '<option value="">All Cities</option>';
            }
        }
        
        // Update popular questions display
        function updatePopularQuestions(questions) {
            const container = document.getElementById('popularQuestions');
            container.innerHTML = '';
            
            if (questions.length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-center py-4">No questions asked yet</p>';
                return;
            }
            
            questions.forEach(q => {
                const div = document.createElement('div');
                div.className = 'flex justify-between items-center p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition';
                div.innerHTML = `
                    <div>
                        <p class="text-sm font-medium">${q.question}</p>
                        <p class="text-xs text-gray-500">${q.count} times asked</p>
                    </div>
                    <i class="fas fa-chevron-right text-gray-400"></i>
                `;
                div.addEventListener('click', () => {
                    document.getElementById('questionInput').value = q.question;
                    askQuestion();
                });
                container.appendChild(div);
            });
        }
        
        // Update top departments display
        function updateTopDepartments(departments) {
            const container = document.getElementById('topDepartments');
            container.innerHTML = '';
            
            if (departments.length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-center py-4">No data available yet</p>';
                return;
            }
            
            departments.forEach(dept => {
                const div = document.createElement('div');
                div.className = 'flex justify-between items-center p-3 bg-gray-50 rounded-lg';
                div.innerHTML = `
                    <div>
                        <p class="text-sm font-medium">${dept.department}</p>
                        <p class="text-xs text-gray-500">${dept.count} documents</p>
                    </div>
                    <div class="w-16 bg-gray-200 rounded-full h-2">
                        <div class="bg-blue-600 h-2 rounded-full" style="width: ${Math.min(100, (dept.count / departments[0].count) * 100)}%"></div>
                    </div>
                `;
                container.appendChild(div);
            });
        }
        
        // Modal utilities
        function showModal(modalId) {
            document.getElementById(modalId).classList.remove('hidden');
            
            // Load data when showing modals
            if (modalId === 'uploadModal' || modalId === 'webSearchModal') {
                loadDepartments();
                loadStates();
            }
        }
        
        function hideModal(modalId) {
            document.getElementById(modalId).classList.add('hidden');
            
            // Reset forms when hiding modals
            const modal = document.getElementById(modalId);
            const forms = modal.querySelectorAll('form');
            forms.forEach(form => form.reset());
        }
        
        // Enhanced toast notification utility
        function showToast(message, type = 'info') {
            const toast = document.getElementById('toast');
            const icon = document.getElementById('toastIcon');
            const messageEl = document.getElementById('toastMessage');
            
            messageEl.textContent = message;
            
            const config = {
                success: { icon: 'fas fa-check-circle text-green-500', border: 'border-green-400' },
                error: { icon: 'fas fa-exclamation-circle text-red-500', border: 'border-red-400' },
                warning: { icon: 'fas fa-exclamation-triangle text-yellow-500', border: 'border-yellow-400' },
                info: { icon: 'fas fa-info-circle text-blue-500', border: 'border-blue-400' }
            };
            
            icon.className = config[type].icon;
            toast.querySelector('div > div').className = `bg-white rounded-lg shadow-lg border-l-4 ${config[type].border} p-4 max-w-sm`;
            
            toast.classList.remove('hidden');
            
            setTimeout(() => {
                hideToast();
            }, 5000);
        }
        
        function hideToast() {
            document.getElementById('toast').classList.add('hidden');
        }
        
        // Auto-refresh dashboard every 30 seconds
        setInterval(loadDashboardStats, 30000);
    </script>
</body>
</html><!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EHS Smart System - SDS Assistant</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card-hover:hover { transform: translateY(-2px); transition: transform 0.3s; }
        .chat-container { max-height: 500px; overflow-y: auto; }
        .message { margin-bottom: 1rem; animation: fadeIn 0.3s ease-in; }
        .user-message { background: #3b82f6; color: white; }
        .ai-message { background: #f3f4f6; color: #374151; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .filter-section { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }
        .confidence-bar { height: 4px; border-radius: 2px; transition: width 0.5s ease; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Enhanced Navigation -->
    <nav class="gradient-bg shadow-lg">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <i class="fas fa-shield-alt text-white text-2xl mr-3"></i>
                    <span class="text-white text-xl font-bold">EHS Smart System</span>
                    <span class="text-white text-sm ml-2 opacity-75">Safety Data Sheet Assistant</span>
                </div>
                <div class="flex items-center space-x-4">
                    <button id="uploadBtn" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition">
                        <i class="fas fa-upload mr-2"></i>Upload SDS
                    </button>
                    <button id="generateLabelBtn" class="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg transition">
                        <i class="fas fa-tags mr-2"></i>Generate Labels
                    </button>
                    <button id="webSearchBtn" class="bg-purple-500 hover:bg-purple-600 text-white px-4
