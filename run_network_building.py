#!/usr/bin/env python3
"""
Network building automation script for LinkedIn DevOps automation.
This script focuses specifically on HR and professional connection building.
"""

import sys
import os

# Add current directory to Python path
sys.path.append('.')

try:
    from linkedin_engagement_automation import LinkedInEngagementBot
    
    # Focus specifically on connection building
    bot = LinkedInEngagementBot()
    
    print('Searching for HR professionals...')
    max_connections = int(os.environ.get('MAX_CONNECTIONS_PER_RUN', '10'))
    hr_professionals = bot.search_hr_professionals(max_connections)
    
    connection_count = 0
    for hr_profile in hr_professionals:
        try:
            profile_id = hr_profile.get('id')
            if profile_id:
                message = bot.generate_connection_message(hr_profile)
                if bot.send_connection_request(profile_id, message):
                    connection_count += 1
                    print(f'Connection request sent ({connection_count})')
        except Exception as e:
            print(f'Error: {e}')
    
    bot.save_engagement_cache()
    print(f'Total connections sent: {connection_count}')
    
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Unexpected error: {e}')
    sys.exit(1)