import logging

from django.db import models
from django.template.defaultfilters import slugify

from drumbeat.models import ModelBase
from drumbeat.utils import get_partition_id, safe_filename
from drumbeat import storage
from richtext.models import RichTextField


log = logging.getLogger(__name__)


def determine_image_upload_path(instance, filename):
    return "images/schools/%(partition)d/%(filename)s" % {
        'partition': get_partition_id(instance.pk),
        'filename': safe_filename(filename),
    }


class School(ModelBase):
    """Placeholder model for schools."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = RichTextField(config_name='rich')
    organizers = models.ManyToManyField('users.UserProfile',
        null=True, blank=True)
    featured = models.ManyToManyField('projects.Project',
        related_name='school_featured', null=True, blank=True)

    logo = models.ImageField(upload_to=determine_image_upload_path, null=True,
                              storage=storage.ImageStorage(), blank=True)
    groups_icon = models.ImageField(upload_to=determine_image_upload_path,
        null=True, storage=storage.ImageStorage(), blank=True)
    background = models.ImageField(upload_to=determine_image_upload_path,
        null=True, storage=storage.ImageStorage(), blank=True)
    site_logo = models.ImageField(upload_to=determine_image_upload_path,
        null=True, storage=storage.ImageStorage(), blank=True)

    headers_color = models.CharField(max_length=7, default='#5a6579')
    headers_color_light = models.CharField(max_length=7, default='#f08c00')
    background_color = models.CharField(max_length=7, default='#ffffff')
    menu_color = models.CharField(max_length=7, default='#36cdc4')
    menu_color_light = models.CharField(max_length=7, default='#4bd2c9')

    sidebar_width = models.CharField(max_length=5, default='245px')
    show_school_organizers = models.BooleanField(default=True)

    extra_styles = models.TextField(blank=True, null=True)

    # The term names are used to import school courses from the old site.
    OLD_TERM_NAME_CHOICES = YEAR_IN_SCHOOL_CHOICES = (
        ('Math Future', 'School of the Mathematical Future'),
        ('SoSI', 'School of Social Innovation'),
        ('Webcraft', 'School of Webcraft'),
    )
    old_term_name = models.CharField(max_length=15, blank=True,
        null=True, choices=OLD_TERM_NAME_CHOICES)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('school_home', (), {
            'slug': self.slug,
        })

    def save(self):
        """Make sure each school has a unique slug."""
        count = 1
        if not self.slug:
            slug = slugify(self.name)
            self.slug = slug
            while True:
                existing = School.objects.filter(slug=self.slug)
                if len(existing) == 0:
                    break
                self.slug = "%s-%s" % (slug, count + 1)
                count += 1
        super(School, self).save()
