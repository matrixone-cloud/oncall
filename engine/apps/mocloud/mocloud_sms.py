import os
import logging

from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from apps.mocloud.mocloud_template import DEFAULT_SMS_VERTIFICATOIN_TEMPLATE, DEFAULT_SMS_NOTIFICATION_TEMPLATE, DEFAULT_SIGN_NAME, read_password_from_file
from ..phone_notifications.exceptions import FailedToSendSMS, FailedToStartVerification


logger = logging.getLogger(__name__)


class MOCloudSMS:
    def __init__(self):
        ALIBABA_CLOUD_ACCESS_KEY_ID = read_password_from_file(
            os.environ['ACCESS_KEY_FILE'])
        ALIBABA_CLOUD_ACCESS_KEY_SECRET = read_password_from_file(
            os.environ['SECRET_KEY_FILE'])
        self.sms_client = MOCloudSMS.create_client(
            ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET)

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> Dysmsapi20170525Client:
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret,
            # Endpoint 请参考 https://api.aliyun.com/product/Dysmsapi
            endpoint=f'dysmsapi.aliyuncs.com'
        )
        return Dysmsapi20170525Client(config)

    def send_sms_notification(self, number, parmas):
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=number,
            sign_name=DEFAULT_SIGN_NAME,
            template_code=DEFAULT_SMS_NOTIFICATION_TEMPLATE,
            template_param=parmas
        )
        try:
            # 复制代码运行请自行打印 API 的返回值
            resp = self.sms_client.send_sms_with_options(
                send_sms_request, util_models.RuntimeOptions())
            print(f"use tmpl:{send_sms_request.template_code} received code:{resp.body.code}, msg:{resp.body.message}")
            logger.info(
                f"send sms notification [{parmas}] to [{number}] success")
        except Exception as error:
            logger.error(
                f"send sms notification [{parmas}] to [{number}] failed")
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            # example of handling provider exceptions and converting them to exceptions from core OnCall code.
            logger.error(f"SimplePhoneProvider.send_sms: failed {error}")
            UtilClient.assert_as_string(error.message)
            raise FailedToSendSMS

    def send_sms_verification(self, number, code):
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=number,
            sign_name=DEFAULT_SIGN_NAME,
            template_code=DEFAULT_SMS_VERTIFICATOIN_TEMPLATE,
            template_param='{"code":"%s"}' % (code)
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = self.sms_client.send_sms_with_options(
                send_sms_request, runtime)
            logger.info(
                f"send verification code [{code}] to [{number}] success")
        except Exception as error:
            logger.error(
                f"send verification code [{code}] to [{number}] failed")
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
