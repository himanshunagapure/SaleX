"""
MongoDB Database Manager for Lead Generation Application
Handles database connections and operations for all scrapers
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from bson import ObjectId
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBManager:
    """MongoDB database manager for lead generation data"""
    
    def __init__(self, 
                 connection_string: str = None,
                 database_name: str = "lead_generation_db",
                 max_pool_size: int = 100):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection string (defaults to localhost)
            database_name: Name of the database
            max_pool_size: Maximum connection pool size
        """
        self.connection_string = connection_string or os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = database_name
        self.max_pool_size = max_pool_size
        self.client = None
        self.db = None
        
        # Collection names for each scraper
        self.collections = {
            'instagram': 'instagram_leads',
            'linkedin': 'linkedin_leads', 
            'web': 'web_leads',
            'youtube': 'youtube_leads'
        }
        
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                self.connection_string,
                maxPoolSize=self.max_pool_size,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            logger.info(f"✅ Connected to MongoDB database: {self.database_name}")
            
            # Create indexes for better performance
            self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Instagram collection indexes
            instagram_collection = self.db[self.collections['instagram']]
            instagram_collection.create_index([("url", 1)], unique=True)
            instagram_collection.create_index([("username", 1)])
            instagram_collection.create_index([("content_type", 1)])
            instagram_collection.create_index([("scraped_at", -1)])
            
            # LinkedIn collection indexes
            linkedin_collection = self.db[self.collections['linkedin']]
            linkedin_collection.create_index([("url", 1)], unique=True)
            linkedin_collection.create_index([("username", 1)])
            linkedin_collection.create_index([("url_type", 1)])
            linkedin_collection.create_index([("scraping_timestamp", -1)])
            
            # Web collection indexes
            web_collection = self.db[self.collections['web']]
            try:
                web_collection.drop_index([("url", 1)])
            except:
                pass
            web_collection.create_index([("source_url", 1)]) # Non-unique
            web_collection.create_index([("domain", 1)])
            web_collection.create_index([("scraped_at", -1)])
            
            # YouTube collection indexes
            youtube_collection = self.db[self.collections['youtube']]
            youtube_collection.create_index([("url", 1)], unique=True)
            youtube_collection.create_index([("channel_name", 1)])
            youtube_collection.create_index([("content_type", 1)])
            youtube_collection.create_index([("scraped_at", -1)])
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to create some indexes: {e}")
    
    def insert_instagram_lead(self, lead_data: Dict[str, Any]) -> bool:
        """
        Insert Instagram lead data into MongoDB
        
        Args:
            lead_data: Instagram lead data dictionary
            
        Returns:
            bool: Success status
        """
        try:
            # Add metadata
            lead_data['scraped_at'] = datetime.utcnow()
            lead_data['source'] = 'instagram_scraper'
            
            # Insert into Instagram collection
            result = self.db[self.collections['instagram']].insert_one(lead_data)
            
            logger.info(f"✅ Instagram lead inserted with ID: {result.inserted_id}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"⚠️ Instagram lead already exists for URL: {lead_data.get('url')}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to insert Instagram lead: {e}")
            return False
    
    def insert_linkedin_lead(self, lead_data: Dict[str, Any]) -> bool:
        """
        Insert LinkedIn lead data into MongoDB
        
        Args:
            lead_data: LinkedIn lead data dictionary
            
        Returns:
            bool: Success status
        """
        try:
            # Add metadata
            lead_data['scraped_at'] = datetime.utcnow()
            lead_data['source'] = 'linkedin_scraper'
            
            # Insert into LinkedIn collection
            result = self.db[self.collections['linkedin']].insert_one(lead_data)
            
            logger.info(f"✅ LinkedIn lead inserted with ID: {result.inserted_id}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"⚠️ LinkedIn lead already exists for URL: {lead_data.get('url')}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to insert LinkedIn lead: {e}")
            return False
    
    def insert_web_lead(self, lead_data: Dict[str, Any]) -> bool:
        """
        Insert web lead data into MongoDB
        
        Args:
            lead_data: Web lead data dictionary
            
        Returns:
            bool: Success status
        """
        try:
            # Add metadata
            lead_data['scraped_at'] = datetime.utcnow()
            lead_data['source'] = 'web_scraper'
            
            # Insert into web collection
            result = self.db[self.collections['web']].insert_one(lead_data)
            
            logger.info(f"✅ Web lead inserted with ID: {result.inserted_id}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"⚠️ Web lead already exists for URL: {lead_data.get('url')}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to insert web lead: {e}")
            return False
    
    def insert_youtube_lead(self, lead_data: Dict[str, Any]) -> bool:
        """
        Insert YouTube lead data into MongoDB
        
        Args:
            lead_data: YouTube lead data dictionary
            
        Returns:
            bool: Success status
        """
        try:
            # Add metadata
            lead_data['scraped_at'] = datetime.utcnow()
            lead_data['source'] = 'youtube_scraper'
            
            # Insert into YouTube collection
            result = self.db[self.collections['youtube']].insert_one(lead_data)
            
            logger.info(f"✅ YouTube lead inserted with ID: {result.inserted_id}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"⚠️ YouTube lead already exists for URL: {lead_data.get('url')}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to insert YouTube lead: {e}")
            return False
    
    def insert_batch_leads(self, leads_data: List[Dict[str, Any]], source: str) -> Dict[str, int]:
        """
        Insert multiple leads from a batch operation
        
        Args:
            leads_data: List of lead data dictionaries
            source: Source scraper ('instagram', 'linkedin', 'web', 'youtube')
            
        Returns:
            Dict with success and failure counts
        """
        if source not in self.collections:
            raise ValueError(f"Invalid source: {source}. Must be one of {list(self.collections.keys())}")
        
        success_count = 0
        failure_count = 0
        duplicate_count = 0
        
        for lead_data in leads_data:
            try:
                # Add metadata
                lead_data['scraped_at'] = datetime.utcnow()
                lead_data['source'] = f'{source}_scraper'
                
                # Insert into appropriate collection
                result = self.db[self.collections[source]].insert_one(lead_data)
                success_count += 1
                
            except DuplicateKeyError:
                duplicate_count += 1
                logger.warning(f"⚠️ Duplicate lead for URL: {lead_data.get('url')}")
            except Exception as e:
                failure_count += 1
                logger.error(f"❌ Failed to insert lead: {e}")
        
        logger.info(f"📊 Batch insert completed - Success: {success_count}, Duplicates: {duplicate_count}, Failures: {failure_count}")
        
        return {
            'success_count': success_count,
            'duplicate_count': duplicate_count,
            'failure_count': failure_count,
            'total_processed': len(leads_data)
        }
    
    def get_leads_by_source(self, source: str, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get leads from a specific source
        
        Args:
            source: Source scraper ('instagram', 'linkedin', 'web', 'youtube')
            limit: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            List of lead documents
        """
        if source not in self.collections:
            raise ValueError(f"Invalid source: {source}. Must be one of {list(self.collections.keys())}")
        
        try:
            cursor = self.db[self.collections[source]].find().sort('scraped_at', -1).skip(skip).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"❌ Failed to get leads from {source}: {e}")
            return []
    
    def search_leads(self, query: Dict[str, Any], source: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search leads across collections
        
        Args:
            query: MongoDB query dictionary
            source: Specific source to search (optional)
            limit: Maximum number of results
            
        Returns:
            List of matching lead documents
        """
        try:
            if source:
                if source not in self.collections:
                    raise ValueError(f"Invalid source: {source}")
                cursor = self.db[self.collections[source]].find(query).limit(limit)
                return list(cursor)
            else:
                # Search across all collections
                results = []
                for collection_name in self.collections.values():
                    cursor = self.db[collection_name].find(query).limit(limit)
                    results.extend(list(cursor))
                return results
        except Exception as e:
            logger.error(f"❌ Failed to search leads: {e}")
            return []
    
    def get_all_urls(self, source: str = 'web', include_metadata: bool = True) -> List[Dict[str, Any]]:
        """
        Get all URLs from the specified collection
        
        Args:
            source: Source collection to retrieve URLs from ('web', 'instagram', 'linkedin', 'youtube')
            include_metadata: Whether to include scraped_at and other metadata
            
        Returns:
            List of URL data dictionaries
        """
        if source not in self.collections:
            raise ValueError(f"Invalid source: {source}. Must be one of {list(self.collections.keys())}")
        
        try:
            # Define projection based on source and metadata preference
            projection = {}
            if not include_metadata:
                projection = {'_id': 0, 'scraped_at': 0, 'source': 0}
            
            # Get all documents from the specified collection
            cursor = self.db[self.collections[source]].find({}, projection).sort('scraped_at', -1)
            urls_data = list(cursor)
            
            logger.info(f"✅ Retrieved {len(urls_data)} URLs from {source} collection")
            return urls_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get URLs from {source} collection: {e}")
            return []
    
    def get_urls_by_domain(self, domain: str, source: str = 'web') -> List[Dict[str, Any]]:
        """
        Get URLs filtered by domain
        
        Args:
            domain: Domain to filter by
            source: Source collection ('web', 'instagram', 'linkedin', 'youtube')
            
        Returns:
            List of URL data dictionaries from the specified domain
        """
        if source not in self.collections:
            raise ValueError(f"Invalid source: {source}. Must be one of {list(self.collections.keys())}")
        
        try:
            query = {'domain': domain}
            cursor = self.db[self.collections[source]].find(query).sort('scraped_at', -1)
            urls_data = list(cursor)
            
            logger.info(f"✅ Retrieved {len(urls_data)} URLs from domain '{domain}' in {source} collection")
            return urls_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get URLs from domain '{domain}': {e}")
            return []

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            stats = {}
            for source, collection_name in self.collections.items():
                count = self.db[collection_name].count_documents({})
                stats[source] = count
            
            stats['total_leads'] = sum(stats.values())
            return stats
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return {}
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()


# Global MongoDB manager instance
mongodb_manager = None

def get_mongodb_manager() -> MongoDBManager:
    """Get or create global MongoDB manager instance"""
    global mongodb_manager
    if mongodb_manager is None:
        mongodb_manager = MongoDBManager()
    return mongodb_manager
