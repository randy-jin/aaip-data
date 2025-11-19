"""
Seed sample success stories for testing
Run this once to populate the database with example stories
"""

import psycopg2
from datetime import date, timedelta
import random

# Sample data
SAMPLE_STORIES = [
    {
        'story_type': 'nomination',
        'aaip_stream': 'Express Entry',
        'timeline_submitted': date(2024, 1, 15),
        'timeline_nominated': date(2024, 4, 20),
        'noc_code': '21232',
        'crs_score': 465,
        'work_permit_type': 'LIMA',
        'city': 'Calgary',
        'story_text': '''I applied through the Express Entry stream in January 2024 with a CRS score of 465. 
        
The entire process was smoother than I expected. I made sure all my documents were ready before applying - LIMA letter from my employer, job description matching my NOC, and all proof of funds.

The key was having a strong employer support letter that clearly explained why they needed me specifically. After submitting my EOI, I received my nomination in about 95 days, which aligned with the processing times at that time.

My advice: Don't wait to prepare documents. Have everything ready so you can submit immediately after receiving your nomination.''',
        'tips': '''1. Prepare all documents beforehand
2. Get a detailed support letter from your employer
3. Make sure your job duties match your NOC code exactly
4. Keep checking the AAIP portal regularly for updates
5. Consider hiring an immigration consultant if you're unsure''',
        'challenges': '''The hardest part was the waiting period. It felt like forever, but staying patient and not constantly checking for updates helped my mental health. Also, coordinating with my employer for additional documents during the process required good communication.''',
        'author_name': 'Anonymous',
        'is_anonymous': True
    },
    {
        'story_type': 'pr_approval',
        'aaip_stream': 'AOS',
        'timeline_submitted': date(2023, 8, 10),
        'timeline_nominated': date(2024, 1, 25),
        'timeline_pr_approved': date(2024, 9, 15),
        'noc_code': '63200',
        'crs_score': 388,
        'work_permit_type': 'LIMA',
        'city': 'Edmonton',
        'story_text': '''Applied through AOS stream as a cook at a restaurant in Edmonton. The journey from application to PR took about 13 months total.

I had been working with my employer for 2 years before applying, which I think helped a lot. They were very supportive throughout the process and provided all necessary documentation quickly.

After receiving the nomination in January, I applied for PR immediately. The federal processing took about 8 months. Finally got my COPR in September!

One thing that surprised me was how important it was to maintain legal status throughout. I renewed my work permit proactively to avoid any gaps.''',
        'tips': '''- Maintain good relationship with your employer
- Keep all employment records organized
- Apply for BOWP as soon as you get nomination
- Don't change jobs after applying (unless absolutely necessary)
- Join online communities for support and updates''',
        'challenges': '''The biggest challenge was the uncertainty and long wait times. There were periods of no updates for months. I also had to renew my work permit during the process, which added stress. Financial planning was crucial - make sure you have savings for unexpected expenses.''',
        'author_name': 'Sarah M.',
        'is_anonymous': False
    },
    {
        'story_type': 'nomination',
        'aaip_stream': 'Dedicated Healthcare',
        'timeline_submitted': date(2024, 3, 5),
        'timeline_nominated': date(2024, 5, 15),
        'noc_code': '31301',
        'crs_score': 420,
        'work_permit_type': 'LMIA-exempt',
        'city': 'Calgary',
        'story_text': '''As a registered nurse in Calgary, I applied through the DHCP stream. The healthcare stream is prioritized, and I experienced this firsthand with a relatively quick nomination - just 71 days!

The key requirements were clear: valid LIMA, working in healthcare in Alberta, and meeting the CRS threshold. I made sure my employer letter explicitly stated my role and responsibilities.

What helped: My employer is a large healthcare facility familiar with AAIP applications, so they knew exactly what documentation was needed. They provided everything in a timely manner.

Currently waiting for PR approval from IRCC (about 4 months in), but having the provincial nomination adds 600 points to your CRS, so I'm confident.''',
        'tips': '''Healthcare workers: Take advantage of the DHCP stream! Processing is faster.
- Ensure your nursing license is up to date
- Get detailed employer documentation
- Network with others who've gone through the process
- Consider joining Alberta nursing associations''',
        'challenges': '''Work-life balance during the application process was tough. Nursing is demanding, and managing paperwork alongside 12-hour shifts was exhausting. I scheduled dedicated time each week just for immigration tasks.''',
        'author_name': 'Anonymous',
        'is_anonymous': True
    },
    {
        'story_type': 'job_offer',
        'aaip_stream': 'Accelerated Tech',
        'timeline_submitted': date(2024, 6, 1),
        'timeline_nominated': date(2024, 7, 20),
        'noc_code': '21232',
        'crs_score': 495,
        'work_permit_type': 'LIMA',
        'city': 'Calgary',
        'story_text': '''Software developer here! Got a job offer from a Calgary tech company and applied through the Accelerated Tech pathway. 

The tech stream is relatively new but incredibly efficient. My employer was already approved as a designated employer, which sped things up significantly.

From job offer to work permit approval took about 4 months. Then after 6 months of working, I submitted my AAIP application. Nomination came in 49 days - fastest among my colleagues!

Alberta's tech scene is growing rapidly. If you're in tech and considering Canada, definitely look at the Alberta Accelerated Tech pathway.''',
        'tips': '''- Check if your employer is a designated tech employer
- Have at least 12 months of experience in your field
- Keep your GitHub/portfolio updated
- Network at Calgary and Edmonton tech meetups
- Consider remote work options if you're not in AB yet''',
        'challenges': '''Relocating from another province to Alberta meant finding housing quickly. Calgary's market is competitive. Also, understanding the difference between federal and provincial requirements took some research. Use official government websites!''',
        'author_name': 'Dev_Mike',
        'is_anonymous': False
    },
    {
        'story_type': 'settlement',
        'aaip_stream': 'Rural Renewal',
        'timeline_submitted': date(2023, 5, 15),
        'timeline_nominated': date(2023, 9, 10),
        'timeline_pr_approved': date(2024, 5, 20),
        'noc_code': '13201',
        'crs_score': 350,
        'work_permit_type': 'LIMA',
        'city': 'Red Deer',
        'story_text': '''We moved to a rural community in Alberta through the Rural Renewal stream. This pathway is perfect for those willing to live and work outside major cities.

The community endorsement process was unique but straightforward. Local economic development officers were incredibly helpful and supportive. They understand the program well and genuinely want to help newcomers settle.

Nominated in about 4 months, PR in total about 12 months from nomination. Now we've been here for over a year as permanent residents.

Life in rural Alberta is different but wonderful. Lower cost of living, tight-knit community, and beautiful landscapes. The kids love it here!''',
        'tips': '''- Visit the community before committing if possible
- Engage with local organizations early
- Understand the settlement requirements (must stay in the community)
- Join community Facebook groups for local info
- Prepare for winter weather if you're from a warm climate!''',
        'challenges': '''Adjusting to small-town life after living in a big city was the biggest challenge. Limited shopping options, need a car for everything, and finding social circles took time. However, the community is welcoming, and we've made great friends. The financial stability and PR status made it all worth it.''',
        'author_name': 'Anonymous',
        'is_anonymous': True
    },
    {
        'story_type': 'nomination',
        'aaip_stream': 'Tourism and Hospitality',
        'timeline_submitted': date(2024, 2, 20),
        'timeline_nominated': date(2024, 6, 5),
        'noc_code': '62020',
        'crs_score': 375,
        'work_permit_type': 'LIMA',
        'city': 'Banff',
        'story_text': '''Working in Banff's hospitality industry, I applied through the Tourism and Hospitality stream. 

Banff is a unique case - high tourism demand but also high competition for AAIP. My employer (a hotel) was very experienced with LIMA applications and provincial nominations.

The key was demonstrating genuine need for my role and my qualifications. I had 3 years of hotel management experience and specific certifications that made my case strong.

Nomination took about 105 days. Now awaiting PR approval but confident with the provincial support.''',
        'tips': '''- Tourism workers: timing matters! Apply during peak season when employer need is clearest
- Get certifications relevant to your role (First Aid, Food Safety, etc.)
- Document your achievements and contributions to the business
- Consider year-round positions over seasonal for stronger applications''',
        'challenges': '''Seasonal nature of tourism work in Alberta was tricky. Had to prove my position was permanent, not seasonal. Make sure your job offer letter specifies "permanent, full-time" clearly. Also, cost of living in Banff is HIGH - budget accordingly!''',
        'author_name': 'Anonymous',
        'is_anonymous': True
    }
]

def seed_success_stories():
    """Seed the database with sample success stories"""
    try:
        conn = psycopg2.connect(
            database='aaip_data',
            user='postgres',
            password='postgres',
            host='localhost'
        )
        cursor = conn.cursor()
        
        print("🌱 Seeding success stories...")
        
        for story in SAMPLE_STORIES:
            cursor.execute("""
                INSERT INTO success_stories (
                    story_type, aaip_stream, timeline_submitted, timeline_nominated,
                    timeline_pr_approved, noc_code, crs_score, work_permit_type, city,
                    story_text, tips, challenges, author_name, is_anonymous, status,
                    approved_at, approved_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'approved', NOW(), 'system')
            """, (
                story['story_type'],
                story['aaip_stream'],
                story['timeline_submitted'],
                story.get('timeline_nominated'),
                story.get('timeline_pr_approved'),
                story.get('noc_code'),
                story.get('crs_score'),
                story.get('work_permit_type'),
                story.get('city'),
                story['story_text'],
                story.get('tips'),
                story.get('challenges'),
                story['author_name'],
                story['is_anonymous']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Successfully seeded {len(SAMPLE_STORIES)} success stories!")
        print("\n📊 Stories by stream:")
        streams = {}
        for story in SAMPLE_STORIES:
            stream = story['aaip_stream']
            streams[stream] = streams.get(stream, 0) + 1
        for stream, count in streams.items():
            print(f"  - {stream}: {count}")
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")

if __name__ == "__main__":
    seed_success_stories()
