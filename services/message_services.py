from urllib.parse import quote
import os
import asyncio
from fastapi import HTTPException
import os
from urllib.parse import quote
from httpx import AsyncClient, HTTPStatusError, RequestError
from typing import Dict, Any

import httpx

async def fetch_availability(settlement: str):
    internal_url = os.getenv("INTERNAL_URL")
    
    if not internal_url:
        raise ValueError("INTERNAL_URL environment variable is not set.")
    if not internal_url.startswith("http://") and not internal_url.startswith("https://"):
        raise ValueError("INTERNAL_URL must start with 'http://' or 'https://'")

    encoded_settlement = quote(settlement)
    external_api_url = f"{internal_url}/availability?settlement={encoded_settlement}"

    async def fetch_with_retry(url, retries=3):
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(url)
                
                if response.status_code == 200:
                    return response
                else:
                    if response.status_code == 500:
                        raise Exception(f"Internal server error: {response.status_code} - {response.text}")
                    else:
                        raise Exception(f"HTTP error occurred: {response.status_code} - {response.text}")

            except httpx.ReadTimeout:
                if attempt < retries - 1:
                    await asyncio.sleep(2)  # Wait before retrying
                else:
                    raise Exception("Request timed out after multiple retries")
            except httpx.RequestError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)  # Wait before retrying
                else:
                    raise Exception(f"Request failed: {str(e)}")

    try:
        response = await fetch_with_retry(external_api_url)
        
        # Debugging output
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)
        
        # Ensure response is in JSON format
        try:
            json_response = response.json()
            # Debugging output for json_response
            print("JSON Response:", json_response)
        except ValueError as ve:
            raise Exception("Response is not valid JSON. Received text: " + response.text) from ve

        names = extract_names(json_response)
        return names

    except Exception as e:
        # Log or print additional details for debugging
        print(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def extract_names(data):
    # Debugging output
    print("Data received in extract_names:", data)
    
    if isinstance(data, dict):
        available_residences = data.get('availableResidencesArray', [])
        names = [f"{hotel['residence']['name']}, {hotel['residence']['city']}" for hotel in available_residences]
        return names
    else:
        raise ValueError("Expected data to be a dictionary but got: " + str(type(data)))



from typing import Any, Dict
from httpx import AsyncClient, RequestError, HTTPStatusError
from fastapi import HTTPException
from urllib.parse import quote
import os

async def get_placement_if_exists(
    residence: str,
    place: str,
    id_number: str,
    people: str,
    phone_number: str
) -> Dict[str, Any]:
    """
    Checks if a placement exists by making a POST request to the reservation API.

    Args:
        residence (str): The name of the residence (e.g., hotel name).
        place (str): The name of the settlement/place.
        id_number (str): The identification number of the user.
        people (str): The number of people.
        phone_number (str): The user's phone number.

    Returns:
        Dict[str, Any]: A dictionary containing the status and the link if successful.

    Raises:
        HTTPException: If there is an error with the request or invalid input.
    """
    internal_url = os.getenv("INTERNAL_URL") + "/reserve"

    if not internal_url:
        raise ValueError("The 'INTERNAL_URL' environment variable is not set.")

    if not isinstance(residence, str):
        raise ValueError("The 'residence' parameter must be a string.")
    if not isinstance(place, str):
        raise ValueError("The 'place' parameter must be a string.")
    if not isinstance(id_number, str):
        raise ValueError("The 'id_number' parameter must be a string.")
    if not isinstance(people, str):
        raise ValueError("The 'people' parameter must be a string.")
    if not isinstance(phone_number, str):
        raise ValueError("The 'phone_number' parameter must be a string.")

    # Encode the residence and place parameters to handle special characters
    encoded_residence = quote(residence.split(',')[0].strip())
    encoded_place = quote(place)

    # Prepare the query parameters as a dictionary
    params = {
        "residence": encoded_residence,
        "settlement": encoded_place,
        "amount": people,
        "idNumber": id_number,
        "phoneNumber": phone_number
    }

    try:
        # Create a client with automatic redirection handling
        async with AsyncClient() as client:
            response = await client.post(internal_url, params=params, headers={"Content-Type": "application/json"})

        # Check if the response was successful
        if response.status_code in (200, 201):
            try:
                response_json = response.json()
                # Extract the status, link, and residence
                status = response_json.get("status")
                link = response_json.get("reservation", {}).get("link")
                residence = response_json.get("reservation", {}).get("residence")

                if status == "success" and link and residence:
                    return {"status": status, "link": link, "residence": residence}
                elif status == "success" and link:
                    return {"status": status, "link": link}
                else:
                    return {"status": status}
            except HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
            except RequestError as e:
                raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
        else:
            # Handle the error if the response is not successful
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

# async def main():
#     residence = "מלון דן"
#     place_value = "אבירים"
#     id_number = '3213223132121'
#     people = '2'
#     phone_number = '3123321312231'

#     result = await get_placement_if_exists(residence, place_value, id_number, people, phone_number)
#     print("Status:", result.get("status"))
#     print("Link:", result.get("link"))

# # Run the main function
# asyncio.run(main())