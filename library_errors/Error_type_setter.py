class Error_type_setter(TypeError):
    """
        error specific to setters for classes, when the type is not the requested one.
    """
    DEFAULT_MESSAGE = "Argument in setter is not of the good type. "

    def __init__(self, *args, **kwargs):
        if args:
            self.message = " ".join([Error_type_setter.DEFAULT_MESSAGE, args[0]])
        super().__init__(self.message, *args, **kwargs)

    def __str__(self):
        if self.message:
            return self.message
        else:
            return Error_type_setter.DEFAULT_MESSAGE
