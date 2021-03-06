# -*- coding: utf-8 -*-

def comment_notification(sender, comment, **kwargs):
    from django.conf import settings
    from django.contrib.auth.models import User
    from django.contrib.sites.models import Site

    ct_commented = comment.content_type

    if ct_commented.model == 'membershiprequest':
        msr_creator_username = comment.content_object.requested_username

        if "pinax.notifications" in settings.INSTALLED_APPS:
            from pinax.notifications import models as notification
            users = User.objects.filter(is_staff=True) | User.objects.filter(username=msr_creator_username)

            if users:
                site_name = Site.objects.get_current().name
                domain = Site.objects.get_current().domain
                membership_url= "https://" + domain +\
                    "/work/membership-discussion/" + str(comment.content_object.id) + "/"
                notification.send(
                    users,
                    "comment_membership_request",
                    {"name": comment.name,
                    "comment": comment.comment,
                    "site_name": site_name,
                    "membership_url": membership_url,
                    "current_site": domain,
                    }
                )

    elif ct_commented.model == 'joinrequest':
        jr_creator = comment.content_object.agent.user()
        jr_managers = comment.content_object.project.agent.managers()

        if "pinax.notifications" in settings.INSTALLED_APPS:
            from pinax.notifications import models as notification
            users = []
            if jr_creator:
                users.append(jr_creator.user)

            for manager in jr_managers:
                if manager.user():
                    users.append(manager.user().user)

            if users:
                site_name = Site.objects.get_current().name
                domain = kwargs['request'].get_host()
                try:
                    slug = comment.content_object.project.fobi_slug
                    if settings.PROJECTS_LOGIN:
                        obj = settings.PROJECTS_LOGIN
                        for pro in obj:
                            if pro == slug:
                                site_name = comment.content_object.project.agent.name
                except:
                    pass

                joinrequest_url= "https://" + domain +\
                    "/work/project-feedback/" + str(comment.content_object.project.agent.id) +\
                    "/" + str(comment.content_object.id) + "/"
                notification.send(
                    users,
                    "comment_join_request",
                    {"name": comment.name,
                    "comment": comment.comment,
                    "site_name": site_name,
                    "joinrequest_url": joinrequest_url,
                    "jn_req": comment.content_object,
                    "current_site": kwargs['request'].get_host(),
                    }
                )


# Connecting signal "comment_was_posted" to comment_notification()
from django_comments.models import Comment
from django_comments.signals import comment_was_posted
comment_was_posted.connect(comment_notification, sender=Comment)
