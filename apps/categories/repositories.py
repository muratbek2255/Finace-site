class CategoryMixin:
    """Categories Mixin"""
    model_class = None
    serializer_class = None
    permission_class = None

    def load_categories(self):
        pass

    def fill_aliases(self):
        pass
