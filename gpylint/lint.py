from pylint.lint import PyLinter

class GPyLinter(PyLinter):

    def close(self):
        self.reporter.close(self)
