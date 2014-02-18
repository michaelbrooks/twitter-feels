from django.views import generic

class HomeView(generic.TemplateView):
    template_name = 'twitter_feels/home.html'


# home = HomeView.as_view()
# for now, just redirect to the thermometer page
home = generic.RedirectView.as_view(pattern_name='thermometer', permanent=False)
