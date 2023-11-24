async def get_query(payload):
    """
    This function handles a user query and generate a response message.
    """
    query = payload['text']
    print("A candidate is asking : " + query)

    res = {
        "fulfillmentResponse": {
            "messages": [{
                "text": {
                    "text": [
                        "Thank you for contacting Maruti Techlabs."
                    ]
                }
            }]
        }
    }

    return res
