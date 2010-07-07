
from django.db.models import get_models
from django.contrib.auth.models import User, Permission
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import NoArgsCommand


perms = ["Blog post", "Page", "Comment"]


class Command(NoArgsCommand):
    """
    Resets the entire Mezzanine demo site on a scheduled basis, steps are:
    
    1) Empty all models.
    2) Reload fixutres.
    3) Set the current site.
    4) Create the demo user.
    5) Give the demo user permissions to the Mezzanine apps.
    6) Import a Tumblr blog.
    """

    def handle_noargs(self, **options):
        options["interactive"] = False
        for model in get_models():
            model.objects.all().delete()
        call_command("syncdb", **options)
        Site.objects.create(domain="mezzanine.jupo.org", 
            name="Mezzanine Demo")
        user = User.objects.create_user("demo", "example@example.com", "demo")
        user.is_staff = True
        for perm in Permission.objects.filter(content_type__name__in=perms):
            user.user_permissions.add(perm)
            user.save()
        call_command("import_tumblr", "steve-mc", "demo", **options)

