"""
Custom password validators for authentication system.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class AlphanumericPasswordValidator:
    """
    Validate that the password contains both letters and numbers.
    Required by Taiwan e-commerce security standards.
    """
    
    def validate(self, password, user=None):
        has_letter = bool(re.search(r'[a-zA-Z]', password))
        has_number = bool(re.search(r'\d', password))
        
        if not (has_letter and has_number):
            raise ValidationError(
                _("密碼必須包含字母和數字。"),
                code='password_no_alphanumeric',
            )
    
    def get_help_text(self):
        return _("您的密碼必須包含至少一個字母和一個數字。")