
"""
Quick test to verify Groq API works
This script sends a fake security alert to Groq and gets a 5-step analysis
"""
import os
import json
import sys

# Add backend to path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the LLM Agent
from app.services.llm_agent import LLMAgent

# ============================================================
# STEP 1: Define a fake security alert
# ============================================================
test_alert = {
    "event_id": "evt_test_001",
    "timestamp": "2025-05-16T10:30:00Z",
    "event_type": "failed_ssh_login",
    "src_ip": "203.0.113.45",
    "dest_host": "prod-web-01",
    "username": "admin",
    "failed_attempts": 47,
    "time_window": "5 minutes"
}

# ============================================================
# STEP 2: Main test function
# ============================================================
def main():
    print("🧪 Testing Groq LLM Agent...")
    print("=" * 60)
    
    try:
        # Initialize Groq agent
        print("📥 Initializing Groq agent...")
        agent = LLMAgent(provider="groq")
        print("✅ Groq agent initialized\n")
        
        # Run 5-step analysis
        print("📊 Running 5-step analysis (this takes ~30-60 seconds)...\n")
        print("Please wait...\n")
        
        results = agent.analyze_alert_multi_step(test_alert)
        
        # ============================================================
        # STEP 3: Print results
        # ============================================================
        print("\n✅ Analysis Complete!\n")
        print("=" * 60)
        print("RESULTS:")
        print("=" * 60)
        
        # Step 1: Classification
        if "step_1_classification" in results:
            print("\n📋 Step 1: Classification")
            print("What type of attack is this?")
            print("-" * 60)
            classification = results.get("step_1_classification")
            print(json.dumps(classification, indent=2))
        
        # Step 2: Threat Assessment
        if "step_2_threat_assessment" in results:
            print("\n⚠️  Step 2: Threat Assessment")
            print("How serious is this attack?")
            print("-" * 60)
            threat = results.get("step_2_threat_assessment")
            print(json.dumps(threat, indent=2))
        
        # Step 3: Investigation Plan
        if "step_3_investigation_plan" in results:
            print("\n🔍 Step 3: Investigation Plan")
            print("What should we investigate?")
            print("-" * 60)
            investigation = results.get("step_3_investigation_plan")
            print(json.dumps(investigation, indent=2))
        
        # Step 4: Root Cause
        if "step_4_root_cause" in results:
            print("\n🎯 Step 4: Root Cause Analysis")
            print("Why did this happen?")
            print("-" * 60)
            root_cause = results.get("step_4_root_cause")
            print(json.dumps(root_cause, indent=2))
        
        # Step 5: Remediation
        if "step_5_remediation" in results:
            print("\n🛠️  Step 5: Remediation Strategy")
            print("How do we fix this?")
            print("-" * 60)
            remediation = results.get("step_5_remediation")
            print(json.dumps(remediation, indent=2))
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Provider: {results.get('provider').upper()}")
        print(f"Model: {results.get('model')}")
        print(f"Total steps completed: 5")
        print("=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nFull error traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# ============================================================
# STEP 4: Run the test
# ============================================================
if __name__ == "__main__":
    main()

