from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from prisma import Prisma
import re
from models.user import UserState 
from helpers.helpers import send_message_non , get_template_sender , TemplateSender , send_message_gen, send_message_name_hotel, get_message_sender, send_message_name_identification, send_message_name_id, send_message_place, send_message_ppl,send_message_reset,send_message_confim

####
# Initialize FastAPI app
app = FastAPI()
# Initialize Prisma
db = Prisma(auto_register=True)
@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()



RESPONSE_ACTIONS = {
    'אישור': 'confirm',
    'אין אישור': 'reset_state'
}

## regex for general questions checking
COMMANDS = {
    'TEXT': re.compile(r' הי| שלום| היי| מה קורה? אהלן'),
}

user_states = {}


def extract_and_map_fields(data: dict[str, Any]) -> Dict[str, Any]:
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

def get_user_state(user_id: str) -> UserState:
    if user_id not in user_states:
        user_states[user_id] = UserState(user_id)
    return user_states[user_id]

 
@app.post("/")
async def receive_message(request: Request):
    # Receive and process the data
    data = await request.json()
    print(data)
    # Extract and map fields
    incoming_message = extract_and_map_fields(data)
    print("Extracted fields:", incoming_message)
    ## edit
    if incoming_message.get("body"):
        user_id = incoming_message.get('from_number')
        user_state = get_user_state(user_id)
        print(f"User ID: {user_id}")
        print(f"User State: {user_state}")
        # Handle state transition with non-empty body
        response_message = handle_transition(user_state, incoming_message)
    else:
        print("Received empty message body. Skipping processing.")
    return JSONResponse(content=incoming_message, status_code=200)

def handle_transition(user_state: UserState, user_input: dict) -> str:
    current_stage = user_state.get_current_stage()
    print(f"Current stage: {current_stage}")

    user_response = user_input.get("body")
    print(f"User response: {user_response}")

    if current_stage == 'start':
        user_state.update_state('identification')
        user_state.update_data('identification', user_response)
        # sender = get_template_sender("start")      
        #response = sender.send_template(user_input) 
        message_sender = get_message_sender("identification")  # Create the appropriate sender instance
        response = send_message_name_identification(user_input.get("to"),user_input.get("from_number"))  # Send the template

    elif current_stage == 'identification':
        user_state.update_data('id_number', user_response)
        # print(f" מה מס תז שלך? {user_response} היי, ")
        # message_sender = get_message_sender("identification")
        send_message_name_id(user_input.get("to"),user_input.get("from_number"),user_response)
        # response = message_sender.send_message(user_input)
        user_state.update_state('id_number')

    elif current_stage == 'id_number':
        user_state.update_data('id_number', user_response)
        send_message_place(user_input.get("to"),user_input.get("from_number"))
        # user_state.update_state('children_exist')
        user_state.update_state('place')

    elif current_stage == 'place':
        user_state.update_data('place', user_response)
        send_message_ppl(user_input.get("to"),user_input.get("from_number"))
        # user_state.update_state('children_exist')
        user_state.update_state('people')

    elif current_stage == 'people':
        user_state.update_data('people', user_response)
        user_state.update_data('accessible', user_response)
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
      # Determine action based on response
        # action = RESPONSE_ACTIONS.get(user_response)
        if user_response == 'אישור':
            send_message_confim(user_input.get("to"), user_input.get("from_number"))
            # await create_user_answer(user_state, user_input)
            user_state.update_state('END')
            # return "Thank you! Your answers have been recorded."
        
        elif user_response == 'אין אישור':
            user_state.update_state('start')
            send_message_reset(user_input.get("to"), user_input.get("from_number"))
            # return "Please provide your details again. The chat will start from the beginning."

        else:
            raise ValueError(f"Unknown response: {user_response}")

    elif current_stage == 'END':
        return "תודה רבה והמשך יום טוב!"



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)