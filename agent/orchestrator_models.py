from uagents import Model

class ForwardConnectionLink(Model):
    asi_one_id: str
    redirect_url: str
    connection_type: str

class ConnectionLinkForwardedResponse(Model):
    success: bool

class DeleteData(Model):
    asi_one_id: str
    data_ids_to_delete: list[str]

class DeleteDataResponse(Model):
    success: bool