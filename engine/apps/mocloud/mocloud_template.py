import json
from apps.alerts.models import AlertGroup

DEFAULT_VMS_ALERT_TEMPLATE = "TTS_287040361"
VMS_ALERT_TEST_TEMPLATE = "TTS_303590024"


DEFAULT_SMS_VERTIFICATOIN_TEMPLATE = "SMS_295745023"
DEFAULT_SMS_NOTIFICATION_TEMPLATE = "SMS_465335627"
SMS_ALERT_TEST_TEMPLATE = "SMS_471485476"

DEFAULT_SIGN_NAME = "深圳矩阵起源科技"


class VMSTemplate:
    def __init__(self, tmplName: str, tmplID: str, tmplStr: str, paramKeys: set):
        self.tmplName = tmplName
        self.tmplID = tmplID
        self.tmplStr = tmplStr
        self.paramKeys = paramKeys

    @staticmethod
    def rander_params(tmplID: str, alert_group: AlertGroup) -> str:
        if tmplID not in VMSTemplateDict:
            raise ValueError("vms template does not exist")
        tmpl = VMSTemplateDict[tmplID]
        parmas = {
            "cluster_env": alert_group.channel.short_name,
            "alert_count": alert_group.alerts.count(),
        }
        return json.dumps(parmas)


# vms template parma keys -> alert label key
AlertLabelDict = {
    "alert_name": "alertname",
    "severity": "severity",
    "cluster_env": "clusterDetail",
}

VMSTemplateDict = {
    "TTS_294960050": VMSTemplate(
        "服务出现带有等级的故障告警",
        "TTS_294960050",
        "${cluster_env} 环境出现服务故障，最高告警等级为 ${severity}，请尽快处理！",
        {"cluster_env", "severity"},
    ),
    "TTS_287105343": VMSTemplate(
        "MOC 内部服务告警",
        "TTS_287105343",
        "你好，集群环境 ${cluster_env} 的服务器产生故障： ${alert_name} ，请及时处理。",
        {"cluster_env", "alert_name"},
    ),
    "TTS_287040361": VMSTemplate(
        "服务故障告警数量",
        "TTS_287040361",
        "你好，集群环境 ${cluster_env} 的服务器产生 ${alert_count} 个故障告警 ，请及时处理。",
        {"cluster_env", "alert_count"},
    ),
}


def read_password_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            password = file.readline().strip()
        return password
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
