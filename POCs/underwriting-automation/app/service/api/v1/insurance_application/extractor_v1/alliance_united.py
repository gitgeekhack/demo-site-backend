import asyncio
import itertools
import re

from mergedeep import merge

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import APPDocumentTemplate, PDF, Section
from app.service.api.v1.insurance_application.extractor_v1.extract_abc import APPExtractABC
from app.service.helper.parser import parse_date, parse_gender


class APPAllianceUnitedDataPointExtractorV1(APPExtractABC):
    def __init__(self, uuid, file):
        super().__init__(uuid, file)
        self.constants = APPDocumentTemplate.AllianceUnited

    async def __check_blocks(self, blocks, word_list):
        block_dict = {}
        for i in range(0, len(blocks)):
            if blocks[i]['type'] == 0 and blocks[i]['lines'][0]['spans'][0]['text'].split(' ')[0] in word_list:
                block_dict[blocks[i]['lines'][0]['spans'][0]['text'].strip().split(' ')[0]] = i
        return block_dict

    async def __check_blocks_for_multiple_occurrence(self, blocks, word_list):
        block_dict = {}
        for word in word_list:
            temp_list = []
            for i in range(0, len(blocks)):
                if blocks[i]['type'] == 0 and blocks[i]['lines'][0]['spans'][0]['text'] == word:
                    temp_list.append(i)
            if len(temp_list):
                block_dict[word] = temp_list
        return block_dict

    async def __get_insured_info(self):
        try:
            page = self.doc[0]
            blocks = page.get_text("dict")['blocks']
            word_list = [self.constants.Key.INSURED]
            block_dict = await self.__check_blocks(blocks, word_list)
            address_list = []
            city = None
            zip_code = None
            state = None
            insured_name = blocks[block_dict[self.constants.Key.INSURED]]['lines'][3]['spans'][0][
                'text']
            for i in range(4, len(blocks[block_dict[self.constants.Key.INSURED]]['lines']) - 1):
                address_list.append(
                    blocks[block_dict[self.constants.Key.INSURED]]['lines'][i]['spans'][0]['text'])
            street = ' '.join([str(elem) for elem in address_list])
            block_num = len(blocks[block_dict[self.constants.Key.INSURED]]['lines']) - 1
            city_state_zipcode = \
                blocks[block_dict[self.constants.Key.INSURED]]['lines'][block_num]['spans'][0][
                    'text'].split(',')

            if len(city_state_zipcode) == 2:
                city = city_state_zipcode[0].strip()
                zipcode = re.search(self.constants.RegexCollection.ZIPCODE_REGEX,
                                    city_state_zipcode[1])
                if zipcode:
                    zip_code = zipcode.group(0)
                    state = city_state_zipcode[1].replace(zip_code, '').strip()
            address = {'street': street,
                       'state': state,
                       'zip': zip_code,
                       'city': city}
            insured = {'name': insured_name, 'address': address}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            insured = None
        return insured

    async def __get_broker_info(self):
        try:
            page = self.doc[0]
            blocks = page.get_text("dict")['blocks']
            word_list = [self.constants.Key.BROKER, self.constants.Key.POLICY,
                         self.constants.Key.NET]
            block_dict = await self.__check_blocks(blocks, word_list)
            broker_name = blocks[block_dict[self.constants.Key.BROKER]]['lines'][3]['spans'][0][
                'text']
            city_state_zipcode = \
                blocks[block_dict[self.constants.Key.BROKER]]['lines'][5]['spans'][0]['text'].split(
                    ',')
            city = None
            if len(city_state_zipcode) == 2:
                city = city_state_zipcode[0].strip()

            address = {'city': city}
            broker_information = {'name': broker_name,
                                  'address': address}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            broker_information = None
        return broker_information

    async def __get_policy_number(self):
        try:
            page = self.doc[1]
            blocks = page.get_text("dict")['blocks']
            word_list = ['POLICY']
            block_dict = await self.__check_blocks(blocks, word_list)
            policy_number = blocks[block_dict['POLICY'] + 1]['lines'][1]['spans'][0]['text']
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            policy_number = None
        return policy_number

    async def __get_policy_type(self):
        try:
            page = self.doc[2]
            blocks = page.get_text("dict")['blocks']
            word_list = [self.constants.Key.APPLICATION]
            block_dict = await self.__check_blocks(blocks, word_list)
            policy_type = \
                blocks[block_dict[self.constants.Key.APPLICATION]]['lines'][0]['spans'][0][
                    'text']
            policy_type = policy_type.replace(self.constants.Key.APPLICATION_FOR, '')
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            policy_type = None
        return policy_type

    async def __get_date_from_string(self, date=None):
        date_dict = {
            'months': int(date.split('/')[0]),
            'day': int(date.split('/')[1]),
            'year': int(date.split('/')[2]),
        }
        return date_dict

    async def __get_policy_period_and_date(self):
        try:
            page = self.doc[2]
            blocks = page.get_text("dict")['blocks']
            word_list = [self.constants.Key.EFFECTIVE]
            block_dict = await self.__check_blocks(blocks, word_list)
            policy_term = \
                blocks[block_dict[self.constants.Key.EFFECTIVE] + 2]['lines'][0]['spans'][0]['text']
            date_list = policy_term.split('To')
            start_date = date_list[0].strip().split(' ')[0]
            end_date = date_list[1].strip().split(' ')[0]
            start_date_dict = await self.__get_date_from_string(start_date)
            end_date_dict = await self.__get_date_from_string(end_date)
            months = end_date_dict['months'] - start_date_dict['months']
            year = end_date_dict['year'] - start_date_dict['year']
            policy_period = None
            if year >= 1:
                policy_period = 'Annual'
            elif months == 6:
                policy_period = 'semi Annual'
            elif months == 3:
                policy_period = 'Quarterly'
            elif months == 1:
                policy_period = 'Monthly'
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            policy_period = None
            start_date = None
            end_date = None
        return policy_period, start_date, end_date

    async def __get_policy_info(self):
        try:
            page = self.doc[0]
            blocks = page.get_text("dict")['blocks']
            word_list = [self.constants.Key.BROKER, self.constants.Key.POLICY,
                         self.constants.Key.NET]
            block_dict = await self.__check_blocks(blocks, word_list)
            receipt_date = \
                blocks[block_dict[self.constants.Key.POLICY]]['lines'][3]['spans'][0]['text'].split(
                    ' ')[0]
            if self.constants.Key.NET in block_dict.keys():
                amount = blocks[block_dict[self.constants.Key.NET]]['lines'][2]['spans'][0]['text']
            else:
                amount = blocks[block_dict[self.constants.Key.BROKER]]['lines'][2]['spans'][0][
                    'text']
            policy_period, start_date, end_date = await self.__get_policy_period_and_date()
            net_amount = await self.__replace_multiple(amount)
            policy_information = {
                'policy_number': await self.__get_policy_number(),
                'receipt_date': parse_date(receipt_date) if receipt_date else None,
                'net_amount': float(net_amount.strip()) if net_amount else 0,
                'insurance_type': await self.__get_policy_type(),
                'policy_term': policy_period,
                'policy_start_date': parse_date(start_date) if start_date else None,
                'policy_end_date': parse_date(end_date) if end_date else None
            }
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            policy_information = None
        return policy_information

    async def __get_driver_list(self, blocks, block_dict):
        temp_list = []
        for i in range(block_dict[self.constants.Key.DRIVERS],
                       block_dict[self.constants.Key.DRIVING]):
            for j in range(0, len(blocks[i]['lines'])):
                temp_list.append(blocks[i]['lines'][j]['spans'][0]['text'])
        temp = temp_list.index('1.')
        temp_list = temp_list[temp:]
        k = 2
        prev = 0
        driver_list = []
        while str(k) + '.' in temp_list:
            n_str = str(k) + '.'
            ind = temp_list.index(n_str)
            if ind > prev:
                drv_list = temp_list[prev:ind]
                prev = ind
                driver_list.append(drv_list)
                k = k + 1
        drv_list = temp_list[prev:]
        driver_list.append(drv_list)
        return driver_list

    async def __get_vehicle_details(self, block_dict_veh):
        try:
            vehicles_list = []
            page = self.doc[block_dict_veh[0]['block']]
            blocks = page.get_text("dict")['blocks']
            end = len(blocks)
            if len(block_dict_veh) == 2 and block_dict_veh[1][self.constants.Key.LOSS] == 0:
                end = len(blocks) - 2
            else:
                if self.constants.Key.LOSS in block_dict_veh[0]:
                    end = block_dict_veh[0][self.constants.Key.LOSS]
            for i in range(block_dict_veh[0][self.constants.Key.VEHICLE], end):
                for j in range(0, len(blocks[i]['lines'])):
                    vehicles_list.append(blocks[i]['lines'][j]['spans'][0]['text'])
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            vehicles_list = None
        return vehicles_list

    async def __get_vehicle_list(self, block_dict_veh):
        vehicles_list = await self.__get_vehicle_details(block_dict_veh)
        prev = 0
        k = 1
        vehicle_list = []
        while str(k) + '.' in vehicles_list:
            n_str = str(k) + '.'
            ind = vehicles_list.index(n_str)
            if ind > prev:
                veh_list = vehicles_list[prev:ind]
                prev = ind
                vehicle_list.append(veh_list)
                k = k + 1
        veh_list = vehicles_list[prev:]
        vehicle_list.append(veh_list)
        return vehicle_list

    async def __get_vehicle_make_model_trim(self, vehicle_list):
        temp = ' '.join(map(str, vehicle_list))
        check_symbols = re.search(self.constants.RegexCollection.VEHICLE_INFO_SYMBOL_REGEX_1,
                                  temp) or re.search(
            self.constants.RegexCollection.VEHICLE_INFO_SYMBOL_REGEX_2, temp)
        make_model_trim = None
        if check_symbols:
            make_model_trim = temp[check_symbols.end():].strip()
            check_date = re.search(self.constants.RegexCollection.DATE_REGEX, make_model_trim)
            if check_date:
                make_model_trim = make_model_trim[check_date.end():].strip()

        return make_model_trim

    async def __get_vehicle_block(self):
        block_dict_veh = []
        for i in range(2, 4):
            page = self.doc[i]
            blocks = page.get_text("dict")['blocks']
            word_list = [self.constants.Key.VEHICLE, self.constants.Key.LOSS]
            block_dict = await self.__check_blocks(blocks, word_list)
            if block_dict:
                block_dict['block'] = i
                block_dict_veh.append(block_dict)
        return block_dict_veh

    async def __get_make_model_trim(self, make_model_trim):
        make = None
        model = None
        trim = None
        make_model_trim_list = str(make_model_trim).split(' ')
        if len(make_model_trim_list) >= 3:
            make = None if make_model_trim_list[0] == self.constants.Key.NON else \
                make_model_trim_list[0]
            model = None if make_model_trim_list[1] == self.constants.Key.NON else \
                make_model_trim_list[1]
            trim = ' '.join(map(str, make_model_trim_list[2:len(make_model_trim_list)]))
            trim = None if make_model_trim_list[1] == self.constants.Key.NON else trim
        elif len(make_model_trim_list) == 2:
            make = None if make_model_trim_list[0] == self.constants.Key.NON else \
                make_model_trim_list[0]
            model = None if make_model_trim_list[1] == self.constants.Key.NON else \
                make_model_trim_list[1]
        elif len(make_model_trim_list) == 1:
            make = None if make_model_trim_list[0] == self.constants.Key.NON else \
                make_model_trim_list[0]
            model = None
            trim = None
        return make, model, trim

    async def __get_vehicle_dict(self, vehicle, vehicle_use, veh_id):
        vehicle_dict = None

        if len(vehicle) > 2:
            make_model_trim = await self.__get_vehicle_make_model_trim(vehicle)
            make, model, trim = await self.__get_make_model_trim(make_model_trim)

            vehicle_dict = {'id': int(veh_id),
                            'year': int(vehicle[1]),
                            'make': make,
                            'model': model,
                            'trim': trim,
                            'vehicle_use': vehicle_use,
                            'vin': vehicle[2]}
        return vehicle_dict

    async def __get_vehicle_info(self):
        vehicle_dict = None
        block_dict_veh = await self.__get_vehicle_block()
        vehicle_list = await self.__get_vehicle_list(block_dict_veh)
        vehicle_use = []

        for i in range(0, len(vehicle_list) - 1):
            vehicle_use.append(vehicle_list[i][-1])
            vehicle_list[i].remove(vehicle_list[i][-1])
        vehicles = []

        i = 0
        for vehicle in vehicle_list:
            vehicle_dict = await self.__get_vehicle_dict(vehicle, vehicle_use[i], i + 1)
            if vehicle_dict:
                vehicles.append(vehicle_dict)
                i = i + 1
        vehicle_dict = {'vehicles': vehicles}
        return vehicle_dict

    async def __replace_multiple(self, text):
        b = {',': '', '$': '', ' Each Person': '', ' Each Accident': ''}
        for x, y in b.items():
            text = text.replace(x, y)
        return text

    async def __get_relationship(self, before_dob_list):
        relationship = ''
        for word in before_dob_list:
            if not word.isupper() and word.isalpha():
                relationship = relationship + ' ' + word
        return relationship.strip()

    async def __get_driver_info(self):
        page = self.doc[2]
        blocks = page.get_text("dict")['blocks']
        word_list = [self.constants.Key.DRIVERS, self.constants.Key.DRIVING]

        block_dict = await self.__check_blocks(blocks, word_list)
        driver_list = await self.__get_driver_list(blocks, block_dict)

        name_index = driver_list[-1].index('Name')
        driver_list[-1] = driver_list[-1][:name_index]
        drivers = []
        drivers_info = None
        for i in range(0, len(driver_list)):
            line = ' '.join(map(str, driver_list[i]))
            date = re.search(self.constants.RegexCollection.DATE_REGEX, line)
            date_of_birth = parse_date(date.group())
            before_dob_list = line[:date.start()].strip().split(' ')
            after_dob_list = line[date.end():].strip().split(' ')
            relationship = await self.__get_relationship(before_dob_list)
            name = ' '.join(map(str, before_dob_list)).replace(relationship, '')
            temp = name.index('.')
            driver_id = int(name[temp - 1])
            name = name[temp + 1:]
            if not relationship and name.find(self.constants.Key.EXCLU):
                relationship = self.constants.Key.EXCLU
                name = name.replace(self.constants.Key.EXCLU, '')
            sr_filing = after_dob_list[5]
            sr_filing_status = True if sr_filing == 'Yes' else False

            driver_dict = {
                'id': driver_id,
                'name': name.strip(),
                'date_of_birth': date_of_birth,
                'relationship': relationship,
                'gender': parse_gender(after_dob_list[0]),
                'marital_status': after_dob_list[1],
                'status': after_dob_list[2],
                'license_number': None if after_dob_list[3] == self.constants.Key.NA else
                after_dob_list[3],
                'license_state': None if after_dob_list[4] == self.constants.Key.NA else
                after_dob_list[4],
                'driving_experience_in_years': None if after_dob_list[
                                                           6] == self.constants.Key.NA else int(
                    after_dob_list[6]),
                'driving_experience_in_months': None if after_dob_list[
                                                            6] == self.constants.Key.NA else int(
                    after_dob_list[6]) * 12,
                'sr_filing': sr_filing_status
            }
            drivers.append(driver_dict)
        drivers_info = {'drivers': drivers}
        return drivers_info

    async def __get_comprehensive_and_collision_deductible_list(self):
        vehicles = []
        try:
            page = self.doc[3]
            blocks = page.get_text("dict")['blocks']
            comp_list = []
            coll_list = []
            word_list = [self.constants.Key.COMPREHENSIVE_DEDUCTIBLE,
                         self.constants.Key.COLLISION_DEDUCTIBLE]
            block_dict = await self.__check_blocks_for_multiple_occurrence(blocks, word_list)
            if self.constants.Key.COMPREHENSIVE_DEDUCTIBLE in block_dict:
                for i in block_dict[self.constants.Key.COMPREHENSIVE_DEDUCTIBLE]:
                    for j in range(1, len(blocks[i]['lines'])):
                        comp_list.append(blocks[i]['lines'][j]['spans'][0]['text'])

            if self.constants.Key.COLLISION_DEDUCTIBLE in block_dict:
                for i in block_dict[self.constants.Key.COLLISION_DEDUCTIBLE]:
                    for j in range(1, len(blocks[i]['lines'])):
                        coll_list.append((blocks[i]['lines'][j]['spans'][0]['text']))

            vehicles = await self.__get_vehicle_comprehensive_and_collision_deductible(comp_list, coll_list)

        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
        return vehicles

    async def __get_vehicle_comprehensive_and_collision_deductible(self, comp_list, coll_list):
        vehicle_list = []
        for i in range(0, len(comp_list)):
            vehicle = {}
            comp = await self.__replace_multiple(comp_list[i])
            coll = await self.__replace_multiple(coll_list[i])
            vehicle['id'] = i + 1
            vehicle[
                'comprehensive_deductible'] = None if comp == self.constants.Key.NO_COVERAGE else int(
                comp.strip())
            vehicle[
                'collision_deductible'] = None if coll == self.constants.Key.NO_COVERAGE else int(
                coll.strip())
            vehicle_list.append(vehicle)
        return vehicle_list

    async def __get_coverage_info(self):
        try:
            page = self.doc[3]
            blocks = page.get_text("dict")['blocks']
            word_list = [self.constants.Key.LIABILITY_TO_OTHERS,
                         self.constants.Key.UMPD,
                         self.constants.Key.UMBI]
            block_dict = await self.__check_blocks_for_multiple_occurrence(blocks, word_list)
            li_bi_person = None
            li_bi_accident = None
            li_pd_accident = None
            uni_bi_person = None
            uni_bi_accident = None
            uni_pd_accident = None

            if self.constants.Key.LIABILITY_TO_OTHERS in block_dict:
                i = block_dict[self.constants.Key.LIABILITY_TO_OTHERS][0]
                li_bi_person = await self.__replace_multiple(blocks[i]['lines'][2]['spans'][0]['text'].split('/')[0])
                li_bi_accident = await self.__replace_multiple(
                    blocks[i]['lines'][2]['spans'][0]['text'].split('/')[1])
                li_pd_accident = await self.__replace_multiple(blocks[i + 1]['lines'][1]['spans'][0]['text'])
            if self.constants.Key.UMBI in block_dict:
                i = block_dict[self.constants.Key.UMBI][0]
                uni_bi_person = await self.__replace_multiple(
                    blocks[i]['lines'][1]['spans'][0]['text'].split('/')[0])
                uni_bi_accident = await self.__replace_multiple(
                    blocks[i]['lines'][1]['spans'][0]['text'].split('/')[1])
            if self.constants.Key.UMPD in block_dict:
                i = block_dict[self.constants.Key.UMPD][0]
                uni_pd_accident = await self.__replace_multiple(blocks[i]['lines'][1]['spans'][0]['text'])
            vehicles = await self.__get_comprehensive_and_collision_deductible_list()
            coverage_dict = {
                'bi_amount_each_person': int(li_bi_person.strip()) if li_bi_person else None,
                'bi_amount_each_accident': int(li_bi_accident.strip()) if li_bi_accident else None,
                'pd_amount_each_accident': int(li_pd_accident.strip()) if li_pd_accident else None,
                'uninsured_bi_amount_each_person': int(uni_bi_person.strip()) if uni_bi_person else None,
                'uninsured_bi_amount_each_accident': int(uni_bi_accident.strip()) if uni_bi_person else None,
                'uninsured_pd_amount_each_accident': int(uni_pd_accident.strip()) if uni_pd_accident else None,
                'vehicles': vehicles if vehicles else None,

            }
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            coverage_dict = None
        return coverage_dict

    async def __check_date(self, section_boxes, date_metadate):
        is_dated = False
        if section_boxes and date_metadate:
            date_bbox = date_metadate
            result = await self.pdf_helper.match_bbox(section_boxes, date_bbox)
            try:
                if set(result).issubset(section_boxes):
                    is_dated = True
            except TypeError as e:
                logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            except Exception as e:
                logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
                is_dated = None
        return is_dated

    async def __check_signature(self, section_bbox, page_number):
        is_signed = False
        if section_bbox:
            try:
                signatures = await self.pdf_helper.get_images_by_page(page_no=page_number)
                is_signed = await self.signature_validator.validate(doc=self.pdf_helper.converted_doc,
                                                                    section_bbox=section_bbox,
                                                                    images=signatures,
                                                                    page=self.pdf_helper.converted_doc[page_number])
            except Exception as e:
                logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
                is_signed = None
        return is_signed

    async def __get_cancellation_request_signature_placeholder(self, metadata, page_number):
        bbox = None
        for i_metadata in metadata:
            if i_metadata[PDF.TEXT] in self.constants.Key.SignatureVerification.SIGNATURE_LABELS:
                x0, y0, x1, y1 = self.constants.Padding.Signature.SECTION[
                    Section.Application.AllianceUnited.CANCELLATION_REQUEST_POLICY]
                bbox = await self.pdf_helper.apply_bbox_padding(page_no=page_number, bbox=i_metadata[PDF.BBOX],
                                                                x0_pad=x0, y0_pad=y0, x1_pad=x1, y1_pad=y1)
                break
        return bbox

    async def __get_cancellation_request_date_placeholder(self, metadata, page_number):
        bbox = None
        temp_x0 = None
        for i_metadata in metadata:
            if i_metadata[PDF.TEXT] in self.constants.Key.SignatureVerification.SIGNATURE_LABELS:
                temp_x0 = i_metadata[PDF.BBOX][0]
            elif temp_x0 and i_metadata[PDF.TEXT] in self.constants.Key.SignatureVerification.DATE_LABELS and temp_x0 < \
                    i_metadata[PDF.BBOX][0]:
                x0, y0, x1, y1 = self.constants.Padding.Date.SECTION[
                    Section.Application.AllianceUnited.CANCELLATION_REQUEST_POLICY]
                bbox = await self.pdf_helper.apply_bbox_padding(page_no=page_number, bbox=i_metadata[PDF.BBOX],
                                                                x0_pad=x0, y0_pad=y0, x1_pad=x1, y1_pad=y1)
                break
        return bbox

    async def __get_parsed_date_bbox(self, metadata):
        bboxes = []
        text = " ".join(i_metadata[PDF.TEXT] for i_metadata in metadata)
        text = text.split(self.constants.Key.CANCELLATION_REQUEST_POLICY_ATTACHED)[-1]
        text = text.split(self.constants.Key.FOR_AGENCY_COMPANY_USE)[0]
        dates = await self._parse_date(text)
        if dates:
            for i_metadata in metadata:
                for date in dates:
                    if date == i_metadata[PDF.TEXT] and i_metadata[PDF.BBOX] not in bboxes:
                        bboxes.append(i_metadata[PDF.BBOX])
        return bboxes[-1]

    async def __get_cancellation_request_signature(self):
        signature = None
        page_number = await self.pdf_helper.find_page_by_text(
            Section.Application.AllianceUnited.CANCELLATION_REQUEST_POLICY)
        if page_number:
            page_number = page_number[0]
            metadata = await self.pdf_helper.get_attributes_by_page(page_number)
            signature_placeholder_bbox = await self.__get_cancellation_request_signature_placeholder(metadata,
                                                                                                     page_number)
            date_placeholder_bbox = await self.__get_cancellation_request_date_placeholder(metadata, page_number)
            date_bbox = await self.__get_parsed_date_bbox(metadata)
            is_signed = await self.__check_signature(section_bbox=signature_placeholder_bbox,
                                                     page_number=page_number)
            is_dated = await self.__check_date(section_boxes=(signature_placeholder_bbox, date_placeholder_bbox),
                                               date_metadate=date_bbox)
            signature = {'is_signed': is_signed, 'is_dated': is_dated}
        return signature

    async def __get_signatures(self):
        signatures = dict.fromkeys(self.constants.Key.SignatureVerification.SECTIONS_RESPONSE_KEY)
        signature_placeholder_bboxes = await self._get_placeholder_bbox(
            sections=self.constants.Key.SignatureVerification.ALLOWED_SECTIONS,
            metadata=self.pdf_helper.metadata,
            doc=self.doc,
            target=self.constants.Label.SIGNATURE)
        date_placeholder_bboxes = await self._get_placeholder_bbox(
            sections=self.constants.Key.SignatureVerification.ALLOWED_SECTIONS,
            metadata=self.pdf_helper.metadata,
            doc=self.doc,
            target=self.constants.Label.DATE)
        sections = list((merge(signature_placeholder_bboxes, date_placeholder_bboxes)).keys())
        for section in sections:
            (sign_x0, sign_y0, sign_x1, sign_y1) = self.constants.Padding.Signature.SECTION[section]
            (date_x0, date_y0, date_x1, date_y1) = self.constants.Padding.Date.SECTION[section]
            page_number = signature_placeholder_bboxes[section]['page_no']
            if page_number:
                if section in self.constants.Key.SignatureVerification.MULTIPLE_DATES_SECTION:
                    date_bbox = await self._get_date_bbox(page_no=page_number,
                                                          section_name=section, index=-1)
                else:
                    date_bbox = await self._get_date_bbox(page_no=page_number,
                                                          section_name=section)
                key = self.constants.Key.SignatureVerification.KEYS.get(section)
                signature_placeholder_bbox = await self.pdf_helper.apply_bbox_padding(page_no=page_number,
                                                                                      bbox=signature_placeholder_bboxes[
                                                                                          section]['signature']['bbox'],
                                                                                      x0_pad=sign_x0, y0_pad=sign_y0,
                                                                                      x1_pad=sign_x1, y1_pad=sign_y1)
                date_placeholder_bbox = await self.pdf_helper.apply_bbox_padding(page_no=page_number,
                                                                                 bbox=date_placeholder_bboxes[section][
                                                                                     'date']['bbox'],
                                                                                 x0_pad=date_x0, y0_pad=date_y0,
                                                                                 x1_pad=date_x1, y1_pad=date_y1)
                signature = await self.__check_signature(section_bbox=signature_placeholder_bbox,
                                                         page_number=page_number)
                date = await self.__check_date(section_boxes=(signature_placeholder_bbox, date_placeholder_bbox),
                                               date_metadate=date_bbox)
                signatures[key] = {'is_signed': signature, 'is_dated': date}
        cancellation_request_signature = await self.__get_cancellation_request_signature()
        key = self.constants.Key.SignatureVerification.KEYS.get(
            Section.Application.AllianceUnited.CANCELLATION_REQUEST_POLICY)
        signatures[key] = cancellation_request_signature
        return signatures

    async def __get_response_data(self):
        data = {}
        data['insured_information'], data['broker_information'], data['policy_information'], data[
            'driver_information'], data['vehicle_information'], data['coverage_information'], data[
            'signature'] = await asyncio.gather(
            self.__get_insured_info(), self.__get_broker_info(), self.__get_policy_info(), self.__get_driver_info(),
            self.__get_vehicle_info(), self.__get_coverage_info(), self.__get_signatures())
        return data

    async def extract(self):
        data = {"insurance_application": None}
        if self.constants.VALID_DOCUMENT_KEY in itertools.chain(*self.pdf_helper.metadata):
            data['insurance_application'] = await self.__get_response_data()
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.uuid)
        return data