from django import template

register = template.Library()

@register.filter
def get_icon(category_name):
    """Retourne l'icône correspondant à la catégorie"""
    icons = {
        'Développement personnel': 'user-tie',
        'Communication': 'comments',
        'Leadership': 'users',
        'Gestion du temps': 'clock',
        'Gestion du stress': 'heartbeat',
        'Créativité': 'lightbulb',
        'Intelligence émotionnelle': 'smile',
        'Travail d\'équipe': 'users-cog',
        'Négociation': 'handshake',
        'Résolution de problèmes': 'puzzle-piece'
    }
    return icons.get(category_name, 'newspaper')
