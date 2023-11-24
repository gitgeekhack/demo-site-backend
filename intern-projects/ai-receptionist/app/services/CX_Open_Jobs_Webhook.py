async def open_jobs():
    jobs = ['QA', 'SalesForce', '.NET', 'Data Science']
    return jobs

async def get_job_list():
    """
    This function retrieves a list of all available jobs in the system.
    """
    openings = await open_jobs()
    if len(openings) == 0:
        response = "Currently we have no openings, please enquire after some time"
    else:
        response = "We have openings in " + openings[0]
        for i in range(1, len(openings)):
            response = response + ", " + openings[i]
        response = response + ". Do you want to apply?"
    res = {
        "fulfillmentResponse": {
            "messages": [{
                "text": {
                    "text": [
                        response
                    ]
                }
            }]
        }
    }

    return res
