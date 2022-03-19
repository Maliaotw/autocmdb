from django.views.generic import ListView


class FilteredListView(ListView):
    filterset_class = None

    def param_replace(self):
        # 支持分頁器
        data = self.request.GET.copy()
        if self.page_kwarg in data.keys():
            data.pop(self.page_kwarg)

        return {k: v for k, v in data.items() if v}

    def get_queryset(self):
        queryset = super().get_queryset()

        get = self.request.GET.copy()

        self.filterset = self.filterset_class(get, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        if self.request.GET.get('contacts'):
            self.paginate_by = int(self.request.GET.get('contacts', 10))

        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['search_field'] = self.param_replace()
        context['page_list'] = [2, 10, 20, 50, 100]
        return context
