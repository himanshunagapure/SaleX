#!/usr/bin/env python3
"""
Test function for main_app.py WebScraperOrchestrator
Simple test that processes a list of URLs and returns results
"""

import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
from web_scraper.main_app import WebScraperOrchestrator


def test_web_scraper_pipeline(urls: List[str], 
                             enable_ai: bool = False,
                             enable_quality: bool = False,
                             max_workers: int = 2,
                             delay: float = 0.5) -> Dict[str, Any]:
    """
    Simple test function for WebScraperOrchestrator
    
    Args:
        urls: List of URLs to test with
        enable_ai: Whether to enable AI features (default: False for faster testing)
        enable_quality: Whether to enable quality engine (default: False for faster testing)
        max_workers: Number of concurrent workers (default: 2 for testing)
        delay: Delay between requests (default: 0.5s for faster testing)
        
    Returns:
        Dictionary containing test results and statistics
    """
    # Create lead_extracted directory in the project root
    project_root = Path(__file__).parent
    storage_dir = project_root / "lead_extracted"
    storage_dir.mkdir(exist_ok=True)
    
    try:
        print(f"Starting test with {len(urls)} URLs...")
        print(f"Test storage directory: {storage_dir}")
        
        # Initialize orchestrator with test settings
        orchestrator = WebScraperOrchestrator(
            storage_path=str(storage_dir),
            enable_ai=enable_ai,
            enable_quality_engine=enable_quality,
            max_workers=max_workers,
            delay_between_requests=delay
        )
        
        # Run the complete pipeline
        results = orchestrator.run_complete_pipeline(
            urls=urls,
            batch_size=10,  # Small batch size for testing
            export_format="json",
            export_path=str(storage_dir / "test_results.json"),
            generate_final_leads=True  # Enable final leads generation for testing
        )
        
        # Print summary
        summary = results["pipeline_summary"]
        print("\n" + "="*50)
        print("TEST RESULTS SUMMARY")
        print("="*50)
        print(f"Total URLs processed: {summary['total_urls']}")
        print(f"Successful leads: {summary['successful_leads']}")
        print(f"Failed URLs: {summary['failed_urls']}")
        print(f"Duplicate leads: {summary['duplicate_leads']}")
        print(f"Processing time: {summary['processing_time_seconds']:.2f} seconds")
        print(f"Success rate: {(summary['successful_leads']/summary['total_urls']*100):.1f}%")
        
        # Show some sample successful leads
        if results["successful_leads"]:
            print(f"\nSample successful leads (showing first 3):")
            for i, lead in enumerate(results["successful_leads"][:3]):
                print(f"\nLead {i+1}:")
                print(f"  URL: {lead.get('source_url', 'N/A')}")
                print(f"  Business: {lead.get('business_name', 'N/A')}")
                print(f"  Email: {lead.get('email', 'N/A')}")
                print(f"  Phone: {lead.get('phone', 'N/A')}")
                print(f"  Lead Score: {lead.get('lead_score', 'N/A')}")
        
        # Show failed URLs
        if results["failed_urls"]:
            print(f"\nFailed URLs (showing first 3):")
            for i, failed in enumerate(results["failed_urls"][:3]):
                print(f"  {i+1}. {failed.get('url', 'N/A')} - {failed.get('error', 'Unknown error')}")
        
        # Show final leads information if generated
        if results.get("final_leads_file"):
            print(f"\n✅ Final leads generated: {results['final_leads_file']}")
        
        print("="*50)
        
        return results
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return {"error": str(e), "test_failed": True}
        
    finally:
        # No cleanup needed - results are stored in lead_extracted/
        print(f"Results stored in: {storage_dir}")
        print(f"Individual lead files: {storage_dir}/lead_*.json")
        print(f"Exported results: {storage_dir}/test_results.json")
        print(f"Final leads: {storage_dir}/final_leads.json")

def run_sample_test():
    """
    Run a sample test with some common website URLs
    """
    # Sample URLs for testing (mix of different types)
    sample_urls = [
        "https://www.cvent.com/"
    ]
    
    print("Running sample test with predefined URLs...")
    results = test_web_scraper_pipeline(sample_urls)
    return results


def quick_test(urls: List[str]) -> Dict[str, Any]:
    """
    Quick test function with minimal settings for fast execution
    
    Args:
        urls: List of URLs to test
        
    Returns:
        Test results dictionary
    """
    return test_web_scraper_pipeline(
        urls=urls,
        enable_ai=False,
        enable_quality=False,
        max_workers=1,
        delay=0.1
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Use URLs provided as command line arguments
        test_urls = sys.argv[1:]
        print(f"Testing with provided URLs: {test_urls}")
        results = test_web_scraper_pipeline(test_urls)
    else:
        # Run sample test
        results = run_sample_test()
    
    # Exit with error code if test failed
    if results.get("test_failed"):
        sys.exit(1)