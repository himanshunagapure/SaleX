from pymongo import MongoClient
from datetime import datetime
from web_url_scraper.config import (
    MONGODB_URI, 
    MONGODB_DATABASE_NAME, 
    MONGODB_COLLECTION_NAME
)

def get_database_connection():
    """
    Create and return a MongoDB database connection.
    
    Returns:
        pymongo.database.Database: Database object
    """
    try:
        print("Connecting to MongoDB...")
        client = MongoClient(MONGODB_URI)
        
        # Test connection
        client.admin.command('ping')
        print("MongoDB connection successful!")
        
        # Return database object
        return client[MONGODB_DATABASE_NAME]
        
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        raise

def get_collection():
    """
    Get the MongoDB collection for storing URLs.
    
    Returns:
        pymongo.collection.Collection: Collection object
    """
    try:
        db = get_database_connection()
        return db[MONGODB_COLLECTION_NAME]
    except Exception as e:
        print(f"Failed to get collection: {e}")
        raise

def save_url(url_data, search_query):
    """
    Save a single URL to the database with duplicate prevention.
    
    Args:
        url_data (dict): Dictionary containing url, title, snippet, url_type
        search_query (str): Original search query
    
    Returns:
        bool: True if saved successfully, False if duplicate or error
    """
    try:
        collection = get_collection()
        
        # Check for existing URL
        existing = collection.find_one({'url': url_data['url']})
        if existing:
            return False  # URL already exists
        
        # Create document
        document = {
            'url': url_data['url'],
            'title': url_data.get('title', ''),
            'snippet': url_data.get('snippet', ''),
            'url_type': url_data.get('url_type', 'general'),  # Add URL type field
            'search_query': search_query.lower(),  # Store in lowercase for case-insensitive matching
            'created_at': datetime.now(),
            'scraped_at': datetime.now()  # Use datetime instead of date
        }
        
        # Insert document
        result = collection.insert_one(document)
        
        if result.inserted_id:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error saving URL {url_data.get('url', 'unknown')}: {e}")
        return False

def save_multiple_urls(urls_list, search_query):
    """
    Save multiple URLs to the database and return statistics.
    
    Args:
        urls_list (list): List of URL dictionaries
        search_query (str): Original search query
    
    Returns:
        dict: Statistics about the operation
    """
    total_processed = 0
    new_inserted = 0
    duplicates_skipped = 0
    
    print(f"Processing {len(urls_list)} URLs for storage...")
    
    for url_data in urls_list:
        total_processed += 1
        
        if save_url(url_data, search_query):
            new_inserted += 1
        else:
            duplicates_skipped += 1
    
    statistics = {
        'total_processed': total_processed,
        'new_inserted': new_inserted,
        'duplicates_skipped': duplicates_skipped
    }
    
    print(f"Storage complete: {new_inserted} new URLs, {duplicates_skipped} duplicates skipped")
    return statistics

def setup_database_indexes():
    """
    Create necessary database indexes for performance and data integrity.
    """
    try:
        collection = get_collection()
        
        # Create unique index on URL to prevent duplicates
        print("Creating unique index on URL field...")
        collection.create_index('url', unique=True)
        
        # Create index on search_query for faster queries
        print("Creating index on search_query field...")
        collection.create_index('search_query')
        
        # Create case-insensitive index for search_query
        print("Creating case-insensitive index on search_query field...")
        collection.create_index([('search_query', 'text')])
        
        # Create index on url_type for faster filtering
        print("Creating index on url_type field...")
        collection.create_index('url_type')
        
        # Create compound index on search_query and url_type for combined queries
        print("Creating compound index on search_query and url_type...")
        collection.create_index([('search_query', 1), ('url_type', 1)])
        
        # Create index on created_at for time-based queries
        print("Creating index on created_at field...")
        collection.create_index('created_at')
        
        print("Database indexes created successfully!")
        
    except Exception as e:
        print(f"Error creating indexes: {e}")
        # Don't raise exception as indexes might already exist

def get_database_stats():
    """
    Get basic statistics about the database.
    
    Returns:
        dict: Database statistics
    """
    try:
        collection = get_collection()
        
        total_documents = collection.count_documents({})
        unique_queries = len(collection.distinct('search_query'))
        
        # Get URL type statistics
        url_type_stats = get_url_type_statistics()
        
        return {
            'total_urls': total_documents,
            'unique_search_queries': unique_queries,
            'url_type_breakdown': url_type_stats['url_types'],
            'unique_url_types': url_type_stats['unique_url_types']
        }
        
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {
            'total_urls': 0, 
            'unique_search_queries': 0,
            'url_type_breakdown': {},
            'unique_url_types': 0
        }

def test_database_connection():
    """
    Test the database connection and return status.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        collection = get_collection()
        # Try a simple operation
        collection.find_one()
        print("Database connection test successful!")
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def delete_urls_by_query(search_query):
    """
    Delete all URLs that match a specific search query.
    
    Args:
        search_query (str): The search query to match for deletion
    
    Returns:
        int: Number of documents deleted
    """
    try:
        collection = get_collection()
        # Convert search query to lowercase for case-insensitive matching
        search_query_lower = search_query.lower()
        result = collection.delete_many({'search_query': search_query_lower})
        print(f"Deleted {result.deleted_count} URLs for query: '{search_query}' (matched as '{search_query_lower}')")
        return result.deleted_count
    except Exception as e:
        print(f"Error deleting URLs for query '{search_query}': {e}")
        return 0

def delete_url_by_url(url):
    """
    Delete a specific URL from the database.
    
    Args:
        url (str): The specific URL to delete
    
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        collection = get_collection()
        result = collection.delete_one({'url': url})
        if result.deleted_count > 0:
            print(f"Deleted URL: {url}")
            return True
        else:
            print(f"URL not found for deletion: {url}")
            return False
    except Exception as e:
        print(f"Error deleting URL '{url}': {e}")
        return False

def delete_urls_by_date_range(start_date, end_date):
    """
    Delete URLs created within a specific date range.
    
    Args:
        start_date (datetime): Start date for deletion range
        end_date (datetime): End date for deletion range
    
    Returns:
        int: Number of documents deleted
    """
    try:
        collection = get_collection()
        result = collection.delete_many({
            'created_at': {
                '$gte': start_date,
                '$lte': end_date
            }
        })
        print(f"Deleted {result.deleted_count} URLs between {start_date} and {end_date}")
        return result.deleted_count
    except Exception as e:
        print(f"Error deleting URLs by date range: {e}")
        return 0

def get_urls_by_query(search_query):
    """
    Get all URLs that match a specific search query (case-insensitive).
    
    Args:
        search_query (str): The search query to match
    
    Returns:
        list: List of matching documents
    """
    try:
        collection = get_collection()
        # Convert search query to lowercase for case-insensitive matching
        search_query_lower = search_query.lower()
        results = list(collection.find({'search_query': search_query_lower}))
        print(f"Found {len(results)} URLs for query: '{search_query}' (matched as '{search_query_lower}')")
        return results
    except Exception as e:
        print(f"Error getting URLs for query '{search_query}': {e}")
        return []

def count_urls_by_query(search_query):
    """
    Count URLs that match a specific search query (case-insensitive).
    
    Args:
        search_query (str): The search query to match
    
    Returns:
        int: Number of matching documents
    """
    try:
        collection = get_collection()
        # Convert search query to lowercase for case-insensitive matching
        search_query_lower = search_query.lower()
        count = collection.count_documents({'search_query': search_query_lower})
        return count
    except Exception as e:
        print(f"Error counting URLs for query '{search_query}': {e}")
        return 0

def clear_all_urls():
    """
    Delete all URLs from the database (use with caution!).
    
    Returns:
        int: Number of documents deleted
    """
    try:
        collection = get_collection()
        result = collection.delete_many({})
        print(f"Deleted all {result.deleted_count} URLs from database")
        return result.deleted_count
    except Exception as e:
        print(f"Error clearing all URLs: {e}")
        return 0

def get_urls_by_type(url_type):
    """
    Get all URLs of a specific type.
    
    Args:
        url_type (str): The URL type to filter by ('instagram', 'facebook', 'reddit', 'quora', 'twitter', 'linkedin', 'general')
    
    Returns:
        list: List of matching documents
    """
    try:
        collection = get_collection()
        results = list(collection.find({'url_type': url_type}))
        print(f"Found {len(results)} URLs of type: {url_type}")
        return results
    except Exception as e:
        print(f"Error getting URLs by type '{url_type}': {e}")
        return []

def count_urls_by_type(url_type):
    """
    Count URLs of a specific type.
    
    Args:
        url_type (str): The URL type to count ('instagram', 'facebook', 'reddit', 'quora', 'twitter', 'linkedin', 'general')
    
    Returns:
        int: Number of matching documents
    """
    try:
        collection = get_collection()
        count = collection.count_documents({'url_type': url_type})
        return count
    except Exception as e:
        print(f"Error counting URLs by type '{url_type}': {e}")
        return 0

def get_url_type_statistics():
    """
    Get statistics about URL types in the database.
    
    Returns:
        dict: Statistics about URL types
    """
    try:
        collection = get_collection()
        
        # Get all unique URL types
        url_types = collection.distinct('url_type')
        
        # Count each type
        type_stats = {}
        for url_type in url_types:
            count = collection.count_documents({'url_type': url_type})
            type_stats[url_type] = count
        
        # Get total count
        total_urls = collection.count_documents({})
        
        return {
            'total_urls': total_urls,
            'url_types': type_stats,
            'unique_url_types': len(url_types)
        }
        
    except Exception as e:
        print(f"Error getting URL type statistics: {e}")
        return {'total_urls': 0, 'url_types': {}, 'unique_url_types': 0}

def get_urls_by_query_and_type(search_query, url_type):
    """
    Get URLs that match both a specific search query and URL type.
    
    Args:
        search_query (str): The search query to match
        url_type (str): The URL type to filter by
    
    Returns:
        list: List of matching documents
    """
    try:
        collection = get_collection()
        # Convert search query to lowercase for case-insensitive matching
        search_query_lower = search_query.lower()
        results = list(collection.find({
            'search_query': search_query_lower,
            'url_type': url_type
        }))
        print(f"Found {len(results)} URLs for query '{search_query}' and type '{url_type}'")
        return results
    except Exception as e:
        print(f"Error getting URLs by query and type: {e}")
        return []

def delete_urls_by_type(url_type):
    """
    Delete all URLs of a specific type.
    
    Args:
        url_type (str): The URL type to delete
    
    Returns:
        int: Number of documents deleted
    """
    try:
        collection = get_collection()
        result = collection.delete_many({'url_type': url_type})
        print(f"Deleted {result.deleted_count} URLs of type: {url_type}")
        return result.deleted_count
    except Exception as e:
        print(f"Error deleting URLs by type '{url_type}': {e}")
        return 0 