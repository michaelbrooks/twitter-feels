from django.views import generic
import models


class MapView(generic.TemplateView):
    template_name = 'map/page.html'


page_view = MapView.as_view()

