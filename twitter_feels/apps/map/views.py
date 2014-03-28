from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest
from django.views import generic
from django.shortcuts import render
from django.db.models import Q, Count
import json

from jsonview.decorators import json_view
from jsonview.exceptions import BadRequest

from models import TreeNode, TweetChunk, Tz_Country



class MapView(generic.TemplateView):
    template_name = 'map/page.html'


page_view = MapView.as_view()


def get_map_results(prefix, query_chunks):

    node = TreeNode.follow_chunks(prefix, query_chunks)
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

    node = TreeNode.follow_chunks(prefix, query_chunks)
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

def get_map_results_faster(prefix, query_chunks):

    node = TreeNode.follow_chunks(prefix, query_chunks)
    query = node.get_most_popular_child_chunk_by_country2()

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


def get_example_tweet(prefix, query_chunks, country_name):
    """Finds an example tweet for the given query"""
    node = TreeNode.follow_chunks(prefix, query_chunks)
    return TweetChunk.get_example_tweet(country_name, node).text


def parse_chunks(request):
    query = request.GET.get('q', '')
    query = query.strip()  # remove whitespace
    chunks = query.split(' ')  # separate into words

    # There should always be at least 2 chunks
    if len(chunks) < 2:
        raise BadRequest("Query did not include prefix")

    prefix = "%s %s" % (chunks[0], chunks[1])

    return prefix, chunks[2:]


###### VIEWS BELOW ##########

@json_view
def map_results_json(request):
    prefix, chunks = parse_chunks(request)
    return get_map_results(prefix, chunks)


def map_results_html(request):
    try:
        prefix, chunks = parse_chunks(request)
    except BadRequest:
        return HttpResponseBadRequest("Query did not include prefix")

    data = get_map_results(prefix, chunks)

    return render(request, 'json.html', {
        'data_json': json.dumps(data, indent=3)
    })

@json_view
def fast_map_results_json(request):
    prefix, chunks = parse_chunks(request)
    return get_map_results_fast(prefix, chunks)

def fast_map_results_html(request):
    try:
        prefix, chunks = parse_chunks(request)
    except BadRequest:
        return HttpResponseBadRequest("Query did not include prefix")

    data = get_map_results_fast(prefix, chunks)

    return render(request, 'json.html', {
        'data_json': json.dumps(data, indent=3)
    })


def faster_map_results_html(request):
    try:
        prefix, chunks = parse_chunks(request)
    except BadRequest:
        return HttpResponseBadRequest("Query did not include prefix")

    data = get_map_results_faster(prefix, chunks)

    return render(request, 'json.html', {
        'data_json': json.dumps(data, indent=3)
    })


@json_view
def faster_map_results_json(request):
    prefix, chunks = parse_chunks(request)
    return get_map_results_faster(prefix, chunks)


def example_tweet_html(request):
    try:
        prefix, chunks = parse_chunks(request)
        country_name = request.GET.get('country', '').strip()
        data = get_example_tweet(prefix, chunks, country_name)
    except BadRequest, e:
        return HttpResponseBadRequest(e.message)

    return render(request, 'json.html', {
        'data_json': json.dumps(data, indent=3)
    })


@json_view
def example_tweet_json(request):
    prefix, chunks = parse_chunks(request)
    country_name = request.GET.get('country', '').strip()
    return get_example_tweet(prefix, chunks, country_name)
