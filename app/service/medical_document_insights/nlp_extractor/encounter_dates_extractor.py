from datetime import datetime
import boto3
import os
import re
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.bedrock import Bedrock
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document


class BedrockDatesExtractor:
    def __init__(self):
        # Initialize the Textract client
        os.environ['AWS_PROFILE'] = "default"
        os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
        self.bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.loaded_llm = self.load_llm_model()

    def load_llm_model(self):
        modelId = "cohere.command-text-v14"
        llm = Bedrock(
            model_id=modelId,
            model_kwargs={
                "max_tokens": 4000,
                "temperature": 0.75,
                "p": 0.01,
                "k": 0,
                "stop_sequences": [],
                "return_likelihoods": "NONE",
            },
            client=self.bedrock,
        )
        return llm

    def generate_response(self, raw_text, llm):
        # Instantiate the LLM model
        llm = llm
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000, chunk_overlap=200
        )
        texts = text_splitter.split_text(raw_text)
        # Create multiple documents
        docs = [Document(page_content=t) for t in texts]

        query = """
        'Encounter Date' in medical records refers to the specific day when a patient had an interaction with a healthcare provider. This could be a visit to a clinic, a hospital admission, a telemedicine consultation, or any other form of medical service. The encounter date is important for tracking patient care, scheduling follow-up appointments, billing, and medical research.
        'Event' which is associated with the corresponding 'Encounter Date' is described as all the activities which are happened on that particular 'Encounter Date'.
        Above text is obtained from the medical record. Give all the actual 'Encounter Date' and corresponding 'Event' in the following JSON format { Encounter Date : Event }. Strictly maintain the given format of JSON.
        Note: Convert all the 'Encounter Date' in 'dd/mm/yyyy' format. Describe events in more detailed manner.
        """
        chain_qa = load_qa_chain(llm, chain_type="refine")
        temp = chain_qa.run(input_documents=docs, question=query)
        return temp

    def data_formatter(self, json_data):
        raw_text = "".join(json_data.values())
        return raw_text

    if __name__ == "__main__":
        json_data = {
            "Page 1": "ROS-HOSPITALS Parmar, Maya 1600 EUREKA ROAD MRN: 110005243704, DOB: 2/7/1974, Sex: F KAISER FOUNDATION HOSPITALS ROSEVILLE CA 95661-3027 Adm: 6/27/2019, D/C: 6/27/2019 Hospital Record LAPAROSCOPIC HYSTERECTOMY N/A 6/27/2019 Performed by Lindgren, Leslie Rae (M.D.) at ROS-MAIN1-OR LAPAROSCOPIC SALPINGO OOPHORECTOMY Bilateral 6/27/2019 Performed by Lindgren, Leslie Rae (M.D.) at ROS-MAIN1-OR SHOULDER ARTHROSCOPY Right 7/27/2017 Performed by Voigtlander, James Patrick (M.D.) at ROS-MAIN1-OR Physical Exam: BP 112/68 I Ht 5' 7\" I Wt 80.5 kg (177 lb 8 oz) I LMP 06/13/2019 BMI 27.80 kg/m\u00b2 Well nourished woman in no apparent distress Abdomen: no masses, soft, non tender, incisions well healed External genitalia: no lesions Vagina: no lesions, normal discharge, cuff intact, not tender Adnexa: non tender, no masses Assessment/Plan: 1. Postop visit. 4 weeks s/p TLHBSO Doing very well, follow up prn Electronically signed by Lindgren, Leslie Rae (M.D.) on 7/25/2019 5:27 PM Encounter on 6/26/2019 Progress Notes Author Status Last Editor Updated Created Lindgren, Leslie Rae Signed Lindgren, Leslie Rae 6/26/2019 2:42 PM 6/26/2019 2:38 PM (M.D.) (M.D.) Gynecology History & Physical / Consult Note Maya Parmar is a 45 Y old female. Chief Complaint: preop History of Present Illness: Maya Parmar is a 45 Y female with a long history of endometriosis, severe dysmenorrhea and pelvic pain. She had been managed medically with good results until recently. She is scheduled for a Total laparoscopic hysterectomy ,bilateral salpingo oophorectomy. Past Medical History / Past Surgical History: Active Ambulatory Problems Diagnosis Date Noted *OTHER MR # EXISTS PELVIC PERITONEUM ENDOMETRIOSIS 04/09/2008 HYPOTHYROIDISM 07/22/2009 PREMENSTRUAL DYSPHORIC DISORDER 02/07/2011 Generated on 4/21/20 3:09 PM ",
            "Page 2": "ROS-HOSPITALS Parmar, Maya 1600 EUREKA ROAD MRN: 110005243704, DOB: 2/7/1974, Sex: F KAISER FOUNDATION HOSPITALS ROSEVILLE CA 95661-3027 Adm: 6/27/2019, D/C: 6/27/2019 Hospital Record NONTRAUMATIC COMPARTMENT SYNDROME OF LEG. 04/03/2012 IMPINGEMENT SYNDROME OF RIGHT SHOULDER 01/11/2013 ADHD, PREDOMINANTLY INATTENTIVE PRESENTATION 09/23/2013 IRRITABLE BOWEL SYNDROME 01/21/2016 MEDI-CAL GMC CARE COORDINATION 09/06/2016 CERVICAL DISC DEGENERATION 02/28/2017 POSTTRAUMATIC STRESS DISORDER 03/17/2017 BULIMIA NERVOSA, IN FULL REMISSION 03/17/2017 CASE / CARE MGMT, CHRONIC PAIN MGMT 07/17/2018 ADMINISTRATIVE ENCOUNTER FOR LEVEL II PAIN GROUP 07/17/2018 SERIES CERVICAL RADICULOPATHY 10/05/2018 FEMALE PELVIC PAIN 10/15/2018 DYSMENORRHEA 10/15/2018 ENDOMETRIOSIS 10/15/2018 IMPINGEMENT SYNDROME OF LEFT SHOULDER 11/16/2018 ADULT OBSTRUCTIVE SLEEP APNEA, MILD 03/05/2019 CHRONIC FEMALE PELVIC PAIN 05/21/2019 GENERALIZED ANXIETY DISORDER 05/30/2019 Additional diagnoses from the Past Medical History section Diagnosis Date ADHD, PREDOMINANTLY INATTENTIVE PRESENTATION 9/23/2013 Eating disorder, in remission. FEMALE PELVIC PAIN 1/25/2008 HYPOTHYROIDISM 7/22/2009 IMPINGEMENT SYNDROME OF RIGHT SHOULDER 1/11/2013 IRRITABLE BOWEL SYNDROME 1/21/2016 PELVIC PERITONEUM ENDOMETRIOSIS 4/9/2008 PREMENSTRUAL DYSPHORIC DISORDER UNSPECIFIED HYPOTHYROIDISM Past Surgical History: Procedure Laterality Date ARTHROSCOPY SHOULDER W DECOMPRESSION Left 4/16/2019 Performed by Voigtlander, James Patrick (M.D.) at FOL-ASU-OR ARTHROSCOPY SHOULDER W PARTIAL 1/11/2013 ACROMIOPLASTY Performed by Voigtlander, James Patrick (M.D.) at FOL-ASU-OR DIAGNOSTIC LAPAROSCOPY 4/2008 Laparoscopy, Diagnostic-endometriosis FASCIOTOMY 5/17/2012 Performed by VOIGTLANDER, JAMES PATRICK (M.D.) at FOL-ASU-OR SHOULDER ARTHROSCOPY Right 7/27/2017 Performed by Voigtlander, James Patrick (M.D.) at ROS-MAIN1-OR Allergies: Ibuprofen; Penicillins class; Adhesive tape; Amoxicillin; and Chlorhexidine Generated on 4/21/20 3:09 PM ",
            "Page 3": "ROS-HOSPITALS Parmar, Maya 1600 EUREKA ROAD MRN: 110005243704, DOB: 2/7/1974, Sex: F KAISER FOUNDATION HOSPITALS ROSEVILLE CA 95661-3027 Adm: 6/27/2019, D/C: 6/27/2019 Hospital Record Active Medication: Outpatient Medications Marked as Taking for the 6/26/19 encounter (Pre-Op) with Lindgren, Leslie Rae (M.D.) Medication oxyCODONE (ROXICODONE) 5 mg Oral Tab Ondansetron (ZOFRAN) 4 mg Oral Tab Estrogens-methyITESTOSTERone (EEMT HS) 0.625-1.25 mg Oral Tab Social History: Social History Tobacco Use Smoking status: Never Smoker Smokeless tobacco: Never Used Substance Use Topics Alcohol use: Not Currently Drug use: No Family History: Family History Problem Relation Age of Onset Diabetes Other MOTHER SIDE Osteoporosis Mother Endometriosis Mother Thyroid Cancer Father Breast Cancer None Ovarian Cancer None Cervical Cancer None Uterine Cancer None Colon Cancer None Heart Disease None None pertinent, reviewed with patient. OB History Gravida Para Term Preterm AB Living 3 2 2 0 1 2 SAB TAB Ectopic Multiple 0 1 0 0 Review of Systems: Constitutional: Oriented and no fever, unexpected weight loss/gain, or fatigue Cardiovascular: No chest pain, irregular heart beat, hypertension, or clots in legs or lungs Respiratory: No wheezing, coughing, or shortness of breath Musculoskeletal: No muscle pain or swollen joints Neurologic: No numbness, headaches, or weakness Generated on 4/21/20 3:09 PM ",
            "Page 4": "ROS-HOSPITALS Parmar, Maya 1600 EUREKA ROAD MRN: 110005243704, DOB: 2/7/1974, Sex: F KAISER FOUNDATION HOSPITALS ROSEVILLE CA 95661-3027 Adm: 6/27/2019, D/C: 6/27/2019 Hospital Record Vitals: BP 119/75 (Site: Left arm, Position: Sitting, Cuff Size: Large adult) Pulse 83 I Temp 96.9 \u00b0F (36.1 \u00b0C) (Oral) Resp 16 I Ht 5' 7\" I Wt 82,6 kg (182 lb) I BMI 28.51 kg/m\u00b2 Physical Exam: Constitutional: Oriented, well developed, well nourished, no acute distress Neck: Supple, no thyromegaly or adenopathy Respiratory: Clear to auscultation, normal respirations Cardiovascular: Heart has regular rate and rhythm, no murmur Abdomen: Nontender, no masses or distention, no hepatosplenomegaly Vulva: No lesions Vagina: No Unusual Discharge or Erythema Cervix: No lesions, discharge or erythema, no cervical motion tenderness Uterus: Normal Size,Shape, and Contour; Nontender Adnexa: no masses or tenderness Perineum, Anus and Rectum: No lesions; confirms bimanual Recent Labs: Basename Value Date/Time HGB 13.5 06/21/2019 WBC COUNT 9.8 06/21/2019 Recent Labs 06/21/19 0818 BHCG <1 Review of Other Relevant Data/Labs: none Assessment and Plan: 1. Preop visit. scheduled for Total Laparoscopic hysterectomy, bilateral salpingo oophorectomy possible laparotomy for endometriosis. 2. Consent: We have discussed alternative options such as OCP'S, IUD and endometrial ablation, but she wants definative therapy. We discussed risks of bleeding, infection and damage to the surrounding organs. She understands that if the procedure cannot be performed Laparoscopically she will need a laparotomy. All of her questions were answered and consent was printed and given to her 3. Postop pain: ibuprofen, tylenol, oxycodone gabapentin 4. Postop nausea: emend, zofran scop 5. Postop bowel management: mineral oil, miralax 6. Postop disposition: home 7. Ovaries: She does want her ovaries to be removed. We had a long discussion about surgical menopause. Will start estratest postop Generated on 4/21/20 3:09 PM "
        }

    extractor = BedrockDatesExtractor()
    raw_text = extractor.data_formatter(json_data)
    result_string = extractor.generate_response(raw_text, extractor.loaded_llm)

    # Use a regular expression to find the dictionary in the string
    dict_string = re.search(r'\{.*?\}', result_string, re.DOTALL).group()
    # Use the json.loads function to convert the string into a dictionary
    result_json = json.loads(dict_string)
    # Convert the keys to datetime objects and store in a new dictionary
    result_with_datetime_keys = {datetime.strptime(date, '%m/%d/%Y'): event for date, event in result_json.items()}
    # Sort the dictionary by keys (i.e., dates) in ascending order
    sorted_result = dict(sorted(result_with_datetime_keys.items()))
    # Convert the datetime objects back to strings
    sorted_result_with_string_keys = {date.strftime('%m/%d/%Y'): event for date, event in sorted_result.items()}

    output_json = sorted_result_with_string_keys
    return output_json