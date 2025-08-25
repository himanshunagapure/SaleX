#!/usr/bin/env python3
"""
Test script to verify the final leads integration in main_app.py
"""

import json
from pathlib import Path
from web_scraper.main_app import WebScraperOrchestrator

def test_final_leads_integration():
    """Test that final leads generation is properly integrated"""
    
    print("Testing final leads integration in main_app.py...")
    
    # Test URLs
    test_urls = ["https://www.narcity.com/i-recently-travelled-from-canada-to-us"]
    
    # Create test storage directory
    storage_dir = Path("test_integration_output")
    storage_dir.mkdir(exist_ok=True)
    
    try:
        # Initialize orchestrator
        orchestrator = WebScraperOrchestrator(
            storage_path=str(storage_dir),
            enable_ai=False,
            enable_quality_engine=False,
            max_workers=1,
            delay_between_requests=0.1
        )
        
        print("Running pipeline with final leads generation enabled...")
        
        # Run pipeline with final leads generation
        results = orchestrator.run_complete_pipeline(
            urls=test_urls,
            batch_size=1,
            export_format="json",
            export_path=str(storage_dir / "test_results.json"),
            generate_final_leads=True
        )
        
        print("✅ Pipeline completed successfully!")
        
        # Check if final leads file was generated
        final_leads_path = storage_dir / "final_leads.json"
        if final_leads_path.exists():
            print(f"✅ Final leads file generated: {final_leads_path}")
            
            # Load and display final leads
            with open(final_leads_path, 'r', encoding='utf-8') as f:
                final_leads_data = json.load(f)
            
            print(f"📊 Final leads statistics:")
            print(f"  Total leads: {final_leads_data['metadata']['total_leads']}")
            print(f"  Traditional leads: {final_leads_data['metadata']['traditional_leads']}")
            print(f"  AI extracted leads: {final_leads_data['metadata']['ai_extracted_leads']}")
            
            # Show sample lead
            if final_leads_data['leads']:
                sample_lead = final_leads_data['leads'][0]
                print(f"\n📋 Sample final lead:")
                for key, value in sample_lead.items():
                    print(f"  {key}: {value}")
        else:
            print("❌ Final leads file not found")
        
        # Check pipeline results
        if results.get("final_leads_file"):
            print(f"✅ Pipeline returned final leads file path: {results['final_leads_file']}")
        else:
            print("❌ Pipeline did not return final leads file path")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_final_leads_integration()
    if success:
        print("\n🎉 Integration test completed successfully!")
    else:
        print("\n💥 Integration test failed!")
