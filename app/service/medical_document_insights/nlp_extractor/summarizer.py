import boto3
import os
from langchain.llms.bedrock import Bedrock
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain


class LanguageModelWrapper:
    def __init__(self, model_id, aws_profile, aws_default_region):
        os.environ['AWS_PROFILE'] = aws_profile
        os.environ['AWS_DEFAULT_REGION'] = aws_default_region

        self.bedrock = boto3.client('bedrock-runtime', region_name=aws_default_region)
        self.modelId = model_id

        self.llm = Bedrock(
            model_id=self.modelId,
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

    def get_num_tokens(self, text):
        return self.llm.get_num_tokens(text)

    def generate_summary(self, text, chunk_size):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200)
        texts = text_splitter.split_text(text)

        docs = [Document(page_content=t) for t in texts]

        chain = load_summarize_chain(self.llm, chain_type='refine')
        summary = chain.run(docs)

        summary_dict = {
            "summary": summary
        }
        return summary_dict


if __name__ == "__main__":
    model_id = "cohere.command-text-v14"
    aws_profile = "maruti-root"
    aws_default_region = "us-east-1"

    language_model = LanguageModelWrapper(model_id, aws_profile, aws_default_region)

    data = {
        "Page 1": "MOBIN NEUROSURGERY FARDAD MOBIN, M.D., F.A.A.N.S Diplomate of the American Board of Neurological Surgeons Minimally Invasive Spine and General Neurosurgery Fellowship Trained Neurological Surgeon April 26, 2017 RE: SAILOR, DEBORAH DOB: 06/27/1957 DOI: 02/09/2015 NEUROSURGICAL POSTOPERATIVE EVALUATION I evaluated the patient in clinic on April 26, 2017. INTERIM HISTORY: She is status post lumbar decompressive surgery L3-4, L4-5 level with interspinous device arthrodesis fusion on April 10, 2017. She has done well postoperatively. She is very happy with the result of the operation. She is able to sit, stand and ambulate almost independently. She is using a walker for long distance ambulation. She is not reporting any fever, chills or drainage from her incision. She states that her burning sensations in the leg are significantly improved. She continues to have spasms of lower back. She is taking Norco and Flexeril as needed. She states that the Flexeril is not helping. She states that she has had much better improvement with Soma on the past. CURRENT STATUS: Lower back pain is presently 3-8/10 intensity. She states that her spasms are 8/10 intensity in the muscles. MEDICATIONS: Include Norco, Flexeril, metformin and additional diabetic pills. She states that her finger sticks are running about 130. PHYSICAL EXAMINATION: On examination, she is 5 feet and 8 inches tall, 169 pounds. She is pleasant, well-nourished, and well-developed woman. Examination of back shows healing midline incision. There is no evidence of fluctuance, drainage or erythema. She is able to sit, stand and ambulate independently. There is no edema or erythema in the lower extremities. DIAGNOSTIC IMPRESSION: 1. Status post interbody fusion stabilization L4-5 level, decompressive surgery L3-4 level. 2. Improvement in overall lumbar radiculopathy. 3. Postoperative spasms. 8929 Wilshire Blvd., Suite 415 www.SpineSurgeonLA.com 2573-B Pacific Coast HWY Beverly Hills, CA 90211 P 310-829-5888 Torrance, CA 90505 F 310-943-2636 ",
        "Page 2": "SAILOR, DEBORAH April 26, 2017 Page 2 DISCUSSION AND RECOMMENDATIONS: I reviewed the findings with the patient in detail. I have recommended physical therapy for her. I have asked her to continue wearing her lumbar brace. She is also educated regarding proper dieting. Additionally she is a candidate for physical therapy with range of motion, core strengthening exercises. I will follow the patient in clinic to monitor her progress after physical therapy has been completed. I have also asked her to see her primary medical doctor for diabetic control as well. Sincerely, Electronically Signed By Fardad Mobin, MD Fardad Mobin M.D., F.A.A.N.S Diplomate of the American Board of Neurological Surgeons 8929 Wilshire Blvd., Suite 415 www.SpineSurgeonLA.com 2573-B Pacific Coast HWY P 310-829-5888 Beverly Hills, CA 90211 Torrance, CA 90505 F 310-943-2636 "
    }

    text = ""
    for page, all_text in data.items():
        text += all_text

    num_tokens = language_model.get_num_tokens(text)

    if num_tokens > 4000:
        summary = language_model.generate_summary(text, chunk_size=10000)
    else:
        summary = language_model.generate_summary(text, chunk_size=3000)
