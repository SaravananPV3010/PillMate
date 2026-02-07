#!/usr/bin/env python3

import requests
import json
import base64
import sys
from pathlib import Path
from datetime import datetime
import time

class PillGuideAPITester:
    def __init__(self):
        self.base_url = "https://pill-guide-1.preview.emergentagent.com/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, status, message="", response_data=None):
        """Log test results"""
        self.tests_run += 1
        if status:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED - {message}")
        
        self.test_results.append({
            "test": name,
            "status": "PASSED" if status else "FAILED", 
            "message": message,
            "response_data": response_data
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"  URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            print(f"  Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            response_json = {}
            
            try:
                response_json = response.json() if response.content else {}
            except:
                response_json = {"raw_response": response.text}

            if success:
                self.log_test(name, True, f"Status: {response.status_code}", response_json)
                return True, response_json
            else:
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}", response_json)
                return False, response_json

        except requests.exceptions.Timeout:
            self.log_test(name, False, "Request timeout (30s)")
            return False, {"error": "timeout"}
        except Exception as e:
            self.log_test(name, False, f"Request error: {str(e)}")
            return False, {"error": str(e)})

    def create_test_prescription_image(self):
        """Create a base64 encoded test image simulating a prescription"""
        # Create a simple test image as base64 (a small PNG)
        # This is a minimal 1x1 white PNG pixel
        test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        return test_image_b64

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )

    def test_upload_prescription_endpoint(self):
        """Test prescription upload with test image"""
        print("\n📸 Testing prescription upload with base64 image...")
        
        test_data = {
            "image_base64": self.create_test_prescription_image(),
            "patient_id": "test-patient-001"
        }
        
        # This test might take longer due to AI processing
        return self.run_test(
            "Upload Prescription (AI Processing)",
            "POST", 
            "prescriptions/upload",
            200,
            test_data
        )

    def test_get_prescriptions(self):
        """Test getting all prescriptions"""
        return self.run_test(
            "Get All Prescriptions",
            "GET",
            "prescriptions",
            200
        )

    def test_add_manual_medication(self):
        """Test adding medication manually"""
        test_medication = {
            "name": "Test Metformin",
            "dosage": "500mg", 
            "frequency": "Twice daily",
            "timing": ["morning", "evening"],
            "duration": "30 days",
            "with_food": True
        }
        
        return self.run_test(
            "Add Manual Medication (AI Processing)",
            "POST",
            "medications", 
            200,
            test_medication
        )

    def test_get_medications(self):
        """Test getting all medications"""
        return self.run_test(
            "Get All Medications",
            "GET",
            "medications",
            200
        )

    def test_contraindication_check(self):
        """Test contraindication checking"""
        test_data = {
            "medication_name": "Aspirin",
            "current_medications": ["Warfarin", "Ibuprofen"]
        }
        
        return self.run_test(
            "Check Contraindications (AI Processing)",
            "POST",
            "contraindications/check",
            200,
            test_data
        )

    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 60)
        print("🧪 PILLGUIDE API TESTING STARTED")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        
        # Test basic connectivity
        success, _ = self.test_root_endpoint()
        if not success:
            print("❌ Root endpoint failed - stopping tests")
            return self.generate_report()

        # Test core functionality
        self.test_get_prescriptions()
        self.test_get_medications()
        
        # Test AI-powered endpoints (might be slower)
        print("\n🤖 Testing AI-powered endpoints (may take longer)...")
        
        # Add a manual medication first
        med_success, med_response = self.test_add_manual_medication()
        if med_success:
            print(f"  Medication added with ID: {med_response.get('id', 'unknown')}")
        
        # Test prescription upload
        upload_success, upload_response = self.test_upload_prescription_endpoint()
        if upload_success:
            print(f"  Prescription processed with {len(upload_response.get('medications', []))} medications")
        
        # Test contraindication check
        self.test_contraindication_check()
        
        return self.generate_report()

    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 60)
        print("📊 PILLGUIDE API TEST REPORT")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "No tests run")
        
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"  {status_icon} {result['test']}: {result['status']}")
            if result["message"]:
                print(f"    📝 {result['message']}")
        
        # Check for critical failures
        critical_endpoints = ["Root Endpoint", "Get All Prescriptions", "Get All Medications"]
        critical_failures = [r for r in self.test_results if r['test'] in critical_endpoints and r['status'] == 'FAILED']
        
        if critical_failures:
            print(f"\n⚠️  CRITICAL: {len(critical_failures)} essential endpoint(s) failing")
            return False
        
        ai_endpoints = ["Upload Prescription (AI Processing)", "Add Manual Medication (AI Processing)", "Check Contraindications (AI Processing)"]
        ai_failures = [r for r in self.test_results if r['test'] in ai_endpoints and r['status'] == 'FAILED']
        
        if ai_failures:
            print(f"\n🤖 WARNING: {len(ai_failures)} AI endpoint(s) failing - check API key and integration")
        
        return self.tests_passed >= (self.tests_run * 0.6)  # 60% pass rate minimum

def main():
    """Main test execution"""
    tester = PillGuideAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())