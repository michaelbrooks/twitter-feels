from django.http import HttpResponseBadRequest
from django.views import generic
from django.shortcuts import render
from django.db.models import Q, Count
import json

from jsonview.decorators import json_view
from jsonview.exceptions import BadRequest

from models import TreeNode, TweetChunk



class MapView(generic.TemplateView):
    template_name = 'map/page.html'


page_view = MapView.as_view()


def get_map_results(prefix, query_chunks):

    root = TreeNode.get_root()
    if not root:
        raise Exception("No root node in tweet tree")

    prefix_node = root.get_child(prefix)
    if prefix_node is None:
        return None

    node = prefix_node
    for chunk in query_chunks:
        node = node.get_child(chunk.lower())
        if not node:
            return None

    countries = node.get_top_chunk_countries_for_children()

    words = []
    for country in countries:
        word, count = node.get_most_popular_child_chunk_in(country)
        words.append({
            'text': word,
            'country': country,
            'count': count
        })

    return {
        'words': words
    }

def get_map_results_fast(prefix, query_chunks):

    root = TreeNode.get_root()
    if not root:
        raise Exception("No root node in tweet tree")

    prefix_node = root.get_child(prefix)
    if prefix_node is None:
        return None

    node = prefix_node
    for chunk in query_chunks:
        node = node.get_child(chunk.lower())
        if not node:
            return None

    query = node.get_most_popular_child_chunk_by_country()

    results = []
    for country, text, count in query:
        results.append({
            'text': text,
            'country': country,
            'count': count
        })

    return {
        'words': results
    }

@json_view
def map_results_json(request):
    query = request.GET.get('q', '')
    query = query.strip()  # remove whitespace
    chunks = query.split(' ')  # separate into words

    # There should always be at least 2 chunks
    if len(chunks) < 2:
        raise BadRequest("Query did not include prefix")

    prefix = "%s %s" % (chunks[0], chunks[1])
    return get_map_results(prefix, chunks[2:])


def map_results_html(request):
    query = request.GET.get('q', '')
    query = query.strip()  # remove whitespace
    chunks = query.split(' ')  # separate into words

    # There should always be at least 2 chunks
    if len(chunks) < 2:
        return HttpResponseBadRequest("Query did not include prefix")

    prefix = "%s %s" % (chunks[0], chunks[1])
    data = get_map_results(prefix, chunks[2:])

    return render(request, 'json.html', {
        'data_json': json.dumps(data, indent=3)
    })

@json_view
def fast_map_results_json(request):
    query = request.GET.get('q', '')
    query = query.strip()  # remove whitespace
    chunks = query.split(' ')  # separate into words

    # There should always be at least 2 chunks
    if len(chunks) < 2:
        raise BadRequest("Query did not include prefix")

    prefix = "%s %s" % (chunks[0], chunks[1])
    return get_map_results_fast(prefix, chunks[2:])

def fast_map_results_html(request):
    query = request.GET.get('q', '')
    query = query.strip()  # remove whitespace
    chunks = query.split(' ')  # separate into words

    # There should always be at least 2 chunks
    if len(chunks) < 2:
        return HttpResponseBadRequest("Query did not include prefix")

    prefix = "%s %s" % (chunks[0], chunks[1])
    data = get_map_results_fast(prefix, chunks[2:])

    return render(request, 'json.html', {
        'data_json': json.dumps(data, indent=3)
    })
