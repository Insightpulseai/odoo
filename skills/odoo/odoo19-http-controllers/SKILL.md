---
name: odoo19-http-controllers
description: Odoo 19 HTTP controllers, routing, request/response objects, JSON-RPC and HTTP dispatchers
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/backend/http.rst"
  extracted: "2026-02-17"
---

# Odoo 19 HTTP Controllers

## Overview

Odoo web controllers handle HTTP requests. Controllers provide their own extension mechanism
separate from ORM models because pre-requisites (database, loaded modules) may not be
available when controllers are needed.

Controllers are created by inheriting from `odoo.http.Controller`. Routes are defined
through methods decorated with `@odoo.http.route`.

---

## Controllers

### Basic Controller Definition

```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route('/some_url', auth='public')
    def handler(self):
        return "Hello World"
```

### Controller Inheritance and Extension

To override a controller, inherit from its class and override relevant methods.
You **must** re-decorate with `@route()` to keep the method visible:

```python
class Extension(MyController):

    @http.route()
    def handler(self):
        do_before()
        return super(Extension, self).handler()
```

Key rules for controller inheritance:

- Decorating with `@route()` is **necessary** to keep the method (and route) visible.
  If the method is redefined without decorating, it will be "unpublished".
- The decorators of all methods are **combined**: if the overriding method's decorator
  has no argument, all previous ones will be kept. Any provided argument will override
  previously defined ones.

```python
class Restrict(MyController):

    @http.route(auth='user')
    def handler(self):
        return super(Restrict, self).handler()
```

This changes `/some_url` from `auth='public'` to `auth='user'` (requiring login).

---

## The `@route` Decorator

```python
@odoo.http.route(route=None, **kw)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `route` | `str` or `list(str)` | — | The URL path(s) this endpoint handles. Supports converter patterns like `<int:id>` |
| `type` | `str` | `'http'` | Request type: `'http'` or `'json'` |
| `auth` | `str` | `'user'` | Authentication method: `'user'`, `'public'`, or `'none'` |
| `methods` | `list(str)` | `None` | HTTP methods allowed, e.g. `['GET', 'POST']`. If not specified, all methods are allowed |
| `cors` | `str` | `None` | CORS `Access-Control-Allow-Origin` header value |
| `csrf` | `bool` | `True` | Whether CSRF protection is enabled for this endpoint |
| `website` | `bool` | `False` | Whether this is a website route (enables website context) |
| `sitemap` | `bool` or `function` | `True` | Sitemap generation control |
| `multilang` | `bool` | `True` | Whether URL is language-prefixed for website routes |

### Authentication Methods

#### `auth='user'`
User must be authenticated. If not, they are redirected to login. The user's
environment (`request.env`) is set with the authenticated user.

#### `auth='public'`
Accessible to everyone. If the user is not logged in, `request.env` uses the
public user. If logged in, uses the authenticated user's environment.

#### `auth='none'`
The method is always accessible. `request.env` is not available. Used primarily
for static resources or endpoints that don't need Odoo.

### Route Patterns and Converters

Routes support Werkzeug URL converters:

```python
@http.route('/items/<int:item_id>', auth='public', type='http')
def get_item(self, item_id):
    # item_id is automatically converted to int
    record = request.env['my.model'].browse(item_id)
    return request.render('my_module.template', {'record': record})

@http.route('/items/<model("product.product"):product>', auth='user')
def product_page(self, product):
    # product is automatically browsed from the database
    return request.render('my_module.product_template', {'product': product})
```

Common converters:
- `<int:name>` - matches integers
- `<string:name>` - matches strings (default)
- `<path:name>` - matches path segments including slashes
- `<model("res.partner"):partner>` - browses an Odoo record

### Multiple Routes on One Method

```python
@http.route(['/path1', '/path2/<int:record_id>'], auth='public')
def multi_route(self, record_id=None):
    if record_id:
        return "Got record %d" % record_id
    return "Default path"
```

---

## Request Object

The request object is automatically set on `odoo.http.request` at the start of
each request.

### Key Attributes

| Attribute | Description |
|-----------|-------------|
| `request.env` | The Odoo environment bound to the current user |
| `request.env.user` | The current user record |
| `request.env.company` | The current company record |
| `request.env.cr` | The database cursor |
| `request.session` | The OpenERP session (dict-like, stored server-side) |
| `request.httprequest` | The underlying Werkzeug request object |
| `request.params` | The request parameters (merged GET/POST) |
| `request.db` | The database name |
| `request.context` | The current context dictionary |
| `request.csrf_token()` | Generate a CSRF token for form protection |

### Common Methods

#### `request.render(template, qcontext=None, lazy=True, **kw)`

Render a QWeb template and return an HTTP response:

```python
@http.route('/my/page', auth='public', type='http', website=True)
def my_page(self):
    values = {
        'records': request.env['my.model'].sudo().search([]),
        'user': request.env.user,
    }
    return request.render('my_module.my_template', values)
```

#### `request.redirect(location, code=303, local=True)`

Redirect to another URL:

```python
@http.route('/old-page', auth='public', type='http')
def old_page(self):
    return request.redirect('/new-page')
```

#### `request.not_found(description=None)`

Return a 404 Not Found response:

```python
@http.route('/item/<int:item_id>', auth='public')
def get_item(self, item_id):
    record = request.env['my.model'].browse(item_id).exists()
    if not record:
        return request.not_found()
    return request.render('my_module.item', {'record': record})
```

#### `request.make_response(data, headers=None, cookies=None)`

Create a response with custom data, headers, or cookies:

```python
@http.route('/download/csv', auth='user', type='http')
def download_csv(self):
    csv_data = "name,value\nfoo,1\nbar,2"
    headers = [
        ('Content-Type', 'text/csv'),
        ('Content-Disposition', 'attachment; filename="export.csv"'),
    ]
    return request.make_response(csv_data, headers=headers)
```

#### `request.make_json_response(data, headers=None, cookies=None, status=200)`

Create a JSON response:

```python
@http.route('/api/items', auth='user', type='http', methods=['GET'])
def api_list_items(self):
    records = request.env['my.model'].search_read([], ['name', 'value'])
    return request.make_json_response({'items': records})
```

### Session

The session object is a dict-like object stored server-side:

```python
@http.route('/set-preference', auth='user', type='http', methods=['POST'])
def set_pref(self, key, value):
    request.session[key] = value
    return request.redirect('/preferences')

@http.route('/get-preference', auth='user', type='http')
def get_pref(self, key):
    value = request.session.get(key, 'default')
    return value
```

### Accessing the Werkzeug Request

The underlying Werkzeug request is available for lower-level operations:

```python
@http.route('/upload', auth='user', type='http', methods=['POST'], csrf=False)
def upload_file(self):
    uploaded = request.httprequest.files.get('file')
    if uploaded:
        content = uploaded.read()
        filename = uploaded.filename
        # process file...
    return request.redirect('/files')
```

---

## Request Dispatchers

### JsonRPCDispatcher

Handles `type='json'` routes. The request body is parsed as JSON-RPC 2.0.

- Request body must be valid JSON-RPC 2.0 format
- Response is wrapped in a JSON-RPC 2.0 response envelope
- Parameters are extracted from `params` key in the JSON body
- Errors are returned as JSON-RPC error objects

```python
@http.route('/api/create_record', type='json', auth='user')
def create_record(self, name, value):
    """Called via JSON-RPC. Parameters come from the JSON body.

    Example request body:
    {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "name": "Test",
            "value": 42
        },
        "id": 1
    }
    """
    record = request.env['my.model'].create({
        'name': name,
        'value': value,
    })
    return {'id': record.id, 'name': record.name}
```

The JSON-RPC dispatcher automatically:
- Parses the JSON request body
- Extracts parameters from `params`
- Wraps the return value in a JSON-RPC response
- Handles errors with proper JSON-RPC error format
- Manages database transactions (commit on success, rollback on error)

### HttpDispatcher

Handles `type='http'` routes. Standard HTTP request/response handling.

- Parameters come from query string (GET) or form data (POST)
- Return values should be strings, `Response` objects, or the result of `request.render()`
- The dispatcher manages content type negotiation

```python
@http.route('/page', type='http', auth='public', website=True)
def my_page(self, **kw):
    # kw contains all GET/POST parameters
    return request.render('my_module.template', {'params': kw})
```

---

## Response Object

`odoo.http.Response` extends Werkzeug's `Response` class.

### Creating Responses

```python
from odoo.http import Response

# Simple text response
response = Response("Hello", status=200, content_type='text/plain')

# Using request.make_response for more control
response = request.make_response(
    data='<html><body>Hello</body></html>',
    headers=[('Content-Type', 'text/html')],
    cookies={'session_pref': 'dark_mode'},
)

# JSON response
response = request.make_json_response(
    data={'status': 'ok', 'count': 42},
    status=200,
)
```

### Response Headers and Cookies

```python
@http.route('/with-headers', auth='public', type='http')
def with_headers(self):
    response = request.make_response("OK")
    response.headers['X-Custom-Header'] = 'value'
    response.set_cookie('my_cookie', 'cookie_value', max_age=3600)
    return response
```

---

## Common Controller Patterns

### Website Controller with Template

```python
from odoo import http
from odoo.http import request

class WebsiteController(http.Controller):

    @http.route('/my/items', type='http', auth='user', website=True)
    def list_items(self, page=1, **kw):
        MyModel = request.env['my.model']
        domain = []
        total = MyModel.search_count(domain)
        pager = request.website.pager(
            url='/my/items',
            total=total,
            page=page,
            step=20,
        )
        items = MyModel.search(domain, limit=20, offset=pager['offset'])
        return request.render('my_module.items_list', {
            'items': items,
            'pager': pager,
        })
```

### REST-like API Controller

```python
from odoo import http
from odoo.http import request

class ApiController(http.Controller):

    @http.route('/api/v1/partners', type='http', auth='user',
                methods=['GET'], csrf=False)
    def list_partners(self, **kw):
        partners = request.env['res.partner'].search_read(
            [], ['name', 'email', 'phone'], limit=100
        )
        return request.make_json_response({'data': partners})

    @http.route('/api/v1/partners/<int:partner_id>', type='http',
                auth='user', methods=['GET'], csrf=False)
    def get_partner(self, partner_id):
        partner = request.env['res.partner'].browse(partner_id).exists()
        if not partner:
            return request.make_json_response(
                {'error': 'Not found'}, status=404
            )
        return request.make_json_response({
            'id': partner.id,
            'name': partner.name,
            'email': partner.email,
        })

    @http.route('/api/v1/partners', type='json', auth='user',
                methods=['POST'])
    def create_partner(self, name, email=None, phone=None):
        vals = {'name': name}
        if email:
            vals['email'] = email
        if phone:
            vals['phone'] = phone
        partner = request.env['res.partner'].create(vals)
        return {'id': partner.id}
```

### JSON-RPC Controller (OWL Frontend)

```python
class MyJsonController(http.Controller):

    @http.route('/my/action/data', type='json', auth='user')
    def get_action_data(self, model, domain=None, fields=None):
        """Called from OWL/JS frontend via JSON-RPC."""
        records = request.env[model].search_read(
            domain or [], fields or ['name']
        )
        return {
            'records': records,
            'total': len(records),
        }
```

### File Download Controller

```python
import base64
from odoo import http
from odoo.http import request, content_disposition

class DownloadController(http.Controller):

    @http.route('/download/<int:attachment_id>', type='http', auth='user')
    def download_attachment(self, attachment_id):
        attachment = request.env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            return request.not_found()

        file_content = base64.b64decode(attachment.datas)
        headers = [
            ('Content-Type', attachment.mimetype or 'application/octet-stream'),
            ('Content-Disposition', content_disposition(attachment.name)),
        ]
        return request.make_response(file_content, headers=headers)
```

### File Upload Controller

```python
import base64
from odoo import http
from odoo.http import request

class UploadController(http.Controller):

    @http.route('/upload', type='http', auth='user', methods=['POST'],
                csrf=True)
    def upload_file(self, **kw):
        uploaded_file = request.httprequest.files.get('file')
        if not uploaded_file:
            return request.make_json_response({'error': 'No file'}, status=400)

        attachment = request.env['ir.attachment'].create({
            'name': uploaded_file.filename,
            'datas': base64.b64encode(uploaded_file.read()),
            'res_model': kw.get('model', 'ir.attachment'),
            'res_id': int(kw.get('res_id', 0)),
        })
        return request.make_json_response({'id': attachment.id})
```

### Public Endpoint (No Auth)

```python
class PublicController(http.Controller):

    @http.route('/health', type='http', auth='none', csrf=False)
    def health_check(self):
        """No authentication, no CSRF. Useful for monitoring."""
        return request.make_json_response({'status': 'ok'})
```

### Controller with CORS

```python
class CorsController(http.Controller):

    @http.route('/api/external', type='json', auth='none',
                cors='*', csrf=False)
    def external_api(self, **kw):
        """Accessible from any origin (CORS *)."""
        return {'message': 'Cross-origin accessible'}
```

---

## CSRF Protection

CSRF protection is enabled by default on all `type='http'` routes. For forms
rendered by Odoo templates, include the CSRF token:

```xml
<form method="POST" action="/my/endpoint">
    <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
    <input type="text" name="name"/>
    <button type="submit">Submit</button>
</form>
```

To disable CSRF on a specific route (e.g., for external APIs):

```python
@http.route('/webhook', type='http', auth='none', csrf=False, methods=['POST'])
def webhook(self, **kw):
    # No CSRF token required
    return 'OK'
```

---

## Error Handling

### HTTP Routes

```python
from werkzeug.exceptions import NotFound, Forbidden

@http.route('/secure/<int:record_id>', auth='user', type='http')
def secure_page(self, record_id):
    record = request.env['my.model'].browse(record_id).exists()
    if not record:
        raise NotFound("Record not found")
    if not record.check_access('read'):
        raise Forbidden("Access denied")
    return request.render('my_module.template', {'record': record})
```

### JSON-RPC Routes

For JSON routes, exceptions are automatically wrapped in JSON-RPC error format:

```python
from odoo.exceptions import AccessError, ValidationError

@http.route('/api/update', type='json', auth='user')
def update_record(self, record_id, values):
    record = request.env['my.model'].browse(record_id)
    if not record.exists():
        raise ValidationError("Record does not exist")
    record.write(values)
    return {'success': True}
```

---

## Binary Content Helper

For serving binary fields (images, files) efficiently:

```python
from odoo.http import request, Stream

class BinaryController(http.Controller):

    @http.route('/my/image/<int:record_id>', type='http', auth='public')
    def get_image(self, record_id, **kw):
        record = request.env['my.model'].sudo().browse(record_id)
        if not record.exists() or not record.image_1920:
            return request.not_found()
        return Stream.from_binary_field(record, 'image_1920').get_response()
```

---

## Summary Table: Route Configuration

| Use Case | `type` | `auth` | `csrf` | `methods` |
|----------|--------|--------|--------|-----------|
| Website page | `http` | `public` | `True` | `['GET']` |
| Form submission | `http` | `user` | `True` | `['POST']` |
| JSON-RPC API | `json` | `user` | `True` | `['POST']` |
| External webhook | `http` | `none` | `False` | `['POST']` |
| Health check | `http` | `none` | `False` | `['GET']` |
| File download | `http` | `user` | `True` | `['GET']` |
| Cross-origin API | `json` | `none` | `False` | — |
