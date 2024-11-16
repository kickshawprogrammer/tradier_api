from tradier_api import LiveConfig, TradierApiController, Endpoints
from _import_token import API_TOKEN as TRADIER_API_TOKEN

def get_user_profile():
    # Initialize the API configuration and controller
    config = LiveConfig(token=TRADIER_API_TOKEN)
    api_controller = TradierApiController(config)
    
    # Fetch user profile data
    user_profile = api_controller.make_request(endpoint=Endpoints.GET_PROFILE)
    
    # Print user profile details
    print("User Profile:")
    for key, value in user_profile.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    get_user_profile()
