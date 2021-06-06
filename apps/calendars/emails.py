from __future__ import annotations

from django_rq import job

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

import apps.utils.typing as td


@job
def send_invitations(event: td.CalendarEvent):
    for attendee in event.attendees.all():
        to = [attendee.email]

        html = render_to_string("emails/base.html", {
            'event': event,
            'attendee': attendee,
        })
        email = EmailMultiAlternatives(
            f"Invitation to {event.name}",
            to=to
        )
        email.mixed_subtype = 'related'
        email.attach(event.get_as_email_attachment())
        email.attach_alternative(html, 'text/html')

        print(email.send())


@job
def send_user_invitations(email):
    to = [email]

    html = render_to_string("emails/invitation.html")
    email = EmailMultiAlternatives(
        f"Invitation to Organize It application",
        to=to
    )
    email.mixed_subtype = 'related'
    email.attach_alternative(html, 'text/html')

    print(email.send())
