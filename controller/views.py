# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from controller.models import *

import csv
import Gnuplot
import tempfile
import datetime
import os

@login_required
def index(request):
        return render_to_response('controller/index.html', {})

@login_required
def experiment_create(request):
    if request.method == "POST":
        form = ExperimentForm(request.POST)
        if form.is_valid():
            experiment = form.save(commit=False)
            experiment.queued = datetime.datetime.now()
            experiment.user = request.user
            experiment.save()

            startcmd = Command.objects.get(name="start_experiment")
            expcmd = CommandExperiment(experiment=experiment)
            expcmd.save()
            stopcmd = Command.objects.get(name="stop_experiment")

            CommandQueue(command=startcmd).save()
            CommandQueue(command=expcmd).save()
            CommandQueue(command=stopcmd).save()

            return HttpResponseRedirect(experiment.get_absolute_url())
    else:
        form = ExperimentForm()
    return render_to_response('controller/experiment.html', {
        "form" : form
    }, context_instance=RequestContext(request))

@login_required
def experiment_plot(request, object_id):
    fnum, tfile = tempfile.mkstemp()
    file = os.fdopen(fnum)

    exp = Experiment.objects.get(id=object_id)
    data = exp.data_set.all().order_by("id")

    data = [ (d.x, d.y) for d in data ]
    g = Gnuplot.Gnuplot()
    g("set term svg")
    g("set output '%s'" % tfile)
    g('set xlabel "DC Magnetic field (Oe)"')
    g('set ylabel "dE/dH (mV/cm.Oe)"')

    g.plot( Gnuplot.Data(data, with_='lp'))
    del g
    response = HttpResponse(mimetype="image/svg+xml")
    response.write(file.read())

    file.close()
    os.unlink(tfile)
    return response

@login_required
def experiment_csv(request, object_id):
    response = HttpResponse(mimetype="text/csv")
    response['Content-Disposition'] = 'attachment; filename=experiment-%s.csv' % object_id
    writer = csv.writer(response)
    exp = Experiment.objects.get(id=object_id)
    data = exp.data_set.all().order_by("id")
    data = [ (d.x, d.y) for d in data ]
    for x,y in data:
        writer.writerow( [x,y])
    return response


@login_required
def compare(request):
    if request.method == "POST":
        #return HttpResponse("<html><body>%s</body></html>" % request.POST.getlist('choose'))
        #if "choose" not in request.POST:
        #    return HttpResponse("<html><body>Not supposed to be here</body></html>")

        expids = [ int(i) for i in  request.POST.getlist("choose") ]
        fnum, tfile = tempfile.mkstemp()
        file = os.fdopen(fnum)

        exps   = [ Experiment.objects.get(id=object_id) for object_id in expids ]
        names  = [ exp.description for exp in exps ]
        datas  = [ exp.data_set.all().order_by("id") for exp in exps ]
        datas  = [ [ (d.x, d.y) for d in data ] for data in datas]

        g = Gnuplot.Gnuplot()
        g("set term svg")
        g("set output '%s'" % tfile)
        g("set key left top")
        gplots = [ Gnuplot.Data(data, with_="lp", title=str(name)) for data, name in zip(datas, names) ]
        g.plot( *gplots )
        del g
        response = HttpResponse(mimetype="image/svg+xml")
        response.write(file.read())

        file.close()
        os.unlink(tfile)
        return response


    else:
        objects = Experiment.objects.all()
        return render_to_response('controller/experiment_compare.html', {
            "object_list" : objects
        }, context_instance=RequestContext(request))
