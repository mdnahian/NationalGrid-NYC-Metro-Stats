#!/usr/bin/env python3
"""
Simplified National Grid Metro NYC energy data retrieval script.
Usage: python3 nationalgridmetro.py username password
Returns: JSON with energy usage and cost data
"""

import asyncio
import aiohttp
import json
import sys
import os
import base64
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

class NationalGridMetroClient:
    def __init__(self):
        self.subdomain = "ngny-gas"
        self.base_url = f"https://{self.subdomain}.opower.com"
        self.auth_url = "https://myaccount.nationalgrid.com"
        self.tokens = None
        self.customer_urn = None
        self.token_cache_dir = os.path.expanduser("~/.ngnycmetro")
        self.token_file = os.path.join(self.token_cache_dir, "tokens.json")

    def ensure_cache_dir(self):
        """Ensure the token cache directory exists."""
        if not os.path.exists(self.token_cache_dir):
            os.makedirs(self.token_cache_dir, mode=0o700)

    def is_token_expired(self, token):
        """Check if a JWT token is expired."""
        try:
            # JWT tokens have 3 parts separated by dots
            parts = token.split('.')
            if len(parts) != 3:
                return True
            
            # Decode the payload (second part)
            payload = parts[1]
            # Add padding if needed for base64 decoding
            payload += '=' * (4 - len(payload) % 4)
            
            decoded = base64.b64decode(payload)
            payload_data = json.loads(decoded)
            
            # Check expiration time (exp field is in seconds since epoch)
            exp_timestamp = payload_data.get('exp')
            if not exp_timestamp:
                return True
            
            # Add a 5-minute buffer to avoid using tokens that expire very soon
            current_time = datetime.now().timestamp()
            return current_time >= (exp_timestamp - 300)  # 5 minutes buffer
            
        except Exception:
            # If we can't decode the token, consider it expired
            return True

    def save_tokens(self, tokens):
        """Save tokens to cache file."""
        try:
            self.ensure_cache_dir()
            cache_data = {
                'tokens': tokens,
                'saved_at': datetime.now().isoformat(),
                'customer_urn': self.customer_urn
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            # Set secure permissions
            os.chmod(self.token_file, 0o600)
            return True
        except Exception as e:
            print(f"Warning: Could not save tokens: {e}", file=sys.stderr)
            return False

    def load_tokens(self):
        """Load tokens from cache file if they exist and are valid."""
        try:
            if not os.path.exists(self.token_file):
                return None
            
            with open(self.token_file, 'r') as f:
                cache_data = json.load(f)
            
            tokens = cache_data.get('tokens', {})
            access_token = tokens.get('access_token')
            
            if not access_token:
                return None
            
            # Check if token is expired
            if self.is_token_expired(access_token):
                # Clean up expired token
                try:
                    os.remove(self.token_file)
                except:
                    pass
                return None
            
            # Token is valid, restore state
            self.tokens = tokens
            self.customer_urn = cache_data.get('customer_urn')
            
            return {
                'success': True,
                'source': 'cache',
                'saved_at': cache_data.get('saved_at')
            }
            
        except Exception as e:
            # If there's any error reading the cache, remove it and continue with fresh login
            try:
                os.remove(self.token_file)
            except:
                pass
            return None

    async def login_and_get_tokens(self, username: str, password: str):
        """Automated login using browser automation to get tokens."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = await context.new_page()
                
                # Clear any existing session to ensure fresh login
                await context.clear_cookies()
                
                # Navigate to login page (use actual login URL)
                login_url = f"{self.auth_url}/login"
                await page.goto(login_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(5000)
                
                # Wait for and fill username
                await page.wait_for_selector('#signInName', timeout=20000)
                await page.fill('#signInName', username)
                
                # Wait for and fill password
                await page.wait_for_selector('#password', timeout=10000)
                await page.fill('#password', password)
                
                # Submit form using multiple approaches (like the working script)
                submitted = False
                
                # Try to find submit button by text
                submit_selector = await page.query_selector('button:has-text("Sign in")') or \
                                await page.query_selector('button:has-text("Log in")') or \
                                await page.query_selector('button:has-text("Submit")') or \
                                await page.query_selector('input[type="submit"]') or \
                                await page.query_selector('button[type="submit"]')
                
                if submit_selector:
                    await submit_selector.click()
                    submitted = True
                else:
                    # Fallback: Press Enter in password field
                    await page.press('#password', 'Enter')
                    submitted = True
                
                if not submitted:
                    return {"success": False, "error": "Could not submit login form"}
                
                # Wait for login completion (wait for redirect to myaccount)
                await page.wait_for_url("**/myaccount.nationalgrid.com/**", timeout=30000)
                
                # Navigate to energy page to trigger opower authentication
                await page.goto(f"{self.auth_url}/Energy", wait_until='networkidle')
                await page.wait_for_timeout(5000)
                
                # Extract MSAL tokens from browser storage
                msal_data = await page.evaluate("""
                    () => {
                        const allData = {};
                        
                        // Check localStorage
                        for (let i = 0; i < localStorage.length; i++) {
                            const key = localStorage.key(i);
                            allData[key] = localStorage.getItem(key);
                        }
                        
                        // Check sessionStorage
                        for (let i = 0; i < sessionStorage.length; i++) {
                            const key = sessionStorage.key(i);
                            allData['session_' + key] = sessionStorage.getItem(key);
                        }
                        
                        return allData;
                    }
                """)
                
                await browser.close()
                
                # Extract access token from MSAL data - more comprehensive search
                access_token = None
                
                # Look for access token in various formats
                for key, value in msal_data.items():
                    if not value:
                        continue
                        
                    # Check for sessionStorage access tokens with long prefixes
                    if 'session_' in key and 'accesstoken' in key.lower():
                        try:
                            token_data = json.loads(value)
                            access_token = token_data.get('secret')
                            if access_token:
                                break
                        except:
                            continue
                    
                    # Check for MSAL access tokens
                    if 'accesstoken' in key.lower() and ('opower' in key.lower() or 'nationalgrid' in key.lower()):
                        try:
                            token_data = json.loads(value)
                            access_token = token_data.get('secret')
                            if access_token:
                                break
                        except:
                            continue
                    
                    # Check for direct token values
                    if 'access_token' in key.lower():
                        try:
                            if value.startswith('{'):
                                token_data = json.loads(value)
                                access_token = token_data.get('access_token') or token_data.get('secret')
                            else:
                                access_token = value
                            if access_token:
                                break
                        except:
                            continue
                    
                    # Check for Bearer tokens in any value
                    if isinstance(value, str) and value.startswith('ey') and len(value) > 100:
                        access_token = value
                        break
                
                if not access_token:
                    # Debug output to see what tokens we found
                    debug_info = {}
                    for key, value in msal_data.items():
                        if value and ('token' in key.lower() or 'auth' in key.lower() or 'msal' in key.lower()):
                            debug_info[key] = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    
                    return {"success": False, "error": "Failed to extract access token", "debug": debug_info}
                
                self.tokens = {"access_token": access_token}
                
                # Save tokens to cache
                self.save_tokens(self.tokens)
                
                return {"success": True, "source": "fresh_login"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_customer_data(self):
        """Get customer information including URN."""
        try:
            headers = {
                'Authorization': f'Bearer {self.tokens["access_token"]}',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/ei/edge/apis/multi-account-v1/cws/ngbk/customers/current",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Handle the actual response format - it's a single customer object
                        if isinstance(data, dict) and 'uuid' in data:
                            # Extract customer URN from uuid
                            self.customer_urn = f"urn:opower:customer:uuid:{data['uuid']}"
                            
                            # Update cache with customer URN
                            if self.tokens:
                                self.save_tokens(self.tokens)
                            
                            return {"success": True, "customer": data}
                        # Fallback: check if it's in a results array
                        elif isinstance(data, dict) and 'results' in data and len(data['results']) > 0:
                            customer = data['results'][0]
                            self.customer_urn = customer.get('urn') or f"urn:opower:customer:uuid:{customer.get('uuid')}"
                            
                            # Update cache with customer URN
                            if self.tokens:
                                self.save_tokens(self.tokens)
                            
                            return {"success": True, "customer": customer}
                        else:
                            return {"success": False, "error": "Unexpected customer data format", "data": data}
                    
                    return {"success": False, "error": f"HTTP {resp.status}", "details": await resp.text()}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_usage_and_cost_data(self):
        """Get energy usage and cost data using GraphQL."""
        if not self.customer_urn:
            return {"success": False, "error": "Customer URN not available"}
        
        try:
            # Calculate time interval (last 2 years) with proper timezone format like HAR file
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)
            # Format like HAR file: "2019-08-05T00:00:00-04:00/2025-07-17T22:02:26-04:00"
            time_interval = f"{start_date.strftime('%Y-%m-%dT00:00:00-04:00')}/{end_date.strftime('%Y-%m-%dT23:59:59-04:00')}"
            
            # Use the exact working GraphQL query from the HAR file
            graphql_query = {
                "operationName": "WDB_GetCostUsageReadsForBills",
                "variables": {
                    "resolution": "BILL",
                    "timeInterval": time_interval,
                    "last": 78,
                    "aliased": False,
                    "forceLegacyData": True,
                    "customerURN": self.customer_urn,
                    "locale": "en-US"
                },
                "query": """
                query WDB_GetCostUsageReadsForBills($customerURN: ID, $last: Int, $timeInterval: TimeInterval, $forceLegacyData: Boolean, $aliased: Boolean) {
                  billingAccountByAuthContext(
                    singlePremise: $customerURN
                    forceLegacyData: $forceLegacyData
                  ) {
                    urn
                    bills(
                      last: $last
                      during: $timeInterval
                      orderBy: ASCENDING
                      preserveDuplicateSegments: true
                    ) {
                      urn
                      timeInterval
                      segments {
                        urn
                        usageInterval
                        serviceAgreement(aliased: $aliased) {
                          urn
                          uuid
                          serviceType
                          __typename
                        }
                        estimated
                        serviceQuantities {
                          unit
                          serviceQuantityIdentifier
                          serviceQuantity {
                            value
                            __typename
                          }
                          __typename
                        }
                        usageCharges {
                          value
                          __typename
                        }
                        currentAmount {
                          value
                          __typename
                        }
                        deferredNEMCharges {
                          value
                          __typename
                        }
                        totalNEMCharges {
                          value
                          __typename
                        }
                        energyPurchased {
                          value
                          __typename
                        }
                        energySold {
                          value
                          __typename
                        }
                        rolloverBalanceEarned {
                          value
                          __typename
                        }
                        rolloverBalanceUsed {
                          value
                          __typename
                        }
                        totalEnergyCosts {
                          value
                          __typename
                        }
                        __typename
                      }
                      __typename
                    }
                    __typename
                  }
                }
                """
            }
            
            headers = {
                'Authorization': f'Bearer {self.tokens["access_token"]}',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/ei/edge/apis/dsm-graphql-v1/cws/graphql",
                    headers=headers,
                    json=graphql_query
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self.process_usage_data(data)
                    else:
                        return {"success": False, "error": f"HTTP {resp.status}", "details": await resp.text()}
                        
        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_usage_data(self, graphql_response):
        """Process GraphQL response into structured usage and cost data."""
        try:
            billing_account = graphql_response.get('data', {}).get('billingAccountByAuthContext', {})
            bills = billing_account.get('bills', [])
            
            if not bills:
                # Debug: Show what we actually got
                return {
                    "success": False, 
                    "error": "No bills data found",
                    "debug": {
                        "has_data": 'data' in graphql_response,
                        "has_billing_account": bool(billing_account),
                        "bills_count": len(bills),
                        "full_response": graphql_response
                    }
                }
            
            # Process bills with the actual HAR file structure
            usage_over_time = []
            cost_over_time = []
            total_usage = 0
            total_cost = 0
            current_month_data = None
            current_month = datetime.now().strftime('%Y-%m')
            
            # Process each bill
            for bill in bills:
                time_interval = bill.get('timeInterval', '')
                segments = bill.get('segments', [])
                
                # Extract time info from timeInterval (format: "2024-06-01T00:00:00-04:00/2024-06-28T23:59:59-04:00")
                start_date = None
                end_date = None
                if '/' in time_interval:
                    start_date, end_date = time_interval.split('/')
                
                # Process segments to get usage and cost data
                bill_usage = 0
                bill_cost = 0
                usage_unit = "therms"
                cost_unit = "USD"
                
                for segment in segments:
                    # Get service quantities (usage data)
                    service_quantities = segment.get('serviceQuantities', [])
                    for sq in service_quantities:
                        unit = sq.get('unit', '')
                        service_quantity = sq.get('serviceQuantity', {})
                        value = service_quantity.get('value', 0)
                        identifier = sq.get('serviceQuantityIdentifier', '')
                        
                        # Match various unit formats for therms
                        if unit and (unit.upper() == 'TH' or 'therm' in unit.lower()):
                            bill_usage += value if value else 0
                            usage_unit = 'therms'  # Standardize to 'therms'
                        elif identifier and ('NET_USAGE' in identifier or 'therm' in identifier.lower()):
                            bill_usage += value if value else 0
                            usage_unit = 'therms'
                        elif unit and ('gas' in unit.lower() or 'cubic' in unit.lower()):
                            bill_usage += value if value else 0
                            usage_unit = unit
                    
                    # Get usage charges (cost data)
                    usage_charges = segment.get('usageCharges', {})
                    if usage_charges and 'value' in usage_charges:
                        bill_cost += usage_charges.get('value', 0)
                    
                    # Also check currentAmount for cost
                    current_amount = segment.get('currentAmount', {})
                    if current_amount and 'value' in current_amount:
                        bill_cost += current_amount.get('value', 0)
                
                period_data = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "usage_amount": bill_usage,
                    "usage_unit": usage_unit,
                    "cost_amount": bill_cost,
                    "cost_unit": cost_unit,
                    "time_interval": time_interval
                }
                
                usage_over_time.append(period_data)
                cost_over_time.append(period_data)
                
                total_usage += bill_usage
                total_cost += bill_cost
                
                # Check if this is current month
                if start_date and start_date.startswith(current_month):
                    current_month_data = period_data
            
            # Calculate current month estimate if we have partial data
            current_month_estimate = None
            if current_month_data:
                current_month_estimate = {
                    "partial_usage": current_month_data["usage_amount"],
                    "partial_cost": current_month_data["cost_amount"],
                    "billing_period": current_month_data
                }
            
            return {
                "success": True,
                "data": {
                    "usage_over_time": usage_over_time,
                    "cost_over_time": cost_over_time,
                    "current_month_estimate": current_month_estimate,
                    "summary": {
                        "total_usage": total_usage,
                        "total_cost": total_cost,
                        "number_of_bills": len(bills),
                        "usage_unit": usage_unit,
                        "cost_unit": cost_unit
                    }
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to process usage data: {str(e)}"}

async def main():
    """Main function - entry point for the script."""
    if len(sys.argv) != 3:
        print(json.dumps({"success": False, "error": "Usage: python3 nationalgridmetro.py username password"}))
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    client = NationalGridMetroClient()
    
    # Step 1: Check for existing valid tokens
    cached_result = client.load_tokens()
    if cached_result:
        # We have valid cached tokens, skip login
        print(f"# Using cached tokens from {cached_result.get('saved_at')}", file=sys.stderr)
        
        # If we don't have customer URN, we need to get it
        if not client.customer_urn:
            customer_result = await client.get_customer_data()
            if not customer_result["success"]:
                # If customer data fails, maybe token is invalid, try fresh login
                print("# Cached token seems invalid, attempting fresh login", file=sys.stderr)
                cached_result = None
    
    # Step 2: If no valid cache, do fresh login
    if not cached_result:
        login_result = await client.login_and_get_tokens(username, password)
        if not login_result["success"]:
            print(json.dumps(login_result))
            sys.exit(1)
        
        print(f"# Fresh login completed", file=sys.stderr)
        
        # Get customer data after fresh login
        customer_result = await client.get_customer_data()
        if not customer_result["success"]:
            print(json.dumps(customer_result))
            sys.exit(1)
    
    # Step 3: Get usage and cost data
    usage_result = await client.get_usage_and_cost_data()
    print(json.dumps(usage_result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
