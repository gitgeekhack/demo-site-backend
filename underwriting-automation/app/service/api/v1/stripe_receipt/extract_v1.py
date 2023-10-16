import asyncio
import re

import dateutil.parser as parser
import fitz

from app import logger
from app.business_rule_exception import InvalidPDFStructureTypeException
from app.constant import StripeReceiptTemplate, PDF
from app.service.api.v1.signature.validate_signature_v1 import ValidateSignatureV1
from app.service.helper.pdf_helper import PDFHelper


class STRPDataPointExtractorV1:
    def __init__(self, uuid, file):
        self.uuid = uuid
        self.signature_validator = ValidateSignatureV1()
        self.constants = StripeReceiptTemplate
        self.response = StripeReceiptTemplate.ResponseKey
        self.file = file
        self.doc = fitz.open(stream=self.file, filetype="pdf")
        self.pdf_helper = PDFHelper(self.doc)

    async def __get_receipt_number(self):
        receipt_number = None
        try:
            page_text = self.pdf_helper.metadata
            section = await self.pdf_helper.get_attributes_by_text(self.constants.Key.RECEIPT)
            receipt = page_text[page_text.index(section[PDF.TEXT])][PDF.TEXT]
            if receipt:
                receipt_number = receipt.replace(self.constants.Key.RECEIPT, '')
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            receipt_number = None
        return receipt_number

    async def __get_amount_paid(self):
        try:
            amount_paid = None
            page_text = self.pdf_helper.metadata
            section = await self.pdf_helper.get_attributes_by_text(self.constants.Key.AMOUNT_PAID)
            amount = page_text[page_text.index(section[PDF.TEXT]) + self.constants.KEY_VALUE_DIFF][PDF.TEXT]
            for x in amount.split():
                match = re.match(self.constants.RegexCollection.CURRENCY, x)
                if match:
                    x = match.group()
                    amount_paid = float(x.replace('$', '').replace(',', ''))
                    break
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            amount_paid = None
        return amount_paid

    async def __get_payment_date(self):
        try:
            page_text = self.pdf_helper.metadata
            section = await self.pdf_helper.get_attributes_by_text(self.constants.Key.DATE_PAID)
            payment_date = page_text[page_text.index(section[PDF.TEXT]) + self.constants.KEY_VALUE_DIFF][PDF.TEXT]
            date = str(parser.parse(payment_date).date())
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            date = None
        return date

    async def __get_payment_notes(self):
        try:
            payment_notes = {"card_last_4_digit": None}
            page_text = self.pdf_helper.metadata
            section = await self.pdf_helper.get_attributes_by_text(self.constants.Key.PAYMENT_NOTES)
            text = page_text[page_text.index(section[PDF.TEXT]) + self.constants.KEY_VALUE_DIFF][PDF.TEXT]
            payment_notes = None
            for x in text.split():
                match = re.match(self.constants.RegexCollection.PAYMENT_NOTES, x)
                if match:
                    payment_notes = {"card_last_4_digit": int(match.group())}
                    break
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            payment_notes = None
        return payment_notes

    async def extract(self):
        data = {"stripe_receipt": None}
        section = tuple(filter(lambda x: self.constants.Key.RECEIPT in x[PDF.TEXT], self.pdf_helper.metadata))
        if section:
            receipt_number, amount_paid, payment_date, payment_notes = await asyncio.gather(self.__get_receipt_number(),
                                                                                            self.__get_amount_paid(),
                                                                                            self.__get_payment_date(),
                                                                                            self.__get_payment_notes())
            data['stripe_receipt'] = {self.response.RECEIPT_NUMBER: receipt_number,
                                      self.response.AMOUNT_PAID: amount_paid,
                                      self.response.PAYMENT_DATE: payment_date,
                                      self.response.PAYMENT_NOTES: payment_notes}
        else:
            logger.warning(f'Request ID: [{self.uuid}] ')
            raise InvalidPDFStructureTypeException(self.uuid)
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')

        return data
