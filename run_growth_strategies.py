#!/usr/bin/env python3
"""
Growth strategy execution script for LinkedIn DevOps automation.
This script generates content plans and executes advanced growth strategies.
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to Python path
sys.path.append('.')

try:
    from advanced_growth_strategies import AdvancedGrowthStrategies
    
    print("📈 Executing advanced growth strategies...")
    
    # Initialize growth strategies
    growth = AdvancedGrowthStrategies()
    
    print("💡 Generating content series ideas...")
    
    # Generate weekly content plan
    post_ideas = growth.generate_thought_leadership_post_ideas(10)
    community_strategy = growth.generate_community_engagement_strategy()
    content_series = growth.generate_content_series_ideas()
    
    # Save to cache for use by other automation
    growth_plan = {
        'generated_date': datetime.now().isoformat(),
        'post_ideas': post_ideas,
        'community_strategy': community_strategy,
        'content_series': content_series
    }
    
    with open('weekly_growth_plan.json', 'w') as f:
        json.dump(growth_plan, f, indent=2)
    
    print(f'✅ Generated {len(post_ideas)} post ideas')
    print(f'✅ Created strategy for {len(community_strategy)} communities')
    print(f'✅ Planned {len(content_series)} content series')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Unexpected error: {e}')
    sys.exit(1)