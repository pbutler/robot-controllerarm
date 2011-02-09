from django.db import models
from django.forms import ModelForm

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

class Status(models.Model):
    value = models.CharField(max_length=100)

    def __unicode__(self):
        return "Status: %s" % self.value

class Command(models.Model):
    name = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType)
    # Child model
    child = generic.GenericForeignKey(fk_field='id')

    def cmd(self):
        return self.child.cmd() #"" #aise NotImplementedError

    def save(self, **kwargs):
        if not self.id:
            self.content_type = ContentType.objects.get_for_model(self)
        super(Command, self).save(**kwargs)

    def __unicode__(self):
        type = self.child.__class__.__name__.replace("Command", "")
        cmd = self.cmd().replace("\n", " | ")
        return u"%s(%s): %s" % ( type, self.name, cmd)

class CommandBasic(Command):
    command = models.CharField(max_length=250)
    device = models.CharField(max_length=255)

    def cmd(self):
        return self.command

class CommandPause(Command):
    time = models.FloatField()

    def cmd(self):
        return "Pause for %0.02f" % self.time


class CommandRepeat(Command):
    times = models.IntegerField()
    command = models.ForeignKey(Command, related_name="repeatcmd")

    def cmd(self):
        return "Repeat %s %d times" % (self.command.cmd, self.times)


class CommandMulti(Command):
    commands  = models.ManyToManyField(Command, related_name="cmd_list",
            through="SubCommand")

    def cmd(self):
        return "\n".join( [ c.cmd() for c in self.commands.all()])

class SubCommand(models.Model):
    command = models.ForeignKey(Command)
    master = models.ForeignKey(CommandMulti, related_name="master")
    order = models.IntegerField()

    class Meta:
        ordering = ( 'master', 'order' )
    def __unicode__(self):
        return "<SubCmd: %s(%d): %s>" % (self.master.name, self.order,
                self.command.name)


class Experiment(models.Model):
    description = models.CharField(max_length=100)
    sample      = models.IntegerField()
    parameters  = models.CharField(max_length=100)
    queued = models.DateTimeField()
    started = models.DateTimeField(null = True)
    finished = models.DateTimeField(null = True)
    user = models.ForeignKey(User, related_name='+')

    def __unicode__(self):
        return "Experiment: %s @ %s" % (self.description, self.queued)

    @models.permalink
    def get_absolute_url(self):
            return ('django.views.generic.list_detail.object_detail', [str(self.id)])

class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment
        exclude = ("queued", "started", "finished", "user")

class Data(models.Model):
    experiment = models.ForeignKey(Experiment)
    x = models.FloatField()
    y = models.FloatField()

class CommandQueue(models.Model):
    command = models.ForeignKey(Command, related_name="callthis")

class CommandExperiment(Command):
    experiment = models.ForeignKey(Experiment)

    def cmd(self):
        return "Experiment: %d" % (self.experiment.id)

