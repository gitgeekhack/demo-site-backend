import os

USER_DATA_PATH = os.getenv("USER_DATA_PATH")


class AWS:
    class BotoClient:
        AWS_KEY_PATH = "user-data"
        AWS_DEFAULT_REGION = "us-east-1"
        read_timeout = 3600
        connect_timeout = 3600

    class S3:
        MEDICAL_BUCKET_NAME = 'ds-medical-insights-extractor'
        ENCRYPTION_KEY = eval(os.getenv("S3_ENCRYPTION_KEY"))


class AllowedFileType:
    IMAGE = ['jpg', 'png', 'jpeg']
    PDF = ['pdf']


class ExceptionMessage:
    INVALID_FILE_EXCEPTION_MESSAGE = 'Input file is invalid'
    FAILED_TO_DOWNLOAD_FILE_FROM_URL_EXCEPTION_MESSAGE = 'Unable to download file from url'
    NO_IMAGE_FOUND_EXCEPTION_MESSAGE = "Unable to find image in PDF"
    FILE_LIMIT_EXCEEDED_EXCEPTION_MESSAGE = "File limit exceeded, only upload file upto 25 MB"
    MAX_FILE_SIZE_EXCEEDED_ERROR = "File limit exceeded, only upload file upto 100 MB"
    FILE_PATH_NULL_EXCEPTION_MESSAGE = "File is not uploaded"
    INPUT_QUERY_NULL_EXCEPTION_MESSAGE = "Input query is empty or null"
    MULTIPLE_FILE_UPLOADED_EXCEPTION_MESSAGE = "Multiple files are uploaded, only upload single file"
    MISSING_REQUEST_BODY_EXCEPTION_MESSAGE = "Missing request body in the request"
    INVALID_REQUEST_BODY_EXCEPTION_MESSAGE = "Invalid request body received"
    FILE_UPLOAD_LIMIT_REACHED_EXCEPTION_MESSAGE = "Uploaded more than {x} files"
    TOTAL_PAGE_EXCEEDED_EXCEPTION_MESSAGE = "Combined document pages must not exceed {page_count_threshold}. Please upload fewer pages."
    FOLDER_PATH_NULL_EXCEPTION_MESSAGE = "Project not uploaded"


class MedicalInsights:
    AWS_BUCKET = "ds-medical-insights-extractor"
    TOTAL_PAGES_THRESHOLD = 1000
    REQUEST_FOLDER_NAME = "request"
    RESPONSE_FOLDER_NAME = "response"
    EMBEDDING_FOLDER_NAME = "embeddings"
    TEXTRACT_FOLDER_NAME = "textract_response"
    PREFIX = "s3://ds-medical-insights-extractor/"
    EMBEDDING_PICKLE_FILE_NAME = "embeddings.pkl"
    EMBEDDING_FAISS_FILE_NAME = "embeddings.faiss"
    S3_FOLDER_NAME = 'user-data'
    LOCAL_FOLDER_NAME = 'static'
    OUTPUT_FILE_NAME = 'output.json'

    class Prompts:
        PROMPT_TEMPLATE = """
        Human: Use the following pieces of context to provide a concise answer to the question at the end. If you don't know the answer, don't try to make up an answer.
        <context>
        {context}
        </context>

        Question: {question}

        Assistant:
        """

        PHI_PROMPT = """
        Your role is to extract important dates from a medical document, specifically focusing on the injury dates, admission dates, and discharge dates. This information is vital for medical records management and analysis. Your sole purpose is to provide the output in JSON format, without any additional text output.Don't refine anything, give an original answer.
        Provide the information in JSON format as follows: {"Injury Date": ["dd/mm/yyyy", ...], "Admission Date": ["dd/mm/yyyy", ...], "Discharge Date": ["dd/mm/yyyy", ...]}. Strictly maintain the consistency in this format.
        Note: Don't include visit dates, encounter dates, date of birth, MRI scan dates, X-ray dates, checkup dates, admin date/time, follow-up dates and 'filed at' date. Avoid including times in the output.

        Here is the definition of valid Injury Date, Admission Date and Discharge Date:
        Injury Date: In the medical field context, the injury date refers to the specific date on which a patient sustained an injury or trauma. Accident date of patient is also considered as injury date. It is the date when the event leading to the patient's medical condition or injury occurred.
        Admission Date: The admission date, in the medical field context, refers to the date on which a patient is formally admitted to a healthcare facility, such as a hospital. It marks the beginning of the patient's stay for medical evaluation, treatment, or surgery.
        Discharge Date: The discharge date, in the medical field context, refers to the date when a patient is released or discharged from a healthcare facility after receiving medical care or treatment. It marks the end of the patient's stay in the facility.

        Instructions:
        1. 'Injury Date': Extract the date of the patient's injury from the given medical text. There can be multiple injury dates present in the text. If the injury date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "injury date" as the key.
        2. 'Admission Date': Extract the date of the patient's admission from the given medical text. There can be multiple admission dates present in the text. Consider the date of the initial examination, initial visit, or the first time the patient was seen in as the admission date. The date with labels such as "Admit date" or "Admission date" should be considered as the admission date. If the admission date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "admission date" as the key.
        3. 'Discharge Date': Extract the date of the patient's discharge from the given medical text. There can be multiple discharge dates present in the text. Consider the date of the last visit or the last time the patient was seen as the discharge date. The date with labels such as "Discharge date" or "Date of Discharge" should be considered as the discharge date. If the discharge date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "discharge date" as the key.

        Note: Convert the final output to dd/mm/yyyy format
        """

        DOC_TYPE_PROMPT = """
        You are provided with a text excerpt from a medical report. Your task is to determine the type of document based on its content and context. Utilize the following definitions as guidelines for classification:

        Ambulance: A medical report generated by emergency medical services (EMS) following an ambulance call. It includes patient identification, medical details, clinical observations, incident information, transport details, insurance and billing information, narrative notes, and crew information, serving as a comprehensive account for legal, billing, and medical record purposes.
        Emergency: An Emergency Department Report is a detailed and structured medical document that chronicles the events and clinical management of a patient's acute visit to the emergency department.

        Carefully analyze the medical text excerpt and determine the most appropriate document type based on its characteristics. Don't include your analysis in the response. If the document type matches one of the categories given, strictly respond in the following format:
        {"document_type": "Identified_Document_Type"}.

        If the report is not from any above categories, give the response in following format:
        {"document_type": "Other"}
        """

        ENCOUNTER_PROMPT = """
        Above text is obtained from medical records. Based on the information provided, you are tasked with extracting the 'Encounter Date' and corresponding 'Event' from medical records.

        'Encounter Date' : In medical record, it is defined as the specific date when a patient had an interaction with a healthcare provider. This could be a visit to a clinic, a hospital admission, a telemedicine consultation, or any other form of medical service.
        Notes to keep in mind while extracting 'Encounter Date' :
        - Extract only actual 'Encounter Date' and avoid giving any other types of dates which are listed below :
          1. 'Birth date' : In medical record, it is defined as the specific date when a patient is born. It is typically recorded and used for identification, legal, and administrative purposes. It is also used to calculate a person's age.
          2. 'Received date' : In medical record, it is defined as the specific date when a lab, hospital, or clinic received the test result.
          3. 'Printed date' : In medical record, it is defined as the specific date when the document was created, updated, or reviewed.
          4. 'Resulted date' : In medical record, it is defined as the specific date when the results of certain tests, procedures or treatments are made available or reported.
        - Ensure all the actual 'Encounter Date' are strictly converted to the same format of 'MM/DD/YYYY'.
        - Ensure none of the actual 'Encounter Date' is left behind. Ensure dates from Past Medical History / Past Surgical History are also included.

        'Event' : It is associated with the corresponding 'Encounter Date'. It is described as the summary of all activities that occurred on that particular 'Encounter Date'.
        Notes to keep in mind while extracting 'Event' :
        - Ensure all 'Event' descriptions should include the key points, context, and any relevant supporting details.
        - Also ensure all 'Event' descriptions are more detailed, thorough and comprehensive yet a concise summary in medium-sized paragraph.

        'Reference' : It is an exact reference text from the medical record which is most relevant to the extracted date and event.
        Notes to keep in mind while extracting 'Reference' :
        - Ensure to provide the exact reference text avoiding any deviations from the original text.
        - Strictly ensure to restrict the length of 'Reference' to the medium-sized phrase.
        - Ensure to provide the 'Reference' in the json format as below :
        {
          'Reference' : "Reference"
        }

        You are required to present this output in a specific format using 'Tuple' and 'List'.
        Strictly adhere to the format explained as below and strictly avoid giving output in any other format.
        'Tuple' : It is used to store multiple items - in this case, the 'Encounter Date' and 'Event'. It is created using parentheses and should be formatted as ("Encounter Date", "Event", "Reference").
        'List' : It is used to store multiple items - in this case, the 'Tuple'. It is created using square brackets and should be formatted as [ ("Encounter Date", "Event", "Reference") ].
        Additionally, arrange all tuples in the list in ascending or chronological order based on the 'Encounter Date'.
        Note: This extraction process is crucial for various aspects of healthcare, including patient care tracking, scheduling follow-up appointments, billing, and medical research. Your attention to detail and accuracy in this task is greatly appreciated.
        """

        PATIENT_INFO_PROMPT = """
        Your task is to identify the valid name and the date of birth of the patient from the user-provided text without including additional information, notes, and context. 

        Please follow the below guidelines:
        1) Consider Date of Birth, Birth Date, and DOB as date_of_birth.
        2) Do not consider age as value in date_of_birth.
        3) Consider Patient Name, only Patient, only Name and RE as patient_name.

        Please strictly only provide a JSON result containing the keys 'patient_name' and 'date_of_birth' containing a string as a value.
        """

        ENTITY_PROMPT = """
        Your task is to identify valid diagnoses, valid treatments and valid medications from the user-provided text without including additional information, notes, and context. 

        The definition of a valid diagnosis, valid treatment and valid medications is given below:
        Diagnosis: It is a process of identifying a patient's medical condition based on the evaluation of symptoms, history, and clinical evidence.
        Treatment: It is a proven, safe, and effective therapeutic intervention aligned with medical standards, to manage or cure a diagnosed health condition.
        Medication: It refers to drugs or substances used to treat, prevent, or diagnose diseases, relieve symptoms, or improve health.

        Please follow the below guidelines:
        1. Do not consider any diagnosis, treatment or medication information with negation.
        2. Do not misinterpret the symptoms as diagnoses or treatments.
        3. Associate the system organs and direction of organs with the medical entities.
        4. Ensure a clear distinction between diagnosis, treatment and medications entities, avoiding overlap.
        5. Consider Signs and Medical Conditions as a diagnosis. 
        6. Consider Surgery, Psychotherapy, Immunotherapy, Imaging tests, and procedures as a treatment. 
        7. Do not consider any diagnosis or treatment with hypothetical or conditional statements.
        8. Do not consider the specialty of the doctor or practitioner as a medical entity.
        9. Avoid repeating diagnoses and treatments when different terms refer to the same medical condition or treatment.

        Please strictly only provide a JSON result containing the keys 'diagnosis', 'treatments' and 'medications' containing a list of valid entities.
    """

        SUMMARY_PROMPT = """Generate a detailed and accurate summary based on the user's input. Specifically, concentrate on identifying key medical diagnoses, outlining treatment plans, and highlighting pertinent aspects of the medical history. Strive for precision and conciseness to deliver a focused and insightful summary."""

        CONCATENATE_SUMMARY = "Concatenate the summaries and remove the duplicate information from the summaries and make one summary without losing any information."

    class TemplateResponse:
        SUMMARY_RESPONSE = "It seems that the PDF you provided is blank. Unfortunately, I can't generate a summary from empty content. Please upload a PDF with readable text."
        PHI_RESPONSE = {'patient_information': {'admission_dates': ['None'], 'date_of_birth': 'None',
                                                'discharge_dates': ['None'], 'injury_dates': ['None'],
                                                'patient_name': 'None'}}
        QNA_RESPONSE = {'query': "", 'result': "It seems that the PDF document is empty", 'source_documents': []}

    class LineRemove:
        SUMMARY_FIRST_LINE_REMOVE = [
            'Based on the provided medical report, here is a summary of the key information:',
            'Here is a detailed and accurate summary based on the provided medical notes:',
            'Here is a consolidated summary without duplicate information:',
            'Based on the consultation note, the key points are:']
