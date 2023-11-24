async def submit_application(payload):
    """
    This function handles the submission of a job application and generates a response message.
    """
    args = payload['sessionInfo']['parameters']
    notice_period = args['duration']['original']
    experience = args['duration1']['original']
    cur_ctc = args['number']
    exp_ctc = args['number1']
    field = args['technology']

    response = f"We have a application in {field}, with current CTC of {cur_ctc} and expecting {exp_ctc}. He has " \
           f"experience of {experience}, he can join in {notice_period}."

    print("New Application : " + response)

    res = {
        "fulfillmentResponse": {
            "messages": [{
                "text": {
                    "text": [
                        "We have received your application please expect a call back from us."
                    ]
                }
            }]
        }
    }

    return res
