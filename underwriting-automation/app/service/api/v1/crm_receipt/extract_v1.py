import asyncio
import datetime
import math

import fitz

from app import logger
from app.service.helper.file_downloader import get_file_stream
from app.constant import CRMDocumentTemplate


class CRMDataPointExtractorV1():
    def __init__(self, uuid):
        self.uuid = uuid

    async def __get_payment_date_reference_number(self, blocks):
        result = {'payment_date': None, 'reference_number': None}
        try:
            block = blocks[CRMDocumentTemplate.Block.PAYMENT_DATE]['lines']
            text = []
            for line in block:
                for span in line['spans']:
                    text.append(span['text'].strip())
            keys = text[::2]
            values = text[1::2]
            text_dict = {}
            if len(keys) == len(values):
                for key, value in zip(keys, values):
                    text_dict[key] = value
            try:
                x_date = text_dict[CRMDocumentTemplate.Key.PAYMENT_DATE]
                x_date = datetime.datetime.strptime(x_date, '%B %d, %Y')
                result['payment_date'] = x_date.strftime('%Y-%m-%d')
            except KeyError as e:
                logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
                result['payment_date'] = None
            try:
                result['reference_number'] = text_dict[CRMDocumentTemplate.Key.REFERENCE_NUMBER].replace('#', '')
            except KeyError as e:
                logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
                result['reference_number'] = None
            return result
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            return result

    async def __get_name(self, blocks):
        result = {'name': None}
        try:
            line = blocks[CRMDocumentTemplate.Block.NAME]['lines']
            result['name'] = line[0]['spans'][0]['text'].strip()
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
        return result

    async def __get_address(self, blocks):
        result = {'address': None}
        try:
            address = [blocks[x]['lines'][0]['spans'][0]['text'].strip() for x in CRMDocumentTemplate.Block.ADDRESS]
            address_dict = None
            if len(address) == 2:
                city, state, zipcode = [x.strip() for x in address[1].split(',')]
                address_dict = {'street': address[0].strip(),
                                'city': city,
                                'state': state,
                                'zip': zipcode}
            result['address'] = address_dict
        except IndexError as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
        return result

    async def __get_payment_notes(self, blocks):
        result = {'payment_notes': None}
        try:
            payment_notes = None
            word_list = [CRMDocumentTemplate.Key.PAYMENT_NOTES]
            block_dict = await self.__check_blocks(blocks, word_list)
            if CRMDocumentTemplate.Key.PAYMENT_NOTES in block_dict.keys():
                payment_notes = blocks[block_dict[CRMDocumentTemplate.Key.PAYMENT_NOTES] + 1]['lines'][0]['spans'][0][
                    'text']
            if payment_notes:
                card = int(payment_notes[-4:])
                notes = payment_notes[:-4]
                if len(notes) > 4:
                    notes = notes.replace('-', '').strip()
                result['payment_notes'] = {'card_last_4_digit': card,
                                           'notes': notes.strip() if notes and isinstance(notes, str) else None}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
        return result

    async def __get_payment_method(self, blocks):
        result = {}
        try:
            payment_method = None
            word_list = [CRMDocumentTemplate.Key.PAYMENT_METHOD]
            block_dict = await self.__check_blocks(blocks, word_list)
            if CRMDocumentTemplate.Key.PAYMENT_METHOD in block_dict.keys():
                payment_method = blocks[block_dict[CRMDocumentTemplate.Key.PAYMENT_METHOD]]['lines'][0]['spans'][1][
                    'text'].strip()
            result['payment_method'] = payment_method
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            result['payment_method'] = None
        return result

    async def __round(self, x):
        return {k: math.floor(v * 10 ** 2) / 10 ** 2 if v and type(v) is float else v for k, v in x.items()}

    async def __get_policy_number_and_line_of_business(self, blocks):
        result = {}
        policy_number = None
        line_of_business = None
        word_list = [CRMDocumentTemplate.Key.AMOUNTS_BILLED]
        block_dict = await self.__check_blocks(blocks, word_list)
        if CRMDocumentTemplate.Key.AMOUNTS_BILLED in block_dict.keys() and len(
                blocks[block_dict[CRMDocumentTemplate.Key.AMOUNTS_BILLED] + 1]['lines']) > 2:
            policy_number = blocks[block_dict[CRMDocumentTemplate.Key.AMOUNTS_BILLED] + 1]['lines'][2]['spans'][0][
                'text']
            line_of_business = blocks[block_dict[CRMDocumentTemplate.Key.AMOUNTS_BILLED] + 1]['lines'][1]['spans'][0][
                'text']
        result['policy_number'] = None if '$' in policy_number else policy_number
        result['line_of_business'] = None if '$' in line_of_business else line_of_business
        return result

    async def __vr_fee(self, blocks):
        result = {}
        vr_fee = None
        word_list = [CRMDocumentTemplate.Key.VR_FEE]
        block_dict = await self.__check_blocks(blocks, word_list)
        if CRMDocumentTemplate.Key.VR_FEE in block_dict.keys():
            line_length = len(blocks[block_dict[CRMDocumentTemplate.Key.VR_FEE]]['lines'])
            vr_fee = blocks[block_dict[CRMDocumentTemplate.Key.VR_FEE]]['lines'][line_length - 1]['spans'][0]['text']
        result['vr_fee_amount'] = float(vr_fee.replace('$', '')) if vr_fee else None
        return result

    async def __get_nb_eft_to_company_amount_and_broker_fee_amount(self, blocks):
        result = {}
        nb_eft = None
        total_due_amount = None
        word_list = [CRMDocumentTemplate.Key.NB_EFT_TO_COMPANY, CRMDocumentTemplate.Key.TOTALS_SUMMARIES]
        block_dict = await self.__check_blocks(blocks, word_list)
        if CRMDocumentTemplate.Key.NB_EFT_TO_COMPANY in block_dict.keys():
            length_line = len(blocks[block_dict[CRMDocumentTemplate.Key.NB_EFT_TO_COMPANY]]['lines'])
            nb_eft = \
                blocks[block_dict[CRMDocumentTemplate.Key.NB_EFT_TO_COMPANY]]['lines'][length_line - 1]['spans'][0][
                    'text']
        result['nb_eft_to_company_amount'] = float(nb_eft.replace('$', '')) if nb_eft else None

        if CRMDocumentTemplate.Key.TOTALS_SUMMARIES in block_dict.keys():
            total_due_amount = blocks[block_dict[CRMDocumentTemplate.Key.TOTALS_SUMMARIES] - 1]['lines'][0]['spans'][0][
                'text']
            total_due_amount = float(total_due_amount.replace('$', ''))
        broker_fee_amount = await self.__get_broker_fee_amount(total_due_amount,
                                                               result['nb_eft_to_company_amount'])
        result['broker_fee_amount'] = broker_fee_amount if broker_fee_amount else None
        return result

    async def __check_blocks(self, blocks, word_list):
        block_dict = {}
        try:
            for i in range(0, len(blocks)):
                if blocks[i]['type'] == 0 and blocks[i]['lines'][0]['spans'][0]['text'] in word_list:
                    block_dict[blocks[i]['lines'][0]['spans'][0]['text']] = i
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            block_dict = None
        return block_dict

    async def __get_amount_left_to_pay(self, total_due_amount, amount_paid):
        if total_due_amount and amount_paid:
            amount_left_to_pay = total_due_amount - amount_paid
        elif total_due_amount and not amount_paid:
            amount_left_to_pay = total_due_amount
        else:
            amount_left_to_pay = None
        return amount_left_to_pay

    async def __get_broker_fee_amount(self, total_due_amount, nb_eft_to_company_amount):
        broker_fee_amount = None
        try:
            broker_fee_amount = total_due_amount - nb_eft_to_company_amount
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
        return broker_fee_amount

    async def __get_amount_paid_and_amount_left_to_pay(self, blocks):
        result = {}
        word_list = [CRMDocumentTemplate.Key.TOTALS_SUMMARIES]
        block_dict = await self.__check_blocks(blocks, word_list)
        total_due_amount = blocks[block_dict[CRMDocumentTemplate.Key.TOTALS_SUMMARIES] - 1]['lines'][0]['spans'][0][
            'text']
        total_due_amount = float(total_due_amount.replace('$', ''))
        amount_paid = blocks[block_dict[CRMDocumentTemplate.Key.TOTALS_SUMMARIES] - 1]['lines'][0]['spans'][0]['text']
        result['amount_paid'] = float(amount_paid.replace('$', '')) if amount_paid else None
        result['amount_left_to_pay'] = await self.__get_amount_left_to_pay(total_due_amount,
                                                                           result['amount_paid'])
        return result

    async def __extract_blocks(self, blocks):
        result = {}
        result_list = await asyncio.gather(self.__get_payment_date_reference_number(blocks), self.__get_name(blocks),
                                           self.__get_address(blocks), self.__get_payment_notes(blocks),
                                           self.__get_payment_method(blocks), self.__vr_fee(blocks),
                                           self.__get_nb_eft_to_company_amount_and_broker_fee_amount(blocks),
                                           self.__get_policy_number_and_line_of_business(blocks),
                                           self.__get_amount_paid_and_amount_left_to_pay(blocks))
        for i in result_list:
            result |= i
        result = await self.__round(result)
        return result

    async def extract(self, file):
        data = {"crm_receipt": None}
        doc = fitz.open(stream=file, filetype="pdf")
        blocks = []
        page = list(doc.pages())[0]
        blocks.extend(page.get_text("dict")['blocks'])
        blocks_result = await self.__extract_blocks(blocks)
        if blocks_result:
            data['crm_receipt'] = blocks_result
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')

        return data
