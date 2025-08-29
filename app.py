#!/usr/bin/env python3
"""
Flask API for Lead Generation Backend
Provides essential endpoints for the complete lead generation pipeline.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the orchestrator from main.py
from main import LeadGenerationOrchestrator
from filter_web_lead import MongoDBLeadProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global orchestrator instance
orchestrator = None

def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = LeadGenerationOrchestrator()
    return orchestrator

def run_async(coro):
    """Helper function to run async code in Flask"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Lead Generation Backend"
    })

@app.route('/api/scrapers', methods=['GET'])
def get_available_scrapers():
    """Get list of available scrapers"""
    try:
        orch = get_orchestrator()
        return jsonify({
            "success": True,
            "data": {
                "available_scrapers": list(orch.available_scrapers.keys()),
                "scrapers_info": {
                    "web_scraper": "General web scraping for websites",
                    "instagram": "Instagram profiles and posts",
                    "linkedin": "LinkedIn profiles and companies", 
                    "youtube": "YouTube channels and videos"
                }
            }
        })
    except Exception as e:
        logger.error(f"Error getting scrapers: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/icp/template', methods=['GET'])
def get_icp_template():
    """Get ICP (Ideal Customer Profile) template"""
    try:
        orch = get_orchestrator()
        template = orch.get_hardcoded_icp()
        
        return jsonify({
            "success": True,
            "data": {
                "icp_template": template,
                "description": "Use this template to structure your ICP data"
            }
        })
    except Exception as e:
        logger.error(f"Error getting ICP template: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/lead-generation/run', methods=['POST'])
def run_lead_generation():
    """
    Main endpoint to run the complete lead generation pipeline
    
    Expected payload:
    {
        "icp_data": {
            "product_details": {...},
            "icp_information": {...}
        },
        "selected_scrapers": ["web_scraper", "instagram", "linkedin", "youtube"]
    }
    """
    try:
        # Validate request
        if not request.is_json:
            raise BadRequest("Request must be JSON")
        
        data = request.get_json()
        
        # Extract and validate required fields
        icp_data = data.get('icp_data')
        selected_scrapers = data.get('selected_scrapers', ['web_scraper'])
        
        if not icp_data:
            return jsonify({
                "success": False,
                "error": "icp_data is required"
            }), 400
        
        if not isinstance(selected_scrapers, list) or not selected_scrapers:
            return jsonify({
                "success": False,
                "error": "selected_scrapers must be a non-empty list"
            }), 400
        
        logger.info(f"Starting lead generation pipeline with scrapers: {selected_scrapers}")
        
        # Get orchestrator instance
        orch = get_orchestrator()
        
        # Run the complete pipeline asynchronously
        result = run_async(run_pipeline_async(orch, icp_data, selected_scrapers))
        
        return jsonify({
            "success": True,
            "data": result,
            "message": "Lead generation pipeline completed successfully"
        })
        
    except BadRequest as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in lead generation pipeline: {e}")
        return jsonify({
            "success": False,
            "error": f"Pipeline failed: {str(e)}"
        }), 500

async def run_pipeline_async(orch, icp_data, selected_scrapers):
    """
    Run the complete lead generation pipeline asynchronously
    """
    pipeline_start = datetime.now()
    
    try:
        # Step 1: Generate search queries with Gemini AI
        logger.info("🤖 Step 1: Generating search queries...")
        queries = await orch.generate_search_queries(icp_data, selected_scrapers)
        
        if not queries:
            raise Exception("No search queries were generated")
        
        logger.info(f"✅ Generated {len(queries)} search queries")
        
        # Step 2: Collect URLs using web_url_scraper
        logger.info("🔍 Step 2: Collecting URLs...")
        classified_urls = await orch.collect_urls_from_queries(queries)
        
        total_urls = sum(len(urls) for urls in classified_urls.values())
        if total_urls == 0:
            raise Exception("No URLs were collected from the search queries")
        
        logger.info(f"✅ Collected {total_urls} URLs")
        
        # Step 3: Run selected scrapers
        logger.info("🚀 Step 3: Running scrapers...")
        scraper_results = await orch.run_selected_scrapers(classified_urls, selected_scrapers)
        
        # Step 4: Filter and process leads using MongoDBLeadProcessor
        logger.info("🧹 Step 4: Filtering and processing leads...")
        lead_filtering_results = {}
        try:
            lead_processor = MongoDBLeadProcessor()
            
            # Create indexes for the target collection
            lead_processor.create_indexes()
            
            # Process all leads from web_leads collection to leadgen_leads collection
            filtering_results = lead_processor.process_leads(batch_size=50)
            
            # Get processing statistics
            processing_stats = lead_processor.get_processing_stats()
            
            lead_filtering_results = {
                'filtering_stats': filtering_results,
                'processing_stats': processing_stats
            }
            
            lead_processor.close_connection()
            
        except Exception as e:
            logger.error(f"❌ Error in lead filtering: {e}")
            lead_filtering_results = {'error': str(e)}
        
        # Add filtering results to scraper results
        scraper_results['lead_filtering'] = lead_filtering_results
        
        # Step 5: Generate final report
        logger.info("📊 Step 5: Generating final report...")
        report_file = orch.generate_final_report(icp_data, selected_scrapers, scraper_results)
        
        pipeline_end = datetime.now()
        execution_time = (pipeline_end - pipeline_start).total_seconds()
        
        # Prepare response
        response_data = {
            "pipeline_metadata": {
                "execution_time_seconds": execution_time,
                "start_time": pipeline_start.isoformat(),
                "end_time": pipeline_end.isoformat(),
                "selected_scrapers": selected_scrapers,
                "total_queries_generated": len(queries),
                "total_urls_collected": total_urls
            },
            "url_collection": {
                "classified_urls_count": {k: len(v) for k, v in classified_urls.items()},
                "total_urls": total_urls
            },
            "scraper_results_summary": {},
            "report_file": report_file,
            "queries_used": queries
        }
        
        # Generate summary for each scraper
        successful_scrapers = 0
        for scraper, result in scraper_results.items():
            if scraper == 'lead_filtering':
                # Handle lead filtering results separately
                if result.get('error'):
                    response_data["scraper_results_summary"][scraper] = {
                        "status": "failed", 
                        "error": result['error']
                    }
                else:
                    successful_scrapers += 1
                    filtering_stats = result.get('filtering_stats', {})
                    response_data["scraper_results_summary"][scraper] = {
                        "status": "success",
                        "leads_processed": filtering_stats.get('total', 0),
                        "leads_filtered": filtering_stats.get('filtered', 0),
                        "leads_extracted": filtering_stats.get('extracted', 0),
                        "leads_inserted": filtering_stats.get('inserted', 0),
                        "email_based_leads": filtering_stats.get('email_based', 0),
                        "phone_based_leads": filtering_stats.get('phone_based', 0)
                    }
            elif result.get('error'):
                response_data["scraper_results_summary"][scraper] = {
                    "status": "failed", 
                    "error": result['error']
                }
            else:
                successful_scrapers += 1
                if scraper == 'web_scraper':
                    summary = result.get('summary', {})
                    response_data["scraper_results_summary"][scraper] = {
                        "status": "success",
                        "leads_found": summary.get('successful_leads', 0),
                        "urls_processed": summary.get('urls_processed', 0)
                    }
                elif scraper == 'instagram':
                    response_data["scraper_results_summary"][scraper] = {
                        "status": "success",
                        "profiles_found": len(result.get('data', [])),
                        "success_rate": result.get('summary', {}).get('success_rate', 0)
                    }
                elif scraper == 'linkedin':
                    metadata = result.get('scraping_metadata', {})
                    response_data["scraper_results_summary"][scraper] = {
                        "status": "success",
                        "profiles_found": metadata.get('successful_scrapes', 0),
                        "failed_scrapes": metadata.get('failed_scrapes', 0)
                    }
                elif scraper == 'youtube':
                    response_data["scraper_results_summary"][scraper] = {
                        "status": "success" if result.get('success') else "failed"
                    }
        
        # Count successful scrapers (excluding lead_filtering)
        actual_successful_scrapers = len([r for r in scraper_results.values() 
                                        if not r.get('error') and r != scraper_results.get('lead_filtering')])
        
        response_data["pipeline_metadata"]["successful_scrapers"] = actual_successful_scrapers
        response_data["pipeline_metadata"]["total_scrapers"] = len(selected_scrapers)
        response_data["pipeline_metadata"]["lead_filtering_successful"] = not lead_filtering_results.get('error')
        
        logger.info(f"✅ Pipeline completed successfully in {execution_time:.2f} seconds")
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        raise

@app.route('/api/queries/generate', methods=['POST'])
def generate_queries_only():
    """
    Generate search queries only (without running scrapers)
    
    Expected payload:
    {
        "icp_data": {...},
        "selected_scrapers": [...]
    }
    """
    try:
        if not request.is_json:
            raise BadRequest("Request must be JSON")
        
        data = request.get_json()
        icp_data = data.get('icp_data')
        selected_scrapers = data.get('selected_scrapers', ['web_scraper'])
        
        if not icp_data:
            return jsonify({
                "success": False,
                "error": "icp_data is required"
            }), 400
        
        orch = get_orchestrator()
        
        # Generate queries asynchronously
        queries = run_async(orch.generate_search_queries(icp_data, selected_scrapers))
        
        return jsonify({
            "success": True,
            "data": {
                "queries": queries,
                "total_queries": len(queries),
                "selected_scrapers": selected_scrapers
            }
        })
        
    except BadRequest as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error generating queries: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/lead-filtering/run', methods=['POST'])
def run_lead_filtering():
    """
    Run only the lead filtering process
    
    Expected payload:
    {
        "query_filter": {},  # Optional MongoDB query filter
        "batch_size": 50     # Optional batch size
    }
    """
    try:
        # Validate request
        if not request.is_json:
            raise BadRequest("Request must be JSON")
        
        data = request.get_json() or {}
        query_filter = data.get('query_filter', {})
        batch_size = data.get('batch_size', 50)
        
        logger.info(f"Starting lead filtering process with batch_size: {batch_size}")
        
        # Initialize lead processor
        lead_processor = MongoDBLeadProcessor()
        
        # Create indexes
        lead_processor.create_indexes()
        
        # Process leads
        filtering_results = lead_processor.process_leads(
            query_filter=query_filter, 
            batch_size=batch_size
        )
        
        # Get processing statistics
        processing_stats = lead_processor.get_processing_stats()
        
        # Close connection
        lead_processor.close_connection()
        
        return jsonify({
            "success": True,
            "data": {
                "filtering_results": filtering_results,
                "processing_stats": processing_stats,
                "timestamp": datetime.now().isoformat()
            },
            "message": "Lead filtering completed successfully"
        })
        
    except BadRequest as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in lead filtering: {e}")
        return jsonify({
            "success": False,
            "error": f"Lead filtering failed: {str(e)}"
        }), 500

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Get system status and capabilities"""
    try:
        orch = get_orchestrator()
        
        # Check Gemini AI availability
        gemini_available = orch.gemini_model is not None
        
        # Check MongoDB availability  
        mongodb_available = orch.mongodb_manager is not None
        
        return jsonify({
            "success": True,
            "data": {
                "system_status": "operational",
                "components": {
                    "gemini_ai": {
                        "available": gemini_available,
                        "status": "connected" if gemini_available else "not_configured"
                    },
                    "mongodb": {
                        "available": mongodb_available,
                        "status": "connected" if mongodb_available else "not_connected"
                    },
                    "scrapers": orch.available_scrapers
                },
                "timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET /health - Health check",
            "GET /api/scrapers - Get available scrapers", 
            "GET /api/icp/template - Get ICP template",
            "POST /api/lead-generation/run - Run complete pipeline",
            "POST /api/queries/generate - Generate queries only",
            "POST /api/lead-filtering/run - Run lead filtering only",
            "GET /api/status - Get system status"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

if __name__ == '__main__':
    # Development server
    print("🚀 Starting Lead Generation Flask API...")
    print("📋 Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /api/scrapers - Get available scrapers")
    print("  GET  /api/icp/template - Get ICP template") 
    print("  POST /api/lead-generation/run - Run complete pipeline")
    print("  POST /api/queries/generate - Generate queries only")
    print("  POST /api/lead-filtering/run - Run lead filtering only")
    print("  GET  /api/status - Get system status")
    print("")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )