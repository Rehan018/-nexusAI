"""
Main LinkedIn Outreach Agent
Autonomous agent for reaching out to recruiters at target companies
"""
import os
import sys
from dotenv import load_dotenv
from src.linkedin_auth import LinkedInAuth
from src.profile_search import ProfileSearch
from src.outreach_handler import OutreachHandler
from src.resume_parser import ResumeParser
from src.gemini_client import GeminiClient
from src.rate_limiter import RateLimiter
from src.activity_logger import ActivityLogger
import config


def load_companies(file_path: str = "data/companies.txt"):
    """Load company list from file"""
    if not os.path.exists(file_path):
        print(f"❌ Companies file not found: {file_path}")
        print(f"Please create {file_path} with one company name per line.")
        return []
    
    with open(file_path, 'r') as f:
        companies = [line.strip() for line in f if line.strip()]
    
    return companies


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🤖 LinkedIn Autonomous Outreach Agent")
    print("=" * 60)
    print()


def print_summary(logger: ActivityLogger, rate_limiter: RateLimiter):
    """Print final summary"""
    print("\n" + "=" * 60)
    print("📊 OUTREACH SUMMARY")
    print("=" * 60)
    
    summary = logger.get_summary()
    rate_stats = rate_limiter.get_stats()
    
    print(f"\n✅ Total Actions: {summary['total_actions']}")
    print(f"🏢 Companies Contacted: {summary['companies_contacted']}")
    print(f"🤝 Connection Requests Sent: {summary['connections_sent']}")
    print(f"💬 Messages Sent: {summary['messages_sent']}")
    print(f"✔️  Successful Actions: {summary['successful_actions']}")
    print(f"❌ Failed Actions: {summary['failed_actions']}")
    
    print(f"\n📈 Rate Limit Status:")
    print(f"  Connections Remaining Today: {rate_stats['connections_remaining']}")
    print(f"  Messages Remaining Today: {rate_stats['messages_remaining']}")
    
    print("\n" + "=" * 60)


def main():
    """Main execution function"""
    # Load environment variables
    load_dotenv()
    
    print_banner()
    
    # Initialize components
    print("🔧 Initializing components...")
    
    try:
        # Check for resume
        resume_path = "data/resume.pdf"
        if not os.path.exists(resume_path):
            resume_path = "data/resume.txt"
            if not os.path.exists(resume_path):
                print("❌ Resume not found. Please add data/resume.pdf or data/resume.txt")
                return
        
        # Parse resume
        print("📄 Parsing resume...")
        resume_parser = ResumeParser(resume_path)
        resume_data = resume_parser.get_summary()
        print(f"  ✓ Extracted {len(resume_data['skills'])} skills")
        print(f"  ✓ Skills: {', '.join(resume_data['skills'][:5])}")
        
        # Initialize Gemini
        print("🤖 Initializing Gemini AI...")
        gemini = GeminiClient()
        print("  ✓ Gemini AI ready")
        
        # Initialize rate limiter
        rate_limiter = RateLimiter()
        stats = rate_limiter.get_stats()
        print(f"📊 Rate Limiter Status:")
        print(f"  Today: {stats['date']}")
        print(f"  Connections remaining: {stats['connections_remaining']}")
        print(f"  Messages remaining: {stats['messages_remaining']}")
        
        # Initialize activity logger
        logger = ActivityLogger()
        print("📝 Activity logger ready")
        
        # Load companies
        companies = load_companies()
        if not companies:
            return
        
        print(f"\n🎯 Targeting {len(companies)} companies:")
        for i, company in enumerate(companies, 1):
            print(f"  {i}. {company}")
        
        # Confirm before proceeding
        print("\n⚠️  WARNING: This will interact with LinkedIn on your behalf.")
        response = input("Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Cancelled by user")
            return
        
        # Initialize LinkedIn
        print("\n🌐 Connecting to LinkedIn...")
        linkedin = LinkedInAuth()
        linkedin.init_browser()
        
        if not linkedin.login():
            print("❌ Failed to login to LinkedIn")
            linkedin.close()
            return
        
        # Initialize search and outreach handlers
        searcher = ProfileSearch(linkedin.driver, linkedin.wait)
        outreach = OutreachHandler(linkedin.driver, linkedin.wait)
        
        # Process each company
        for company_idx, company in enumerate(companies, 1):
            print(f"\n{'='*60}")
            print(f"📍 Company {company_idx}/{len(companies)}: {company}")
            print(f"{'='*60}")
            
            # Check company stats
            company_stats = logger.get_company_stats(company)
            if company_stats['total_contacted'] > 0:
                print(f"ℹ️  Already contacted {company_stats['total_contacted']} people at {company}")
            
            # Search for recruiters
            profiles = searcher.search_recruiters(company, max_results=5, gemini_client=gemini)
            
            if not profiles:
                print(f"⚠️  No recruiters found at {company}")
                continue
            
            # Process each profile
            for profile_idx, profile in enumerate(profiles, 1):
                print(f"\n👤 Profile {profile_idx}/{len(profiles)}: {profile['name']}")
                
                # Check if already contacted
                # Smart Duplicate Check
                # 1. If we have already MESSAGED this person, we are done. Skip.
                if logger.is_duplicate(profile['profile_url'], action_type='message'):
                    print("  ⏭️  Already messaged, skipping...")
                    continue
                
                # 2. If we haven't messaged, we might need to send a message (if connected)
                #    or send a connection request (if not connected).
                #    We proceed to check status.
                
                # Check connection status
                connection_status = searcher.check_connection_status(profile['profile_url'])
                print(f"  Status: {connection_status}")
                
                # Granular Duplicate Check for Connection Requests
                if connection_status == 'not_connected':
                    if logger.is_duplicate(profile['profile_url'], action_type='connection_request'):
                        print("  ⏭️  Already sent connection request, skipping...")
                        continue
                
                # Decide action based on connection status and rate limits
                if connection_status == 'connected':
                    # Send message
                    if not rate_limiter.can_send_message():
                        print("  ⚠️  Daily message limit reached")
                        break
                    
                    # Generate personalized message
                    message = gemini.generate_message(
                        name=profile['name'],
                        company=company,
                        role=profile['role'],
                        skills=resume_data['skills'],
                        experience=resume_data['experience'],
                        resume_text=resume_data.get('full_text')
                    )
                    
                    print(f"  📧 Generated message preview: {message[:100]}...")
                    
                    # Send message
                    success = outreach.send_message(profile['profile_url'], message)
                    
                    if success:
                        rate_limiter.record_message()
                        logger.log_action(
                            company=company,
                            profile_url=profile['profile_url'],
                            name=profile['name'],
                            role=profile['role'],
                            connection_status='connected',
                            action_type='message',
                            message_sent=message,
                            status='success'
                        )
                    else:
                        logger.log_action(
                            company=company,
                            profile_url=profile['profile_url'],
                            name=profile['name'],
                            role=profile['role'],
                            connection_status='connected',
                            action_type='message',
                            message_sent=message,
                            status='failed'
                        )
                
                elif connection_status == 'not_connected':
                    # Send connection request
                    if not rate_limiter.can_send_connection():
                        print("  ⚠️  Daily connection limit reached")
                        break
                    
                    # Generate personalized note
                    note = gemini.generate_connection_note(
                        company=company,
                        role=profile['role'],
                        skills=resume_data['skills']
                    )
                    
                    print(f"  📤 Generated note: {note}")
                    
                    # Send connection request
                    success = outreach.send_connection_request(profile['profile_url'], note)
                    
                    if success:
                        rate_limiter.record_connection()
                        logger.log_action(
                            company=company,
                            profile_url=profile['profile_url'],
                            name=profile['name'],
                            role=profile['role'],
                            connection_status='not_connected',
                            action_type='connection_request',
                            message_sent=note,
                            status='success'
                        )
                    else:
                        logger.log_action(
                            company=company,
                            profile_url=profile['profile_url'],
                            name=profile['name'],
                            role=profile['role'],
                            connection_status='not_connected',
                            action_type='connection_request',
                            message_sent=note,
                            status='failed'
                        )
                
                elif connection_status == 'pending':
                    print("  ⏳ Connection already pending, skipping...")
                    logger.log_action(
                        company=company,
                        profile_url=profile['profile_url'],
                        name=profile['name'],
                        role=profile['role'],
                        connection_status='pending',
                        action_type='skipped',
                        message_sent='',
                        status='skipped'
                    )
                
                # Apply rate limiting delay
                rate_limiter.apply_delay()
                
                # Check if we've hit daily limits
                if not rate_limiter.can_send_connection() and not rate_limiter.can_send_message():
                    print("\n⚠️  Daily limits reached for both connections and messages")
                    break
            
            # Check if we should stop
            if not rate_limiter.can_send_connection() and not rate_limiter.can_send_message():
                print("\n⚠️  Stopping: Daily limits reached")
                break
        
        # Export logs
        print("\n📊 Exporting activity log...")
        logger.export_to_csv()
        
        # Close browser
        linkedin.close()
        
        # Print summary
        print_summary(logger, rate_limiter)
        
        print("\n✅ Outreach campaign completed!")
        print(f"📄 Check {config.LOG_CSV_PATH} for detailed logs")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        if 'linkedin' in locals():
            linkedin.close()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'linkedin' in locals():
            linkedin.close()


if __name__ == "__main__":
    main()
