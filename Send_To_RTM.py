#!/usr/bin/python
#
#  Send_To_RTM.py
#  Send_To_RTM
#
#  Created by Gordon on 10/26/09.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

"""A python search source for QSB.
"""

__author__ = 'Gordon'

import sys
import thread
import AppKit
import Foundation

try:
  import Vermilion  # pylint: disable-msg=C6204
except ImportError:

  class Vermilion(object):
    """A mock implementation of the Vermilion class.

    Vermilion is provided in native code by the QSB
    runtime. We create a stub Result class here so that we
    can develop and test outside of QSB from the command line.
    """
    
    IDENTIFIER = 'IDENTIFIER'
    DISPLAY_NAME = 'DISPLAY_NAME'
    SNIPPET = 'SNIPPET'
    IMAGE = 'IMAGE'
    DEFAULT_ACTION = 'DEFAULT_ACTION'

    class Query(object):
      """A mock implementation of the Vermilion.Query class.

      Vermilion is provided in native code by the QSB
      runtime. We create a stub Result class here so that we
      can develop and test outside of QSB from the command line.
      """
      
      def __init__(self, phrase):
        self.raw_query = phrase
        self.normalized_query = phrase
        self.pivot_object = None
        self.finished = False
        self.results = []

      def SetResults(self, results):
        self.results = results

      def Finish(self):
        self.finished = True

CUSTOM_RESULT_VALUE = 'CUSTOM_RESULT_VALUE'

class Send_To_RTMSearch(object):
  """Send_To_RTM search source.

  This class conforms to the QSB search source protocol by
  providing the mandatory PerformSearch method and the optional
  IsValidSourceForQuery method.

  """

  def PerformSearch(self, query):
    """Performs the search.

    Args:
      query: A Vermilion.Query object containing the user's search query
    """
    results = [];
    result = {};
    result[Vermilion.IDENTIFIER] = 'Send_To_RTM://result';
    result[Vermilion.SNIPPET] = 'So here\'s a bunny with a pancake on it\'s head!';
    result[Vermilion.IMAGE] = 'Send_To_RTM.png';
    result[Vermilion.DISPLAY_NAME] = 'Send_To_RTM Result';
    result[Vermilion.DEFAULT_ACTION] = 'com.yourcompany.action.Send_To_RTM';
    result[CUSTOM_RESULT_VALUE] = 'http://www.fsinet.or.jp/~sokaisha/rabbit/rabbit.htm';
    results.append(result);
    query.SetResults(results)
    query.Finish()

  def IsValidSourceForQuery(self, query):
    """Determines if the search source is willing to handle the query.

    Args:
      query: A Vermilion.Query object containing the user's search query

    Returns:
      True if our source handles the query
    """
    return True
    
class Send_To_RTMAction(object):
  """Send_To_RTM Action

  This class conforms to the QSB search action protocol by
  providing the mandatory AppliesToResults and Perform methods.
  
  """
  def AppliesToResults(self, result):
    """Determines if the result is one we can act upon."""
    return True

  def Perform(self, results):
    """Perform the action"""
    for result in results:
      url = Foundation.NSURL.URLWithString_(result[CUSTOM_RESULT_VALUE])
      workspace = AppKit.NSWorkspace.sharedWorkspace()
      workspace.openURL_(url)

def main():
  """Command line interface for easier testing."""
  argv = sys.argv[1:]
  if not argv:
    print 'Usage: Send_To_RTM <query>'
    return 1

  query = Vermilion.Query(argv[0])
  search = Send_To_RTMSearch()
  if not search.IsValidSourceForQuery(Vermilion.Query(argv[0])):
    print 'Not a valid query'
    return 1
  search.PerformSearch(query)

  while query.finished is False:
    time.sleep(1)

  for result in query.results:
    print result


if __name__ == '__main__':
  sys.exit(main())
