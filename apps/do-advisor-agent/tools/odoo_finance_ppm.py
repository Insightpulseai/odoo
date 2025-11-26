#!/usr/bin/env python3
"""
Odoo Finance PPM Integration Tools

Provides export/import capabilities for Finance PPM data following
Odoo 18 documentation: https://www.odoo.com/documentation/18.0/applications/essentials/export_import_data.html

Usage:
    python odoo_finance_ppm.py export --model ipai.finance.logframe --output logframe.csv
    python odoo_finance_ppm.py import --model ipai.finance.logframe --input logframe.csv
"""

import os
import csv
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
import xmlrpc.client


class OdooFinancePPM:
    """Odoo Finance PPM Integration Client"""

    def __init__(
        self,
        url: str = None,
        database: str = None,
        username: str = None,
        password: str = None,
    ):
        self.url = url or os.getenv('ODOO_ENDPOINT', 'https://odoo.insightpulseai.net')
        self.database = database or os.getenv('ODOO_DATABASE', 'odooprod')
        self.username = username or os.getenv('ODOO_USERNAME', 'admin')
        self.password = password or os.getenv('ODOO_PASSWORD', '')

        self.uid = None
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

    def authenticate(self) -> int:
        """Authenticate with Odoo and return user ID"""
        self.uid = self.common.authenticate(
            self.database,
            self.username,
            self.password,
            {}
        )
        if not self.uid:
            raise Exception("Authentication failed")
        return self.uid

    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute Odoo model method"""
        if not self.uid:
            self.authenticate()

        return self.models.execute_kw(
            self.database,
            self.uid,
            self.password,
            model,
            method,
            args,
            kwargs
        )

    # =========================================================================
    # Export Functions
    # =========================================================================

    def export_model(
        self,
        model: str,
        fields: List[str] = None,
        domain: List = None,
        format: str = 'csv',
        output_path: str = None,
    ) -> str:
        """
        Export records from an Odoo model.

        Args:
            model: Odoo model name (e.g., 'ipai.finance.logframe')
            fields: List of field names to export (None = all fields)
            domain: Search domain filter
            format: Output format ('csv' or 'json')
            output_path: Output file path

        Returns:
            Path to exported file
        """
        if not self.uid:
            self.authenticate()

        # Get model fields if not specified
        if not fields:
            fields = self._get_exportable_fields(model)

        # Search for records
        domain = domain or []
        record_ids = self.execute(model, 'search', domain)

        if not record_ids:
            print(f"No records found for {model}")
            return None

        # Read records
        records = self.execute(model, 'read', record_ids, fields)

        # Generate output path
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"{model.replace('.', '_')}_{timestamp}.{format}"

        # Export based on format
        if format == 'csv':
            self._export_csv(records, fields, output_path)
        else:
            self._export_json(records, output_path)

        print(f"Exported {len(records)} records to {output_path}")
        return output_path

    def _get_exportable_fields(self, model: str) -> List[str]:
        """Get list of exportable fields for a model"""
        fields_info = self.execute(model, 'fields_get', [], {'attributes': ['string', 'type', 'store']})

        # Filter to stored, non-computed fields
        exportable = []
        skip_types = {'one2many', 'many2many', 'binary'}
        skip_fields = {'__last_update', 'display_name'}

        for name, info in fields_info.items():
            if name in skip_fields:
                continue
            if info.get('type') in skip_types:
                continue
            if info.get('store', True):
                exportable.append(name)

        return exportable

    def _export_csv(self, records: List[Dict], fields: List[str], output_path: str):
        """Export records to CSV file"""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()

            for record in records:
                # Flatten many2one fields to IDs or names
                row = {}
                for field in fields:
                    value = record.get(field)
                    if isinstance(value, (list, tuple)) and len(value) == 2:
                        # Many2one field: [id, name]
                        row[field] = value[0]  # Use ID for import compatibility
                    elif isinstance(value, bool) and not value:
                        row[field] = ''
                    else:
                        row[field] = value
                writer.writerow(row)

    def _export_json(self, records: List[Dict], output_path: str):
        """Export records to JSON file"""
        # Convert date/datetime objects to strings
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, default=serialize)

    # =========================================================================
    # Import Functions
    # =========================================================================

    def import_model(
        self,
        model: str,
        input_path: str,
        update_existing: bool = True,
        key_field: str = 'id',
    ) -> Dict[str, Any]:
        """
        Import records into an Odoo model.

        Args:
            model: Odoo model name
            input_path: Input file path (CSV or JSON)
            update_existing: Update existing records if found
            key_field: Field to use for matching existing records

        Returns:
            Import result summary
        """
        if not self.uid:
            self.authenticate()

        # Determine format from extension
        is_csv = input_path.endswith('.csv')

        # Read input data
        if is_csv:
            records = self._read_csv(input_path)
        else:
            records = self._read_json(input_path)

        results = {
            'created': 0,
            'updated': 0,
            'errors': [],
            'total': len(records),
        }

        for idx, record in enumerate(records):
            try:
                # Convert external ID if present
                external_id = record.pop('id', None)
                if external_id and isinstance(external_id, str) and '.' in external_id:
                    # Handle external IDs like 'module.xml_id'
                    existing_id = self._resolve_external_id(external_id)
                    if existing_id:
                        record['id'] = existing_id

                # Check for existing record
                existing_id = None
                if update_existing and key_field in record:
                    existing_ids = self.execute(
                        model, 'search',
                        [(key_field, '=', record[key_field])],
                        {'limit': 1}
                    )
                    if existing_ids:
                        existing_id = existing_ids[0]

                # Create or update
                if existing_id:
                    self.execute(model, 'write', [existing_id], record)
                    results['updated'] += 1
                else:
                    self.execute(model, 'create', record)
                    results['created'] += 1

            except Exception as e:
                results['errors'].append({
                    'row': idx + 1,
                    'error': str(e),
                    'data': record,
                })

        print(f"Import complete: {results['created']} created, {results['updated']} updated, {len(results['errors'])} errors")
        return results

    def _read_csv(self, input_path: str) -> List[Dict]:
        """Read records from CSV file"""
        records = []
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert empty strings to None
                record = {}
                for key, value in row.items():
                    if value == '':
                        record[key] = False
                    elif value.isdigit():
                        record[key] = int(value)
                    elif self._is_float(value):
                        record[key] = float(value)
                    elif value.lower() in ('true', 'false'):
                        record[key] = value.lower() == 'true'
                    else:
                        record[key] = value
                records.append(record)
        return records

    def _read_json(self, input_path: str) -> List[Dict]:
        """Read records from JSON file"""
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _is_float(self, value: str) -> bool:
        """Check if string is a float"""
        try:
            float(value)
            return '.' in value
        except ValueError:
            return False

    def _resolve_external_id(self, external_id: str) -> Optional[int]:
        """Resolve external ID to database ID"""
        try:
            module, xml_id = external_id.split('.', 1)
            result = self.execute(
                'ir.model.data', 'search_read',
                [('module', '=', module), ('name', '=', xml_id)],
                {'fields': ['res_id'], 'limit': 1}
            )
            if result:
                return result[0]['res_id']
        except Exception:
            pass
        return None

    # =========================================================================
    # Finance PPM Specific Functions
    # =========================================================================

    def export_finance_logframe(self, output_path: str = None) -> str:
        """Export Finance PPM Logframe data"""
        fields = [
            'name', 'code', 'description', 'category',
            'target_value', 'actual_value', 'unit',
            'start_date', 'end_date', 'status',
            'responsible_id', 'project_id',
        ]
        return self.export_model(
            'ipai.finance.logframe',
            fields=fields,
            output_path=output_path
        )

    def export_finance_closing(self, period: str = None, output_path: str = None) -> str:
        """Export Monthly Closing data"""
        domain = []
        if period:
            domain.append(('period', '=', period))

        fields = [
            'name', 'period', 'state', 'date_start', 'date_end',
            'total_expenses', 'total_revenue', 'net_income',
            'bir_filed', 'bir_filing_date',
        ]
        return self.export_model(
            'ipai.finance.monthly.closing',
            fields=fields,
            domain=domain,
            output_path=output_path
        )

    def export_expenses(self, date_from: str = None, date_to: str = None, output_path: str = None) -> str:
        """Export Expense records"""
        domain = []
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))

        fields = [
            'name', 'date', 'employee_id', 'product_id',
            'unit_amount', 'total_amount', 'currency_id',
            'state', 'description', 'reference',
        ]
        return self.export_model(
            'hr.expense',
            fields=fields,
            domain=domain,
            output_path=output_path
        )

    def sync_logframe_to_superset(self) -> Dict:
        """
        Sync Logframe data to Supabase for Superset dashboards.
        Uses the canonical Supabase instance from CLAUDE.md.
        """
        import requests

        # Export logframe data
        records = self.execute(
            'ipai.finance.logframe', 'search_read',
            [],
            {'fields': ['name', 'code', 'category', 'target_value', 'actual_value', 'status']}
        )

        # Supabase credentials from CLAUDE.md
        supabase_url = os.getenv('SUPABASE_URL', 'https://spdtwktxdalcfigzeqrz.supabase.co')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_key:
            return {'success': False, 'error': 'SUPABASE_SERVICE_ROLE_KEY not set'}

        # Upsert to Supabase
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates',
        }

        response = requests.post(
            f'{supabase_url}/rest/v1/finance_logframe',
            headers=headers,
            json=records
        )

        return {
            'success': response.ok,
            'synced': len(records),
            'status_code': response.status_code,
        }


def main():
    parser = argparse.ArgumentParser(description='Odoo Finance PPM Export/Import Tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export data from Odoo')
    export_parser.add_argument('--model', '-m', required=True, help='Odoo model name')
    export_parser.add_argument('--output', '-o', help='Output file path')
    export_parser.add_argument('--format', '-f', choices=['csv', 'json'], default='csv')
    export_parser.add_argument('--domain', '-d', help='Search domain (JSON string)')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import data into Odoo')
    import_parser.add_argument('--model', '-m', required=True, help='Odoo model name')
    import_parser.add_argument('--input', '-i', required=True, help='Input file path')
    import_parser.add_argument('--no-update', action='store_true', help='Skip updating existing records')

    # Finance PPM shortcuts
    subparsers.add_parser('export-logframe', help='Export Finance Logframe')
    subparsers.add_parser('export-closing', help='Export Monthly Closing')
    subparsers.add_parser('export-expenses', help='Export Expenses')
    subparsers.add_parser('sync-superset', help='Sync Logframe to Superset')

    args = parser.parse_args()

    client = OdooFinancePPM()

    if args.command == 'export':
        domain = json.loads(args.domain) if args.domain else None
        client.export_model(args.model, domain=domain, format=args.format, output_path=args.output)

    elif args.command == 'import':
        client.import_model(args.model, args.input, update_existing=not args.no_update)

    elif args.command == 'export-logframe':
        client.export_finance_logframe()

    elif args.command == 'export-closing':
        client.export_finance_closing()

    elif args.command == 'export-expenses':
        client.export_expenses()

    elif args.command == 'sync-superset':
        result = client.sync_logframe_to_superset()
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
