"""
Test the complete sync functionality
"""

import sys
sys.path.append('./src')

from config_manager import ConfigManager
from sync_engine import SyncEngine

def test_full_sync():
    print('=== Testing Complete Dry-Run Sync ===')
    config_manager = ConfigManager()
    sync_engine = SyncEngine(config_manager)
    
    print('Running complete sync process...')
    results = sync_engine.run_sync(dry_run=True)
    
    print('\n=== RESULTS ===')
    for key, value in results.items():
        if key != 'reports':
            print(f'{key}: {value}')
    
    print('\n=== SUMMARY REPORT ===')
    if 'reports' in results and 'summary' in results['reports']:
        print(results['reports']['summary'])
    
    print('\n=== UNMATCHED BOOKS SAMPLE ===')
    if 'reports' in results and 'unmatched' in results['reports']:
        unmatched_lines = results['reports']['unmatched'].split('\n')
        for line in unmatched_lines[:15]:  # Show first 15 lines
            if line.strip():
                print(line)

if __name__ == '__main__':
    test_full_sync()