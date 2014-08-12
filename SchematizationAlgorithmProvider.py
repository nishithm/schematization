# -*- coding: utf-8 -*-

"""
***************************************************************************
    SchematizationAlgorithmProvider.py
    ---------------------
    Date                 : May 2014
    Copyright            : (C) 2014 by Nishith Maheshwari
    Email                : nshthm at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Nishith Maheshwari'
__date__ = 'May 2014'
__copyright__ = '(C) 2014, Nishith Maheshwari'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingConfig import Setting, ProcessingConfig
from schematization.SimplificationAlgorithm import SimplificationAlgorithm
from schematization.AngleConstraintAlgorithm import AngleConstraintAlgorithm


class SchematizationAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)

        # Deactivate provider by default
        self.activate = False

        # Load algorithms : We have the Simplification algorithm and the algorithm
        #                   to apply the angle constraints
        self.alglist = [SimplificationAlgorithm(), AngleConstraintAlgorithm()]
        for alg in self.alglist:
            alg.provider = self

    def initializeSettings(self):
        """In this method we add settings needed to configure our
        provider.
        """
        AlgorithmProvider.initializeSettings(self)
        
    def unload(self):
        """Setting is removed here, so it does not appear anymore
        when the plugin is unloaded.
        """
        AlgorithmProvider.unload(self)
        
    def getName(self):
        """The name that will appear on the toolbox group.
        It is also used to create the command line name of all the
        algorithms from this provider.
        """
        return 'Schematization Provider'

    def getDescription(self):
        return 'Schematization algorithms'

    def getIcon(self):
        """Returns the default icon."""
        return AlgorithmProvider.getIcon(self)

    def _loadAlgorithms(self):
        """The list of algorithms in self.algs."""
        self.algs = self.alglist
