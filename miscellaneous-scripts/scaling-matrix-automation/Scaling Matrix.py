import pandas
import numpy
from datetime import datetime


def create_matrix(filepath):
    service_names = {
        "nlp-flow-documentsplitter": [],
        "nlp-flow-textclassifier": [],
        "nlp-flow-layout-segmentation": [],
        "nlp-flow-handwritten-detection": [],
        "Textract async - TensorIOT": [],
        "nlp-flow-section-classification": [],
        "nlp-flow-checkbox-mark-detection": [],
        "nlp-flow-encounter-detection": [],
        "nlp-flow-entity-extraction": []
    }

    service_time = {
        "nlp-flow-documentsplitter": [],
        "nlp-flow-textclassifier": [],
        "nlp-flow-layout-segmentation": [],
        "nlp-flow-handwritten-detection": [],
        "Textract async - TensorIOT": [],
        "nlp-flow-section-classification": [],
        "nlp-flow-checkbox-mark-detection": [],
        "nlp-flow-encounter-detection": [],
        "nlp-flow-entity-extraction": []
    }

    data = pandas.read_csv(filepath)

    min_time_list = data.groupby(by=["app"])["timestamp"].min()
    max_time_list = data.groupby(by=["app"])["timestamp"].max()
    index = 0
    for x in service_names:
        if x != "nlp-flow-section-classification" and x != "Textract async - TensorIOT" and x != "nlp-flow-checkbox-mark-detection":
            if index != 0:
                y = list(service_names.keys())[index - 1]
            else:
                y = "nlp-flow-documentsplitter"
            if x == "nlp-flow-textclassifier":
                datetime_string = max_time_list[y]
            else:
                datetime_string = min_time_list[y]
            dt_object = datetime.fromisoformat(datetime_string[:-6])
            time = dt_object.time().strftime("%I:%M:%S %p")
            service_names[x].append(time)

        if x != "Textract async - TensorIOT":
            datetime_string = max_time_list[x]
            dt_object = datetime.fromisoformat(datetime_string[:-6])
            time = dt_object.time().strftime("%I:%M:%S %p")
            service_names[x].append(time)
        index += 1

    section_classification_start = data.groupby(by=["message"])["timestamp"].min()["Section Classification Started."]
    dt_object = datetime.fromisoformat(section_classification_start[:-6])
    time = dt_object.time().strftime("%I:%M:%S %p")
    service_names["nlp-flow-section-classification"].insert(0, time)

    timestamp = data.groupby(by=["app", "message"])["timestamp"].max()
    check_box_start = []
    tensor_iot_start = []
    tensor_iot_end = []
    for index in timestamp.index:
        if "nlp-flow-section-classification" == index[0] and "nlp-flow completed" in index[1]:
            check_box_start.append(timestamp[index])
        if "nlp-flow-handwritten-detection" == index[0] and "nlp-flow completed" in index[1]:
            tensor_iot_start.append(timestamp[index])
        if "nlp-flow-section-classification" == index[0] and "Section Classification Started." in index[1]:
            tensor_iot_end.append(timestamp[index])

    dt_object = datetime.fromisoformat(min(check_box_start)[:-6])
    time = dt_object.time().strftime("%I:%M:%S %p")
    service_names["nlp-flow-checkbox-mark-detection"].insert(0, time)

    dt_object = datetime.fromisoformat(min(tensor_iot_start)[:-6])
    time = dt_object.time().strftime("%I:%M:%S %p")
    service_names["Textract async - TensorIOT"].append(time)

    dt_object = datetime.fromisoformat(max(tensor_iot_end)[:-6])
    time = dt_object.time().strftime("%I:%M:%S %p")
    service_names["Textract async - TensorIOT"].append(time)

    for x in service_names:
        start = datetime.strptime(service_names[x][0], "%I:%M:%S %p")
        end = datetime.strptime(service_names[x][1], "%I:%M:%S %p")
        time_taken = end - start
        service_names[x].append(str(time_taken))

    batch_id = int(data.groupby(by=["app"])["batch_id"].max()["nlp-flow-handwritten-detection"])
    handwritten = list(numpy.zeros(batch_id))
    section = list(numpy.zeros(batch_id))
    diff = list(numpy.zeros(batch_id))

    for i, r in data.iterrows():
        if "nlp-flow completed" in r["message"]:
            s = r["message"].replace("nlp-flow completed in [", "")
            s = s.replace(" seconds]", "")
            service_time[r["app"]].append(float(s))
            if r["app"] == "nlp-flow-handwritten-detection":
                handwritten[int(r["batch_id"] - 1)] = r["timestamp"]
        if r["app"] == "nlp-flow-section-classification" and r["message"] == "Section Classification Started.":
            section[int(r["batch_id"] - 1)] = r["timestamp"]

    for x in service_time:
        if service_time[x]:
            minutes, seconds = divmod(max(service_time[x]), 60)
            hours, minutes = divmod(minutes, 60)
            service_names[x].append(f"{int(hours):02d}:{int(minutes):02d}:{seconds:02.0f}")

    for x in range(batch_id):
        start = datetime.fromisoformat(handwritten[x][:-6])
        end = datetime.fromisoformat(section[x][:-6])
        time_taken = end - start
        diff[x] = str(time_taken)[:-7]
    service_names["Textract async - TensorIOT"].append(max(diff))
    for x in service_time:
        print(x, service_names[x])

    res = pandas.DataFrame(service_names).T
    res.index.name = "Service_Name"
    res.columns = ["Start Time", "End Time", "SLA Time (Mins)", "Service Max Time (Mins)"]
    res.to_csv(f"Scaling_Matrix_{datetime.now()}.csv")


create_matrix(filepath="All-Messages-search-result (3).csv")
