from .AbletonShellControlSurface import AbletonShellControlSurface

""" Bootstrap the control surface """
def create_instance(c_instance):
    return AbletonShellControlSurface(c_instance)