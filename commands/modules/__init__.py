import os
dir_path = os.path.dirname(os.path.realpath(__file__))
__all__= [os.path.splitext(i)[0] for i in os.listdir(dir_path) if i.endswith('.py') and not i == '__init__.py']