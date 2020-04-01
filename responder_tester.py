import responder

from marshmallow import Schema, fields, ValidationError

class AllIdRespSchema(Schema):
    # Schema定義 (intのlist)
    exist_ids = fields.List(fields.Int())

class AllExistIDModel():
    # responseのmock
    # この中身を後で本番用に置き換える
    def __init__(self):
        self.exist_ids = [1, 2, 3, 4, 5]

class IdReqSchema(Schema):
    # if required=True, the field must exist
    id = fields.Int(required=True)

class IsExistRespSchema(Schema):
    is_exist = fields.Bool()

class ErrorRespSchema(Schema):
    error = fields.Str()
    errorDate = fields.Date()

class IsExistIDModel():
    def __init__(self, data):
        id = data.get('id')
        self.is_exist = id in [1, 2, 3, 4, 5]

class ErrorModel():
    def __init__(self, error):
        self.error = str(error)
        self.errorDate = datetime.datetime.now()

api = responder.API(
    openapi='3.0.0',  # OpenAPI version
    docs_route='/docs',  # endpoint for interactive documentation by swagger UI. if None, this is not available.
)

api.schema("IdReqSchema")(IdReqSchema)
api.schema("ErrorRespSchema")(ErrorRespSchema)
api.schema("IsExistRespSchema")(IsExistRespSchema)
api.schema("AllIdRespSchema")(AllIdRespSchema)

@api.route("/")
async def view(req, resp):
    resp.media = {'success': True}

@api.route("/schema_driven")
async def schema_driven_view(req, resp):
    """exist id checker endpoint.
    ---
    name: is_exist
    get:
        description: Get the all exist id
        responses:
            200:
                description: All exist_id to be returned
                content:
                    application/json:
                        schema:
                            $ref: "#/components/schemas/AllIdRespSchema"
    post:
        description: Check the id exists or not
        requestBody:
            content:
                appliation/json:
                    schema:
                        $ref: "#/components/schemas/IdReqSchema"
        responses:
            200:
                description: true/false whether id exists to be returned
                content:
                    application/json:
                        schema:
                            $ref: "#/components/schemas/IsExistRespSchema"
            400:
                description: validation error
                content:
                    application/json:
                        schema:
                            $ref: "#/components/schemas/ErrorRespSchema"
    """
    if req.method == "get":
        # validate response data
        resp.media = AllIdRespSchema().dump(AllExistIDModel())

    elif req.method == "post":
        request = await req.media()
        try:
            print(request)
            # validate request data using Schema
            data = IdReqSchema().load(request)

        except ValidationError as error:
            # raise ValidationError
            resp.status_code = api.status_codes.HTTP_400
            # validate response data
            resp.media = ErrorRespSchema().dump(ErrorModel(error))
            return

        # validate response data
        resp.media = IsExistRespSchema().dump(IsExistIDModel(data))

if __name__ == "__main__":
    api.run()