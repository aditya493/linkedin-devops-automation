#!/usr/bin/env python3
"""
Analytics report generation script for LinkedIn DevOps automation.
This script collects metrics from different automation jobs and generates comprehensive reports.
"""

import json
import os
from datetime import datetime

def load_metrics_safely(file_path, default=None):
    """Safely load JSON metrics file."""
    if default is None:
        default = {}
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f'Warning: Failed to load {file_path}: {e}')
    
    return default

def main():
    try:
        print("Generating comprehensive analytics report...")
        
        # Collect all metrics from different jobs
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'content_posting': {},
            'engagement': {},
            'networking': {},
            'growth_strategy': {}
        }
        
        # Load content metrics
        metrics['content_posting'] = load_metrics_safely('content-posting-metrics/metrics.json')
        
        # Load engagement metrics  
        engagement_data = load_metrics_safely('engagement-metrics/engagement_cache.json')
        if engagement_data:
            metrics['engagement'] = engagement_data
        
        # Load networking metrics
        networking_data = load_metrics_safely('network-building-results/engagement_cache.json')
        if networking_data:
            metrics['networking'] = {
                'connections_sent': len(networking_data.get('connected_profiles', [])),
                'total_network_size': len(networking_data.get('connected_profiles', []))
            }
        
        # Generate summary report
        report = """
LinkedIn DevOps Automation - Daily Report
==================================================

Date: {date}

Content Performance:
• Posts created: {posts_created}
• Total impressions: {impressions}
• Engagement rate: {engagement_rate}

Engagement Activity:
• Comments posted: {comments}
• Posts liked: {likes}
• Trending posts engaged: {trending}

Network Building:
• Connection requests sent: {connections}
• Total network size: {network_size}
• HR connections made: {hr_connections}

Growth Metrics:
• Weekly follower growth target: 50-100 new followers
• Engagement velocity: Improved through strategic timing
• Authority building: Consistent thought leadership content

Next 24 Hours Focus:
• Continue engaging with high-performing content
• Target 10 new HR connections
• Share 1 thought leadership post
• Respond to all comments within 2 hours

==================================================
        """.format(
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            posts_created=metrics['content_posting'].get('posts_created', 0),
            impressions=metrics['content_posting'].get('total_impressions', 'N/A'),
            engagement_rate=metrics['content_posting'].get('engagement_rate', 'N/A'),
            comments=len(metrics['engagement'].get('commented_posts', [])),
            likes=len(metrics['engagement'].get('liked_posts', [])),
            trending=metrics['engagement'].get('trending_engagement', 0),
            connections=metrics['networking'].get('connections_sent', 0),
            network_size=metrics['networking'].get('total_network_size', 0),
            hr_connections=metrics['networking'].get('hr_connections', 0)
        )
        
        print(report)
        
        # Save detailed metrics for historical tracking
        with open('daily_automation_report.json', 'w') as f:
            json.dump(metrics, f, indent=2)
            
    except Exception as e:
        print(f'Error generating analytics report: {e}')

if __name__ == '__main__':
    main()