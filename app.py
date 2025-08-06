# Enhanced SDS Assistant with Web Search Integration
import os
from flask import Flask, render_template_string, request, jsonify, send_file, session
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
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sds-assistant-secret-key-2024')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create necessary directories
for folder in ['static/uploads', 'static/stickers', 'static/exports', 'data']:
    Path(folder).mkdir(parents=True, exist_ok=True)

class EnhancedSDSAssistant:
    def __init__(self, db_path: str = "data/sds_database.db"):
        self.db_path = db_path
        self.setup_database()
        self.populate_us_cities()
        
        # Web search configuration
        self.search_engines = {
            'google': 'https://www.google.com/search?q=',
            'duckduckgo': 'https://duckduckgo.com/?q=',
            'bing': 'https://www.bing.com/search?q='
        }
        
        # Common SDS providers
        self.sds_providers = [
            'sigmaaldrich.com',
            'fishersci.com',
            'merckmillipore.com',
            'thermofisher.com',
            'vwr.com',
            'honeywell.com',
            'dupont.com'
        ]
    
    def setup_database(self):
        """Initialize the database with enhanced tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add web_search_cache table for caching web results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS web_search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_query TEXT NOT NULL,
                search_results TEXT NOT NULL,
                source_url TEXT,
                confidence_score REAL DEFAULT 0.0,
                cache_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_valid BOOLEAN DEFAULT 1,
                UNIQUE(search_query)
            )
        ''')
        
        # Enhanced Q&A history with web source tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                document_id INTEGER,
                location_id INTEGER,
                user_session TEXT,
                confidence_score REAL,
                source_type TEXT DEFAULT 'local',
                web_source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES sds_documents (id),
                FOREIGN KEY (location_id) REFERENCES locations (id)
            )
        ''')
        
        # Enhanced chemical_hazards table
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
                ghs_precautionary_statements TEXT,
                first_aid TEXT,
                fire_fighting TEXT,
                handling_storage TEXT,
                exposure_controls TEXT,
                physical_properties TEXT,
                toxicological_info TEXT,
                source_type TEXT DEFAULT 'upload',
                web_source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES sds_documents (id)
            )
        ''')
        
        # Add indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_web_search_query ON web_search_cache(search_query)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_qa_source_type ON qa_history(source_type)')
        
        conn.commit()
        conn.close()
    
    def search_web_for_chemical_info(self, chemical_name: str, question_context: str = "") -> Dict:
        """Search web for chemical safety information"""
        try:
            # Check cache first
            cache_result = self.get_cached_search_result(chemical_name, question_context)
            if cache_result:
                return cache_result
            
            # Prepare search queries
            search_queries = self.prepare_search_queries(chemical_name, question_context)
            
            best_result = {"success": False, "answer": "", "sources": [], "confidence": 0.0}
            
            for query in search_queries:
                try:
                    result = self.perform_web_search(query)
                    if result["success"] and result["confidence"] > best_result["confidence"]:
                        best_result = result
                        
                    # Cache the result
                    self.cache_search_result(query, result)
                    
                    # If we found a good result, break
                    if result["confidence"] > 0.7:
                        break
                        
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error in web search for query '{query}': {str(e)}")
                    continue
            
            return best_result
            
        except Exception as e:
            print(f"Error in web search: {str(e)}")
            return {
                "success": False,
                "answer": "Sorry, I couldn't search the web for additional information at this time.",
                "sources": [],
                "confidence": 0.0
            }
    
    def prepare_search_queries(self, chemical_name: str, question_context: str) -> List[str]:
        """Prepare targeted search queries based on question context"""
        base_queries = []
        
        # Determine question type for targeted searches
        context_lower = question_context.lower()
        
        if any(word in context_lower for word in ["first aid", "emergency", "exposure", "poisoning"]):
            base_queries.extend([
                f'"{chemical_name}" safety data sheet first aid emergency',
                f'"{chemical_name}" SDS first aid measures exposure treatment',
                f'"{chemical_name}" emergency procedures safety'
            ])
        elif any(word in context_lower for word in ["fire", "firefighting", "extinguish", "combustible"]):
            base_queries.extend([
                f'"{chemical_name}" safety data sheet fire fighting measures',
                f'"{chemical_name}" SDS fire extinguishing firefighting',
                f'"{chemical_name}" fire hazard combustible flammable'
            ])
        elif any(word in context_lower for word in ["storage", "handling", "precautions"]):
            base_queries.extend([
                f'"{chemical_name}" safety data sheet handling storage',
                f'"{chemical_name}" SDS storage conditions handling precautions',
                f'"{chemical_name}" safe handling storage requirements'
            ])
        elif any(word in context_lower for word in ["ppe", "protection", "protective equipment"]):
            base_queries.extend([
                f'"{chemical_name}" safety data sheet PPE personal protective equipment',
                f'"{chemical_name}" SDS protective equipment exposure controls',
                f'"{chemical_name}" safety equipment protection measures'
            ])
        elif any(word in context_lower for word in ["hazard", "danger", "toxic", "health"]):
            base_queries.extend([
                f'"{chemical_name}" safety data sheet health hazards',
                f'"{chemical_name}" SDS toxicity health effects',
                f'"{chemical_name}" chemical hazards health risks'
            ])
        else:
            # General safety information
            base_queries.extend([
                f'"{chemical_name}" safety data sheet SDS',
                f'"{chemical_name}" chemical safety information',
                f'"{chemical_name}" MSDS safety sheet'
            ])
        
        # Add site-specific searches for major SDS providers
        for provider in self.sds_providers[:3]:  # Limit to top 3 to avoid too many requests
            base_queries.append(f'site:{provider} "{chemical_name}" safety data sheet')
        
        return base_queries[:5]  # Limit to 5 queries to avoid rate limiting
    
    def perform_web_search(self, query: str) -> Dict:
        """Perform actual web search and extract relevant information"""
        try:
            # Use DuckDuckGo for search (no API key required)
            search_url = f"https://duckduckgo.com/html/?q={quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse search results
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('a', class_='result__a')
            
            if not results:
                return {"success": False, "answer": "", "sources": [], "confidence": 0.0}
            
            # Try to extract information from top results
            best_info = {"answer": "", "source_url": "", "confidence": 0.0}
            
            for result in results[:3]:  # Check top 3 results
                try:
                    url = result.get('href')
                    if not url or not self.is_reliable_source(url):
                        continue
                    
                    # Try to fetch and parse the page
                    page_info = self.extract_info_from_page(url, query)
                    if page_info["confidence"] > best_info["confidence"]:
                        best_info = page_info
                        
                except Exception as e:
                    print(f"Error processing search result {url}: {str(e)}")
                    continue
            
            if best_info["confidence"] > 0.3:
                return {
                    "success": True,
                    "answer": best_info["answer"],
                    "sources": [{"url": best_info["source_url"], "type": "web"}],
                    "confidence": best_info["confidence"]
                }
            else:
                return {"success": False, "answer": "", "sources": [], "confidence": 0.0}
                
        except Exception as e:
            print(f"Error in web search: {str(e)}")
            return {"success": False, "answer": "", "sources": [], "confidence": 0.0}
    
    def is_reliable_source(self, url: str) -> bool:
        """Check if the URL is from a reliable source"""
        reliable_domains = [
            'sigmaaldrich.com', 'fishersci.com', 'merckmillipore.com',
            'thermofisher.com', 'vwr.com', 'honeywell.com', 'dupont.com',
            'cdc.gov', 'osha.gov', 'epa.gov', 'nist.gov',
            'nih.gov', 'pubchem.ncbi.nlm.nih.gov'
        ]
        
        return any(domain in url.lower() for domain in reliable_domains)
    
    def extract_info_from_page(self, url: str, query: str) -> Dict:
        """Extract relevant safety information from a web page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for safety-related sections
            safety_sections = []
            
            # Common safety section indicators
            safety_keywords = [
                'first aid', 'emergency', 'fire fighting', 'firefighting',
                'handling', 'storage', 'exposure controls', 'personal protection',
                'hazard', 'precaution', 'safety'
            ]
            
            # Extract text from paragraphs and divs
            for element in soup.find_all(['p', 'div', 'td', 'li']):
                text = element.get_text().strip()
                if len(text) > 50 and any(keyword in text.lower() for keyword in safety_keywords):
                    safety_sections.append(text)
            
            if safety_sections:
                # Combine and limit the text
                combined_text = '. '.join(safety_sections[:3])  # Top 3 sections
                if len(combined_text) > 500:
                    combined_text = combined_text[:500] + "..."
                
                confidence = min(0.8, len(safety_sections) * 0.2)  # Max 0.8 confidence
                
                return {
                    "answer": combined_text,
                    "source_url": url,
                    "confidence": confidence
                }
            
            return {"answer": "", "source_url": url, "confidence": 0.0}
            
        except Exception as e:
            print(f"Error extracting info from {url}: {str(e)}")
            return {"answer": "", "source_url": url, "confidence": 0.0}
    
    def cache_search_result(self, query: str, result: Dict):
        """Cache web search results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO web_search_cache 
                (search_query, search_results, source_url, confidence_score)
                VALUES (?, ?, ?, ?)
            ''', (
                query, 
                json.dumps(result),
                result.get("sources", [{}])[0].get("url", "") if result.get("sources") else "",
                result.get("confidence", 0.0)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error caching search result: {str(e)}")
    
    def get_cached_search_result(self, chemical_name: str, question_context: str) -> Optional[Dict]:
        """Get cached search result if available and recent"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Look for recent cache entries (within 24 hours)
            cursor.execute('''
                SELECT search_results FROM web_search_cache 
                WHERE search_query LIKE ? 
                AND cache_timestamp > datetime('now', '-24 hours')
                AND is_valid = 1
                ORDER BY confidence_score DESC
                LIMIT 1
            ''', (f"%{chemical_name}%",))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                cached_result = json.loads(result[0])
                cached_result["from_cache"] = True
                return cached_result
                
            return None
            
        except Exception as e:
            print(f"Error retrieving cached search result: {str(e)}")
            return None
    
    def answer_question(self, question: str, location_id: int = None, user_session: str = None) -> Dict:
        """Enhanced question answering with automatic web search fallback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # First, search local SDS documents
            local_result = self.search_local_documents(question, location_id, cursor)
            
            if local_result["success"] and local_result["confidence"] > 0.5:
                # Good local result found
                self.log_qa_interaction(cursor, question, local_result, location_id, user_session, "local")
                conn.commit()
                conn.close()
                return local_result
            
            # Extract chemical name from question for web search
            chemical_name = self.extract_chemical_name_from_question(question)
            
            if chemical_name:
                print(f"Searching web for chemical: {chemical_name}")
                web_result = self.search_web_for_chemical_info(chemical_name, question)
                
                if web_result["success"]:
                    # Combine local and web results
                    combined_result = self.combine_local_and_web_results(local_result, web_result)
                    self.log_qa_interaction(cursor, question, combined_result, location_id, user_session, "web")
                    conn.commit()
                    conn.close()
                    return combined_result
            
            # No good results found
            conn.close()
            return {
                "success": False,
                "answer": "I couldn't find specific information about this in your SDS documents or through web search. Please check if you have uploaded the relevant SDS file, or try rephrasing your question with the specific chemical name.",
                "sources": [],
                "confidence": 0.0
            }
            
        except Exception as e:
            print(f"Error in answer_question: {str(e)}")
            return {"success": False, "answer": f"Error processing question: {str(e)}", "sources": []}
    
    def search_local_documents(self, question: str, location_id: int, cursor) -> Dict:
        """Search local SDS documents"""
        search_query = '''
            SELECT sd.id, sd.product_name, sd.full_text, 
                   ch.first_aid, ch.fire_fighting, ch.handling_storage, ch.exposure_controls,
                   l.department, l.city, l.state
            FROM sds_documents sd
            LEFT JOIN chemical_hazards ch ON sd.id = ch.document_id
            LEFT JOIN locations l ON sd.location_id = l.id
            WHERE sd.full_text LIKE ? OR sd.product_name LIKE ?
        '''
        
        params = [f"%{question}%", f"%{question}%"]
        
        if location_id:
            search_query += " AND sd.location_id = ?"
            params.append(location_id)
        
        search_query += " ORDER BY sd.created_at DESC LIMIT 10"
        
        cursor.execute(search_query, params)
        documents = cursor.fetchall()
        
        if not documents:
            return {"success": False, "answer": "", "sources": [], "confidence": 0.0}
        
        return self.generate_answer_from_documents(question, documents)
    
    def extract_chemical_name_from_question(self, question: str) -> str:
        """Extract chemical name from question"""
        # Common chemical name patterns
        chemical_patterns = [
            r'\b([A-Z][a-z]*(?:\s+[A-Z][a-z]*)*)\b',  # Proper nouns
            r'\b(\w+(?:\s+\w+)*)\s+(?:chemical|compound|substance)\b',
            r'(?:chemical|compound|substance)\s+(\w+(?:\s+\w+)*)',
            r'\b(acetone|benzene|toluene|methanol|ethanol|sulfuric\s+acid|hydrochloric\s+acid|sodium\s+hydroxide|ammonia|chlorine|formaldehyde)\b'
        ]
        
        question_lower = question.lower()
        
        # Check for common chemicals first
        common_chemicals = [
            'acetone', 'benzene', 'toluene', 'methanol', 'ethanol', 'water',
            'sulfuric acid', 'hydrochloric acid', 'sodium hydroxide', 'ammonia',
            'chlorine', 'formaldehyde', 'hydrogen peroxide', 'bleach'
        ]
        
        for chemical in common_chemicals:
            if chemical in question_lower:
                return chemical
        
        # Try to extract from patterns
        for pattern in chemical_patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            if matches:
                return matches[0] if isinstance(matches[0], str) else matches[0][0]
        
        return ""
    
    def combine_local_and_web_results(self, local_result: Dict, web_result: Dict) -> Dict:
        """Combine local and web search results"""
        combined_answer = ""
        combined_sources = []
        combined_confidence = 0.0
        
        if local_result.get("answer"):
            combined_answer += "**From your SDS documents:**\n" + local_result["answer"] + "\n\n"
            combined_sources.extend(local_result.get("sources", []))
            combined_confidence += local_result.get("confidence", 0.0) * 0.7  # Weight local higher
        
        if web_result.get("answer"):
            combined_answer += "**Additional information from web sources:**\n" + web_result["answer"]
            web_sources = web_result.get("sources", [])
            for source in web_sources:
                source["type"] = "web"
            combined_sources.extend(web_sources)
            combined_confidence += web_result.get("confidence", 0.0) * 0.3  # Weight web lower
        
        return {
            "success": True,
            "answer": combined_answer.strip(),
            "sources": combined_sources,
            "confidence": min(combined_confidence, 1.0),
            "has_web_results": bool(web_result.get("answer"))
        }
    
    def log_qa_interaction(self, cursor, question: str, result: Dict, location_id: int, user_session: str, source_type: str):
        """Log Q&A interaction with source tracking"""
        web_source_url = ""
        if result.get("sources"):
            web_sources = [s for s in result["sources"] if s.get("type") == "web"]
            if web_sources:
                web_source_url = web_sources[0].get("url", "")
        
        cursor.execute('''
            INSERT INTO qa_history (
                question, answer, location_id, user_session, 
                confidence_score, source_type, web_source_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            question, result.get("answer", ""), location_id, user_session,
            result.get("confidence", 0.0), source_type, web_source_url
        ))
    
    def generate_enhanced_ghs_sticker(self, product_name: str, custom_data: Dict = None) -> Dict:
        """Generate enhanced GHS sticker with more options"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get existing data or use custom data
            if custom_data:
                hazard_data = custom_data
                actual_name = product_name
            else:
                cursor.execute('''
                    SELECT ch.ghs_signal_word, ch.ghs_pictograms, ch.ghs_hazard_statements,
                           ch.ghs_precautionary_statements, sd.product_name
                    FROM chemical_hazards ch
                    JOIN sds_documents sd ON ch.document_id = sd.id
                    WHERE LOWER(sd.product_name) LIKE ?
                    ORDER BY ch.created_at DESC LIMIT 1
                ''', (f"%{product_name.lower()}%",))
                
                result = cursor.fetchone()
                if not result:
                    conn.close()
                    return {"success": False, "message": f"No GHS data found for {product_name}"}
                
                signal_word, pictograms, hazard_statements, precautionary_statements, actual_name = result
                hazard_data = {
                    "signal_word": signal_word or "WARNING",
                    "pictograms": pictograms or "",
                    "hazard_statements": hazard_statements or "",
                    "precautionary_statements": precautionary_statements or ""
                }
            
            conn.close()
            
            # Generate comprehensive GHS label
            svg_content = self.create_enhanced_ghs_svg(actual_name, hazard_data)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            sticker_filename = f"ghs_{secure_filename(actual_name)}_{timestamp}.svg"
            sticker_path = Path('static/stickers') / sticker_filename
            
            with open(sticker_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            return {
                "success": True,
                "filename": sticker_filename,
                "sticker_type": "GHS",
                "data": hazard_data
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error generating GHS sticker: {str(e)}"}
    
    def create_enhanced_ghs_svg(self, product_name: str, hazard_data: Dict) -> str:
        """Create enhanced GHS SVG with proper formatting"""
        
        # GHS pictogram symbols (simplified representations)
        pictogram_symbols = {
            "explosive": "💥",
            "flammable": "🔥", 
            "oxidizing": "⭕",
            "compressed gas": "🫧",
            "corrosive": "⚠️",
            "toxic": "☠️",
            "harmful": "⚠️",
            "health hazard": "⚠️",
            "environmental": "🐟"
        }
        
        # Determine pictogram symbols to display
        pictograms = hazard_data.get("pictograms", "").lower()
        symbols_to_show = []
        for key, symbol in pictogram_symbols.items():
            if key in pictograms:
                symbols_to_show.append(symbol)
        
        # Limit to 4 symbols
        symbols_to_show = symbols_to_show[:4]
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="500" xmlns="http://www.w3.org/2000/svg">
    <style>
        .header {{ font-family: Arial, sans-serif; font-size: 20px; font-weight: bold; text-anchor: middle; }}
        .product {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; text-anchor: middle; }}
        .signal {{ font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; text-anchor: middle; }}
        .section-title {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; }}
        .content {{ font-family: Arial, sans-serif; font-size: 12px; }}
        .pictogram {{ font-size: 30px; text-anchor: middle; }}
    </style>
    
    <!-- Border -->
    <rect width="400" height="500" fill="white" stroke="red" stroke-width="4"/>
    
    <!-- Header -->
    <rect x="0" y="0" width="400" height="50" fill="#ff0000"/>
    <text x="200" y="30" class="header" fill="white">GHS SAFETY LABEL</text>
    
    <!-- Product Name -->
    <text x="200" y="80" class="product" fill="black">{product_name[:35]}</text>
    
    <!-- Signal Word -->
    <text x="200" y="110" class="signal" fill="red">{hazard_data.get('signal_word', 'WARNING')}</text>
    
    <!-- Pictograms -->
    <g transform="translate(0, 130)">
        <text x="20" y="20" class="section-title" fill="black">Hazard Pictograms:</text>'''
        
        # Add pictogram symbols
        for i, symbol in enumerate(symbols_to_show):
            x_pos = 50 + (i * 80)
            svg_content += f'\n        <text x="{x_pos}" y="60" class="pictogram">{symbol}</text>'
        
        svg_content += f'''
    </g>
    
    <!-- Hazard Statements -->
    <g transform="translate(0, 220)">
        <text x="20" y="20" class="section-title" fill="black">Hazard Statements:</text>
        <foreignObject x="20" y="30" width="360" height="80">
            <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Arial; font-size: 11px; line-height: 1.3;">
                {(hazard_data.get('hazard_statements', 'See SDS for complete hazard information'))[:200]}
            </div>
        </foreignObject>
    </g>
    
    <!-- Precautionary Statements -->
    <g transform="translate(0, 320)">
        <text x="20" y="20" class="section-title" fill="black">Precautionary Statements:</text>
        <foreignObject x="20" y="30" width="360" height="80">
            <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Arial; font-size: 11px; line-height: 1.3;">
                {(hazard_data.get('precautionary_statements', 'Read SDS before use. Wear appropriate PPE.'))[:200]}
            </div>
        </foreignObject>
    </g>
    
    <!-- Footer -->
    <text x="200" y="470" class="content" text-anchor="middle" fill="black">
        Consult Safety Data Sheet for complete information
    </text>
    <text x="200" y="490" class="content" text-anchor="middle" fill="gray">
        Generated: {datetime.now().strftime('%Y-%m-%d')}
    </text>
    
</svg>'''
        
        return svg_content

# Additional route for enhanced GHS generation with options
@app.route('/api/generate-ghs-enhanced', methods=['POST'])
def generate_ghs_enhanced():
    """Generate enhanced GHS sticker with custom options"""
    data = request.json
    product_name = data.get('product_name')
    custom_data = data.get('custom_data')  # Optional custom GHS data
    
    if not product_name:
        return jsonify({"success": False, "message": "Product name is required"})
    
    result = sds_assistant.generate_enhanced_ghs_sticker(product_name, custom_data)
    return jsonify(result)

# Enhanced route for question answering
@app.route('/api/ask-question-enhanced', methods=['POST'])
def ask_question_enhanced():
    """Enhanced question answering with web search"""
    data = request.json
    question = data.get('question')
    location_id = data.get('location_id')
    user_session = session.get('user_id', 'anonymous')
    
    if not question:
        return jsonify({"success": False, "answer": "Please provide a question"})
    
    result = sds_assistant.answer_question(question, location_id, user_session)
    return jsonify(result)

# Initialize the enhanced assistant
sds_assistant = EnhancedSDSAssistant()
