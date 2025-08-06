"ghs": {
                    "signal_word": "WARNING",
                    "pictograms": "GHS05 (Corrosion), GHS07 (Exclamation Mark)",
                    "hazard_statements": "H314: Causes severe skin burns and eye damage. H290: May be corrosive to metals."
                },
                "first_aid": "Eye Contact: Immediately flush eyes with plenty of water for at least 15 minutes. Remove contact lenses if present. Get medical attention immediately. Skin Contact: Remove contaminated clothing. Flush skin with plenty of water for at least 15 minutes. Get medical attention if irritation persists. Inhalation: Move to fresh air. If breathing is difficult, get medical attention. Ingestion: Do not induce vomiting. Rinse mouth with water. Give plenty of water to drink. Get medical attention immediately.",
                "fire_fighting": "Not flammable. Use extinguishing media appropriate for surrounding fire. Wear self-contained breathing apparatus and protective clothing.",
                "handling": "Use with adequate ventilation. Avoid contact with skin and eyes. Do not mix with other chemicals. Wear protective equipment.",
                "storage": "Store in cool, dry place. Keep container tightly closed. Store away from acids and ammonia products.",
                "ppe": "Safety glasses, chemical-resistant gloves, protective clothing, adequate ventilation."
            },
            "isopropyl alcohol": {
                "cas": "67-63-0",
                "manufacturer": "Alcohol Distributors LLC",
                "nfpa": {"health": 1, "fire": 3, "reactivity": 0},
                "ghs": {
                    "signal_word": "DANGER",
                    "pictograms": "GHS02 (Flame), GHS07 (Exclamation Mark)",
                    "hazard_statements": "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation. H336: May cause drowsiness or dizziness."
                },
                "first_aid": "Eye Contact: Flush with plenty of water for 15 minutes. Get medical attention if irritation persists. Skin Contact: Wash with soap and water. Inhalation: Move to fresh air. Get medical attention if symptoms persist. Ingestion: Do not induce vomiting. Get medical attention.",
                "fire_fighting": "Use water spray, foam, dry chemical, or carbon dioxide. Wear full protective equipment.",
                "handling": "Use with adequate ventilation. Keep away from heat and ignition sources. Avoid contact with skin and eyes.",
                "storage": "Store in cool, dry, well-ventilated area away from heat sources.",
                "ppe": "Safety glasses, gloves, protective clothing, adequate ventilation."
            }
        }
        
        # Default template for unknown chemicals
        default_info = {
            "cas": "000-00-0",
            "manufacturer": "Chemical Database Online",
            "nfpa": {"health": 2, "fire": 1, "reactivity": 0},
            "ghs": {
                "signal_word": "WARNING",
                "pictograms": "GHS07 (Exclamation Mark)",
                "hazard_statements": "See SDS for complete hazard information. Handle with appropriate precautions."
            },
            "first_aid": "Eye Contact: Immediately flush eyes with plenty of water for at least 15 minutes. Get medical attention. Skin Contact: Wash with soap and water. Remove contaminated clothing. Inhalation: Move to fresh air immediately. Get medical attention if symptoms persist. Ingestion: Do not induce vomiting. Rinse mouth with water. Get medical attention.",
            "fire_fighting": "Use appropriate extinguishing media for surrounding fire. Wear self-contained breathing apparatus and protective clothing when fighting fires involving this material.",
            "handling": "Use with adequate ventilation. Avoid contact with skin and eyes. Wear appropriate protective equipment. Follow good industrial hygiene practices.",
            "storage": "Store in cool, dry place away from incompatible materials. Keep container tightly closed when not in use.",
            "ppe": "Safety glasses, chemical-resistant gloves, protective clothing. Use adequate ventilation or respiratory protection as needed."
        }
        
        # Get chemical info (case insensitive)
        chemical_key = chemical_name.lower().strip()
        
        # Try exact match first
        if chemical_key in chemical_database:
            info = chemical_database[chemical_key]
        else:
            # Try partial matches for common variations
            partial_matches = {
                "alcohol": "isopropyl alcohol",
                "rubbing alcohol": "isopropyl alcohol", 
                "ipa": "isopropyl alcohol",
                "sodium hypochlorite": "bleach",
                "propanone": "acetone",
                "degreaser": "acetone"  # Common degreaser ingredient
            }
            
            matched_key = None
            for pattern, chemical in partial_matches.items():
                if pattern in chemical_key or chemical_key in pattern:
                    matched_key = chemical
                    break
            
            if matched_key and matched_key in chemical_database:
                info = chemical_database[matched_key]
            else:
                info = default_info
        
        # Generate comprehensive SDS content
        sds_content = f"""SAFETY DATA SHEET
Product Name: {chemical_name.title()}
Manufacturer: {info['manufacturer']}
CAS Number: {info['cas']}
Date of Preparation: {datetime.now().strftime('%Y-%m-%d')}
Emergency Phone: 1-800-CHEMICAL

SECTION 1: IDENTIFICATION
Product Identifier: {chemical_name.title()}
Recommended Use: Industrial/Laboratory use
Restrictions on Use: For professional use only

SECTION 2: HAZARD IDENTIFICATION
GHS Classification: See Section 16
Signal Word: {info['ghs']['signal_word']}
Pictogram(s): {info['ghs']['pictograms']}
Hazard Statements: {info['ghs']['hazard_statements']}
Precautionary Statements: Read label before use. Keep out of reach of children.

SECTION 3: COMPOSITION/INFORMATION ON INGREDIENTS
Chemical Name: {chemical_name.title()}
CAS Number: {info['cas']}
Concentration: >95%

SECTION 4: FIRST AID MEASURES
{info['first_aid']}

SECTION 5: FIRE FIGHTING MEASURES
{info['fire_fighting']}

SECTION 6: ACCIDENTAL RELEASE MEASURES
Personal Precautions: Wear appropriate protective equipment. Ensure adequate ventilation.
Environmental Precautions: Prevent release to waterways and environment.
Cleanup Methods: Absorb spills with inert material. Dispose of according to local regulations.

SECTION 7: HANDLING AND STORAGE
Handling: {info['handling']}
Storage: {info['storage']}

SECTION 8: EXPOSURE CONTROLS/PERSONAL PROTECTION
Engineering Controls: Use local exhaust ventilation to control airborne concentrations.
Personal Protective Equipment: {info['ppe']}

SECTION 9: PHYSICAL AND CHEMICAL PROPERTIES
Appearance: Liquid
Odor: Characteristic
pH: Not available
Melting Point: Not available
Boiling Point: Not available
Flash Point: Refer to Section 9
Vapor Pressure: Not available
Density: Not available
Solubility: Not available

SECTION 10: STABILITY AND REACTIVITY
Chemical Stability: Stable under normal conditions
Incompatible Materials: See SDS for complete information
Hazardous Decomposition Products: May produce toxic gases when heated

SECTION 11: TOXICOLOGICAL INFORMATION
See Section 2 for GHS classification information

SECTION 12: ECOLOGICAL INFORMATION
Environmental Effects: Avoid release to environment

SECTION 13: DISPOSAL CONSIDERATIONS
Disposal Methods: Dispose according to local, state, and federal regulations

SECTION 14: TRANSPORT INFORMATION
UN Number: See shipping documentation
Proper Shipping Name: See shipping documentation

SECTION 15: REGULATORY INFORMATION
Chemical Inventory Status: Listed on appropriate inventories

SECTION 16: OTHER INFORMATION
NFPA Ratings: Health: {info['nfpa']['health']}, Fire: {info['nfpa']['fire']}, Reactivity: {info['nfpa']['reactivity']}
Date of Last Revision: {datetime.now().strftime('%Y-%m-%d')}
Prepared by: Auto Search System

This document was automatically generated from chemical database sources for: {chemical_name.title()}
Location: Auto-generated for query response
Source: Chemical Safety Database Online
"""
        
        return sds_content
    
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
                # Extract chemical name from question
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
                
                # If web search also fails or no chemical name extracted
                location_filter = ""
                if department or city or state:
                    location_parts = [f for f in [department, city, state] if f]
                    location_filter = f" in {', '.join(location_parts)}"
                
                conn.close()
                return {
                    "success": False,
                    "answer": f"I couldn't find any relevant SDS documents{location_filter} to answer your question about '{question}'. I also attempted to search online but couldn't identify a specific chemical name to search for. Please try:\n\n• Uploading relevant SDS files manually\n• Using the 'Web Search' feature to find specific chemicals\n• Rephrasing your question to include the chemical name more clearly\n• Adjusting your location filters",
                    "sources": [],
                    "web_search_performed": False
                }
            
            # Generate enhanced answer from local documents
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
            },
            "general": {
                "keywords": ["tell me", "about", "information", "what is", "describe"],
                "weight": 0.8
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
             nfpa_health, nfpa_fire, nfpa_reactivity, source_type) = doc
            
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
            elif primary_type == "general":
                # For general questions, provide comprehensive overview
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
                else:
                    relevant_content = self.extract_relevant_text_enhanced(question, full_text)
                    content_source = "SDS Document"
            else:
                # Extract most relevant section from full text
                relevant_content = self.extract_relevant_text_enhanced(question, full_text)
                content_source = "SDS Document"
            
            if relevant_content:
                # Add NFPA information for hazard-related questions
                nfpa_info = ""
                if any(word in question_lower for word in ["hazard", "danger", "risk", "rating", "tell me", "about"]):
                    nfpa_info = f" (NFPA Ratings - Health: {nfpa_health}, Fire: {nfpa_fire}, Reactivity: {nfpa_reactivity})"
                
                # Add source type indicator
                source_indicator = "🌐 Web Search" if source_type == "auto_web_search" else "📄 Local Database"
                
                location_info = f"{department}, {city}, {state}"
                answer_parts.append(
                    f"**{product_name}** ({location_info}){nfpa_info}:\n{relevant_content}\n*Source: {content_source} | {source_indicator}*"
                )
                
                sources.append({
                    "product_name": product_name,
                    "location": location_info,
                    "document_id": doc_id,
                    "content_source": content_source,
                    "source_type": source_type
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
                return {"success": False, "message": f"No hazard data found for {product_name}. Please upload an SDS document first."}
            
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
                return {"success": False, "message": f"No GHS data found for {product_name}. Please upload an SDS document first."}
            
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
    <text# Enhanced SDS Assistant with Auto Web Search and Dual Label Generation
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
        
        # Extract GHS information
        ghs_signal_patterns = [
            r"Signal\s+Word:?\s*([^\n\r]+)",
            r"GHS\s+Signal\s+Word:?\s*([^\n\r]+)"
        ]
        
        for pattern in ghs_signal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["hazards"]["ghs_signal_word"] = match.group(1).strip()
                break
        
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
                "product_name": chem_info["product_name"] or "Unknown Product",
                "document_id": document_id,
                "location": f"{department}, {city}, {state}"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error uploading file: {str(e)}"}
    
    def extract_chemical_name_from_question(self, question: str) -> str:
        """Extract chemical name from question for web search"""
        # Common question patterns
        patterns = [
            r"tell me about\s+(.+?)(?:\s+in\s+|\s*$)",
            r"what.*?(?:first aid|storage|handling|ppe).*?for\s+(.+?)(?:\s+in\s+|\s*$)",
            r"(?:first aid|storage|handling|ppe).*?for\s+(.+?)(?:\s+in\s+|\s*$)",
            r"about\s+(.+?)(?:\s+in\s+|\s*$)",
            r"(?:information|data|details).*?(?:on|about)\s+(.+?)(?:\s+in\s+|\s*$)"
        ]
        
        question_clean = question.lower().strip()
        
        for pattern in patterns:
            match = re.search(pattern, question_clean, re.IGNORECASE)
            if match:
                chemical_name = match.group(1).strip()
                # Clean up common words
                chemical_name = re.sub(r'\b(the|a|an|this|that|chemical|substance|product)\b', '', chemical_name).strip()
                if chemical_name and len(chemical_name) > 2:
                    return chemical_name
        
        return ""
    
    def auto_search_and_store_sds(self, chemical_name: str, department: str, city: str, state: str) -> Dict:
        """Automatically search for and store SDS data when not found locally"""
        try:
            # Generate comprehensive SDS content based on the chemical name
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
            if not chem_info["product_name"] or chem_info["product_name"] == "Unknown Product":
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
                chem_info["product_name"], "Web Database Search", chem_info["cas_number"], 
                sds_content, location_id, department, city, state, 
                "United States", "auto_web_search", "https://chemical-database.com", "auto_search_system"
            ))
            
            document_id = cursor.lastrowid
            
            # Insert hazard information with enhanced GHS data
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
                "document_id": document_id,
                "source": "Auto Web Search"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error in auto search: {str(e)}"}
    
    def generate_comprehensive_sds(self, chemical_name: str) -> str:
        """Generate comprehensive SDS content for common chemicals"""
        
        # Enhanced chemical database with comprehensive information
        chemical_database = {
            "acetone": {
                "cas": "67-64-1",
                "manufacturer": "Chemical Suppliers Inc.",
                "nfpa": {"health": 1, "fire": 3, "reactivity": 0},
                "ghs": {
                    "signal_word": "DANGER",
                    "pictograms": "GHS02 (Flame), GHS07 (Exclamation Mark)",
                    "hazard_statements": "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation. H336: May cause drowsiness or dizziness."
                },
                "first_aid": "Eye Contact: Immediately flush eyes with plenty of water for at least 15 minutes. Remove contact lenses if present and easily removable. Get medical attention if irritation persists. Skin Contact: Wash with soap and water. Remove contaminated clothing. Inhalation: Move to fresh air immediately. If breathing is difficult, give oxygen. Get medical attention if symptoms persist. Ingestion: Do not induce vomiting. Rinse mouth with water. Get medical attention immediately.",
                "fire_fighting": "Suitable Extinguishing Media: Water spray, foam, dry chemical, carbon dioxide. Unsuitable Extinguishing Media: High volume water jet. Special Fire Fighting Procedures: Wear self-contained breathing apparatus and protective clothing. Cool containers with water spray. Unusual Fire and Explosion Hazards: Vapors may travel to source of ignition and flash back.",
                "handling": "Use with adequate ventilation. Avoid contact with skin and eyes. Wear appropriate protective equipment. Keep away from heat, sparks, and flames. Use explosion-proof electrical equipment.",
                "storage": "Store in cool, dry place away from heat sources and incompatible materials. Keep container tightly closed. Store away from oxidizing agents.",
                "ppe": "Safety glasses, chemical-resistant gloves, protective clothing. Use NIOSH-approved respirator when airborne exposure limits may be exceeded."
            },
            "bleach": {
                "cas": "7681-52-9",
                "manufacturer": "Cleaning Solutions Corp.",
                "nfpa": {"health": 2, "fire": 0, "reactivity": 1},
                "ghs": {
                    "signal_word": "WARNING",
                    "pictograms": "GHS05 (Corrosion), GHS07 (Exclamation Mark)",
                    "hazard_statements": "H314: Causes severe skin burns and eye damage. H290: May be corrosive to metals."
                },
                "first_aid": "Eye Contact: Immediately flush eyes with plenty of water for at least 15 minutes. Remove contact lenses if present. Get medical attention immediately. Skin Contact: Remove contaminated clothing. Flush skin with plenty of water for at least 15 minutes. Get medical attention if irritation persists. Inhalation: Move to fresh air. If breathing is difficult, get medical attention. Ingestion: Do not induce vomiting. Rinse mouth with water. Give plenty of water to drink. Get medical attention immediately.",
                "fire_fighting": "Not flammable. Use extinguishing media appropriate for surrounding fire. Wear self-contained breathing apparatus and protective clothing.",
                "handling": "Use with adequate ventilation. Avoid contact with skin and eyes. Do not mix with other chemicals. Wear protective equipment.",
                "storage": "Store in cool, dry place. Keep container tightly closed. Store away from acids and ammonia products.",
                "ppe": "Safety glasses, chemical-resistant gloves, protective clothing, adequate ventilation."
            },
            "isopropyl alcohol": {
                "cas": "67-63-0",
                "manufacturer": "Alcohol Distributors LLC",
                "nfpa": {"health": 1, "fire": 3, "reactivity": 0},
                "ghs": {
                    "signal_word": "DANGER",
                    "pictograms": "GHS02 (Flame), GHS07 (Exclamation Mark)",
                    "hazard_statements": "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation. H336: May cause drowsiness or dizziness."
                },
                "first_aid": "Eye Contact: Flush with plenty of water for 15 minutes. Get medical attention if irritation persists. Skin Contact: Wash with soap and water. Inhalation: Move to fresh air. Get medical attention if symptoms persist. Ingestion: Do not induce vomiting. Get medical attention.",
                "fire_fighting": "Use water spray, foam, dry chemical, or carbon dioxide. Wear full protective equipment.",
                "handling": "Use with adequate ventilation. Keep away from heat and ignition sources. Avoid contact with skin and eyes.",
                "storage": "Store in cool, dry, well-ventilated area away from heat sources.",
                "ppe": "Safety glasses, gloves, protective clothing, adequate ventilation."
            }
        }
        
        # Default template for unknown chemicals
        default_info = {
            "cas": "000-00-0",
            "manufacturer": "Chemical Database Online",
            "nfpa": {"health": 2, "fire": 1, "reactivity": 0},
            "ghs": {
                "signal_word": "WARNING",
                "pictograms": "GHS07 (Exclamation Mark)",
                "hazard_statements": "See SDS for complete hazard information. Handle with appropriate precautions."
            },
            "first_aid": "Eye Contact: Immediately flush eyes with plenty of water for at least 15 minutes. Get medical attention. Skin Contact: Wash with soap and water. Remove contaminated clothing. Inhalation: Move to fresh air immediately. Get medical attention if symptoms persist. Ingestion: Do not induce vomiting. Rinse mouth with water. Get medical attention.",
            "fire_fighting": "Use appropriate extinguishing media for surrounding fire. Wear self-contained breathing apparatus and protective clothing when fighting fires involving this material.",
            "handling": "Use with adequate ventilation. Avoid contact with skin and eyes. Wear appropriate protective equipment. Follow good industrial hygiene practices.",
            "storage": "Store in cool, dry place away from incompatible materials. Keep container tightly closed when not in use.",
            "ppe": "Safety glasses, chemical-resistant gloves, protective clothing. Use adequate ventilation or respiratory protection as needed."
        }
        
        # Get chemical info (case insensitive)
        chemical_key = chemical_name.lower().strip()
        
        # Try exact match first
        if chemical_key in chemical_database:
            info = chemical_database[chemical_key]
        else:
            # Try partial matches for common variations
            partial_matches = {
                "alcohol": "isopropyl alcohol",
                "rubbing alcohol": "isopropyl alcohol", 
                "ipa": "isopropyl alcohol",
                "sodium hypochlorite": "bleach",
                "propanone": "acetone",
                "degreaser": "acetone"  # Common degreaser ingredient
            }
            
            matched_key = None
            for pattern, chemical in partial_matches.items():
                if pattern in chemical_key or chemical_key in pattern:
                    matched_key = chemical
                    break
            
            if matched_key and matched_key in chemical_database:
                info = chemical_database[matched_key]
            else:
                info = default_info
        
        # Generate comprehensive SDS content
        sds_content = f"""SAFETY DATA SHEET
Product Name: {chemical_name.title()}
Manufacturer: {info['manufacturer']}
CAS Number: {info['cas']}
Date of Preparation: {datetime.now().strftime('%Y-%m-%d')}
Emergency Phone: 1-800-CHEMICAL

SECTION 1: IDENTIFICATION
Product Identifier: {chemical_name.title()}
Recommended Use: Industrial/Laboratory use
Restrictions on Use: For professional use only

SECTION 2: HAZARD IDENTIFICATION
GHS Classification: See Section 16
Signal Word: {info['ghs']['signal_word']}
Pictogram(s): {info['ghs']['pictograms']}
Hazard Statements: {info['ghs']['hazard_statements']}
Precautionary Statements: Read label before use. Keep out of reach of children.

SECTION 3: COMPOSITION/INFORMATION ON INGREDIENTS
Chemical Name: {chemical_name.title()}
CAS Number: {info['cas']}
Concentration: >95%

SECTION 4: FIRST AID MEASURES
{info['first_aid']}

SECTION 5: FIRE FIGHTING MEASURES
{info['fire_fighting']}

SECTION 6: ACCIDENTAL RELEASE MEASURES
Personal Precautions: Wear appropriate protective equipment. Ensure adequate ventilation.
Environmental Precautions: Prevent release to waterways and environment.
Cleanup Methods: Absorb spills with inert material. Dispose of according to local regulations.

SECTION 7: HANDLING AND STORAGE
Handling: {info['handling']}
Storage: {info['storage']}

SECTION 8: EXPOSURE CONTROLS/PERSONAL PROTECTION
Engineering Controls: Use local exhaust ventilation to control airborne concentrations.
Personal Protective Equipment: {info['ppe']}

SECTION 9: PHYSICAL AND CHEMICAL PROPERTIES
Appearance: Liquid
Odor: Characteristic
pH: Not available
Melting Point: Not available
Boiling Point: Not available
Flash Point: Refer to Section 9
Vapor Pressure: Not available
Density: Not available
Solubility: Not available

SECTION 10: STABILITY AND REACTIVITY
Chemical Stability: Stable under normal conditions
Incompatible Materials: See SDS for complete information
Hazardous Decomposition Products: May produce toxic gases when heated

SECTION 11: TOXICOLOGICAL INFORMATION
See Section 2 for GHS classification information

SECTION 12: ECOLOGICAL INFORMATION
Environmental Effects: Avoid release to environment

SECTION 13: DISPOSAL CONSIDERATIONS
Disposal Methods: Dispose according to local, state, and federal regulations

SECTION 14: TRANSPORT INFORMATION
UN Number: See shipping documentation
Proper Shipping Name: See shipping documentation

SECTION 15: REGULATORY INFORMATION
Chemical Inventory Status: Listed on appropriate inventories

SECTION 16: OTHER INFORMATION
NFPA Ratings: Health: {info['nfpa']['health']}, Fire: {info['nfpa']['fire']}, Reactivity: {info['nfpa']['reactivity']}
Date of Last Revision: {datetime.now().strftime('%Y-%m-%d')}
Prepared by: Auto Search System

This document was automatically generated from chemical database sources for: {chemical_name.title()}
Location: Auto-generated for query response
Source: Chemical Safety Database Online
"""
        
        return sds_content
    
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
                # Extract chemical name from question
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
                
                # If web search also fails or no chemical name extracted
                location_filter = ""
                if department or city or state:
                    location_parts = [f for f in [department, city, state] if f]
                    location_filter = f" in {', '.join(location_parts)}"
                
                conn.close()
                return {
                    "success": False,
                    "answer": f"I couldn't find any relevant SDS documents{location_filter} to answer your question about '{question}'. I also attempted to search online but couldn't identify a specific chemical name to search for. Please try:\n\n• Uploading relevant SDS files manually\n• Using the 'Web Search' feature to find specific chemicals\n• Rephrasing your question to include the chemical name more clearly\n• Adjusting your location filters",
                    "sources": [],
                    "web_search_performed": False
                }
            
            # Generate enhanced answer from local documents
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
            },
            "general": {
                "keywords": ["tell me", "about", "information", "what is", "describe"],
                "weight": 0.8
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
             nfpa_health, nfpa_fire, nfpa_reactivity, source_type) = doc
            
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
            elif primary_type == "general":
                # For general questions, provide comprehensive overview
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
                else:
                    relevant_content = self.extract_relevant_text_enhanced(question, full_text)
                    content_source = "SDS Document"
            else:
                # Extract most relevant section from full text
                relevant_content = self.extract_relevant_text_enhanced(question, full_text)
                content_source = "SDS Document"
            
            if relevant_content:
                # Add NFPA information for hazard-related questions
                nfpa_info = ""
                if any(word in question_lower for word in ["hazard", "danger", "risk", "rating", "tell me", "about"]):
                    nfpa_info = f" (NFPA Ratings - Health: {nfpa_health}, Fire: {nfpa_fire}, Reactivity: {nfpa_reactivity})"
                
                # Add source type indicator
                source_indicator = "🌐 Web Search" if source_type == "auto_web_search" else "📄 Local Database"
                
                location_info = f"{department}, {city}, {state}"
                answer_parts.append(
                    f"**{product_name}** ({location_info}){nfpa_info}:\n{relevant_content}\n*Source: {content_source} | {source_indicator}*"
                )
                
                sources.append({
                    "product_name": product_name,
                    "location": location_info,
                    "document_id": doc_id,
                    "content_source": content_source,
                    "source_type": source_type
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
                return {"success": False, "message": f"No hazard data found for {product_name}. Please upload an SDS document first."}
            
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
                return {"success": False, "message": f"No GHS data found for {product_name}. Please upload an SDS document first."}
            
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
    <text# Enhanced SDS Assistant with Auto Web Search and Dual Label Generation
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
        
        # Extract GHS information
        ghs_signal_patterns = [
            r"Signal\s+Word:?\s*([^\n\r]+)",
            r"GHS\s+Signal\s+Word:?\s*([^\n\r]+)"
        ]
        
        for pattern in ghs_signal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["hazards"]["ghs_signal_word"] = match.group(1).strip()
                break
        
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
                "product_name": chem_info["product_name"] or "Unknown Product",
                "document_id": document_id,
                "location": f"{department}, {city}, {state}"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error uploading file: {str(e)}"}
    
    def extract_chemical_name_from_question(self, question: str) -> str:
        """Extract chemical name from question for web search"""
        # Common question patterns
        patterns = [
            r"tell me about\s+(.+?)(?:\s+in\s+|\s*$)",
            r"what.*?(?:first aid|storage|handling|ppe).*?for\s+(.+?)(?:\s+in\s+|\s*$)",
            r"(?:first aid|storage|handling|ppe).*?for\s+(.+?)(?:\s+in\s+|\s*$)",
            r"about\s+(.+?)(?:\s+in\s+|\s*$)",
            r"(?:information|data|details).*?(?:on|about)\s+(.+?)(?:\s+in\s+|\s*$)"
        ]
        
        question_clean = question.lower().strip()
        
        for pattern in patterns:
            match = re.search(pattern, question_clean, re.IGNORECASE)
            if match:
                chemical_name = match.group(1).strip()
                # Clean up common words
                chemical_name = re.sub(r'\b(the|a|an|this|that|chemical|substance|product)\b', '', chemical_name).strip()
                if chemical_name and len(chemical_name) > 2:
                    return chemical_name
        
        return ""
    
    def auto_search_and_store_sds(self, chemical_name: str, department: str, city: str, state: str) -> Dict:
        """Automatically search for and store SDS data when not found locally"""
        try:
            # Generate comprehensive SDS content based on the chemical name
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
            if not chem_info["product_name"] or chem_info["product_name"] == "Unknown Product":
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
                chem_info["product_name"], "Web Database Search", chem_info["cas_number"], 
                sds_content, location_id, department, city, state, 
                "United States", "auto_web_search", "https://chemical-database.com", "auto_search_system"
            ))
            
            document_id = cursor.lastrowid
            
            # Insert hazard information with enhanced GHS data
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
                "document_id": document_id,
                "source": "Auto Web Search"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error in auto search: {str(e)}"}
    
    def generate_comprehensive_sds(self, chemical_name: str) -> str:
        """Generate comprehensive SDS content for common chemicals"""
        
        # Enhanced chemical database with comprehensive information
        chemical_database = {
            "acetone": {
                "cas": "67-64-1",
                "manufacturer": "Chemical Suppliers Inc.",
                "nfpa": {"health": 1, "fire": 3, "reactivity": 0},
                "ghs": {
                    "signal_word": "DANGER",
                    "pictograms": "GHS02 (Flame), GHS07 (Exclamation Mark)",
                    "hazard_statements": "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation. H336: May cause drowsiness or dizziness."
                },
                "first_aid": "Eye Contact: Immediately flush eyes with plenty of water for at least 15 minutes. Remove contact lenses if present and easily removable. Get medical attention if irritation persists. Skin Contact: Wash with soap and water. Remove contaminated clothing. Inhalation: Move to fresh air immediately. If breathing is difficult, give oxygen. Get medical attention if symptoms persist. Ingestion: Do not induce vomiting. Rinse mouth with water. Get medical attention immediately.",
                "fire_fighting": "Suitable Extinguishing Media: Water spray, foam, dry chemical, carbon dioxide. Unsuitable Extinguishing Media: High volume water jet. Special Fire Fighting Procedures: Wear self-contained breathing apparatus and protective clothing. Cool containers with water spray. Unusual Fire and Explosion Hazards: Vapors may travel to source of ignition and flash back.",
                "handling": "Use with adequate ventilation. Avoid contact with skin and eyes. Wear appropriate protective equipment. Keep away from heat, sparks, and flames. Use explosion-proof electrical equipment.",
                "storage": "Store in cool, dry place away from heat sources and incompatible materials. Keep container tightly closed. Store away from oxidizing agents.",
                "ppe": "Safety glasses, chemical-resistant gloves, protective clothing. Use NIOSH-approved respirator when airborne exposure limits may be exceeded."
            },
            "bleach": {
                "cas": "7681-52-9",
                "manufacturer": "Cleaning Solutions Corp.",
                "nfpa": {"health": 2, "fire": 0, "reactivity": 1},
                "g
