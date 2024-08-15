import os
from fastapi import HTTPException
import requests


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
        self.template_name = "accessible_room_he"

class StageTwoSender(TemplateSender):
    def __init__(self):
        super().__init__()
        self.template_name = "pet_he"


class StageThree(TemplateSender):
    def __init__(self):
        super().__init__()
        self.template_name = "finale_3"

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
        "body": "תודה רבה לך, ואני כאן בשבילך לשאלות כלליות"
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
        "body": " שלום הגעתם לבוט של משרד התיירות, בשביל לדעת לאיזה מלון אתם צריכים להגיע בהתאם ליישוב מגורכם, נוודא את זהותכם, מה שמכם המלא?"
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
        "body": f" היי,  {sender_name} מה מס תז שלך?"
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
        "body": f"היי מספר תז שהקלדת לא חוקי, בשביל שנוכל לשבץ אותך נא הקלד שוב.  "
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
        "body": f" תודה רבה, מאיזה ישוב אתם?"
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
        "body": f"קיבלתי, אני מחפש חדרים רלוונטיים עבורכם ואחזור אליך מייד לאחר שאמצא. "
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
        self.body_message = f" מה מס תז שלך? {self.sender_name} היי,"
        

class LegalMessageNotApproved(MessageSender):
    def __init__(self):
        super().__init__()
        self.template_name = "תודה רבה לך, ואני כאן בשבילך לשאלות כלליות"

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

def find_best_settlement_match(place: str) -> str:
    try:
        # Attempt to load the CSV file
        current_dir = os.path.dirname(__file__)  # Directory of the current script
        setup_dir = os.path.abspath(os.path.join(current_dir, '..', 'Setup'))  # Navigate up one level and then into 'setup'
        file_path = os.path.join(setup_dir, 'settlements.csv')

        # Load the CSV file
        settlements_df = pd.read_csv(file_path)
        # Extract only the official settlement names for matching
        settlement_names = settlements_df['Settlement'].tolist()
        print(settlement_names)

        # Perform fuzzy matching
        best_match, score = process.extractOne(place, settlement_names)
        print(best_match, score)

        # Set a threshold score to determine if the match is good enough
        if score >= 60:  # You can adjust this threshold as needed
            return best_match
        else:
            return "failed"
    
    except FileNotFoundError:
        print("Error: The file 'settlements.csv' was not found.")
        return "File not found"

    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
        return "Empty file"

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "An error occurred"
    


