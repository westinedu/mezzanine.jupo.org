
import os
from shutil import rmtree

from django.db.models import get_models, Q
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import NoArgsCommand

from mezzanine.blog.models import BlogPost


class Command(NoArgsCommand):
    """
    Resets the Mezzanine models for the Mezzanine demo site.
    """

    def handle_noargs(self, **options):

        # Build a list of demo-editable models, which is everything
        # in Cartridge and Mezzanine, apart from mezzanine.twitter
        packages = ("mezzanine", "cartridge")
        twitter = "mezzanine.twitter"
        reset = lambda a: a.split(".")[0] in packages and a != twitter
        apps = [a.split(".")[-1] for a in settings.INSTALLED_APPS if reset(a)]
        models = [m for m in get_models() if m._meta.app_label in apps]

        # Delete all demo-editable data.
        for model in models:
            meta = model._meta
            print "Flushing %s.%s" % (meta.app_label, meta.object_name)
            model.objects.all().delete()

        # Maintain permissons for the demo account.
        demo_username = "demo"
        demo_user = User.objects.get(username=demo_username)
        demo_user.user_permissions.remove()
        for model in models:
            ct = ContentType.objects.get_for_model(model)
            for permission in Permission.objects.filter(content_type=ct):
                demo_user.user_permissions.add(permission)

        # Delete any created user accounts.
        keep_users = Q(is_superuser=True) | Q(username=demo_username)
        User.objects.exclude(keep_users).delete()

        # Load initial demo data.,
        call_command("loaddata", "mezzanine", **options)
        call_command("loaddata", "cartridge", **options)
        call_command("import_rss", rss_url="http://blog.jupo.org/atom.xml",
                     mezzanine_user=demo_username, **options)
        mezzanine_posts = Q(keywords_string__contains="mezzanine")
        cartridge_posts = Q(keywords_string__contains="cartridge")
        BlogPost.objects.exclude(mezzanine_posts | cartridge_posts).delete()

        # Delete any uploaded files.
        uploads = os.path.join(settings.MEDIA_ROOT, "uploads")
        if os.path.exists(uploads):
            rmtree(uploads)
        os.mkdir(uploads)
