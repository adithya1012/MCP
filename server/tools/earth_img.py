import datetime
import os
from typing import Any
import httpx
# from mcp.server.fastmcp import FastMCP

async def get_earth_image_definition(earth_date: Any = None, type: Any = None) -> str:
    """Request to Earth Polychromatic Imaging Camera (EPIC) API. Fetch satellite images of Earth from NASA's DSCOVR satellite.\n
    Parameters:\n
        - earth_date: (optional) Date when the photo was taken. This should be in "YYYY-MM-DD" format. If not provided, will get latest available images.\n
        - type: (optional) Type of image to retrieve. Options are:\n
            "natural" - Natural color images (default)\n
            "enhanced" - Enhanced color images\n
    """

    base_api = "https://epic.gsfc.nasa.gov/api/"
    
    # Build URL
    param_url = base_api
    
    # Handle image type
    if type:
        if type.lower() in ["natural", "enhanced", "aerosol", "cloud"]:
            param_url += f"{type.lower()}/"
        else:
            return f"Error: Invalid type '{type}'. Valid options: 'natural', 'enhanced','aerosol', 'cloud'"
    else:
        param_url += "natural/"
        
    
    # Handle date parameter
    if earth_date:
        try:
            datetime.datetime.strptime(earth_date, "%Y-%m-%d")
            year, month, day = earth_date.split("-")
            param_url += f"date/{year}-{month}-{day}"
        except ValueError:
            return "Error: earth_date must be in YYYY-MM-DD format"
    
    try:
        print(f"Calling EARTH API FUNCTION with URL: {param_url}")
        
        # Make API request
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
        ) as client:
            response = await client.get(param_url, timeout=30.0)
            # return param_url
            response.raise_for_status()
            
            data = response.json()
            
            # Check if images were found
            if not data or len(data) == 0:
                return "No images found for the specified parameters"
            
            # Extract image information from first result
            first_image = data[0]
            image_date = first_image["date"]
            image_name = first_image["image"]
            caption = first_image.get("caption", "No caption available")
            
            # Parse date to build archive URL
            # Date format is typically "2015-10-31 00:36:33" or "2015-10-31"
            date_parts = image_date.split("-")
            year = date_parts[0]
            month = date_parts[1]
            
            # Handle day extraction (might have time component)
            day_part = date_parts[2]
            if " " in day_part:
                day = day_part.split(" ")[0]
            else:
                day = day_part
            
            # Use the type from URL (natural or enhanced)
            image_type = "natural"
            if "enhanced" in param_url:
                image_type = "enhanced"
            elif "aerosol" in param_url:
                image_type = "aerosol"
            elif "cloud" in param_url:
                image_type = "cloud"
            
            
            # Build final image URL
            final_image_url = f"https://epic.gsfc.nasa.gov/archive/{image_type}/{year}/{month}/{day}/png/{image_name}.png"
            
            # Build result string
            result = f"Earth Image Found!\n"
            result += f"Image URL: {final_image_url}\n"
            result += f"Caption: {caption}\n"
            result += f"Date: {image_date}\n"
            result += f"Image Type: {image_type.title()}\n"
            result += f"Total images available: {len(data)}"
            
            return result+" "+ param_url
            # return param_url
            
    except httpx.TimeoutException:
        return "Error: Request timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"