import asyncio
from datetime import datetime

from app import logger
from app.constant import SRC_INSURANCE_APPLICATION, SRC_CRM_RECEIPT, TRG_CRM_RECEIPT, TRG_BROKER_PACKAGE, \
    SRC_STRIPE_RECEIPT, VerificationTemplate
from app.service.api.v1.insurance_application.verifier_v1.alliance_united.base import AllianceUnitedV1


class PaymentInformationVerifier(AllianceUnitedV1):

    def __init__(self, uuid, data):
        super(PaymentInformationVerifier, self).__init__(uuid, data)
        self.response_key = VerificationTemplate.ResponseKey

    async def __verify_payment_date(self):
        payment_date = None
        try:
            stripe_payment_date = self.stripe_receipt.payment_date
        except AttributeError:
            return None

        try:
            crm_payment_date = self.crm_receipt.payment_date
        except AttributeError:
            crm_payment_date = None

        if stripe_payment_date:
            valid_date = None
            if crm_payment_date:
                diff = datetime.fromisoformat(stripe_payment_date) - datetime.fromisoformat(crm_payment_date)
                valid_date = True if 2 > diff.days >= 0 else False
            payment_date = {'source': SRC_STRIPE_RECEIPT,
                            'target': {TRG_CRM_RECEIPT: valid_date}}
        return payment_date

    async def __verify_down_payment(self):
        down_payment = None
        try:
            if self.application.policy_information.net_amount:
                down_payment = await self.is_equal(self.crm_receipt.nb_eft_to_company_amount,
                                                   self.application.policy_information.net_amount)
                down_payment = {'source': SRC_INSURANCE_APPLICATION, 'target': {TRG_CRM_RECEIPT: down_payment}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return down_payment

    async def __verify_vr_fee(self):
        vr_fee_crm = None
        try:
            if self.crm_receipt.vr_fee_amount:
                vr_fee_crm = {'source': {TRG_CRM_RECEIPT: True}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return vr_fee_crm

    async def __verify_broker_fee(self):
        broker_fee = None
        try:
            if self.crm_receipt.broker_fee_amount:
                broker_fee = {'source': SRC_CRM_RECEIPT,
                              'target': {TRG_BROKER_PACKAGE: await self.is_equal(self.broker_package.broker_fee,
                                                                                 self.crm_receipt.broker_fee_amount)}}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return broker_fee

    async def __verify_reference_number(self):
        reference_no = None
        try:
            stripe_receipt_number = self.stripe_receipt.receipt_number
        except AttributeError:
            return None

        try:
            crm_reference_number = self.crm_receipt.reference_number
        except AttributeError:
            crm_reference_number = None

        if stripe_receipt_number:
            reference_no = {'source': SRC_STRIPE_RECEIPT, 'target': {}}
            reference_no['target'][TRG_CRM_RECEIPT] = await self.is_equal(stripe_receipt_number, crm_reference_number)
        return reference_no

    async def __verify_amount_paid(self):
        amount_paid = None
        try:
            stripe_amount_paid = self.stripe_receipt.amount_paid
        except AttributeError:
            return None

        try:
            crm_amount_paid = self.crm_receipt.amount_paid
        except AttributeError:
            crm_amount_paid = None

        if stripe_amount_paid:
            amount_paid = {'source': SRC_STRIPE_RECEIPT,
                           'target': {TRG_CRM_RECEIPT: await self.is_equal(stripe_amount_paid,
                                                                           crm_amount_paid)}}
        return amount_paid

    async def __verify_payment_method(self):
        payment_method = None
        try:
            stripe_payment_method = self.stripe_receipt.payment_notes.card_last_4_digit
        except AttributeError:
            return None

        try:
            crm_payment_method = self.crm_receipt.payment_notes.card_last_4_digit
        except AttributeError:
            crm_payment_method = None

        if stripe_payment_method:
            payment_method = {'source': SRC_STRIPE_RECEIPT,
                              'target': {TRG_CRM_RECEIPT: await self.is_equal(stripe_payment_method,
                                                                              crm_payment_method)}}
        return payment_method

    async def verify(self):
        payment_info = None
        try:
            payment_date, down_payment, vr_fee, broker_fee, reference_no, amount_paid, payment_method = await asyncio.gather(
                self.__verify_payment_date(),
                self.__verify_down_payment(),
                self.__verify_vr_fee(),
                self.__verify_broker_fee(),
                self.__verify_reference_number(),
                self.__verify_amount_paid(), self.__verify_payment_method())
            payment_info = {self.response_key.PAYMENT_DATE: payment_date,
                            self.response_key.DOWN_PAYMENT: down_payment,
                            self.response_key.VR_FEE: vr_fee,
                            self.response_key.BROKER_FEE: broker_fee,
                            self.response_key.REFERENCE_NUMBER: reference_no,
                            self.response_key.AMOUNT_PAID: amount_paid,
                            self.response_key.PAYMENT_METHOD: payment_method}
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}] -> {e}')
        return payment_info
