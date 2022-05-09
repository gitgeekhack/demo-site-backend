import asyncio

import numpy as np

from app.service.helper.cv_helper import CVHelper


class COTHelper(CVHelper):

    async def get_skew_angel(self, extracted_objects):
        find_skew_angles = [self._calculate_skew_angel(extracted_object['detected_object']) for
                            extracted_object in extracted_objects]
        skew_angles = await asyncio.gather(*find_skew_angles)
        skew_angle = np.mean(skew_angles)
        return skew_angle
