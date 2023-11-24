import json

import app.services.CX_Open_Jobs_Webhook as Jobs
import app.services.CX_Submit_Webhook as Submit
import app.services.CX_Status_Webhook as Status
import app.services.CX_Question_Webhook as Question
import app.services.CX_callerID_Webhook as callerID


async def handle_webhook(req):
    """
    This function handles an incoming webhook by performing some actions with the webhook data.
    """
    tag = req["fulfillmentInfo"]["tag"]
    if tag == "Job Openings":
        res = await Jobs.get_job_list()
    elif tag == "Submit":
        res = await Submit.submit_application(req)
    elif tag == "Status":
        res = await Status.get_status()
    elif tag == "Question":
        res = await Question.get_query(req)
    elif tag == "check":
        number = await callerID.get_caller_id(req)
        print(number)
        res = {}
    else:
        text = f"There are no fulfillment responses defined for {tag} tag"
        res = {"fulfillment_response": {"messages": [{"text": {"text": [text]}}]}}
    res = str(res)
    return res
