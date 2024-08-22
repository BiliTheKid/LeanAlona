from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import re
from models.user import UserState
from helpers.helpers import (
    send_message_non, get_template_sender, TemplateSender, send_message_gen,
    send_message_name_hotel, get_message_sender, send_message_name_identification,
    send_message_name_id, send_message_place, send_message_ppl, send_message_reset,
    send_message_confim, is_israeli_id_number, send_message_name_id_error, find_best_settlement_match,
    send_message_correct_place, send_message_approve_place, get_settlement_code, process_user_state,
    send_message_place_stage_validtion, get_random_hotel_names_from_file,send_hotel_option, is_numeric, send_message_ppl_error,
send_hotel_voucher_no_rooms,send_hotel_defulat,send_hotel_room
)
from services.message_services import fetch_availability,get_placement_if_exists
from models.user_answer import UserAnswerCreate
from services.services import create_user_answer_endpoint

# Initialize FastAPI app
app = FastAPI()

from services.services import create_user_answer_endpoint
from Config.prisma_client import init_prisma_client, disconnect_prisma_client

@app.on_event("startup")
async def startup():
    # Connect to the database when the application starts
    await init_prisma_client()

@app.on_event("shutdown")
async def shutdown():
    # Disconnect from the database when the application stops
    await disconnect_prisma_client()

# Define mappings for handling specific responses (e.g., confirmation and reset actions)
RESPONSE_ACTIONS = {
    'אישור': 'confirm',
    'אין אישור': 'reset_state'
}

# Define regex patterns for matching text commands in user messages
COMMANDS = {
    'TEXT': re.compile(r' הי| שלום| היי| מה קורה? אהלן'),
}

# In-memory store for user states (could be replaced by a persistent store)
user_states = {}

# Function to extract and map fields from the incoming request data
def extract_and_map_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    # Map incoming data to a standardized format
    mapped_data = {
        "status": data.get('status', ''),
        "from_number": data.get('from', ''),
        "to": data.get('to', ''),
        "sender_name": data.get('senderName', ''),
        "type": data.get('type', ''),
        "body": data.get('body', ''),
        "media": data.get('media', False),
        "timestamp": data.get('timestamp', '')
    }
    return mapped_data

# Function to retrieve the user state, creating a new one if it doesn't exist
def get_user_state(user_id: str) -> UserState:
    if user_id not in user_states:
        user_states[user_id] = UserState(user_id)
    return user_states[user_id]

@app.post("/")
async def receive_message(request: Request):
    # Receive and process incoming data
    data = await request.json()
    print(data)

    # Extract and map fields for easier handling
    incoming_message = extract_and_map_fields(data)
    print("Extracted fields:", incoming_message)

    # Check if the message body is present (non-empty)
    if incoming_message.get("body"):
        user_id = incoming_message.get('from_number')
        user_state = get_user_state(user_id)
        print(f"User ID: {user_id}")
        print(f"User State: {user_state}")

        # Handle the state transition based on the current state and user input
        response_message = await handle_transition(user_state, incoming_message)
    else:
        print("Received empty message body. Skipping processing.")

    # Return the response (this could be adjusted based on your needs)
    return JSONResponse(content=incoming_message, status_code=200)

# Function to handle state transitions and send responses based on user input
async def handle_transition(user_state: UserState, user_input: Dict[str, Any]) -> str:
    current_stage = user_state.get_current_stage()
    print(f"Current stage: {current_stage}")
    place_value = None

    user_response = user_input.get("body")
    print(f"User response: {user_response}")

    matched_place = None  # Initialize matched_place to avoid reference errors

    # Handle different stages of conversation based on the user state
    if current_stage == 'start':
        user_state.update_state('identification')
        message_sender = get_message_sender("identification")
        response = send_message_name_identification(user_input.get("to"), user_input.get("from_number"))
        

    elif current_stage == 'identification':
        user_state.update_data('identification', user_response)
        send_message_name_id(user_input.get("to"), user_input.get("from_number"), user_response)
        user_state.update_state('id_number')

    elif current_stage == 'id_number':
        if not is_israeli_id_number(user_response):
            # If invalid, send an error message and keep the state as 'id_number'
            send_message_name_id_error(user_input.get("to"), user_input.get("from_number"), "מספר תעודת זהות לא תקין, אנא נסה שוב.")
            return "Invalid ID number. Please try again."

        # If valid, proceed with the next steps
        user_state.update_data('id_number', user_response)
        send_message_place(user_input.get("to"), user_input.get("from_number"))
        user_state.update_state('place')

    elif current_stage == 'place':
        matched_place, score = find_best_settlement_match(user_response)
        print("matched place", matched_place)

        if matched_place == "failed":
            # If no match found, prompt the user to try again
            send_message_correct_place(user_input.get("to"), user_input.get("from_number"))
            return "No match found. Please try again."

        if score == 100:
            # If the match is perfect, proceed to the next stage
            send_message_ppl(user_input.get("to"), user_input.get("from_number"))
            user_state.update_data('place', matched_place)
            user_state.update_state('people')
        else:
            # If the match is not perfect, ask for confirmation
            sender = get_template_sender("confirm_place")
            response = sender.send_template(user_input, matched_place)
            # Wait for the user to confirm
            user_state.update_data('place', matched_place)
            user_state.update_state('confirm_place')

    elif current_stage == 'confirm_place':
        if user_response == 'כן':
            # If user confirms, proceed to the next stage
            send_message_ppl(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('people')
        else:
            # If user does not confirm, re-prompt for the place
            send_message_place_stage_validtion(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('place')

    elif current_stage == 'people':
        if not is_numeric(user_response):
            send_message_ppl_error(user_input.get("to"), user_input.get("from_number"))
            return {"error": "The response must be a number."}
        else:
            user_state.update_data('people', user_response)
            # user_state.update_data('accessible', user_response)
            sender = get_template_sender("accessible")
            response = sender.send_template(user_input)
            user_state.update_state('accessible')

    elif current_stage == 'accessible':
        user_state.update_data('accessible', user_response)
        sender = get_template_sender("pet")
        response = sender.send_template(user_input)
        user_state.update_state('pet')

    elif current_stage == 'pet':
        user_state.update_data('pet', user_response)
        sender = get_template_sender("before_end")
        response = sender.send_template(user_input, user_state.get_data())
        user_state.update_state('finale')

    elif current_stage == 'finale':
        user_state.update_data('finale', user_response)

        # Handle final stage responses and determine next steps
        if user_response == 'אישור':
            place_value = user_state.data.get('place')
            settlement_code = get_settlement_code(place_value) # Updated to use get_data
            user_state.update_data('place', int(settlement_code))
            print(user_state.get_data)
            user_answer_data = process_user_state(user_state.data)
            # print("user-answer-data",user_answer_data)
            #### now it will not work (write to db, cause there is a chnge to do settlemnt-code and settlment)
            # Call the endpoint function with the processed data
            #await create_user_answer_endpoint(user_answer_data)
            place_str = str(place_value)
            user_state.update_data('place', place_str)
            send_message_confim(user_input.get("to"), user_input.get("from_number"))
            hotels_options = await fetch_availability(place_value)
            print(hotels_options)
            hotels = await send_hotel_option(user_input.get("to"), user_input.get("from_number"),hotels_options)
            print(hotels)
            user_state.update_state('hotel_allocation')

        elif user_response == 'תיקון':
            user_state.update_state('start')
            send_message_reset(user_input.get("to"), user_input.get("from_number"))

        else:
            raise ValueError(f"Unknown response: {user_response}")

    elif current_stage == 'hotel_allocation':
        """
        the user get 3-4 option for hotel, he need to choose 
        option if what choosen exist(rooms exist) he get voucher
        elif: we choose for him what exist. and he get voucher.
        else: sorry we dont have rooms for you.
        """
        # hotels_options = await get_random_hotel_names_from_file()
        # print(hotels_options)
        # hotels = send_hotel_option(user_input.get("to"), user_input.get("from_number"),hotels_options)
        # print(hotels)
        #random_chice = get_random_hotel_names_from_file()
        residence = user_response
        print("place user" , user_state.get_value('place'))
        place_value = user_state.get_value('place')
        voucher_response  = await get_placement_if_exists(residence, place_value,user_state.get_value('id_number'),user_state.get_value('people'),user_state.user_id)
        voucher_status = voucher_response.get("status")
        voucher_link = voucher_response.get("link")
        print("voucher_response:", voucher_response)
        
        if voucher_status == "error-no-available-rooms":
            send_hotel_voucher_no_rooms(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('END')

        elif voucher_status == "error-other-residence-reserved":
                send_hotel_defulat(user_input.get("to"), user_input.get("from_number"), voucher_link)
                user_state.update_state('END')

        elif voucher_status == "success":
                send_hotel_room(user_input.get("to"), user_input.get("from_number"), voucher_link)
                user_state.update_state('END')

    elif current_stage == 'END':
        return "תודה רבה והמשך יום טוב!"
    

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
