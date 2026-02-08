from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from difflib import SequenceMatcher

User = get_user_model()


def _nombre_similar(a, b):
    """Comprueba si dos nombres son similares (tolera typos)."""
    if not a or not b:
        return True
    a = ' '.join(a.lower().split())
    b = ' '.join(b.lower().split())
    if a in b or b in a:
        return True
    return SequenceMatcher(None, a, b).ratio() >= 0.6


class CustomPasswordResetForm(PasswordResetForm):
    """Formulario para restablecer contraseña con verificación opcional de nombre."""
    first_name = forms.CharField(required=False, label='Nombre', max_length=150)
    last_name = forms.CharField(required=False, label='Apellido', max_length=150)

    def get_users(self, email):
        """Obtiene usuarios por email. Si se proporcionó nombre, verifica coincidencia flexible."""
        email = (email or '').strip().lower()
        first = (self.cleaned_data.get('first_name') or '').strip()
        last = (self.cleaned_data.get('last_name') or '').strip()
        active_users = User.objects.filter(email__iexact=email, is_active=True)
        for user in active_users:
            if first or last:
                user_full = f"{user.first_name} {user.last_name}".strip()
                provided = f"{first} {last}".strip()
                if not _nombre_similar(provided, user_full):
                    continue
            yield user
