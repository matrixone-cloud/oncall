import logging
from random import randint


import os
import sys



from django.core.cache import cache

from ..phone_notifications.exceptions import FailedToSendSMS, FailedToStartVerification
from ..phone_notifications.phone_provider import PhoneProvider, ProviderFlags
from apps.mocloud.mocloud_sms import MOCloudSMS
from apps.mocloud.mocloud_vms import MOCloudVMS

logger = logging.getLogger(__name__)

class MOCloudPhoneProvider(PhoneProvider):
    """
    MOCloudPhoneProvider is phone provider which supports only SMS/VMS messages for mo-ob.
    It is currently only support aliyun cloud backend.
    """

    def __init__(self):
        self.sms_client = MOCloudSMS()
        self.vms_client = MOCloudVMS()

    def make_notification_call(self, number, text):
        # 需要做内容截断，不能超过 1000 字
        # 不可发送 ip，确实要的话需要转成_
        self.vms_client.send_vms_notification(number, text)

    def send_notification_sms(self, number, message):
        try:
            self.sms_client.send_sms_notification(number,message)
        except Exception as e:
            # Example of handling provider exceptions and converting them to exceptions from core OnCall code.
            logger.error(
                f"SimplePhoneProvider.send_notification_sms: failed {e}")
            raise FailedToSendSMS
        

    def send_verification_sms(self, number):
        code = str(randint(100000, 999999))
        cache.set(self._cache_key(number), code, timeout=10 * 60)
        try:
            self._write_to_stdout(number, f"Your verification code is {code}")
            self.sms_client.send_sms_verification(number, code)
        except Exception as e:
            # Example of handling provider exceptions and converting them to exceptions from core OnCall code.
            logger.error(
                f"SimplePhoneProvider.send_verification_sms: failed {e}")
            raise FailedToStartVerification

    def finish_verification(self, number, code):
        """
        Skip sms verification
        """
        has = cache.get(self._cache_key(number))
        if has is not None and has == code:
            return number
        else:
            return None

    def _cache_key(self, number):
        return f"mocloud_provider_{number}"

    def _write_to_stdout(self, number, text):
        # print is just example of sending sms.
        # In real-life provider it will be some external api call.
        print(f'send message "{text}" to {number}')

    @property
    def flags(self) -> ProviderFlags:
        return ProviderFlags(
            configured=True,
            test_sms=True,
            test_call=False,
            verification_call=False,
            verification_sms=True,)
