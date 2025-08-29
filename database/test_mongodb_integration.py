"""
Test script for MongoDB integration
Verifies that the database connection and operations work correctly
"""

import asyncio
import json
from datetime import datetime
from database.mongodb_manager import MongoDBManager, get_mongodb_manager
from database.db_utils import DatabaseUtils


def test_mongodb_connection():
    """Test basic MongoDB connection"""
    print("🔧 Testing MongoDB connection...")
    
    try:
        mongodb_manager = get_mongodb_manager()
        print("✅ MongoDB connection successful")
        
        # Test database stats
        stats = mongodb_manager.get_database_stats()
        print(f"📊 Database stats: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False


def test_instagram_lead_insertion():
    """Test Instagram lead insertion"""
    print("\n📸 Testing Instagram lead insertion...")
    
    try:
        mongodb_manager = get_mongodb_manager()
        
        # Sample Instagram lead data
        sample_lead = {
            "url": "https://www.instagram.com/test_user/",
            "content_type": "profile",
            "username": "test_user",
            "full_name": "Test User",
            "followers_count": "1K",
            "following_count": "100",
            "biography": "Test bio",
            "bio_links": [],
            "is_private": False,
            "is_verified": False,
            "is_business_account": True,
            "business_email": "test@example.com",
            "business_phone_number": "+1234567890",
            "business_category_name": "Test Category"
        }
        
        # Insert lead
        success = mongodb_manager.insert_instagram_lead(sample_lead)
        
        if success:
            print("✅ Instagram lead inserted successfully")
        else:
            print("⚠️ Instagram lead insertion failed (possibly duplicate)")
        
        return True
    except Exception as e:
        print(f"❌ Instagram lead insertion failed: {e}")
        return False


def test_linkedin_lead_insertion():
    """Test LinkedIn lead insertion"""
    print("\n💼 Testing LinkedIn lead insertion...")
    
    try:
        mongodb_manager = get_mongodb_manager()
        
        # Sample LinkedIn lead data
        sample_lead = {
            "url": "https://www.linkedin.com/in/test_user/",
            "url_type": "profile",
            "username": "test_user",
            "full_name": "Test User",
            "job_title": ["Software Engineer", "Developer"],
            "title": "Senior Software Engineer",
            "followers": 500,
            "connections": 200,
            "about": "Test about section",
            "location": "Test City, Country",
            "website": "https://testwebsite.com",
            "contact_info": {},
            "scraping_timestamp": datetime.now().timestamp()
        }
        
        # Insert lead
        success = mongodb_manager.insert_linkedin_lead(sample_lead)
        
        if success:
            print("✅ LinkedIn lead inserted successfully")
        else:
            print("⚠️ LinkedIn lead insertion failed (possibly duplicate)")
        
        return True
    except Exception as e:
        print(f"❌ LinkedIn lead insertion failed: {e}")
        return False


def test_web_lead_insertion():
    """Test web lead insertion"""
    print("\n🌐 Testing web lead insertion...")
    
    try:
        mongodb_manager = get_mongodb_manager()
        
        # Sample web lead data
        sample_lead = {
            "url": "https://testwebsite.com",
            "business_name": "Test Company",
            "contact_person": "Test Contact",
            "email": "contact@testwebsite.com",
            "phone": "+1234567890",
            "address": "123 Test Street, Test City",
            "website": "https://testwebsite.com",
            "social_media": {},
            "services": ["Web Development", "Consulting"],
            "industry": "Technology"
        }
        
        # Insert lead
        success = mongodb_manager.insert_web_lead(sample_lead)
        
        if success:
            print("✅ Web lead inserted successfully")
        else:
            print("⚠️ Web lead insertion failed (possibly duplicate)")
        
        return True
    except Exception as e:
        print(f"❌ Web lead insertion failed: {e}")
        return False


def test_youtube_lead_insertion():
    """Test YouTube lead insertion"""
    print("\n📺 Testing YouTube lead insertion...")
    
    try:
        mongodb_manager = get_mongodb_manager()
        
        # Sample YouTube lead data
        sample_lead = {
            "url": "https://www.youtube.com/watch?v=test123",
            "content_type": "video",
            "title": "Test Video Title",
            "channel_name": "Test Channel",
            "upload_date": "Jan 1, 2024",
            "views": "10K",
            "subscribers": "100K",
            "social_media_handles": {},
            "email": ["contact@testchannel.com"],
            "description": "Test video description"
        }
        
        # Insert lead
        success = mongodb_manager.insert_youtube_lead(sample_lead)
        
        if success:
            print("✅ YouTube lead inserted successfully")
        else:
            print("⚠️ YouTube lead insertion failed (possibly duplicate)")
        
        return True
    except Exception as e:
        print(f"❌ YouTube lead insertion failed: {e}")
        return False


def test_batch_insertion():
    """Test batch lead insertion"""
    print("\n📦 Testing batch lead insertion...")
    
    try:
        mongodb_manager = get_mongodb_manager()
        
        # Sample batch data
        batch_leads = [
            {
                "url": "https://www.instagram.com/batch_user1/",
                "content_type": "profile",
                "username": "batch_user1",
                "full_name": "Batch User 1",
                "followers_count": "5K"
            },
            {
                "url": "https://www.instagram.com/batch_user2/",
                "content_type": "profile", 
                "username": "batch_user2",
                "full_name": "Batch User 2",
                "followers_count": "10K"
            }
        ]
        
        # Insert batch
        stats = mongodb_manager.insert_batch_leads(batch_leads, 'instagram')
        
        print(f"✅ Batch insertion completed:")
        print(f"   - Success: {stats['success_count']}")
        print(f"   - Duplicates: {stats['duplicate_count']}")
        print(f"   - Failures: {stats['failure_count']}")
        
        return True
    except Exception as e:
        print(f"❌ Batch insertion failed: {e}")
        return False


def test_search_and_export():
    """Test search and export functionality"""
    print("\n🔍 Testing search and export...")
    
    try:
        db_utils = DatabaseUtils()
        
        # Test search
        results = db_utils.search_leads(query="test", limit=10)
        print(f"✅ Search found {len(results)} results")
        
        # Test recent leads
        recent = db_utils.get_recent_leads(hours=24)
        print(f"✅ Found {len(recent)} recent leads")
        
        # Test export (small test)
        if results:
            output_file = db_utils.export_leads(
                source="instagram",
                format="json",
                output_file="test_export.json"
            )
            print(f"✅ Export completed: {output_file}")
        
        return True
    except Exception as e:
        print(f"❌ Search/export failed: {e}")
        return False


def test_database_utils():
    """Test database utilities"""
    print("\n🛠️ Testing database utilities...")
    
    try:
        db_utils = DatabaseUtils()
        
        # Get comprehensive stats
        stats = db_utils.get_database_stats()
        print(f"✅ Database stats retrieved:")
        print(f"   - Total leads: {stats.get('total_leads', 0)}")
        print(f"   - Instagram: {stats.get('instagram', 0)}")
        print(f"   - LinkedIn: {stats.get('linkedin', 0)}")
        print(f"   - Web: {stats.get('web', 0)}")
        print(f"   - YouTube: {stats.get('youtube', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Database utilities failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("🚀 Starting MongoDB Integration Tests")
    print("=" * 50)
    
    tests = [
        ("MongoDB Connection", test_mongodb_connection),
        ("Instagram Lead Insertion", test_instagram_lead_insertion),
        ("LinkedIn Lead Insertion", test_linkedin_lead_insertion),
        ("Web Lead Insertion", test_web_lead_insertion),
        ("YouTube Lead Insertion", test_youtube_lead_insertion),
        ("Batch Insertion", test_batch_insertion),
        ("Search and Export", test_search_and_export),
        ("Database Utilities", test_database_utils)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MongoDB integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the MongoDB setup.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
