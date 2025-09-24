import asyncio
from crawl4ai import *
import json
import google.generativeai as genai
from json_repair import repair_json
from typing import List, Dict, Any, Optional
import re
import sys
import time
from datetime import datetime
import pandas as pd
import os
import urllib.parse

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb_manager import get_mongodb_manager
GOOGLE_API_KEY='AIzaSyD-Gsdh5u9JamamQdzH-pIi-5q78GOxWV4'
genai.configure(api_key=GOOGLE_API_KEY)

def format_json_llm(text):
    regex_pattern = r'```json(.*?)```'
    match = re.findall(regex_pattern,text, flags=re.S)

    if match:
        repaired_json = repair_json(match[0])
        res = json.loads(repaired_json)
        return res
    else:
        try:
            return json.loads(text)
        except Exception as e:
            return None

def convert_to_unified_format(lead_data):
    """Convert the extracted lead data to the unified format"""
    
    def extract_emails(data):
        """Extract emails from contact_info"""
        contact_info = data.get('contact_info', {})
        emails = []
        if contact_info.get('email') and contact_info.get('email') != 'NA':
            emails.append(contact_info.get('email'))
        return emails
    
    def extract_phones(data):
        """Extract phone numbers from contact_info"""
        contact_info = data.get('contact_info', {})
        phones = []
        if contact_info.get('phone') and contact_info.get('phone') != 'NA':
            phones.append(contact_info.get('phone'))
        return phones
    
    def extract_social_media(data):
        """Extract social media handles"""
        contact_info = data.get('contact_info', {})
        social_media = {}
        
        social_media['linkedin'] = contact_info.get('linkedin') if contact_info.get('linkedin') != 'NA' else None
        social_media['twitter'] = contact_info.get('twitter') if contact_info.get('twitter') != 'NA' else None
        social_media['facebook'] = contact_info.get('facebook') if contact_info.get('facebook') != 'NA' else None
        social_media['instagram'] = None
        social_media['youtube'] = None
        social_media['tiktok'] = None
        
        # Handle other social media links
        other_links = []
        socialmedialinks = contact_info.get('socialmedialinks', [])
        if isinstance(socialmedialinks, list):
            other_links.extend([link for link in socialmedialinks if link])
        
        return social_media, other_links
    
    def get_websites(data):
        """Extract website URLs"""
        websites = []
        contact_info = data.get('contact_info', {})
        
        if data.get('source_url'):
            websites.append(data.get('source_url'))
        
        if contact_info.get('website') and contact_info.get('website') != 'NA':
            websites.append(contact_info.get('website'))
            
        return websites
    
    # Extract social media data
    social_media, other_social_links = extract_social_media(lead_data)
    
    # Determine lead category based on type
    lead_category = "potential_customer" if lead_data.get('type', '').lower() == 'lead' else "competitor"
    lead_sub_category = lead_data.get('link_details', '')
    
    unified_data = {
        "url": lead_data.get('source_url', ''),
        "platform": "web",
        "content_type": "",
        "source": "web-scraper",
        "profile": {
            "username": "",
            "full_name": lead_data.get('name', '') or lead_data.get('company_name', ''),
            "bio": lead_data.get('bio', ''),
            "location": lead_data.get('location', ''),
            "job_title": "",
            "employee_count": ""
        },
        "contact": {
            "emails": extract_emails(lead_data),
            "phone_numbers": extract_phones(lead_data),
            "address": lead_data.get('address', ''),
            "websites": get_websites(lead_data),
            "social_media_handles": {
                "instagram": social_media.get('instagram'),
                "twitter": social_media.get('twitter'),
                "facebook": social_media.get('facebook'),
                "linkedin": social_media.get('linkedin'),
                "youtube": social_media.get('youtube'),
                "tiktok": social_media.get('tiktok'),
                "other": other_social_links
            },
            "bio_links": []
        },
        "content": {
            "caption": "",
            "upload_date": "",
            "channel_name": "",
            "author_name": ""
        },
        "metadata": {
            "scraped_at": datetime.utcnow().isoformat(),
            "data_quality_score": "0.45"
        },
        "industry": lead_data.get('industry', ''),
        "revenue": "",
        "lead_category": lead_category,
        "lead_sub_category": lead_sub_category,
        "company_name": lead_data.get('company_name', ''),
        "company_type": lead_data.get('company_type', ''),
        "decision_makers": lead_data.get('name', ''),
        "bdr": "AKG",
        "product_interests": None,
        "timeline": None,
        "interest_level": None
    }
    
    return unified_data

def check_lead_duplication(lead_data: Dict[str, Any], existing_leads: List[Dict[str, Any]]) -> bool:
    """
    Check if a lead is a duplicate based on the specified criteria:
    1. Email is different (if present)
    2. Phone is different (if present) 
    3. If both email and phone are empty, check full_name + url + company_name + company_type
    """
    lead_emails = lead_data.get('contact', {}).get('emails', [])
    lead_phones = lead_data.get('contact', {}).get('phone_numbers', [])
    lead_full_name = lead_data.get('profile', {}).get('full_name', '')
    lead_url = lead_data.get('url', '')
    lead_company_name = lead_data.get('company_name', '')
    lead_company_type = lead_data.get('company_type', '')
    
    # Normalize email and phone lists
    lead_emails = [email.lower().strip() for email in lead_emails if email and email.strip()]
    lead_phones = [phone.strip() for phone in lead_phones if phone and phone.strip()]
    
    for existing_lead in existing_leads:
        existing_emails = existing_lead.get('contact', {}).get('emails', [])
        existing_phones = existing_lead.get('contact', {}).get('phone_numbers', [])
        existing_full_name = existing_lead.get('profile', {}).get('full_name', '')
        existing_url = existing_lead.get('url', '')
        existing_company_name = existing_lead.get('company_name', '')
        existing_company_type = existing_lead.get('company_type', '')
        
        # Normalize existing email and phone lists
        existing_emails = [email.lower().strip() for email in existing_emails if email and email.strip()]
        existing_phones = [phone.strip() for phone in existing_phones if phone and phone.strip()]
        
        # Check email duplication
        if lead_emails and existing_emails:
            if any(email in existing_emails for email in lead_emails):
                return True
        
        # Check phone duplication
        if lead_phones and existing_phones:
            if any(phone in existing_phones for phone in lead_phones):
                return True
        
        # If both email and phone are empty, check other fields
        if not lead_emails and not lead_phones and not existing_emails and not existing_phones:
            if (lead_full_name.lower().strip() == existing_full_name.lower().strip() and
                lead_url.strip() == existing_url.strip() and
                lead_company_name.lower().strip() == existing_company_name.lower().strip() and
                lead_company_type.lower().strip() == existing_company_type.lower().strip()):
                return True
    
    return False

def store_unified_leads(leads: List[Dict[str, Any]], mongodb_manager, icp_identifier: str = 'default') -> Dict[str, Any]:
    """
    Store leads in unified_leads collection with duplication checking
    """
    if not leads:
        return {"stored": 0, "duplicates": 0, "errors": 0}
    
    try:
        # Get existing leads from unified_leads collection
        existing_leads = list(mongodb_manager.get_collection('unified').find({}))
        
        stored_count = 0
        duplicate_count = 0
        error_count = 0
        
        for lead in leads:
            try:
                # Check for duplication
                if check_lead_duplication(lead, existing_leads):
                    duplicate_count += 1
                    continue
                
                # Add metadata
                lead['created_at'] = datetime.utcnow()
                lead['source'] = 'web_crawler'
                lead['icp_identifier'] = icp_identifier
                
                # Store in unified_leads collection
                result = mongodb_manager.get_collection('unified').insert_one(lead)
                if result.inserted_id:
                    stored_count += 1
                    # Add to existing_leads list to check against future leads
                    existing_leads.append(lead)
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"Error storing lead: {e}")
                error_count += 1
        
        print(f"Unified leads storage complete: {stored_count} stored, {duplicate_count} duplicates, {error_count} errors")
        
        return {
            "stored": stored_count,
            "duplicates": duplicate_count,
            "errors": error_count,
            "total_processed": len(leads)
        }
        
    except Exception as e:
        print(f"Error in store_unified_leads: {e}")
        return {"stored": 0, "duplicates": 0, "errors": len(leads)}

async def main_google_search(google_search_url):
    """Modified main function to handle Google search results"""
    async with AsyncWebCrawler() as crawler:
        all_links = []
        
        # Get Google search results
        try:
            result = await crawler.arun(url=google_search_url)
            # Extract links from Google search results
            all_links.extend(result.links['external'])
            # Limit to top 10 results to avoid overwhelming
            all_links = all_links[:10]
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error crawling Google search: {e}")
            return []
            
        print(f"Found {len(all_links)} links from Google search")
        final_output = []
        
        lead_json_format = {
            "name": "",
            "contact_info": {
                "email": "",
                "phone": "",
                "linkedin": "",
                "twitter": "",
                "website": "",
                "others": "",
                "socialmedialinks": []
            },
            "company_name": "",
            "time": "",
            "link_details": "provide a short description of the link",
            "type": "provide whether its a lead/competitor",
            "what_we_can_offer": "",
            "source_url": "",
            "source_platform": "",
            "location": "",
            "industry": "",
            "company_type": "",
            "bio": "",
            "address": ""
        }
        
        for link in all_links:
            if not link['href'].startswith(('http://', 'https://')):
                print(f"Skipping invalid URL: {link['href']}")
                continue
                
            # Skip Google-related URLs
            if any(domain in link['href'].lower() for domain in ['google.com', 'youtube.com', 'maps.google']):
                continue
                
            try:
                profile = await crawler.arun(url=link['href'])
                result = profile.markdown
                truncated_result = result[:4000] if result else ""
                
                model = "gemini-2.5-flash"
                content = f'''From this profile/website extract important information for lead generation purposes. Focus on finding potential customers, not competitors. Include phone numbers and email addresses if found. Identify the source URL and the platform from which the information was extracted. 

Profile/Website Content: {truncated_result}

Extract the information in the following json format and if any information is not present, leave the field empty. Also extract location, industry, company_type, bio, and address if available.

{json.dumps(lead_json_format)}

IMPORTANT: Only extract information if this appears to be a potential customer/lead. Return an empty dictionary if:
- This is a competitor or service provider in the same industry
- No contact information is available
- The content is not relevant to lead generation
'''
                
                response = genai.GenerativeModel(model).generate_content(contents=content)
                res = format_json_llm(response.text)
                
                if res and res != {}:
                    res['source_url'] = link['href']
                    # Determine platform
                    if 'linkedin.com' in link['href']:
                        res['source_platform'] = 'LinkedIn'
                    elif 'facebook.com' in link['href']:
                        res['source_platform'] = 'Facebook'
                    elif 'twitter.com' in link['href']:
                        res['source_platform'] = 'Twitter'
                    else:
                        res['source_platform'] = 'Website'
                    final_output.append(res)
                    print(f"Extracted lead from: {link['href']}")
                    
            except Exception as e:
                print(f"Error processing link {link['href']}: {e}")
            
            await asyncio.sleep(2)  # Rate limiting
            
        print(f"Total leads extracted: {len(final_output)}")
        return final_output

def generic_web_crawl(icp_data):
    """Modified function using Google search approach"""
    start_time = time.time()
    
    # Extract ICP information
    product_name = icp_data["product_details"]["product_name"]
    product_category = icp_data["product_details"]["product_category"]
    usps = ", ".join(icp_data["product_details"]["usps"])
    pain_points_solved = ", ".join(icp_data["product_details"]["pain_points_solved"])
    
    target_industry = ", ".join(icp_data["icp_information"]["target_industry"])
    decision_maker_persona = ", ".join(icp_data["icp_information"]["decision_maker_persona"])
    region = ", ".join(icp_data["icp_information"]["region"])
    
    # Handle specific occasions (generic field)
    specific_occasions = icp_data["icp_information"].get("specific_occasions", 
                                                        icp_data["icp_information"].get("travel_occasions", []))
    if isinstance(specific_occasions, list):
        specific_occasions = ", ".join(specific_occasions)
    
    # Generate intent-based Google search queries
    prompt = f'''I run a {product_name} business in {product_category} and I want to find potential customers on the internet who might need my services — not competitors. 

TARGET PROFILE:
- Industries: {target_industry}
- Decision Makers: {decision_maker_persona}
- Geographic Focus: {region}
- Pain Points I Solve: {pain_points_solved}
- Key Benefits: {usps}
- Specific Use Cases: {specific_occasions}

Generate 3 Google search queries in **URL format** (https://www.google.com/search?q=...) that help me find potential customers expressing intent or need for my services.

REQUIREMENTS:
- Use double quotes for exact phrases potential customers might use
- Include location-based terms when relevant for {region}
- Focus on intent keywords (looking for, need, want, seeking, require, hiring)
- Use OR statements to combine related phrases
- Avoid competitor-focused searches
- Make queries realistic and copy-paste ready

Example formats:
https://www.google.com/search?q=%22looking+to+buy+a+flat%22+OR+%22need+apartment%22+OR+%22property+wanted%22

Provide the output in a json object with key "queries" and value as list of URLs.
'''

    model = "gemini-2.5-flash"
    response = genai.GenerativeModel(model).generate_content(contents=prompt)
    res = format_json_llm(response.text)
    
    search_queries = []
    if res and "queries" in res:
        search_queries = res["queries"]
        print(f"Generated {len(search_queries)} search queries")
    else:
        print("Error: Could not extract search queries. Using fallback.")
        # Fallback queries based on product type
        fallback_terms = product_name.replace(' ', '+').lower()
        search_queries = [
            f"https://www.google.com/search?q=%22looking+for%22+OR+%22need%22+{fallback_terms}",
            f"https://www.google.com/search?q=%22seeking%22+OR+%22require%22+{fallback_terms}"
        ]
    
    print(f"Search queries to execute: {search_queries}")
    
    final_output = []
    for query_url in search_queries:
        print(f"Executing search query: {query_url}")
        try:
            output = asyncio.run(main_google_search(query_url))
            final_output.extend(output)
            time.sleep(3)  # Rate limiting between searches
        except Exception as e:
            print(f"Error executing search {query_url}: {e}")
    
    # Convert to unified format and filter valid leads
    unified_output = []
    for lead in final_output:
        contact_info = lead.get("contact_info", {})
        # Enhanced validation for lead quality
        if (contact_info.get("email") and contact_info.get("email") not in ["NA", "", "N/A"]) or \
           (contact_info.get("phone") and contact_info.get("phone") not in ["NA", "", "N/A"]) or \
           (contact_info.get("linkedin") and contact_info.get("linkedin") not in ["NA", "", "N/A"]) or \
           (contact_info.get("website") and contact_info.get("website") not in ["NA", "", "N/A"]):
            
            # Additional quality check - ensure lead has meaningful content
            if (lead.get("name") and lead.get("name") not in ["", "NA"]) or \
               (lead.get("company_name") and lead.get("company_name") not in ["", "NA"]):
                unified_lead = convert_to_unified_format(lead)
                unified_output.append(unified_lead)
    
    # Store leads with duplication checking
    try:
        mongodb_manager = get_mongodb_manager()
        storage_results = store_unified_leads(unified_output, mongodb_manager, icp_identifier)
        print(f"Unified leads storage: {storage_results['stored']} stored, {storage_results['duplicates']} duplicates, {storage_results['errors']} errors")
    except Exception as e:
        print(f"Error storing unified leads: {e}")
        # Fallback: save to file
        # with open('leads_unified_google_search.json', 'w') as f:
        #     json.dump(unified_output, f, indent=2)
        # print("Unified leads saved to leads_unified_google_search.json (fallback)")
    
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
    print(f"Total high-quality leads found: {len(unified_output)}")
    
    return unified_output

async def run_web_crawler_async(icp_data: Dict[str, Any], icp_identifier: str = 'default') -> Dict[str, Any]:
    """Async wrapper with Google search approach"""
    try:
        start_time = time.time()
        
        # Extract ICP information  
        product_name = icp_data["product_details"]["product_name"]
        product_category = icp_data["product_details"]["product_category"]
        usps = ", ".join(icp_data["product_details"]["usps"])
        pain_points_solved = ", ".join(icp_data["product_details"]["pain_points_solved"])
        
        target_industry = ", ".join(icp_data["icp_information"]["target_industry"])
        decision_maker_persona = ", ".join(icp_data["icp_information"]["decision_maker_persona"])
        region = ", ".join(icp_data["icp_information"]["region"])
        
        # Handle specific occasions (generic field)
        specific_occasions = icp_data["icp_information"].get("specific_occasions", 
                                                            icp_data["icp_information"].get("travel_occasions", []))
        if isinstance(specific_occasions, list):
            specific_occasions = ", ".join(specific_occasions)
        
        # Generate Google search queries
        prompt = f'''I run a {product_name} business and want to find potential customers who might need my services.

TARGET: {target_industry} companies
PAIN POINTS: {pain_points_solved}
USE CASES: {specific_occasions}

Generate 2 Google search queries in **URL format** (https://www.google.com/search?q=...) 
that help me find potential customers, prospects, or decision-makers. 

Requirements:
- Use double quotes for exact phrases potential customers might use
- Focus on intent keywords (looking for, need, want, seeking, require, hiring)
- Use OR statements to combine related phrases
- Avoid competitor-focused searches
- Make queries realistic and copy-paste ready
- keep it short and concise

Example query:
https://www.google.com/search?q=%22looking+to+buy+a+flat%22+OR+%22need+apartment%22+OR+%22property+wanted%22

Return as: {{"queries": ["url1", "url2"]}}
'''
        
        model = "gemini-2.5-flash"
        response = genai.GenerativeModel(model).generate_content(contents=prompt)
        res = format_json_llm(response.text)
        
        search_queries = []
        if res and "queries" in res:
            search_queries = res["queries"][:2]  # Limit for async
        else:
            fallback_terms = product_name.replace(' ', '+').lower()
            search_queries = [
                f"https://www.google.com/search?q=%22looking+for%22+{fallback_terms}"
            ]
        # search_queries = [
        #     "https://www.google.com/search?q=real+estate+agents+in+New+York",
        #     "https://www.google.com/search?q=buy+commercial+property+New+York"
        # ]
        final_output = []
        for query_url in search_queries:
            print(f"Executing async search: {query_url}")
            output = await main_google_search(query_url)
            final_output.extend(output)
        
        # Convert to unified format
        unified_output = []
        for lead in final_output:
            contact_info = lead.get("contact_info", {})
            if (contact_info.get("email") and contact_info.get("email") not in ["NA", "", "N/A"]) or \
               (contact_info.get("phone") and contact_info.get("phone") not in ["NA", "", "N/A"]) or \
               (contact_info.get("linkedin") and contact_info.get("linkedin") not in ["NA", "", "N/A"]):
                unified_lead = convert_to_unified_format(lead)
                unified_output.append(unified_lead)
        
        # Store leads
        storage_results = {"stored": 0, "duplicates": 0, "errors": 0}
        try:
            mongodb_manager = get_mongodb_manager()
            storage_results = store_unified_leads(unified_output, mongodb_manager, icp_identifier)
        except Exception as e:
            print(f"Error storing leads: {e}")
            storage_results = {"stored": 0, "duplicates": 0, "errors": len(unified_output)}
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return {
            "success": True,
            "data": unified_output,
            "summary": {
                "total_leads_found": len(unified_output),
                "leads_stored": storage_results["stored"],
                "duplicates_found": storage_results["duplicates"],
                "errors": storage_results["errors"],
                "queries_executed": len(search_queries),
                "execution_time_seconds": execution_time
            },
            "storage_results": storage_results
        }
        
    except Exception as e:
        print(f"Error in run_web_crawler_async: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "summary": {
                "total_leads_found": 0,
                "leads_stored": 0,
                "duplicates_found": 0,
                "errors": 1,
                "queries_executed": 0,
                "execution_time_seconds": 0
            }
        }

if __name__ == "__main__":
    import asyncio
    # Example for Real Estate
    real_estate_icp = {
        "product_details": {
            "product_name": "Residential and Commercial Real Estate Sales",
            "product_category": "Real Estate Services",
            "usps": [
                "Expert local market knowledge",
                "Comprehensive property listings",
                "Professional negotiation skills",
                "Fast closing process",
                "Personalized customer service"
            ],
            "pain_points_solved": [
                "Difficulty finding suitable properties",
                "Complex buying process",
                "Market pricing confusion",
                "Legal documentation hassles",
                "Time-consuming property search"
            ]
        },
        "icp_information": {
            "target_industry": [
                "First-time home buyers",
                "Real estate investors",
                "Growing families",
                "Business owners",
                "Relocating professionals"
            ],
            "company_size": "Individual to small business",
            "decision_maker_persona": [
                "Home buyers",
                "Property investors", 
                "Business owners",
                "Family heads",
                "Corporate relocation managers"
            ],
            "region": ["Local city", "Suburban areas", "Commercial districts"],
            "budget_range": "$100,000-$2,000,000",
            "specific_occasions": [
                "First home purchase",
                "Property investment",
                "Business expansion",
                "Family growth",
                "Relocation needs"
            ]
        }
    }
    
    print("Testing Real Estate Lead Generation with Google Search Approach...")
    result = asyncio.run(run_web_crawler_async(real_estate_icp))
    print(json.dumps(result, indent=2))