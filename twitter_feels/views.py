from django.views import generic

class HomeView(generic.TemplateView):
    template_name = 'twitter_feels/home.html'


home = HomeView.as_view()

class ExternalView(generic.TemplateView):
    template_name = 'twitter_feels/external.html'

external = ExternalView.as_view()