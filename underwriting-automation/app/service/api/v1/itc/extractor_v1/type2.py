import asyncio

from app import logger
from app.constant import ITCDocumentTemplate, ExceptionMessage
from app.service.api.v1.itc.extractor_v1.extract_abc import ITCExtractABC


class Type2Extractor(ITCExtractABC):

    async def _get_insured_bbox(self, doc):
        result = None
        block_dic = await self._get_blocks_dict(doc, page_no=0)
        x0 = y0 = x1 = y1 = None
        page = doc[0]
        blocks = page.get_text('dict')['blocks']
        try:
            _, _, x1, _ = blocks[4]['bbox']
            for key in block_dic:
                if ITCDocumentTemplate.Key.INSURED_INFO in block_dic[key]:
                    x0, y0, _, _ = key
                    break
            for key in block_dic:
                if ITCDocumentTemplate.Key.LEAD_SOURCE in block_dic[key]:
                    _, _, _, y1 = key
                    break
            for block in blocks:
                if not block['type']:
                    _, _, temp_x1, _ = block['bbox']
                    if x1 < temp_x1:
                        x1 = temp_x1
            if None not in (x0, y0, x1, y1):
                result = (x0, y0, x1, y1)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            result = None
        return result

    async def _get_vehicle_bbox(self, doc):
        result = None
        block_dic = await self._get_blocks_dict(doc, page_no=0)
        x0 = y0 = x1 = y1 = None
        page = doc[0]
        blocks = page.get_text('dict')['blocks']
        try:
            x0, _, x1, _ = blocks[10]['bbox']
            for key in block_dic:
                if ITCDocumentTemplate.Key.VEH1 in block_dic[key]:
                    _, y0, _, _ = key
                    break
            for key in block_dic:
                if ITCDocumentTemplate.Key.VEHICLE_ATTRIBUTES in block_dic[key]:
                    _, _, _, y1 = key
                    break
            for block in blocks:
                if not block['type']:
                    _, _, temp_x1, _ = block['bbox']
                    if x1 < temp_x1:
                        x1 = temp_x1
            if y1 is None:
                _, _, _, y1 = page.CropBox
            if None not in (x0, y0, x1, y1):
                result = (x0, y0, x1, y1)
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            result = None
        return result

    async def _get_eod_bbox(self, doc):
        result = None
        block_dic = await self._get_blocks_dict(doc, page_no=-1)
        x0 = y0 = x1 = y1 = None
        page = doc[-1]
        blocks = page.get_text('dict')['blocks']
        try:
            x0, _, _, _ = blocks[0]['bbox']
            _, _, x1, y1 = page.CropBox
            for block in blocks:
                if not block['type']:
                    temp_x0, _, _, _ = block['bbox']
                    if x0 > temp_x0:
                        x0 = temp_x0
            for key in block_dic:
                if ITCDocumentTemplate.Key.COMPANY_QUESTIONS in block_dic[key]:
                    _, y0, _, _ = key
            if y0 is None:
                _, y0, _, _ = page.CropBox
            if None not in (x0, y0, x1, y1):
                result = (x0, y0, x1, y1)
            else:
                logger.warning(
                    f'Request ID: [{self.uuid}]  -> {ExceptionMessage.UNABLE_TO_EXTRACT_EOD_SECTION}')
        except Exception as e:
            logger.warning(f'Request ID: [{self.uuid}]  -> {e}')
            result = None
        return result

    async def extract(self):
        logger.info(f'Request ID: [{self.uuid}] Extractor Type:[{self.__class__.__name__}]')
        data = {}
        (data[ITCDocumentTemplate.ResponseKey.INSURED_INFORMATION],
         data[ITCDocumentTemplate.ResponseKey.AGENT_INFORMATION]), data[
            ITCDocumentTemplate.ResponseKey.INSURANCE_COMPANY], data[
            ITCDocumentTemplate.ResponseKey.DRIVER_INFORMATION], \
        data[ITCDocumentTemplate.ResponseKey.VEHICLE_INFORMATION], data[
            ITCDocumentTemplate.ResponseKey.SIGNATURES] = await asyncio.gather(self._get_insured_and_agent_info(),
                                                                               self._get_company_info(),
                                                                               self._get_driver_information(),
                                                                               self._get_vehicle_information(),
                                                                               self._get_signature())
        return data
