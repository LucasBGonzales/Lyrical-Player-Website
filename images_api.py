from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logger as log

# Get the URL for the first image retrieved from the given search term.
def getImageURL(search_term):
    # Start googleapiclient discovery service. 
    service = build("customsearch","v1", developerKey="AIzaSyAbkHE2KMDT2TrsMyF1boszVac-61mCJ1c")
    
    # Flag for successful retrieval
    bln_success = False
    
    # Get images
    try:
        res = service.cse().list(q=search_term,
                                 cx="010353834715554425105:0qjeydycvkx",
                                 searchType="image").execute()
        bln_success = True
    except HttpError:
        log.debug("images_api.getImageAPI(): " + "Failed to Get Image: HttpError: Probably ran out of daily limit.")
    except:
        log.debug("images_api.getImageAPI(): " + "Failed to Get Image. Unknown Error:")
    
    # Check length of returned list.
    if(len(res['items']) < 1):
        log.debug("images_api.getImageURL(): " + "No images were returned.")
        bln_success = False
    
    # Test for success. If so, return first item in list.
    if(bln_success):
        log.debug("images_api.getImageAPI(): " + "Sucess, returning: " + str(res['items'][0].get('link')).strip())
        return str(res['items'][0].get('link')).strip()
    log.debug("images_api.getImageAPI(): " + "Failure, returning \"\"")
    return ""
