#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Armel Thöni <armel.thoni@inra.fr>"
__email__ = "armel.thoni@inra.fr"




class InputException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)


############################################################################

class GitException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)


############################################################################


class ProcedureException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)


############################################################################
############################################################################


class LocalCodebaseRepos :
    
  def __init__(self, path, origin="Local"):
        
    self.Origin = origin  # "GitHub" or "Local"
    self.LocalPath = path
  
  def __str__(self):
    info = "Origin: %s\nLocal path: %s"%(self.Origin, self.LocalPath)
    return info
      

############################################################################


class GitRepos(LocalCodebaseRepos) :
    
  def __init__(self, urlPortion, path, branch=None):
    
    LocalCodebaseRepos.__init__(self, path, origin="GitHub")
    self.GitRepos = urlPortion
    self.Branch = branch
  
  def __str__(self):
    info = "Github Repo: %s"%self.GitRepos
    if self.Branch is not None:
      info += "\nGithub Branch: %s"%self.Branch
    return LocalCodebaseRepos.__str__(self)+"\n"+info