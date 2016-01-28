from flask import render_template
from flask.views import View


class GraphiQLView(View):
    template_name = 'graphiql.html'
    default_query = None
    methods = ['GET']

    def __init__(self, **kwargs):
        super(GraphiQLView, self).__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def dispatch_request(self):
        return render_template(self.template_name, default_query=self.default_query)
