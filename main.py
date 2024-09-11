from typing import Any, Dict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
import json
import re
from models.user import UserState
from helpers.helpers import (
    send_message_non, get_template_sender, TemplateSender, send_message_gen,
    send_message_name_hotel, get_message_sender, send_message_name_identification,
    send_message_name_id, send_message_place, send_message_ppl, send_message_reset,
    send_message_confim, is_israeli_id_number, send_message_name_id_error, find_best_settlement_match,
    send_message_correct_place, send_message_approve_place, get_settlement_code, process_user_state,
    send_message_place_stage_validtion, get_random_hotel_names_from_file,send_hotel_option, is_numeric, send_message_ppl_error,
send_hotel_voucher_no_rooms,send_hotel_defulat,send_hotel_room,confirm_or_cancle_hotel,thanks_for_approval,thanks_for_decline
,end_confirm,end_decline,connect_106,send_message_limit_ppl,value_error, send_hotel_search_prompt, send_hotel_not_found, send_hotel_found, send_hotels_found
)
from services.message_services import fetch_availability,get_placement_if_exists
from models.user_answer import UserAnswerCreate
from services.services import create_user_answer_endpoint
from Config.prisma_client import init_prisma_client, disconnect_prisma_client
from models.user import ThreadSafeUserStateManager


#from redis import asyncio as aioredis
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await init_prisma_client()
    # global redis
    # redis = aioredis.from_url("redis://localhost")
    # await redis.ping()
    print("Application startup complete")
    
    yield  # This is where the app runs
    
    # Shutdown code
    await disconnect_prisma_client()
    # await redis.close()
    print("Application shutdown complete")

# Create the FastAPI app with the lifespan
app = FastAPI(lifespan=lifespan)
# Define mappings for handling specific responses (e.g., confirmation and reset actions)
# RESPONSE_ACTIONS = {
#     'אישור': 'confirm',
#     'אין אישור': 'reset_state'
# }

# Define regex patterns for matching text commands in user messages
# COMMANDS = {
#     'TEXT': re.compile(r' הי| שלום| היי| מה קורה? אהלן'),
# }

# In-memory store for user states (could be replaced by a persistent store) before edit
#user_states = {}
user_state_manager = ThreadSafeUserStateManager()


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

#before edit!
# Function to retrieve the user state, creating a new one if it doesn't exist
# def get_user_state(user_id: str) -> UserState:
#     if user_id not in user_states:
#         user_states[user_id] = UserState(user_id)
#     return user_states[user_id]

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
        #before edit
        # user_id = incoming_message.get('from_number')
        # user_state = get_user_state(user_id)
        user_id = incoming_message.get('from_number')
        user_state = user_state_manager.get_user_state(user_id)
        print(f"User ID: {user_id}")
        print(f"User State: {user_state}")
        # Handle the state transition based on the current state and user input
        response_message = await handle_transition(user_state, incoming_message)
        
        # Update the user state after handling the transition
        user_state_manager.update_user_state(user_id, user_state)
    
    
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
        #message_sender = get_message_sender("identification")
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
            user_state.update_state('start')
            return "No match found. Please try again."

        if score == 100:
            # If the match is perfect, proceed to the next stage
            send_message_ppl(user_input.get("to"), user_input.get("from_number"))
            user_state.update_data('place', matched_place)
            user_state.update_state('num_of_people')
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
            user_state.update_state('num_of_people')
        elif user_response == 'לא':
            # If user does not confirm, re-prompt for the place
            connect_106(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('start')
        else:
            value_error(user_input.get("to"), user_input.get("from_number"))

    elif current_stage == 'confirm_ppl':
            send_message_ppl(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('num_of_people')


    elif current_stage == 'num_of_people':
        if not is_numeric(user_response):
            send_message_ppl_error(user_input.get("to"), user_input.get("from_number"))
            return {"error": "The response must be a number."}
        else:
            if int(user_response) > 10:
                send_message_limit_ppl(user_input.get("to"), user_input.get("from_number"))
                user_state.update_state('nav_to_106_or_cont')
            else:
                user_state.update_data('people', user_response)
                # user_state.update_data('accessible', user_response)
                sender = get_template_sender("accessible")
                response = sender.send_template(user_input)
                user_state.update_state('accessible')

    elif current_stage == 'people':
            user_state.update_data('people', user_response)
            # user_state.update_data('accessible', user_response)
            sender = get_template_sender("accessible")
            response = sender.send_template(user_input)
            user_state.update_state('accessible')

    elif current_stage == 'nav_to_106_or_cont':
        if user_response == 'כן':
            send_message_ppl(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('people')

        elif user_response == 'לא':
            connect_106(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('start')
        else:
            value_error(user_input.get("to"), user_input.get("from_number"))
            
            

    elif current_stage == 'accessible':
        if user_response not in ['נדרש', 'לא נדרש']:
            # Handle invalid response
            value_error(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('accessible')
        else:
            # Handle valid response
            user_state.update_data('accessible', user_response)
            sender = get_template_sender("pet")
            response = sender.send_template(user_input)
            user_state.update_state('pet')

    elif current_stage == 'pet':
        # Check if the user response is valid
        if user_response not in ['לא', 'כן']:
            # Handle invalid response
            value_error(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('pet')  # Reset or handle invalid response
        else:
            # Valid response, update state and data
            user_state.update_data('pet', user_response)
            sender = get_template_sender("before_end")
            response = sender.send_template(user_input, user_state.get_data())
            user_state.update_state('finale')

    elif current_stage == 'finale':
        user_state.update_data('finale', user_response)

        # Handle final stage responses and determine next steps
        if user_response == 'אישור':
            try:
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
                # add test here.
                # hotels_options = await fetch_availability(place_value)
                hotels_options = [
                    "מלון דן, תל אביב",
                    "מלון לאונרדו, אילת",
                    "מלון קינג דיויד, ירושלים",
                    "מלון ישרוטל, חיפה",
                    "מלון הרודס, תל אביב",
                    "מלון נפטון, ים המלח",
                    "מלון אואזיס, אילת",
                    "מלון קראון פלאזה, ירושלים",
                    "מלון רמדה, נתניה",
                    "מלון דויד אינטרקונטיננטל, תל אביב",
                    "מלון הילטון, תל אביב",
                    "מלון פבריק, תל אביב",
                    "מלון טמרס, הרצליה",
                    "מלון דיוויד ריזורט, ים המלח",
                    "מלון בראשית, מצפה רמון",
                    "מלון רוטשילד, תל אביב",
                    "מלון אברהם הוסטל, ירושלים",
                    "מלון דן פנורמה, חיפה",
                    "מלון בוטיק נורמן, תל אביב",
                    "מלון וורט, אשדוד",
                    "מלון דן כרמל, חיפה",
                    "מלון אורכידאה, אילת",
                    "מלון ישרוטל ים סוף, אילת",
                    "מלון גרנד קורט, ירושלים",
                    "מלון מרינה, תל אביב",
                    "מלון נורדוי, תל אביב",
                    "מלון מגדל דוד, נתניה",
                    "מלון דן קיסריה, קיסריה",
                    "מלון הרודס ויטאליס, אילת",
                    "מלון דן אכדיה, הרצליה",
                    "מלון הבירה, ירושלים",
                    "מלון אלמא, זכרון יעקב",
                    "מלון יערות הכרמל, חיפה",
                    "מלון ריץ קרלטון, הרצליה",
                    "מלון נוף גינוסר, כנרת",
                    "מלון שירת הים, כנרת",
                    "מלון לאונרדו פלאזה, טבריה",
                    "מלון עין גדי, ים המלח",
                    "מלון המלך שלמה, אילת",
                    "מלון ישרוטל טאואר, תל אביב",
                    "מלון רויאל פלאזה, טבריה",
                    "מלון מטיילים גשר הזיו, גליל מערבי",
                    "מלון בוטיק ארמון, ירושלים",
                    "מלון דיוויד דדון, נתניה",
                    "מלון ממילא, ירושלים",
                    "מלון וולדורף אסטוריה, ירושלים",
                    "מלון ישרוטל מצפה הימים, גליל עליון",
                    "מלון שדה בוקר, מצפה רמון",
                    "מלון אוליב, תל אביב",
                    "מלון אסטרל פאלמה, אילת"
                ]


                if not hotels_options:
                    send_hotel_voucher_no_rooms(user_input.get("to"), user_input.get("from_number"))
                    user_state.update_state('start')
                    
                else:
                    try: 
                        #send_hotel_voucher_no_rooms(user_input.get("to"), user_input.get("from_number"))
                        print("before hotel await",hotels_options)
                        print("hotel type",type(hotels_options))
                        hotels = await send_hotel_option(user_input.get("to"), user_input.get("from_number"),hotels_options, 1)
                        print("hotels await",hotels)
                        user_state.update_data('hotels',hotels)
                        user_state.update_data('hotels_page_number', 1)
                        user_state.update_state('hotel_allocation')
                    except: 
                        user_state.update_state('start')
                        print(f"An error occurred: {e}")

            except Exception as e:
                # Handle any errors that occur during the process
                print(f"An error occurred: {e}")
        
        elif user_response == 'תיקון':
            user_state.update_state('from_reset')
            # message_sender = get_message_sender("identification")
            # response = send_message_name_identification(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('identification')
            #message_sender = get_message_sender("identification")
            response = send_message_name_identification(user_input.get("to"), user_input.get("from_number"))
        

        else:
            value_error(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('finale')

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
        print("user----hotels",user_state.get_value('hotels'))
        if user_response in user_state.get_value('hotels'):
            residence = user_response
            print("place user" , user_state.get_value('place'))
            place_value = user_state.get_value('place')
            print("here!!!!!!",residence, place_value,user_state.get_value('id_number'),user_state.get_value('people'),user_state.user_id)
            voucher_response  = await get_placement_if_exists(residence, place_value,user_state.get_value('id_number'),user_state.get_value('people'),user_state.user_id)
            voucher_status = voucher_response.get("status")
            voucher_link = voucher_response.get("link")
            voucher_residence = voucher_response.get("residence")
            print("voucher_response:", voucher_response)
            
            if voucher_status == "error-no-available-rooms":
                send_hotel_voucher_no_rooms(user_input.get("to"), user_input.get("from_number"))
                user_state.update_state('start')

            elif voucher_status == "error-other-residence-reserved":
                    send_hotel_defulat(user_input.get("to"), user_input.get("from_number"), voucher_link)
                    user_state.update_state('DEFAULTHOTEL')

            elif voucher_status == "success":
                    send_hotel_room(user_input.get("to"), user_input.get("from_number"), voucher_link)
                    user_state.update_state('DEFAULTHOTEL')
        elif user_response == "הצגת אפשרויות נוספות":
            next_page_number = user_state.get_value('hotels_page_number') + 1
            hotels = await send_hotel_option(user_input.get("to"), user_input.get("from_number"),user_state.get_value('hotels'), next_page_number)
            user_state.update_data('hotels_page_number',next_page_number)
            user_state.update_state('hotel_allocation')
        elif user_response == "חיפוש":
            send_hotel_search_prompt(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('hotel_search')
        else:
            value_error(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('hotel_allocation')        
    elif current_stage == 'hotel_search':
        hotels = user_state.get_value('hotels')
        filtered_hotels = [hotel for hotel in hotel_strings if searchValue in hotel]
        filtered_hotels_size = len(filtered_hotels)
        if filtered_hotels_size == 0:
            await send_hotel_not_found(user_input.get("to"), user_input.get("from_number"))
            await send_hotel_option(user_input.get("to"), user_input.get("from_number"),user_state.get_value('hotels'), user_state.get_value('hotels_page_number'))
            user_state.update_state('hotel_allocation')
        elif filtered_hotels_size == 1:
            await send_hotel_found(user_input.get("to"), user_input.get("from_number"), filtered_hotels[0])
            user_state.update_data('search_hotel_found_allocation', filtered_hotels[0])
            user_state.update_state('search_hotel_found_allocation')
        else:
            await send_hotels_found(user_input.get("to"), user_input.get("from_number"), filtered_hotels)
            user_state.update_data('search_hotels_found_allocation', filtered_hotels[0])
            user_state.update_state('search_hotels_found_allocation')

    elif current_stage == 'search_hotel_found_allocation':
        if user_response == 'אישור':
            residence = user_state.get_value('search_hotel_found_allocation')
            print("place user" , user_state.get_value('place'))
            place_value = user_state.get_value('place')
            print("here!!!!!!",residence, place_value,user_state.get_value('id_number'),user_state.get_value('people'),user_state.user_id)
            voucher_response  = await get_placement_if_exists(residence, place_value,user_state.get_value('id_number'),user_state.get_value('people'),user_state.user_id)
            voucher_status = voucher_response.get("status")
            voucher_link = voucher_response.get("link")
            voucher_residence = voucher_response.get("residence")
            print("voucher_response:", voucher_response)
            if voucher_status == "error-no-available-rooms":
                send_hotel_voucher_no_rooms(user_input.get("to"), user_input.get("from_number"))
                user_state.update_state('start')
            elif voucher_status == "error-other-residence-reserved":
                    send_hotel_defulat(user_input.get("to"), user_input.get("from_number"), voucher_link)
                    user_state.update_state('DEFAULTHOTEL')
            elif voucher_status == "success":
                    send_hotel_room(user_input.get("to"), user_input.get("from_number"), voucher_link)
                    user_state.update_state('DEFAULTHOTEL')
        else:
            await send_hotel_option(user_input.get("to"), user_input.get("from_number"),user_state.get_value('hotels'), user_state.get_value('hotels_page_number'))
            user_state.update_state('hotel_allocation')

    elif current_stage == 'search_hotels_found_allocation':
        if user_response in user_state.get_value('search_hotels_found_allocation'):
            residence = user_response
            print("place user" , user_state.get_value('place'))
            place_value = user_state.get_value('place')
            print("here!!!!!!",residence, place_value,user_state.get_value('id_number'),user_state.get_value('people'),user_state.user_id)
            voucher_response  = await get_placement_if_exists(residence, place_value,user_state.get_value('id_number'),user_state.get_value('people'),user_state.user_id)
            voucher_status = voucher_response.get("status")
            voucher_link = voucher_response.get("link")
            voucher_residence = voucher_response.get("residence")
            print("voucher_response:", voucher_response)
            if voucher_status == "error-no-available-rooms":
                send_hotel_voucher_no_rooms(user_input.get("to"), user_input.get("from_number"))
                user_state.update_state('start')
            elif voucher_status == "error-other-residence-reserved":
                    send_hotel_defulat(user_input.get("to"), user_input.get("from_number"), voucher_link)
                    user_state.update_state('DEFAULTHOTEL')
            elif voucher_status == "success":
                    send_hotel_room(user_input.get("to"), user_input.get("from_number"), voucher_link)
                    user_state.update_state('DEFAULTHOTEL')
        else:
            await send_hotel_option(user_input.get("to"), user_input.get("from_number"),user_state.get_value('hotels'), user_state.get_value('hotels_page_number'))
            user_state.update_state('hotel_allocation')

    elif current_stage == 'DEFAULTHOTEL':
        # confirm_or_cancle_hotel(user_input.get("to"), user_input.get("from_number"))
        if user_response == 'אישור':
            thanks_for_approval(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('start')
        elif user_response ==  "ביטול":
            thanks_for_decline(user_input.get("to"), user_input.get("from_number"))
            user_state.update_state('identification')
        else:
            value_error(user_input.get("to"), user_input.get("from_number"))


    # elif current_stage == 'END':
    #     # return "תודה רבה והמשך יום טוב!"
    #     if user_response == 'אישור':
    #         end_confirm(user_input.get("to"), user_input.get("from_number"))

    #     elif user_response ==  'ביטול':
    #         end_decline(user_input.get("to"), user_input.get("from_number"))

    elif current_stage == 'ENDF':
        return "תודה רבה והמשך יום טוב!"

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
