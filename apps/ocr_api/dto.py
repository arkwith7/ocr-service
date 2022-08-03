from flask_restx import Namespace, fields
 
 
class DocumentDto:
    api = Namespace('document', description='document related operations')
    document = api.model('document', {
        'doc_class': fields.String(required=True, description='document class'),
        'doc_image_url': fields.String(required=True, description='document url'),
        'secret_key': fields.String(required=True, description='document secret_key'),
    })