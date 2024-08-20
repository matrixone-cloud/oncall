import os
from django.conf import settings

from alibabacloud_dyvmsapi20170525.client import Client as Dyvmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dyvmsapi20170525 import models as dyvmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from apps.mocloud.mocloud_template import DEFAULT_VMS_ALERT_TEMPLATE, VMS_ALERT_TEST_TEMPLATE, read_password_from_file


class MOCloudVMS:
    def __init__(self):
        if os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID") != None:
            ALIBABA_CLOUD_ACCESS_KEY_ID = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
        else:
            ALIBABA_CLOUD_ACCESS_KEY_ID = read_password_from_file(os.environ.get("ACCESS_KEY_FILE"))

        if os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET") != None:
            ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        else:
            ALIBABA_CLOUD_ACCESS_KEY_SECRET = read_password_from_file(os.environ.get("SECRET_KEY_FILE"))

        self.vms_client = MOCloudVMS.create_client(ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET)

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> Dyvmsapi20170525Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret,
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Dyvmsapi
        config.endpoint = f"dyvmsapi.aliyuncs.com"
        return Dyvmsapi20170525Client(config)

    def send_vms_notification_ops(self, callee_number, parmas, env, incidentID, userID):
        phone_key_map_1_ack = dyvmsapi_20170525_models.IvrCallRequestMenuKeyMap(key="1", code=settings.MOC_DEFAULT_ALERT_ACK_TMPL)
        phone_key_map_2_resolve = dyvmsapi_20170525_models.IvrCallRequestMenuKeyMap(key="2", code=settings.MOC_DEFAULT_ALERT_RESOLVE_TMPL)
        phone_key_map_3_ignore = dyvmsapi_20170525_models.IvrCallRequestMenuKeyMap(key="3", code=settings.MOC_DEFAULT_ALERT_IGNORE_TMPL)
        ivr_call_request = dyvmsapi_20170525_models.IvrCallRequest(
            menu_key_map=[phone_key_map_1_ack, phone_key_map_2_resolve, phone_key_map_3_ignore],
            # PROD#ANCDEFGHXY21T#bruce
            out_id=env + "#" + incidentID + "#" + userID,
            play_times=3,
            start_code=settings.MOC_DEFAULT_ALERT_OPS_TMPL,
            # '{"cluster_region_env":"生产环境","alert_name":"CPU占用过高"}'
            start_tts_params=parmas,
            called_show_number=settings.MOC_DEFAULT_ALERT_CALLER,
            called_number=callee_number,
        )
        try:
            # 复制代码运行请自行打印 API 的返回值
            print("send vms notification to ",callee_number)
            self.vms_client.ivr_call_with_options(ivr_call_request, util_models.RuntimeOptions())
        except Exception as error:
            print(error.message)
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)

    def send_vms_notification(self, number, parmas):
        single_call_by_voice_request = dyvmsapi_20170525_models.SingleCallByTtsRequest(
            tts_param=parmas,
            speed=5,
            play_times=3,
            called_number=number,
            tts_code=DEFAULT_VMS_ALERT_TEMPLATE,
            volume=100,
        )
        try:
            # 复制代码运行请自行打印 API 的返回值
            self.vms_client.single_call_by_tts_with_options(single_call_by_voice_request, util_models.RuntimeOptions())
        except Exception as error:
            # 错误 message
            # print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)

    def send_vms_test(self, number, parmas):
        single_call_by_voice_request = dyvmsapi_20170525_models.SingleCallByTtsRequest(
            called_show_number=settings.MOC_DEFAULT_ALERT_CALLER,
            tts_param=parmas,
            speed=5,
            play_times=3,
            called_number=number,
            tts_code=VMS_ALERT_TEST_TEMPLATE,
            volume=100,
        )
        try:
            self.vms_client.single_call_by_tts_with_options(single_call_by_voice_request, util_models.RuntimeOptions())
        except Exception as error:
            # 错误 message
            # print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
        pass
