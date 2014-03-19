from django.views import generic
import models


class FishView(generic.TemplateView):
    template_name = 'fish/page.html'


page_view = FishView.as_view()

