import random

async def __status():
    statuses = ['Screening', 'Initial Round', 'Technical Round', 'HR Round', 'Final Round']
    return random.choice(statuses)

async def get_status():
    """
    This function retrieves the current status of an application and generates a response message.
    """
    current_status = await __status()
    str = "Your Application is under " + current_status + "."
    res = {
        "fulfillmentResponse": {
            "messages": [{
                "text": {
                    "text": [
                        str
                    ]
                }
            }]
        }
    }

    return res
