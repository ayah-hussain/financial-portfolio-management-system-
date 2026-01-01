import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = 'http://localhost:8000/api'  

class TestAPI:
    def __init__(self):
        self.token = None
        self.test_user = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }
        self.portfolio_id = None

    def run_all_tests(self):
        """Run all test methods in sequence"""
        try:
            # Authentication tests
            print("\n=== Running Authentication Tests ===")
            self.test_register()
            self.test_login()

            # Portfolio tests
            print("\n=== Running Portfolio Tests ===")
            self.test_create_portfolio()
            self.test_get_portfolios()
            self.test_get_portfolio_value()
            self.test_get_portfolio_performance()

            # Asset tests
            print("\n=== Running Asset Tests ===")
            self.test_get_available_assets()
            self.test_add_asset_to_portfolio()
            self.test_get_portfolio_assets()
            self.test_delete_asset_from_portfolio()

            # News tests
            print("\n=== Running News Tests ===")
            self.test_get_news()
            self.test_interact_with_news()

            # Profile tests
            print("\n=== Running Profile Tests ===")
            self.test_update_profile()
            self.test_change_password()

            # Investment simulation test
            print("\n=== Running Investment Simulation Test ===")
            self.test_simulate_investment()

            # Cleanup
            print("\n=== Running Cleanup ===")
            self.test_delete_portfolio()

            print("\n✅ All tests completed successfully!")

        except AssertionError as e:
            print(f"\n❌ Test failed: {str(e)}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")

    def _make_request(self, method, endpoint, data=None, params=None):
        """Helper method to make HTTP requests with authentication"""
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        url = f"{BASE_URL}/{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return response

    def test_register(self):
        """Test user registration"""
        print("Testing user registration...")
        response = self._make_request('POST', 'auth/register/', self.test_user)
        assert response.status_code == 200, f"Registration failed: {response.text}"
        print("✓ Registration successful")

    def test_login(self):
        """Test user login"""
        print("Testing user login...")
        credentials = {
            'username': self.test_user['username'],
            'password': self.test_user['password']
        }
        response = self._make_request('POST', 'auth/login/', credentials)
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()['token']
        print("✓ Login successful")

    def test_create_portfolio(self):
        """Test portfolio creation"""
        print("Testing portfolio creation...")
        data = {'portfolio_name': 'Test Portfolio'}
        response = self._make_request('POST', 'portfolios/', data)
        assert response.status_code == 200, f"Portfolio creation failed: {response.text}"
        self.portfolio_id = response.json()['portfolio_id']
        print("✓ Portfolio created successfully")

    def test_get_portfolios(self):
        """Test getting list of portfolios"""
        print("Testing get portfolios...")
        response = self._make_request('GET', 'portfolios/')
        assert response.status_code == 200, f"Get portfolios failed: {response.text}"
        portfolios = response.json()
        assert isinstance(portfolios, list), "Expected list of portfolios"
        print("✓ Retrieved portfolios successfully")

    def test_get_portfolio_value(self):
        """Test getting portfolio value"""
        print("Testing get portfolio value...")
        response = self._make_request('GET', f'portfolios/{self.portfolio_id}/value/')
        assert response.status_code == 200, f"Get portfolio value failed: {response.text}"
        data = response.json()
        assert 'total_value' in data, "Response missing total_value"
        print("✓ Retrieved portfolio value successfully")

    def test_get_portfolio_performance(self):
        """Test getting portfolio performance"""
        print("Testing get portfolio performance...")
        response = self._make_request('GET', f'portfolios/{self.portfolio_id}/performance/')
        assert response.status_code == 200, f"Get portfolio performance failed: {response.text}"
        data = response.json()
        assert 'performance_data' in data, "Response missing performance_data"
        print("✓ Retrieved portfolio performance successfully")

    def test_get_available_assets(self):
        """Test getting available assets"""
        print("Testing get available assets...")
        response = self._make_request('GET', 'assets/')
        assert response.status_code == 200, f"Get assets failed: {response.text}"
        data = response.json()
        assert 'assets' in data, "Response missing assets list"
        print("✓ Retrieved available assets successfully")

    def test_add_asset_to_portfolio(self):
        """Test adding asset to portfolio"""
        print("Testing add asset to portfolio...")
        data = {
            'ticker': 'AAPL',  # Assuming AAPL exists in your assets table
            'quantity': 10,
            'purchase_price': 150.00
        }
        response = self._make_request('POST', f'portfolios/{self.portfolio_id}/assets/', data)
        assert response.status_code == 200, f"Add asset failed: {response.text}"
        print("✓ Added asset to portfolio successfully")

    def test_get_portfolio_assets(self):
        """Test getting portfolio assets"""
        print("Testing get portfolio assets...")
        response = self._make_request('GET', f'portfolios/{self.portfolio_id}/assets/')
        assert response.status_code == 200, f"Get portfolio assets failed: {response.text}"
        data = response.json()
        assert 'assets' in data, "Response missing assets"
        print("✓ Retrieved portfolio assets successfully")

    def test_delete_asset_from_portfolio(self):
        """Test deleting asset from portfolio"""
        print("Testing delete asset from portfolio...")
        response = self._make_request('DELETE', f'portfolios/{self.portfolio_id}/assets/AAPL/')
        assert response.status_code == 200, f"Delete asset failed: {response.text}"
        print("✓ Deleted asset from portfolio successfully")

    def test_get_news(self):
        """Test getting news"""
        print("Testing get news...")
        response = self._make_request('GET', 'news/')
        assert response.status_code == 200, f"Get news failed: {response.text}"
        data = response.json()
        assert 'news' in data, "Response missing news"
        print("✓ Retrieved news successfully")

    def test_interact_with_news(self):
        """Test interacting with news"""
        print("Testing news interaction...")
        # Get first news article ID
        news_response = self._make_request('GET', 'news/')
        news_id = news_response.json()['news'][0]['id']
        
        data = {
            'sentiment': 'Positive',
            'comment': 'Test comment'
        }
        response = self._make_request('POST', f'news/{news_id}/interact/', data)
        assert response.status_code == 200, f"News interaction failed: {response.text}"
        print("✓ News interaction successful")

    def test_update_profile(self):
        """Test updating user profile"""
        print("Testing profile update...")
        data = {
            'email': 'updated@example.com'
        }
        response = self._make_request('PUT', 'auth/profile/', data)
        assert response.status_code == 200, f"Profile update failed: {response.text}"
        print("✓ Profile updated successfully")

    def test_change_password(self):
        """Test changing password"""
        print("Testing password change...")
        data = {
            'current_password': self.test_user['password'],
            'new_password': 'newpass123'
        }
        response = self._make_request('POST', 'auth/change-password/', data)
        assert response.status_code == 200, f"Password change failed: {response.text}"
        self.test_user['password'] = 'newpass123'
        print("✓ Password changed successfully")

    def test_simulate_investment(self):
        """Test investment simulation"""
        print("Testing investment simulation...")
        data = {
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'asset_allocation': {
                'AAPL': 50,
                'GOOGL': 50
            },
            'monthly_budget': 1000
        }
        response = self._make_request('POST', 'simulate-investment/', data)
        assert response.status_code == 200, f"Investment simulation failed: {response.text}"
        data = response.json()
        assert 'simulation_data' in data, "Response missing simulation data"
        print("✓ Investment simulation successful")

    def test_delete_portfolio(self):
        """Test portfolio deletion"""
        print("Testing portfolio deletion...")
        response = self._make_request('DELETE', f'portfolios/{self.portfolio_id}/')
        assert response.status_code == 200, f"Portfolio deletion failed: {response.text}"
        print("✓ Portfolio deleted successfully")


if __name__ == '__main__':
    # Create and run test suite
    test_suite = TestAPI()
    test_suite.run_all_tests() 