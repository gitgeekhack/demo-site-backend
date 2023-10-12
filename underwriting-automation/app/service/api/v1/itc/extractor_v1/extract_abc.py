import abc
import asyncio
import re
from collections import Counter

from app import logger
from app.constant import ITCDocumentTemplate, ExceptionMessage
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper.parser import parse_date, parse_gender
from app.service.helper.pdf_helper import PDFHelper


class ITCExtractABC():
    __metaclass__ = abc.ABCMeta

    def __init__(self, uuid, doc):
        self.uuid = uuid
        self.signature_validator = ValidateSignatureV1()
        self.doc_text = ''
        self.doc = doc
        for page in doc:
            self.doc_text = self.doc_text + page.get_text()
        self.doc_text = self.doc_text.replace('\n', ' ')
        self.indexof = {x: re.search(x, self.doc_text).start() for x in ITCDocumentTemplate.Key.TITLES if
                        x in self.doc_text}
        """indexof is a dictionary which contains indexes of all constants,
            with constant string as key and index as value """

    async def __check_empty_dictionary(self, input_dict):
        if input_dict and all(value == None for value in input_dict.values()):
            input_dict = None
        return input_dict

    async def __remove_empty_values(self, input_list):
        if input_list:
            input_list = [None if x == ITCDocumentTemplate.NO_BREAK_SPACE_REPLACEMENT else x for x in input_list]
        return input_list

    async def __get_driver_violations(self):
        page_text = self.doc_text
        total_violations = None
        violations_by_driver = None
        try:
            start = page_text.index(ITCDocumentTemplate.Key.AMT_2) + len(
                ITCDocumentTemplate.Key.AMT_2) if page_text.count(ITCDocumentTemplate.Key.AMT_2) > 0 else None
            end = page_text.index(ITCDocumentTemplate.Key.DRIVER_SUSPENSIONS) if start else None
            violations = page_text[start:end] if start and end else None
            total_violations = 0
            if violations:
                violations = violations.strip().split('\n \n \n')
                driver_id_list = [int(x[0]) for x in violations]
                violations_by_driver = Counter(driver_id_list)
                total_violations = len(driver_id_list)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
        return total_violations, violations_by_driver

    async def __get_driver_name_list(self, page_text, driver_length):
        name_dict = None
        try:
            start = page_text.index(
                ITCDocumentTemplate.Key.DRIVER_ATTRIBUTES) + ITCDocumentTemplate.ATTRIBUTE_LABEL_LENGTH if \
                page_text.count(ITCDocumentTemplate.Key.DRIVER_ATTRIBUTES) > 0 else None
            end = page_text.index(ITCDocumentTemplate.Key.INDUSTRY) if start else None
            name_list = page_text[start:end] if start and end else None
            driver_id = list(range(1, driver_length + 1))
            name_dict = dict(zip(driver_id, [None] * len(driver_id)))
            if name_list:
                name_list = name_list.split(ITCDocumentTemplate.Key.NAME)[1].strip().split('\n')
                if len(name_list) == driver_length:
                    name_dict = dict(zip(driver_id, name_list))
                elif len(name_list) == driver_length * 2:
                    name_list = [" ".join([x, y]) for x, y in zip(name_list[0::2], name_list[1::2])]
                    name_dict = dict(zip(driver_id, name_list))
                else:
                    logger.warning(
                        f'Request ID: [{self.uuid}]  -> {ExceptionMessage.UNABLE_TO_EXTRACT_NAME}')
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')

        return name_dict

    async def __split_city_state_zip(self, city_state_zip):
        address = {}
        city = None
        state = None
        zip_code = None
        city_state_zipcode = city_state_zip.split(',')
        if len(city_state_zipcode) == 2:
            city = city_state_zipcode[0].strip()
            zipcode = re.search(ITCDocumentTemplate.RegexCollection.ZIPCODE_REGEX, city_state_zipcode[1])
            if zipcode:
                zip_code = zipcode.group(0)
                state = city_state_zipcode[1].replace(zip_code, '').strip()
        address['city'] = city
        address['state'] = state
        address['zip'] = zip_code
        return address

    async def __get_insured_and_agent_names(self):
        names = None
        if ITCDocumentTemplate.Key.NAME in self.indexof and ITCDocumentTemplate.Key.ADDRESS in self.indexof:
            names = self.doc_text[self.indexof[ITCDocumentTemplate.Key.NAME] + len(ITCDocumentTemplate.Key.NAME):
                                  self.indexof[ITCDocumentTemplate.Key.ADDRESS]]
            names = names.strip().split(ITCDocumentTemplate.Key.NAME)
        insured_name = names[0].strip() if names and len(names) >= 1 else None
        agent_name = names[1].strip() if names and len(names) >= 2 else None
        return insured_name, agent_name

    async def __get_insured_and_agent_address(self):
        insured_address = {'city': None, 'state': None, 'zip': None, 'street': None}
        agent_address = {'city': None, 'state': None, 'zip': None}
        if ITCDocumentTemplate.Key.ADDRESS in self.indexof and ITCDocumentTemplate.Key.CITY_STATE_ZIP in self.indexof:
            street = self.doc_text[self.indexof[ITCDocumentTemplate.Key.ADDRESS] + len(ITCDocumentTemplate.Key.ADDRESS):
                                   self.indexof[ITCDocumentTemplate.Key.CITY_STATE_ZIP]]
            street = street.split(ITCDocumentTemplate.Key.ADDRESS)
            if ITCDocumentTemplate.Key.PHONE in self.indexof:
                city_state_zip = self.doc_text[self.indexof[ITCDocumentTemplate.Key.CITY_STATE_ZIP] + len(
                    ITCDocumentTemplate.Key.CITY_STATE_ZIP):self.indexof[
                                                   ITCDocumentTemplate.Key.PHONE]]
                city_state_zip = city_state_zip.split(ITCDocumentTemplate.Key.CITY_STATE_ZIP)
                split_address = [self.__split_city_state_zip(x.strip()) for x in
                                 city_state_zip]
                address = await asyncio.gather(*split_address)
                insured_address = address[0]
                agent_address = address[1]
            insured_address['street'] = await self.__get_value_for_index(street, 0)
        insured_address = await self.__check_empty_dictionary(insured_address)
        agent_address = await self.__check_empty_dictionary(agent_address)
        return insured_address, agent_address

    @abc.abstractmethod
    async def _get_insured_and_agent_info(self):
        try:
            insured_name, agent_name = await self.__get_insured_and_agent_names()
            insured_address, agent_address = await self.__get_insured_and_agent_address()

            producer_code = None
            if ITCDocumentTemplate.Key.PRODUCER_CODE in self.indexof and ITCDocumentTemplate.Key.QUOTE_NUMBER in self.indexof:
                producer_code = self.doc_text[self.indexof[ITCDocumentTemplate.Key.PRODUCER_CODE] +
                                              len(ITCDocumentTemplate.Key.PRODUCER_CODE):
                                              self.indexof[ITCDocumentTemplate.Key.QUOTE_NUMBER]].strip()
            insured_info = {'name': insured_name, 'address': insured_address}
            agent_info = {'name': agent_name, 'address': agent_address,
                          'producer_code': producer_code if producer_code else None}

            insured_info = await self.__check_empty_dictionary(insured_info)
            agent_info = await self.__check_empty_dictionary(agent_info)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            insured_info = agent_info = None
        return insured_info, agent_info

    @abc.abstractmethod
    async def _get_company_info(self):
        try:
            name = policy_term = None
            company_info = {}

            if ITCDocumentTemplate.Key.COMPANY in self.indexof and ITCDocumentTemplate.Key.QUOTE_DATE_TIME in self.indexof:
                name = self.doc_text[
                       self.indexof[ITCDocumentTemplate.Key.COMPANY] + len(ITCDocumentTemplate.Key.COMPANY):
                       self.indexof[ITCDocumentTemplate.Key.QUOTE_DATE_TIME]].strip()
            if ITCDocumentTemplate.Key.POLICY_TERM in self.indexof and ITCDocumentTemplate.Key.POLICY_TIER in self.indexof:
                policy_term = self.doc_text[self.indexof[ITCDocumentTemplate.Key.POLICY_TERM] + len(
                    ITCDocumentTemplate.Key.POLICY_TERM):
                                            self.indexof[ITCDocumentTemplate.Key.POLICY_TIER]].strip()
            company_info['name'] = name
            company_info['policy_term'] = policy_term
            company_info = await self.__check_empty_dictionary(company_info)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            company_info = None

        return company_info

    async def __get_vehicle_driver_id(self):
        veh = self.doc_text[self.indexof[ITCDocumentTemplate.Key.VEHICLE]:self.indexof[ITCDocumentTemplate.Key.DRIVER]]
        drv = self.doc_text[
              self.indexof[ITCDocumentTemplate.Key.DRIVER]:self.indexof[ITCDocumentTemplate.Key.ITC_TRANSACTION_ID]]
        veh_list = re.findall(ITCDocumentTemplate.RegexCollection.VEH_LIST, veh)
        drv_list = re.findall(ITCDocumentTemplate.RegexCollection.DRV_LIST, drv)
        veh = [int(re.search(ITCDocumentTemplate.RegexCollection.SINGLE_DIGIT, x).group()) for x in
               veh_list if ITCDocumentTemplate.Key.VEHICLE in x]
        drv = [int(re.search(ITCDocumentTemplate.RegexCollection.SINGLE_DIGIT, x).group()) for x in
               drv_list if ITCDocumentTemplate.Key.DRIVER in x]
        drivers = []
        for x in drv:
            if x not in drivers:
                drivers.append(x)
        vehicles = []
        for x in veh:
            if x not in vehicles:
                vehicles.append(x)
        return vehicles, drivers

    async def __extract_word_list_from_key(self, label, length=-1):
        """Takes in a string label, if the label is present in indexof,
         returns the list of words from the specified length else returns None,
         if length is not specified, the default consideration will be end of the string."""
        info = None
        if label in self.indexof:
            info = self.doc_text[self.indexof[label] + len(label):].replace(ITCDocumentTemplate.NO_BREAK_SPACE,
                                                                            ITCDocumentTemplate.NO_BREAK_SPACE_REPLACEMENT).strip()
            info = info.split(' ')[:length]
        return info

    async def __get_driver_gender(self, info):
        gender = None
        try:
            gender = parse_gender(info[0])
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
        return gender

    async def __get_driver_marital_status(self, info):
        marital_status = None
        try:
            if info[3] == 'M':
                marital_status = 'Married'
            elif info[3] == 'S':
                marital_status = 'Single'
            else:
                marital_status = None
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
        return marital_status

    async def __get_driver_dob(self, info):
        date_of_birth = None
        try:
            if info:
                date_of_birth = parse_date(info)
            else:
                date_of_birth = None
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
        return date_of_birth

    async def __get_driver_attributes(self, driver_length):
        months_foreign = None
        months_mvr_us = None
        if ITCDocumentTemplate.Key.MONTHS_FOREIGN_LICENSE in self.indexof:
            months_foreign = [x for x in
                              await self.__extract_word_list_from_key(ITCDocumentTemplate.Key.MONTHS_FOREIGN_LICENSE,
                                                                      driver_length * 2) if x != 'months']
            months_foreign = None if not months_foreign else months_foreign
        if ITCDocumentTemplate.Key.MONTHS_MVR_US in self.indexof:
            months_mvr_us = [x for x in
                             await self.__extract_word_list_from_key(ITCDocumentTemplate.Key.MONTHS_MVR_US,
                                                                     driver_length * 2)
                             if x != 'months']
            months_mvr_us = None if not months_mvr_us else months_mvr_us
        return months_foreign, months_mvr_us

    async def __get_value_for_index(self, input_list, index):
        value = None
        if input_list and index <= len(input_list):
            value = input_list[index].strip() if input_list[index] else None
            value = int(value) if value and value.isdigit() else value
        return value

    async def __get_excluded_drivers(self):
        excluded_drivers = None
        if ITCDocumentTemplate.Key.RELATIONSHIP in self.indexof:
            excluded_drivers = []
            text = self.doc_text[
                   self.indexof[ITCDocumentTemplate.Key.RELATIONSHIP] + len(ITCDocumentTemplate.Key.RELATIONSHIP):]
            excl = re.findall(ITCDocumentTemplate.RegexCollection.EXCLUDED_DRIVER, text)
            for x in excl:
                dob = re.search(ITCDocumentTemplate.RegexCollection.EXCLUDED_DOB, x).group()
                other = re.search(ITCDocumentTemplate.RegexCollection.EXCLUDED_OTHER, x).group()
                name = x.replace(other, '').replace(dob, '').strip()
                info = {'name': name, 'date_of_birth': await self.__get_driver_dob(dob)}
                excluded_drivers.append(info)
        return excluded_drivers

    async def __get_driver_info_by_driver(self, violations_by_driver):
        vehicles, drivers = await self.__get_vehicle_driver_id()
        drivers_info_by_id = None
        if drivers:
            driver_info = await self.__extract_word_list_from_key(ITCDocumentTemplate.Key.DRIVER_INFORMATION,
                                                                  len(drivers))
            driver_info = await self.__remove_empty_values(driver_info)
            driver_dob = await self.__extract_word_list_from_key(ITCDocumentTemplate.Key.DRIVER_DOB, len(drivers))
            driver_dob = await self.__remove_empty_values(driver_dob)
            fr_filing = await self.__extract_word_list_from_key(ITCDocumentTemplate.Key.FR_FILING, len(drivers))
            fr_filing = await self.__remove_empty_values(fr_filing)
            months_foreign, months_mvr_us = await self.__get_driver_attributes(len(drivers))
            months_foreign = await self.__remove_empty_values(months_foreign)
            months_mvr_us = await self.__remove_empty_values(months_mvr_us)

            name = await self.__get_driver_name_list(self.doc_text, len(drivers))
            drivers_info_by_id = []
            for i, driver_id in enumerate(drivers):
                driverinfo = await self.__get_value_for_index(driver_info, i)
                temp_obj = {'id': driver_id,
                            'name': name[driver_id],
                            'gender': await self.__get_driver_gender(driverinfo),
                            'age': int(driverinfo[1:3]) if driverinfo else None,
                            'marital_status': await self.__get_driver_marital_status(driverinfo),
                            'date_of_birth': await self.__get_driver_dob(
                                await self.__get_value_for_index(driver_dob, i)),
                            'fr_filing': await self.__get_value_for_index(fr_filing, i),
                            'number_of_violations': violations_by_driver[
                                driver_id] if violations_by_driver and driver_id in violations_by_driver else 0,
                            'attributes': {
                                'months_foreign_license': await self.__get_value_for_index(months_foreign, i),
                                'months_mvr_experience_us': await self.__get_value_for_index(months_mvr_us, i)
                            }}
                temp_obj = await self.__check_empty_dictionary(temp_obj)
                if temp_obj:
                    drivers_info_by_id.append(temp_obj)

        return drivers_info_by_id

    async def _get_driver_information(self):
        try:

            uni_bi_person, uni_bi_accident = None, None
            bi_person, bi_accident = None, None
            liability_bi = await self.__extract_word_list_from_key(ITCDocumentTemplate.Key.LIABILITY_BI, 1)
            liability_pd = await self.__extract_word_list_from_key(ITCDocumentTemplate.Key.LIABILITY_PD, 1)

            uni_bi = await self.__extract_word_list_from_key(ITCDocumentTemplate.Key.UNINSURED_BI, 1)
            uni_pd = await self.__extract_word_list_from_key(ITCDocumentTemplate.Key.UNINSURED_PD, 1)
            if liability_bi is not None:
                bi_person = int(liability_bi[0].split('/')[0])
                bi_accident = int(liability_bi[0].split('/')[1])

            if uni_bi is not None:
                uni_bi_person = int(uni_bi[0].split('/')[0])
                uni_bi_accident = int(uni_bi[0].split('/')[1])
            excluded_drivers = await self.__get_excluded_drivers()
            driver_information = {'bi_amount_each_person': bi_person,
                                  'bi_amount_each_accident': bi_accident,
                                  'pd_amount_each_accident': await self.__get_value_for_index(liability_pd, 0),
                                  'uninsured_bi_amount_each_person': uni_bi_person,
                                  'uninsured_bi_amount_each_accident': uni_bi_accident,
                                  'uninsured_pd_amount_each_accident': await self.__get_value_for_index(uni_pd, 0),
                                  'excluded_drivers': excluded_drivers}
            total_violations, violations_by_driver = await self.__get_driver_violations()
            driver_information['total_number_of_violations'] = total_violations
            driver_information['drivers'] = await self.__get_driver_info_by_driver(violations_by_driver)
            driver_information = await self.__check_empty_dictionary(driver_information)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            driver_information = None
        return driver_information

    async def __get_vin_year_make_model(self, veh_info):
        vehicles = None
        if veh_info:
            veh_info = ' ' + veh_info
            veh_info = re.split(ITCDocumentTemplate.RegexCollection.VEHICLE_ID, veh_info)
            veh_info = [x for x in veh_info if x != '' and len(x) != 1 and not x.isdigit()]
            vehicles = []
            for i, x in enumerate(veh_info):
                vin = year = make = model = None
                x = x.strip()
                match = re.search(ITCDocumentTemplate.RegexCollection.VEHICLE_VIN, x)
                if match:
                    vin = match.group().strip()
                    x = x.replace(vin, '')
                year_make_model = x.split()
                match_year = re.search(ITCDocumentTemplate.RegexCollection.VEHICLE_YEAR, year_make_model[-1])
                if match_year:
                    year = int(match_year.group())
                    year_make_model.remove(year_make_model[-1])
                make = year_make_model[0]
                year_make_model.remove(make)
                model = ' '.join(map(str, year_make_model))
                info_i = {'id': i + 1, 'year': year, 'make': make, 'model': model, 'vin': vin}
                info_i = await self.__check_empty_dictionary(info_i)
                if info_i:
                    vehicles.append(info_i)

        return vehicles

    async def _get_vehicle_information(self):
        vehicle_information = None
        try:
            vehicles, drivers = await self.__get_vehicle_driver_id()
            if vehicles:
                vehicle_information = {}
                coll_deductible = await self.__extract_word_list_from_key(ITCDocumentTemplate.Key.COLLISION_DEDUCTIBLE,
                                                                          len(vehicles))
                coll_deductible = await self.__remove_empty_values(coll_deductible)
                comp_deductible = await self.__extract_word_list_from_key(
                    ITCDocumentTemplate.Key.COMPREHENSIVE_DEDUCTIBLE,
                    len(vehicles))
                comp_deductible = await self.__remove_empty_values(comp_deductible)
                annual_miles_driven = await self.__extract_word_list_from_key(
                    ITCDocumentTemplate.Key.ANNUAL_MILES_DRIVEN,
                    len(vehicles))
                annual_miles_driven = await self.__remove_empty_values(annual_miles_driven)
                veh_info = None
                if ITCDocumentTemplate.Key.VEHICLE_INFO_LABELS in self.indexof:
                    veh_info = self.doc_text[self.indexof[ITCDocumentTemplate.Key.VEHICLE_INFO_LABELS] +
                                             len(ITCDocumentTemplate.Key.VEHICLE_INFO_LABELS):
                                             self.indexof[ITCDocumentTemplate.Key.VEHICLE_ATTRIBUTES]].strip()
                vehicle_info = await self.__get_vin_year_make_model(veh_info)
                vehicles = []
                for i, vehicle in enumerate(vehicle_info):
                    temp_obj = {'id': vehicle['id'],
                                'vin': vehicle['vin'],
                                'make': vehicle['make'],
                                'model': vehicle['model'],
                                'year': vehicle['year'],
                                'annual_miles_driven': await self.__get_value_for_index(annual_miles_driven, i),
                                'comprehensive_deductible': await self.__get_value_for_index(comp_deductible, i),
                                'collision_deductible': await self.__get_value_for_index(coll_deductible, i),
                                }
                    vehicles.append(temp_obj)
                vehicle_information['vehicles'] = vehicles
                vehicle_information = await self.__check_empty_dictionary(vehicle_information)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            vehicle_information = None
        return vehicle_information

    @abc.abstractmethod
    async def extract(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def _get_insured_bbox(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def _get_vehicle_bbox(self, *args, **kwargs):
        """Required method"""

    @abc.abstractmethod
    async def _get_eod_bbox(self, *args, **kwargs):
        """Required method"""

    async def _get_blocks_dict(self, doc, page_no=0):
        page = doc[page_no]
        blocks = page.get_text('dict')['blocks']
        bbox_text = [(span['bbox'], span['text']) for block in blocks if not block['type'] for line in block['lines']
                     for span in line['spans']]
        return dict(bbox_text)

    async def _check_insured_signature(self, doc, section_box):
        response = {'insured_information': None}
        if section_box:
            signatures = await self.pdf_helper.get_images_by_page(page_no=0)
            is_signed = await self.signature_validator.validate(doc, section_box, signatures, doc[0])
            response['insured_information'] = {'is_signed': is_signed}
        return response

    async def _check_vehicle_signature(self, doc, section_box):
        response = {'vehicle_information': None}
        if section_box:
            signatures = await self.pdf_helper.get_images_by_page(page_no=0)
            is_signed = await self.signature_validator.validate(doc, section_box, signatures, doc[0])
            response['vehicle_information'] = {'is_signed': is_signed}
        return response

    async def _check_eod_signature(self, doc, section_box):
        response = {'eod_information': None}
        if section_box:
            signatures = await self.pdf_helper.get_images_by_page(page_no=-1)
            is_signed = await self.signature_validator.validate(doc, section_box, signatures, doc[-1])
            response['eod_information'] = {'is_signed': is_signed}
        return response

    async def _get_bbox_by_sections(self, doc):
        insured_bbox, vehicle_bbox, eod_bbox = await asyncio.gather(self._get_insured_bbox(doc),
                                                                    self._get_vehicle_bbox(doc),
                                                                    self._get_eod_bbox(doc))
        section_dict = {'insured_information': insured_bbox,
                        'vehicle_information': vehicle_bbox,
                        'eod_information': eod_bbox}
        return section_dict

    async def _get_signature(self):
        doc = self.doc
        response = None
        self.pdf_helper = PDFHelper(doc)
        section_bbox = await self._get_bbox_by_sections(doc)
        new_doc = self.pdf_helper.converted_doc
        results = await asyncio.gather(
            self._check_insured_signature(doc=new_doc,
                                          section_box=section_bbox['insured_information']),
            self._check_vehicle_signature(doc=new_doc,
                                          section_box=section_bbox['vehicle_information']),
            self._check_eod_signature(doc=new_doc,
                                      section_box=section_bbox['eod_information']))
        response = dict((k, v) for x in results for k, v in x.items())
        return response
