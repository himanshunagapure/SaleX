#!/usr/bin/env python3
"""
Test script to verify the complete flow from search query to database storage.
"""

import sys
import os
import time

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
import google_service
import database_service

def test_complete_flow():
    """
    Test the complete flow from search query to database storage.
    """
    print("Testing Complete Flow: Search Query → Google Search → URL Filtering → Database Storage")
    print("=" * 80)
    
    # Test configuration
    print("1. Testing Configuration...")
    if not config.validate_config():
        print("❌ Configuration validation failed!")
        return False
    print("✅ Configuration validation passed!")
    
    # Test database connection
    print("\n2. Testing Database Connection...")
    if not database_service.test_database_connection():
        print("❌ Database connection failed!")
        return False
    print("✅ Database connection successful!")
    
    # Setup database indexes
    print("\n3. Setting up Database Indexes...")
    try:
        database_service.setup_database_indexes()
        print("✅ Database indexes created successfully!")
    except Exception as e:
        print(f"❌ Error setting up indexes: {e}")
        return False
    
    # Test search queries
    test_queries = [
        "Recently I travelled to",
        "My experience treavelling to",
        "I will be travelling to"
    ]
    
    total_tests = len(test_queries)
    passed_tests = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}/{total_tests}: '{query}'")
        print(f"{'='*60}")
        
        try:
            # Step 1: Google Search
            print(f"\nStep 1: Executing Google search for '{query}'...")
            start_time = time.time()
            search_results = google_service.search_multiple_pages(query)
            search_time = time.time() - start_time
            
            if not search_results:
                print(f"❌ No search results found for '{query}'")
                continue
                
            print(f"✅ Found {len(search_results)} search results in {search_time:.2f} seconds")
            
            # Step 2: URL Validation and Type Detection
            print(f"\nStep 2: Filtering and detecting URL types...")
            start_time = time.time()
            valid_urls = google_service.filter_valid_urls(search_results)
            filter_time = time.time() - start_time
            
            if not valid_urls:
                print(f"❌ No valid URLs found for '{query}'")
                continue
                
            print(f"✅ Found {len(valid_urls)} valid URLs in {filter_time:.2f} seconds")
            
            # Analyze URL types
            url_type_breakdown = {}
            for url_data in valid_urls:
                url_type = url_data.get('url_type', 'general')
                url_type_breakdown[url_type] = url_type_breakdown.get(url_type, 0) + 1
            
            print("URL Type Breakdown:")
            for url_type, count in sorted(url_type_breakdown.items()):
                percentage = (count / len(valid_urls)) * 100
                print(f"  {url_type.capitalize()}: {count} ({percentage:.1f}%)")
            
            # Step 3: Database Storage
            print(f"\nStep 3: Saving URLs to database...")
            start_time = time.time()
            storage_stats = database_service.save_multiple_urls(valid_urls, query)
            storage_time = time.time() - start_time
            
            print(f"✅ Storage completed in {storage_time:.2f} seconds")
            print(f"  - Total processed: {storage_stats['total_processed']}")
            print(f"  - New URLs added: {storage_stats['new_inserted']}")
            print(f"  - Duplicates skipped: {storage_stats['duplicates_skipped']}")
            
            # Step 4: Verify Database Storage
            print(f"\nStep 4: Verifying database storage...")
            stored_urls = database_service.get_urls_by_query(query)
            
            if len(stored_urls) >= storage_stats['new_inserted']:
                print(f"✅ Database verification successful! Found {len(stored_urls)} URLs for query")
                
                # Check URL types in database
                db_url_types = {}
                for url_data in stored_urls:
                    url_type = url_data.get('url_type', 'general')
                    db_url_types[url_type] = db_url_types.get(url_type, 0) + 1
                
                print("Database URL Type Breakdown:")
                for url_type, count in sorted(db_url_types.items()):
                    percentage = (count / len(stored_urls)) * 100
                    print(f"  {url_type.capitalize()}: {count} ({percentage:.1f}%)")
                
                passed_tests += 1
            else:
                print(f"❌ Database verification failed! Expected at least {storage_stats['new_inserted']} URLs, found {len(stored_urls)}")
            
            # Add delay between tests to be respectful to APIs
            if i < total_tests:
                print(f"\nWaiting 3 seconds before next test...")
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ Error during test {i}: {e}")
            continue
    
    # Final Results
    print(f"\n{'='*80}")
    print("FINAL RESULTS")
    print(f"{'='*80}")
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Complete flow is working correctly.")
        
        # Show final database statistics
        print(f"\nFinal Database Statistics:")
        final_stats = database_service.get_database_stats()
        print(f"  Total URLs: {final_stats['total_urls']}")
        print(f"  Unique Search Queries: {final_stats['unique_search_queries']}")
        print(f"  Unique URL Types: {final_stats['unique_url_types']}")
        
        if final_stats['url_type_breakdown']:
            print("  URL Type Breakdown:")
            for url_type, count in sorted(final_stats['url_type_breakdown'].items()):
                percentage = (count / final_stats['total_urls'] * 100) if final_stats['total_urls'] > 0 else 0
                print(f"    {url_type.capitalize()}: {count} ({percentage:.1f}%)")
        
        return True
    else:
        print(f"❌ {total_tests - passed_tests} tests failed. Please check the implementation.")
        return False

def test_single_query(query):
    """
    Test a single query with detailed output.
    
    Args:
        query (str): The search query to test
    """
    print(f"Testing Single Query: '{query}'")
    print("=" * 50)
    
    try:
        # Step 1: Google Search
        print(f"1. Searching Google for '{query}'...")
        search_results = google_service.search_multiple_pages(query)
        
        if not search_results:
            print("❌ No search results found")
            return False
            
        print(f"✅ Found {len(search_results)} search results")
        
        # Show first few results
        print("\nFirst 3 search results:")
        for i, result in enumerate(search_results[:3], 1):
            print(f"  {i}. {result.get('title', 'No title')}")
            print(f"     URL: {result.get('url', 'No URL')}")
            print(f"     Type: {google_service.detect_url_type(result.get('url', ''))}")
            print()
        
        # Step 2: URL Filtering
        print("2. Filtering and detecting URL types...")
        valid_urls = google_service.filter_valid_urls(search_results)
        
        if not valid_urls:
            print("❌ No valid URLs found")
            return False
            
        print(f"✅ Found {len(valid_urls)} valid URLs")
        
        # URL type analysis
        url_type_breakdown = {}
        for url_data in valid_urls:
            url_type = url_data.get('url_type', 'general')
            url_type_breakdown[url_type] = url_type_breakdown.get(url_type, 0) + 1
        
        print("\nURL Type Breakdown:")
        for url_type, count in sorted(url_type_breakdown.items()):
            percentage = (count / len(valid_urls)) * 100
            print(f"  {url_type.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Step 3: Database Storage
        print("\n3. Saving to database...")
        storage_stats = database_service.save_multiple_urls(valid_urls, query)
        
        print(f"✅ Storage completed:")
        print(f"  - New URLs added: {storage_stats['new_inserted']}")
        print(f"  - Duplicates skipped: {storage_stats['duplicates_skipped']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Complete Flow Test Suite")
    print("=" * 50)
    print("1. Run complete flow test (multiple queries)")
    print("2. Test single query")
    print("3. Exit")
    
    choice = input("\nSelect an option (1-3): ").strip()
    
    if choice == '1':
        test_complete_flow()
    elif choice == '2':
        query = input("Enter search query: ").strip()
        if query:
            test_single_query(query)
        else:
            print("No query provided.")
    elif choice == '3':
        print("Exiting...")
    else:
        print("Invalid option.") 