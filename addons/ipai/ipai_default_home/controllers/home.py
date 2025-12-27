# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class HomeController(http.Controller):

    @http.route('/api/v1/apps', type='json', auth='user')
    def get_apps(self, **kwargs):
        """API endpoint to get available apps for the home grid"""
        user = request.env.user

        # Get all installed modules that are applications
        modules = request.env['ir.module.module'].sudo().search([
            ('state', '=', 'installed'),
            ('application', '=', True),
        ], order='sequence, name')

        # Get menu items for each app
        apps = []
        for module in modules:
            menu = request.env['ir.ui.menu'].sudo().search([
                ('web_icon', '!=', False),
                ('parent_id', '=', False),
            ], limit=1, order='sequence')

            # Find the root menu for this module
            root_menu = request.env['ir.ui.menu'].sudo().search([
                ('parent_id', '=', False),
                ('web_icon', '!=', False),
            ], order='sequence')

            for m in root_menu:
                if module.name in (m.web_icon or ''):
                    menu = m
                    break

            apps.append({
                'id': module.name,
                'name': module.shortdesc or module.name,
                'moduleId': module.name,
                'icon': module.icon or '/base/static/description/icon.png',
                'color': self._get_module_color(module.name),
                'unread': self._get_unread_count(module.name, user),
                'sequence': module.sequence,
            })

        # Sort by sequence
        apps.sort(key=lambda x: x.get('sequence', 100))

        return {'success': True, 'apps': apps}

    @http.route('/api/v1/apps/favorites', type='json', auth='user')
    def get_favorites(self, **kwargs):
        """Get user's favorite apps"""
        user = request.env.user
        # Store favorites in user preferences (ir.config_parameter or user field)
        param = request.env['ir.config_parameter'].sudo().get_param(
            f'ipai_home.favorites.{user.id}', ''
        )
        favorites = param.split(',') if param else []
        return {'success': True, 'favorites': favorites}

    @http.route('/api/v1/apps/favorite', type='json', auth='user', methods=['POST'])
    def toggle_favorite(self, app_id=None, **kwargs):
        """Toggle app as favorite"""
        if not app_id:
            return {'success': False, 'error': 'app_id required'}

        user = request.env.user
        param_key = f'ipai_home.favorites.{user.id}'
        param = request.env['ir.config_parameter'].sudo().get_param(param_key, '')
        favorites = param.split(',') if param else []

        if app_id in favorites:
            favorites.remove(app_id)
        else:
            favorites.append(app_id)

        # Save back
        request.env['ir.config_parameter'].sudo().set_param(
            param_key, ','.join(filter(None, favorites))
        )

        return {'success': True, 'favorites': favorites}

    def _get_module_color(self, module_name):
        """Get a consistent color for a module"""
        color_map = {
            'mail': '#FF6B35',
            'discuss': '#FF6B35',
            'project': '#9B59B6',
            'account': '#00BCD4',
            'hr': '#FF9800',
            'hr_expense': '#2196F3',
            'sale': '#27AE60',
            'purchase': '#E74C3C',
            'stock': '#3498DB',
            'crm': '#1ABC9C',
            'website': '#E91E63',
            'mrp': '#795548',
            'calendar': '#00BCD4',
            'contacts': '#607D8B',
        }
        return color_map.get(module_name, '#6C63FF')

    def _get_unread_count(self, module_name, user):
        """Get unread notifications for a module"""
        try:
            if module_name in ('mail', 'discuss'):
                # Count unread messages
                count = request.env['mail.message'].sudo().search_count([
                    ('needaction', '=', True),
                    ('partner_ids', 'in', user.partner_id.id),
                ])
                return min(count, 99)  # Cap at 99
        except Exception:
            pass
        return 0
