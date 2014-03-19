from django.views import generic

class HomeView(generic.TemplateView):
    template_name = 'twitter_feels/home.html'


home = HomeView.as_view()
