from datetime import datetime

from app import logger
from app.constant import SRC_PTP, TRG_AGREED_TO_PAY, TRG_PROMISE_TO_PROVIDE, TRG_PTP
from app.service.api.v1.insurance_application.verifier_v1.alliance_united.base import AllianceUnitedV1


class PromiseToProvideVerifier(AllianceUnitedV1):

    def __init__(self, uuid, data):
        super(PromiseToProvideVerifier, self).__init__(uuid, data)

    async def __verify_agree_to_pay_date(self):
        date = {'source': SRC_PTP, 'target': {TRG_PTP: None}}
        try:
            if self.promise_to_provide.promise_to_provide_agreement_date:
                if len(set(self.promise_to_provide.promise_to_provide_agreement_date)) == 1:
                    _date = await self.is_equal(self.promise_to_provide.applied_coverage_effective_date,
                                                self.promise_to_provide.promise_to_provide_agreement_date[0])
                else:
                    _date = False
                date = {'source': SRC_PTP, 'target': {TRG_PTP: _date}}
        except TypeError:
            print(
                f'Request ID: [{self.uuid}] Found Dates: {self.promise_to_provide.promise_to_provide_agreement_date}')
        except AttributeError:
            print(
                f'Request ID: [{self.uuid}] promise_to_provide_agreement_date not found')
        return date

    async def __verify_promise_to_provide_date(self):
        date = {'source': SRC_PTP, 'target': {TRG_PTP: None}}
        try:
            if self.promise_to_provide.promise_to_provide_by_date:
                day_diff = ((datetime.fromisoformat(
                    self.promise_to_provide.promise_to_provide_by_date) - datetime.fromisoformat(
                    self.promise_to_provide.applied_coverage_effective_date)).days)
                _date = True if 0 <= day_diff < 7 else False
                date = {'source': SRC_PTP, 'target': {TRG_PTP: _date}}
        except AttributeError:
            print(f'Request ID: [{self.uuid}] promise_to_provide_by_date not found')
        except ValueError:
            print(
                f'Request ID: [{self.uuid}] Date is not Valid -> {self.promise_to_provide.promise_to_provide_by_date}')
        return date

    async def verify(self):
        ptp_info = None
        if self.promise_to_provide:
            if self.promise_to_provide.applied_coverage_effective_date:
                agreed_to_pay_date = await self.__verify_agree_to_pay_date()
                promise_to_provide_date = await self.__verify_promise_to_provide_date()
                ptp_info = {TRG_AGREED_TO_PAY: agreed_to_pay_date,
                            TRG_PROMISE_TO_PROVIDE: promise_to_provide_date}
            else:
                ptp_info = {TRG_AGREED_TO_PAY: None,
                            TRG_PROMISE_TO_PROVIDE: None}
        return ptp_info
