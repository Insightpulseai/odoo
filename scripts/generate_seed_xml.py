#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed Data XML Generator for Month-End Closing Tasks
Generates Odoo 18 XML seed data from Notion tasks with LogFrame mappings.

Usage:
    python3 scripts/generate_seed_xml.py --input data/notion_tasks_with_logframe.json --output addons/ipai_finance_ppm_tdi/data/month_end_tasks_notion_import.xml

Author: Jake Tolentino
Date: 2025-11-26
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
from xml.etree import ElementTree as ET
from xml.dom import minidom


class SeedDataXMLGenerator:
    """Generates Odoo XML seed data from JSON task data."""

    def __init__(self, employee_directory: Dict[str, Any]):
        self.employees = {emp['code']: emp for emp in employee_directory['employees']}

    def _sanitize_xml_id(self, text: str) -> str:
        """Convert text to valid XML ID (lowercase, underscores, alphanumeric)."""
        # Remove special characters, convert to lowercase, replace spaces with underscores
        sanitized = ''.join(c if c.isalnum() or c == ' ' else '' for c in text.lower())
        sanitized = sanitized.replace(' ', '_')
        # Truncate to 64 characters
        return sanitized[:64]

    def _escape_xml_text(self, text: str) -> str:
        """Escape XML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))

    def generate_task_records(self, tasks: List[Dict[str, Any]]) -> ET.Element:
        """Generate XML records for all tasks."""
        root = ET.Element('odoo')
        data = ET.SubElement(root, 'data', attrib={'noupdate': '1'})

        # Add comment header
        comment = ET.Comment("""
Month-End Closing Tasks - Notion Import
36 tasks extracted from Notion Kanban export and mapped to LogFrame structure.
Generated: 2025-11-26
""")
        data.append(comment)

        # Project record (if needed - may already exist)
        project_record = ET.SubElement(data, 'record', attrib={
            'id': 'project_month_end_closing_notion',
            'model': 'project.project'
        })
        ET.SubElement(project_record, 'field', attrib={'name': 'name'}).text = 'Month-End Closing - Notion Tasks'
        ET.SubElement(project_record, 'field', attrib={'name': 'active'}).text = 'True'
        ET.SubElement(project_record, 'field', attrib={'name': 'privacy_visibility'}).text = 'employees'

        # Generate task records
        for i, task in enumerate(tasks, 1):
            task_id = f"task_notion_{self._sanitize_xml_id(task['title'])}_{i}"

            record = ET.SubElement(data, 'record', attrib={
                'id': task_id,
                'model': 'project.task'
            })

            # Task name
            ET.SubElement(record, 'field', attrib={'name': 'name'}).text = self._escape_xml_text(task['title'])

            # Project reference
            ET.SubElement(record, 'field', attrib={
                'name': 'project_id',
                'ref': 'project_month_end_closing_notion'
            })

            # Description (from Notion)
            if task.get('description'):
                description_field = ET.SubElement(record, 'field', attrib={'name': 'description'})
                description_field.text = self._escape_xml_text(task['description'])

            # Priority (1 = high, 2 = medium, 3 = normal)
            priority = task.get('priority', '3')
            ET.SubElement(record, 'field', attrib={'name': 'priority'}).text = priority

            # Employee assignment (using user reference)
            emp_code = task['assigned_to']['employee_code']
            # Note: In production, this would reference actual user records
            # For now, we'll use external ID references like 'user_finance_supervisor_1'
            user_ref = self._map_employee_code_to_user_ref(emp_code)
            if user_ref:
                ET.SubElement(record, 'field', attrib={
                    'name': 'user_ids',
                    'eval': f"[(4, ref('{user_ref}'))]"
                })

            # LogFrame metadata (stored in custom fields - would need to be added to model)
            # For now, we'll add as description notes
            logframe_note = f"\n\nLogFrame Mapping:\n- Immediate Objective: {task['logframe']['im_name']}\n- Activity: {task['logframe']['activity']}\n- Output: {task['logframe']['output_name']}\n- KPI: {task['logframe']['kpi_indicator']}"

            if record.find(".//field[@name='description']") is not None:
                desc_element = record.find(".//field[@name='description']")
                desc_element.text += self._escape_xml_text(logframe_note)
            else:
                ET.SubElement(record, 'field', attrib={'name': 'description'}).text = self._escape_xml_text(logframe_note)

        return root

    def _map_employee_code_to_user_ref(self, emp_code: str) -> str:
        """Map employee code to Odoo user external ID reference."""
        # This mapping would need to match the actual user records in the system
        # For seed data, we use predictable external IDs
        mapping = {
            'CKVC': 'user_finance_director_1',  # Khalil Veracruz
            'RIM': 'user_senior_finance_manager_1',  # Rey Meran
            'LAS': 'user_finance_manager_1',  # Amor Lasaga
            'BOM': 'user_finance_supervisor_1',  # Beng Manalo
            'JPAL': 'user_finance_assistant_vat_1',  # Jinky Paladin
            'JPL': 'user_finance_assistant_ap_1',  # Jerald Loterte
            'JI': 'user_finance_assistant_assets_1',  # Jasmin Ignacio
            'JO': 'user_finance_assistant_support_1',  # Jhoee Oliva
            'JM': 'user_finance_assistant_support_2',  # Joana Maravillas
            'RMQB': 'user_finance_assistant_payments_1',  # Sally Brillantes
        }
        return mapping.get(emp_code, 'user_finance_supervisor_1')  # Default fallback

    def save_xml(self, root: ET.Element, output_path: Path):
        """Save XML with proper formatting."""
        # Convert to string with pretty printing
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="    ", encoding='utf-8')

        # Remove extra blank lines
        lines = [line for line in pretty_xml.decode('utf-8').split('\n') if line.strip()]
        final_xml = '\n'.join(lines)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            # Remove the XML declaration that minidom adds
            f.write('\n'.join(final_xml.split('\n')[1:]))

        print(f'XML seed data saved to: {output_path}')


def main():
    """Main entry point for seed data XML generator."""
    parser = argparse.ArgumentParser(description='Generate Odoo XML seed data from Notion tasks')
    parser.add_argument('--input', type=Path, required=True, help='Input JSON file with LogFrame-mapped tasks')
    parser.add_argument('--employees', type=Path, default=Path('data/employee_directory.json'), help='Employee directory JSON')
    parser.add_argument('--output', type=Path, required=True, help='Output XML file path')

    args = parser.parse_args()

    # Load data
    with open(args.input, 'r', encoding='utf-8') as f:
        task_data = json.load(f)

    with open(args.employees, 'r', encoding='utf-8') as f:
        employee_dir = json.load(f)

    # Initialize generator
    generator = SeedDataXMLGenerator(employee_dir)

    # Generate XML
    root = generator.generate_task_records(task_data['tasks'])

    # Save
    generator.save_xml(root, args.output)

    print(f'Successfully generated seed data for {len(task_data["tasks"])} tasks')

    return 0


if __name__ == '__main__':
    exit(main())
