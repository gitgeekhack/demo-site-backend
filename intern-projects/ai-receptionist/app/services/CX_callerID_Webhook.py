async def get_caller_id(request):
    """
    This function retrieves the caller ID for the current incoming call.
    """
    # print(request["payload"]["telephony"]["caller_id"])
    # print(json.dumps(request,indent=4))
    caller_id = request["payload"]["telephony"]["caller_id"]
    return caller_id
