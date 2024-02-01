import json
import os
import time
import traceback
import re
import boto3
from dateutil import parser
from json.decoder import JSONDecodeError

from app import logger
from app.constant import USER_DATA_PATH
from app.service.helper.textract import TextractHelper


class COTDataPointExtractorV1:
    def __init__(self, uuid):
        self.uuid = uuid
        self.textract_helper = TextractHelper()
        self.bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.llm_model_id = 'anthropic.claude-instant-v1'

    async def get_llm_response(self, logger, page_text):
        start_time = time.time()
        prompt = f'''{page_text}

            Instructions for Model:
            1. Extract all lienholder details. For example: Extract data for keywords such as FIRST LIENHOLDER, SECOND LIENHOLDER, etc and contextually similar variations as multiple lienholders and add them to lienholders key seperately. If not present return empty list. Don't consider MAIL TO or PREVIOUS OWNERS to this list.
            2. Document type and Title Type should be extracted only if explicitly provided.
            3. Strictly follow output format for all Dates: "yyyy-mm-dd". If value is not present, return empty string "".
            4. Ensure flexibility in recognizing different terms that convey the same or similar meanings. Contextually adapt to variations that may be present in the OCR text.
            5. Extract Title No. only when explicitly mentioned. Examples values can be similar to - TITLE/DOCUMENT NUMBER, Title Number, TITLE NUMBER, etc. Do not confuse title number with any other number. Also, recognize negations and extract accordingly. Don't tream any leading Zeros.
            6. Identify variations of Issue Dates as IssueDate. Examples values can be similar to - "Date issued", "Date of issue", "ISSUE DATE", "DATE" etc. Consider date format as United States's format. Don't confuse it with any other date. 
            6. Any keyword close to or beneath OdometerReading Number should be considered as OdometerBrand. Examples values could be similar to Actual, Exempt, etc. Don't confuse Vehicle Brands as Odometer Brands.
            7. Understand variations such as "Body style", "STYLE", "BODY", etc and similar to extract it as the BodyStyle.Do not consider BodyStyle as Model. Consider single word or two words together as BodyStyle.Example values of BodyStyle can be IN THE REGEX FORMAT "/d[A-z]*" or "/d/s[A-z]*" or "[A-z]*.
            8. Recognize variations like "Odometer" as the Odometer Reading and the value will be an integer value.
            9. Model can be found with key "MODEL" or "MODEL NAME". Don't confuse it with "MODEL YEAR" it shows Year not Model.
            10. Year should be an integer value and if year is not present in text, dont create value on your own.
            11. Recognize variations like "Plate Number", "LicenseNumber" and similar keywords as the LicenseNumber.
            12. If date is written near Lien holder then consider it as LienDate. If File date and Maturity date both are present then File date should be considered as LienDate. Don't consider Lien release date as LienDate. 
            13. Don't include address in Owner and Lienholder names.
            14. Identify conjuctions("AND", "OR") and seperators("&", "/", ",")  between owner names to not merge them into one. Keep space characters.
            15. If any value is not extracted or is null, it should be returned as empty string ("").
            16. If values are not present in the text, do not create values on your own.

            {{
              "lienholders": [{{
              "lienholderName": "[Extracted lienholder Name]",
              "lienholderAddress": {{
                "Street": "[Extracted lienholder Street]",
                "City": "[Extracted lienholder City]",
                "State": "[Extracted lienholder State]",
                "Zipcode": "[Extracted lienholder Zipcode]"
              }},
              "LienDate": "[Extracted Lien Date]"     
              }}],
              "TitleNo": "[Extracted Title No]",
              "Vin": "[Extracted Vin]",
              "Year": "[Extracted Year]",
              "Make": "[Extracted Make]",
              "Model": "[Extracted Model]",
              "BodyStyle": "[Extracted Body Style]",
              "OdometerReading": "[Extracted Odometer Reading]",
              "IssueDate": "[Extracted Issue Date]",
              "Owners":[
                "[Owner1]",
                "[Owner2]"
              ],
              "OwnerAddress": {{
                "Street": "[Extracted Owner Street]",
                "City": "[Extracted Owner City]",
                "State": "[Extracted Owner State]",
                "Zipcode": "[Extracted Owner Zipcode]"
              }},
              "DocumentType": "[Extracted Document Type]",
              "TitleType": "[Extracted Title Type]",
              "OdometerBrand": "[Extracted Odometer Brand]",
              "LicensePlate": "[Extracted License Plate]"
            }}
            '''
        prompt_template = f"\n\nHuman:{prompt}\n\nAssistant:"

        body = {
            "prompt": prompt_template,
            "temperature": 0,
            "top_p": 1,
            "top_k": 250,
            "max_tokens_to_sample": 2048
        }
        body_ = json.dumps(body).encode("ascii")
        response = self.bedrock.invoke_model(
            body=body_,
            contentType='application/json',
            accept='application/json',
            modelId=self.llm_model_id
        )
        logger.info(f"LLM response received in {time.time() - start_time} seconds.")
        return response['body']

    async def __convert_str_to_json(self, text):
        start_index = text.find('{')
        end_index = text.rfind('}') + 1
        json_str = text[start_index:end_index]
        json_str = re.sub(r',\s*\n\s*]', '\n  ]', json_str)
        data = json.loads(json_str)
        return data

    async def __parse_date(self, input_date):
        if input_date:
            try:
                date_object = parser.parse(input_date)
                formatted_date = date_object.strftime("%m-%d-%Y")
                return formatted_date
            except ValueError:
                print("Error: Unable to parse the date.")
        return ''

    async def __post_process(self, record):
        return {
            "title_no": record.get("TitleNo", ''),
            "vin": record.get("Vin", ''),
            "year": record.get("Year", ''),
            "make": record.get("Make", ''),
            "model": record.get("Model", ''),
            "body_style": record.get("BodyStyle", ''),
            "issue_date": await self.__parse_date(record.get("IssueDate", '')),
            "owners": [owner.upper() for owner in record.get("Owners", [])],
            "document_type": record.get("DocumentType", ''),
            "title_type": record.get("TitleType", ''),
            "license_plate": record.get("LicensePlate", ''),
            "odometer": {
                "reading": record.get("OdometerReading", ''),
                "brand": record.get("OdometerBrand", '')
            },
            "owner_address": {
                "street": record.get("OwnerAddress", {}).get("Street", ''),
                "city": record.get("OwnerAddress", {}).get("City", ''),
                "state": record.get("OwnerAddress", {}).get("State", ''),
                "zip_code": record.get("OwnerAddress", {}).get("Zipcode", '')
            },
            "lien_holder": [{
                "name": lien_holder.get("lienholderName", ''),
                "lien_date": await self.__parse_date(lien_holder.get("LienDate", '')) or "",
                "address": {
                    "street": lien_holder.get("lienholderAddress", {}).get("Street", ''),
                    "city": lien_holder.get("lienholderAddress", {}).get("City", ''),
                    "state": lien_holder.get("lienholderAddress", {}).get("State", ''),
                    "zip_code": lien_holder.get("lienholderAddress", {}).get("Zipcode", '')
                }
            } for lien_holder in record.get("lienholders", [])]
        }

    def empty_response(self):
        return {"title_no": "", "vin": "", "year": "", "make": "", "model": "", "body_style": "",
                "issue_date": "", "owners": [], "document_type": "", "title_type": "", "license_plate": "",
                "odometer": {"reading": "", "brand": ""},
                "owner_address": {"street": "", "city": "", "state": "", "zip_code": ""}, "lien_holder": []}

    async def extract(self, image_data):
        data = {}
        try:
            for file_path in image_data:
                page_text = self.textract_helper.get_text(logger, file_path)
                if page_text:
                    llm_response = await self.get_llm_response(logger, page_text)
                    llm_data_json = json.loads(llm_response.read().decode('utf-8'))
                    result = await self.__convert_str_to_json(llm_data_json['completion'])
                    data = await self.__post_process(result)

                    logger.info(f'Request ID: [{self.uuid}] Response: {data}')
                else:
                    logger.info('Empty text given by Textract')
                    return self.empty_response()
        except JSONDecodeError as e:
            logger.error('%s -> %s' % (e, traceback.format_exc()))
            return self.empty_response()
        except Exception as e:
            logger.error('%s -> %s' % (e, traceback.format_exc()))
            data = 500
        return data
