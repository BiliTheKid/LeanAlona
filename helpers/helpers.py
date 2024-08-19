import os
import random
from typing import Any, Dict
from fastapi import HTTPException
import requests
from pathlib import Path
import time

# from models.user import UserState


## helpers function for validtors
def is_israeli_id_number(id_number: str) -> bool:
    # Ensure the input is a string and trim whitespace
    id_number = str(id_number).strip()

    # Check if the ID number is too long or contains non-numeric characters
    if len(id_number) > 9 or not id_number.isdigit():
        return False

    # Pad the ID number with leading zeros if it's less than 9 digits
    id_number = id_number.zfill(9)

    # Calculate the checksum
    checksum = sum(
        int(digit) * ((index % 2) + 1) - 9 if int(digit) * ((index % 2) + 1) > 9 else int(digit) * ((index % 2) + 1)
        for index, digit in enumerate(id_number)
    )

    # Return True if the checksum is divisible by 10, otherwise False
    return checksum % 10 == 0


def send_question(api_key, from_number, to_number, name, language, header_type):
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendTemplate"    # The suffix you want to add
    url = api_99 + suffix
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "name": name,
        "language": language,
        "headerType": header_type
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "Question sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


def send_message_fa(from_number, to_number,body_message,sender_name):
    """
    send message 
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": body_message
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

### genric function template general use depends on the stage
class TemplateSender:
    def __init__(self):
        # Initialize with a default template name
        self.template_name = "default_template"

    def send_template(self, incomingMessage):
        """
        Base implementation of sending a template. This can be overridden by subclasses.
        """
        print("TemplateSender send_template method")
        api_key = os.getenv("API_KEY")
        from_number = os.getenv("PHONE")
        to_number = incomingMessage.get("from_number")
        name = self.template_name  # Use the template name set in the subclass
        language = 1  # Default language
        header_type = 1  # Default header type
        
        return send_question(api_key, from_number, to_number, name, language, header_type)

class StageOneSender(TemplateSender):
    def __init__(self):
        super().__init__()
        self.template_name = "accessible_room_he1"

class StageTwoSender(TemplateSender):
    def __init__(self):
        super().__init__()
        self.template_name = "pet_he1"


class StageThree(TemplateSender):
    def __init__(self):
        super().__init__()
        self.template_name = "finale_5"

    def send_template(self, incomingMessage, userData):
        """
        Override the base send_template method to include specific body variables
        from userData.
        """
        print("StageThree send_template method")
        
        api_key = os.getenv("API_KEY")
        from_number = os.getenv("PHONE")
        to_number = incomingMessage.get("from_number")
        name = self.template_name  # Use the template name set in this subclass
        language = 1  # Assuming this stage requires a different language

        # Construct the payload with specific body variables from userData
        payload = {
            "apiKey": api_key,
            "from": from_number,
            "to": to_number,
            "name": name,
            "language": language,
            "headerType": 1,  # Default header type
            "bodyVariable1": userData.get("identification"),
            "bodyVariable2": userData.get("id_number"),
            "bodyVariable4": userData.get("people"),
            "bodyVariable5": userData.get("accessible"),
            "bodyVariable6": userData.get("pet")
        }

        headers = {
            "Content-Type": "application/json"
        }

        # Send the request with the payload
        api_99 = os.getenv("API_BRIDGE")
        suffix = "/sendTemplate"
        url = api_99 + suffix

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        if response.status_code == 200:
            return {"message": "Question sent successfully."}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

class settlements(TemplateSender):
    def __init__(self):
        super().__init__()
        self.template_name = "approve_settelment"
    def send_template(self, incomingMessage, var):
        """
        Override the base send_template method to include specific body variables
        from userData.
        """
        print("StageThree send_template method")
        
        api_key = os.getenv("API_KEY")
        from_number = os.getenv("PHONE")
        to_number = incomingMessage.get("from_number")
        name = self.template_name  # Use the template name set in this subclass
        language = 1  # Assuming this stage requires a different language

        # Construct the payload with specific body variables from userData
        payload = {
            "apiKey": api_key,
            "from": from_number,
            "to": to_number,
            "name": name,
            "language": language,
            "headerType": 1,  # Default header type
            "bodyVariable1": var
        }

        headers = {
            "Content-Type": "application/json"
        }

        # Send the request with the payload
        api_99 = os.getenv("API_BRIDGE")
        suffix = "/sendTemplate"
        url = api_99 + suffix

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        if response.status_code == 200:
            return {"message": "Question sent successfully."}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

def get_template_sender(stage):
    """
    Factory function to get the appropriate TemplateSender subclass based on the stage.
    """
    if stage == "accessible":
        return StageOneSender()
    elif stage == "pet":
        return StageTwoSender()
    elif stage == "before_end":
        return StageThree()
    elif stage == 'confirm_place':
        return settlements()
    else:
        raise ValueError("Unknown stage: {}".format(stage))  # Error handling for unknown stages

def send_message_non(from_number, to_number):
    """
    send message, for non-legal approved
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": "תודה לך, ואני כאן בשבילך לשאלות כלליות"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_gen(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": "היי, בשלב זה אני מבקשת לעקוב אחרי ההוראות הנדרשות, למען ביטחונך ולמען שירות טוב יותר"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_name_hotel(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": "מה שם המלון בו אתה נמצא?"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_name_identification(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body":"שלום, הגעתם למרכז השיבוץ למלונות של משרד התיירות.\nאשאל אתכם מספר פרטים ואסייע לכם למצוא מלון שמתאים לכם בזריזות.\nמה שמכם המלא?"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_name_id(from_number, to_number,sender_name):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f"שלום {sender_name}, מה מספר תעודת הזהות שלך?"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_name_id_error(from_number, to_number,sender_name):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f"מספר הזהות שהוקלד שגוי, לטובת המשך התהליך אנא הקלידו מספר זהות תקין "
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_place(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f"תודה. מאיזה יישוב אתם מפונים?"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_place_stage_validtion(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f"מאיזה יישוב אתם מפונים"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_ppl(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f" כמה בני משפחה תהיו במלון?"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_reset(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f" מכיוון שהזנתם ,אין אישור,אתם יכולים להכניס את הפרטים מחדש. תודה והמשך יום טוב"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_confim(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f"קיבלתי. אני מחפש עבורכם חדרים מתאימים במלון ואחזור אליכם בהקדם."
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_correct_place(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")   
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f"לא נמצא יישוב תואם, אנא נסה שוב."
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_message_approve_place(from_number, to_number,matched_place):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")   
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f"אתה מתכוון ל-{matched_place}? אם כן, אנא אשר עם 'כן'."
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)



## create override function for diffrent message , not in used for now
class MessageSender:
    def __init__(self):
        # Initialize with a default template name
        self.sender_name = "שם גנרי"
        self.body_message = "default_message"

    def send_message(self, incomingMessage):
        """
        Base implementation of sending a template. This can be overridden by subclasses.
        """
        print("messageSender send_message method")
        api_key = os.getenv("API_KEY")
        from_number = os.getenv("PHONE")
        to_number = incomingMessage.get("from_number")
        sender_name = self.sender_name
        body_message = self.body_message  # Use the template name set in the subclass

        
        return send_message_fa(from_number, to_number, body_message,sender_name)

class MessageId(MessageSender):
    def __init__(self):
        super().__init__()
        self.body_message = f" מה מס ת.ז שלך? {self.sender_name} היי,"
        

class LegalMessageNotApproved(MessageSender):
    def __init__(self):
        super().__init__()
        self.template_name = "תודה לך, ואני כאן בשבילך לשאלות כלליות"

class MessageApt(MessageSender):
    def __init__(self):
        super().__init__()
        self.template_name = "..אנא הזן כתובת בבקשה"

class InfoOther(MessageSender):
    def __init__(self):
        super().__init__()
        self.template_name = "שדה פתוח לבחירתך"


def get_message_sender(stage):
    """
    Factory function to get the appropriate TemplateSender subclass based on the stage.
    """
    if stage == "identification":
        return MessageId()
    elif stage == "END":
        return LegalMessageNotApproved()
    elif stage == "apartment":
       return MessageApt()
    elif stage == "collecting_basic_info_other":
       return InfoOther()
    else:
        raise ValueError("Unknown stage: {}".format(stage))  # Error handling for unknown stages


# Load the CSV file into a DataFrame
import pandas as pd
from fuzzywuzzy import process

def find_best_settlement_match(place: str):
    try:
        # Attempt to load the CSV file
        current_dir = os.path.dirname(__file__)  # Directory of the current script
        setup_dir = os.path.abspath(os.path.join(current_dir, '..', 'Setup'))  # Navigate up one level and then into 'setup'
        file_path = os.path.join(setup_dir, 'settlements.csv')

        # Load the CSV file
        settlements_df = pd.read_csv(file_path)
        # Extract only the official settlement names for matching
        settlement_names = settlements_df['Settlement'].tolist()
        # print(settlement_names)

        # Perform fuzzy matching
        best_match, score = process.extractOne(place, settlement_names)
        # print(best_match, score)

        # Set a threshold score to determine if the match is good enough
        if score >= 60:  # You can adjust this threshold as needed
            return best_match , score  
        else:
            return "failed" , 0
    
    except FileNotFoundError:
        print("Error: The file 'settlements.csv' was not found.")
        return "File not found" , 0 

    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
        return "Empty file" , 0

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "An error occurred"
    
from pathlib import Path

def get_settlement_code(best_match: str) -> str:
    try:
        # Construct the relative path to 'settlements.csv'
        current_dir = Path(__file__).resolve().parent
        setup_dir = current_dir.parent / 'setup'
        file_path = setup_dir / 'settlements.csv'
        
        # Load the CSV file
        settlements_df = pd.read_csv(file_path)
        
        # Check if the DataFrame contains the necessary columns
        if 'Settlement' not in settlements_df.columns or 'Settlement_code' not in settlements_df.columns:
            raise ValueError("CSV file is missing required columns.")
        
        # Find the Settlement_code for the best_match
        matching_row = settlements_df[settlements_df['Settlement'] == best_match]
        
        if not matching_row.empty:
            settlement_code = matching_row['Settlement_code'].values[0]
            return settlement_code 
        else:
            return "No matching settlement found"

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return "File not found"

    except pd.errors.EmptyDataError:
        print(f"Error: The file '{file_path}' is empty.")
        return "Empty file"

    except ValueError as e:
        print(f"Error: {e}")
        return "Error"

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "An error occurred"

def process_user_state(user_state: Dict[str, Any]) -> Dict[str, Any]:
    bool_mapping = {'כן': True, 'לא': False}
    
    def convert_to_boolean(value: str) -> bool:
        return bool_mapping.get(value, False)
    
    def convert_to_int(value: Any) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    def validate_string(value: Any) -> str:
        return str(value) if isinstance(value, str) else ''
    
    return {
        'identification': validate_string(user_state.get('identification', '')),
        'id_number': validate_string(user_state.get('id_number', '')),
        'place': convert_to_int(user_state.get('place')),
        'people': convert_to_int(user_state.get('people', 0)),
        'accessible': convert_to_boolean(user_state.get('accessible', '')),
        'pet': convert_to_boolean(user_state.get('pet', ''))
    }


async def send_hotel_option(from_number, to_number,hotel_options):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendButtons"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "header":1,
        "body": "מצאתי לכם חדרים פנויים. אנא בחר מתוך האפשרויות הבאות : ",
        "button1": hotel_options[0],
        "button2": hotel_options[1],
        "button3": hotel_options[2]
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


def get_random_hotel_names_from_file(num_options=3):
    # Construct the relative path to 'hotels.csv'
    current_dir = Path(__file__).resolve().parent
    setup_dir = current_dir.parent / 'Setup'
    file_path = setup_dir / 'hotels.csv'

    time.sleep(3)
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Extract the hotel names
    hotel_names = df['Hotel Name'].tolist()
    
    # Check if the number of options requested is greater than the number of available hotels
    if num_options > len(hotel_names):
        raise ValueError("Number of requested options exceeds the number of available hotels.")
    
    # Select random hotel names
    random_hotel_names = random.sample(hotel_names, num_options)
    
    return random_hotel_names

# print(get_random_hotel_names_from_file())

def send_message_ppl_error(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f"בבקשה להזין את המידע מספרית"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def is_numeric(value):
    """
    Check if the provided value is numeric.
    """
    return value.isdigit() if isinstance(value, str) else False

def send_hotel_voucher_no_rooms(from_number, to_number):
    """
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendMessage"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "body": f"היי מצטערים נורא, מכסת החדרים הקיימים במערכות אינטרנט נגמרו צרו קשר עם מנהל הקהילה שלכם"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_hotel_room(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendFile"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "caption":" בבקשה הוואצר של המלון שביקשתם, נא להגיע לשם...",
        "body": "https://dl.dropboxusercontent.com/scl/fi/txkt0y6f3le7p7s4lvkj3/output.pdf?rlkey=0tonyfy32rx8knvh0us83k2xt&st=dlk851xt"
    
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def send_hotel_defulat(from_number, to_number):
    """"
    send message for users that insert wrong input.
    """
    api_99 = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    #url = os.getenv("API_BRIDGE")  # Replace with your actual API endpoint
    suffix = "/sendFile"    # The suffix you want to add
    url = api_99 + suffix
    api_key = os.getenv("API_KEY")
    payload = {
        "apiKey": api_key ,
        "from": from_number,
        "to": to_number,
        "caption":"לצערנו הרב, אין מקום פנוי במלון שביקשתם, אתם מתבקשים להגיע לכאן",
        "body": "https://dl.dropboxusercontent.com/scl/fi/txkt0y6f3le7p7s4lvkj3/output.pdf?rlkey=0tonyfy32rx8knvh0us83k2xt&st=dlk851xt"
    
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    if response.status_code == 200:
        return {"message": "message sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)



# if __name__ == "__main__":
#     print(get_settlement_code("גונן​"))
