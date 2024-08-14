import os
from fastapi import HTTPException
import requests

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
        self.template_name = "website_welcome_he"

class StageTwoSender(TemplateSender):
    def __init__(self):
        super().__init__()
        self.template_name = "current_loc_he"

class StageThree(TemplateSender):
    def __init__(self):
        super().__init__()
        self.template_name = "settlements_he"

def get_template_sender(stage):
    """
    Factory function to get the appropriate TemplateSender subclass based on the stage.
    """
    if stage == "start":
        return StageOneSender()
    elif stage == "collecting_basic_info":
        return StageTwoSender()
    elif stage == "settlements":
        return StageThree()
    else:
        raise ValueError("Unknown stage: {}".format(stage))  # Error handling for unknown stages



## create override function for diffrent message

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
        "body": f" היי,  {sender_name} מה מס תז השלך?"
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


# def translate_name_to_hebrew(name: str) -> str:
#     translator = Translator()
#     translation = translator.translate(name, src='en', dest='he')
#     return translation.text
