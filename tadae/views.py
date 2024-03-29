from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect
from .models import EntityAnn
import annotator
import os
import subprocess
from .settings import UPLOAD_DIR, BASE_DIR
from commons import random_string
from .models import AnnRun


# ENDPOINT = "http://dbpedia.org/sparql"
# ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"
ENDPOINT = os.environ['endpoint']


def sample_data_view(request):
    return render(request, 'sample_data.html')


def about(request):
    return render(request, 'about.html')


def ent_ann_list(request):
    return render(request, 'ent_ann_list.html', {'eanns': EntityAnn.objects.all()})


def ent_ann_stored_results(request):
    annotation = EntityAnn.objects.get(id=request.GET['id'].strip())
    return render(request, 'ent_ann_stored_results.html', {'classes': annotation.results.split(',')})


def ent_ann_raw_results(request):
    annotation = EntityAnn.objects.get(id=request.GET['id'].strip())
    return render(request, 'ent_ann_raw_results.html', {'entity_ann': annotation})


def ent_ann_recompute(request):
    eanns = EntityAnn.objects.all()
    alpha = 0.01
    default_fsid = 3
    if 'alpha' in request.GET and 'ann' in request.GET:
        # from annotator import load_graph, score_graph, get_nodes, get_edges
        alpha = float(request.GET['alpha'])
        entity_ann = EntityAnn.objects.get(id=request.GET['ann'])
        graph = annotator.load_graph(entity_ann=entity_ann)
        # fsid = 0
        # if 'fsid' in request.GET:
        #     fsid = int(request.GET['fsid'])
        fsid = int(request.GET['fsid'])
        results = annotator.score_graph(entity_ann=entity_ann, alpha=alpha, graph=graph, fsid=fsid)
        return render(request, 'ent_ann_recompute.html',
                      {'anns': eanns, 'alpha': alpha, 'network': 'network',
                       'highlights': results[:3], 'nodes': annotator.get_nodes(graph), 'fsid': fsid,
                       'edges': annotator.get_edges(graph), 'results': results, 'selected': entity_ann.id})
    else:
        if len(eanns) == 0:
            selected = 0
        else:
            selected = eanns[0].id
            if 'ann' in request.GET:
                entity_ann = EntityAnn.objects.get(id=request.GET['ann'].strip())
                selected = entity_ann.id
        return render(request, 'ent_ann_recompute.html', {'anns': eanns, 'alpha': alpha, 'selected': selected,
                                                          'fsid': default_fsid,
                                                          })


def handle_uploaded_file(f, dest):
    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print("written: "+dest)


class EntAnnAddView(TemplateView):
    template_name = "ent_ann_add.html"

    def post(self, request):
        if 'file' in request.FILES and 'name' in request.POST:
            LAZY = True  # run the command in a separate process and return a message to the user
            name = request.POST['name'].strip()
            dest_file_name = name+"__"+random_string(length=10)+".csv"
            dest_file_name = dest_file_name.replace(" ", "_")
            dest_file_dir = os.path.join(UPLOAD_DIR, dest_file_name)
            handle_uploaded_file(request.FILES['file'], dest_file_dir)
            ann_run = AnnRun(name=name)
            ann_run.save()
            if 'col_id' in request.POST and len(request.POST['col_id'].strip()) > 0:
                col_id = int(request.POST['col_id'])
            else:
                col_id = 0
            prefix = None
            if 'prefix' in request.POST and len(request.POST['prefix'].strip()) > 0:
                prefix = request.POST['prefix'].strip()
            print("prefix: "+str(prefix))
            camel = False
            if 'camel' in request.POST:
                camel = True
            print("calling the workflow annotate")
            if LAZY:
                if camel:
                    camelstr = '--camelcase'
                else:
                    camelstr = ''
                virtual_env_dir = os.path.join(BASE_DIR, '.venv')
                virtual_py = os.path.join(virtual_env_dir, 'bin', 'python')
                cmd_dir = os.path.join(BASE_DIR, 'annotator', 'cmd.py')
                comm = "%s %s %d --dotype --csvfiles %s %s --onlyprefix %s --entitycol %d" % (
                    virtual_py, cmd_dir,
                                                ann_run.id,
                                                dest_file_dir,
                                                camelstr,
                                                prefix,
                                                col_id)
                print("comm: "+comm)
                import sys
                sys.stdout.flush()
                subprocess.Popen(comm, shell=True)
                return render(request, self.template_name, {'msg': '''The annotation is under processing, check 
                    again in a few minutes'''})
            else:
                annotator.annotate_csv(ann_run_id=ann_run.id, csv_file_dir=dest_file_dir, endpoint=ENDPOINT,
                                                hierarchy=False, entity_col_id=col_id, onlyprefix=prefix, camel_case=camel)
                print("return from the annotate")
                annotator.dotype(ann_run=ann_run, endpoint=ENDPOINT, onlyprefix=None)
                print("return from dotype")
                return render(request, self.template_name, {'msg': 'The annotation is completed'})
        return render(request, self.template_name, {'error': 'missing parameters'})

