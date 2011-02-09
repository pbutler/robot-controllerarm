# vim: ts=4 sts=4 sw=4 tw=79 sta et
"""%prog [options]
Python source code - replace this with a description of the code and write the code below this text.
"""

__author__ = 'Patrick Butler'
__email__  = 'pbutler@killertux.org'

from robotarm.controller.models import *
from django.contrib import admin


class CommandAdmin(admin.ModelAdmin):
    fields = ['name']

class CommandPauseAdmin(admin.ModelAdmin):
    fields = ['name', 'time']

class CommandBasicAdmin(admin.ModelAdmin):
    fields = ['name', 'command', "device"]

class SubCommandInline(admin.TabularInline):
    model = SubCommand
    fk_name = "master"

class CommandMultiAdmin(admin.ModelAdmin):
    fields = ['name']
    inlines = [ SubCommandInline, ]

class SubCommandAdmin(admin.ModelAdmin):
    fields = ['master', 'command', 'order' ]

class ExperimentAdmin(admin.ModelAdmin):
    fields = [ 'description', 'queued', 'started', 'finished', 'user']

class DataAdmin(admin.ModelAdmin):
    fields = [ 'x', 'y', 'experiment' ]

class CommandQueueAdmin(admin.ModelAdmin):
    fields = ['command']
admin.site.register(CommandQueue, CommandQueueAdmin)
admin.site.register(Command, CommandAdmin)
admin.site.register(CommandPause, CommandPauseAdmin)
admin.site.register(SubCommand, SubCommandAdmin)
admin.site.register(CommandBasic, CommandBasicAdmin)
admin.site.register(CommandMulti, CommandMultiAdmin)

admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Data, DataAdmin)
