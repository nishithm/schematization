# -*- coding: utf-8 -*-

"""
***************************************************************************
    SchematizationTest.py
    ---------------------
    Date                 : June 2014
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
__date__ = 'June 2014'
__copyright__ = '(C) 2014, Nishith Maheshwari'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import unittest
import processing
from processing.tools import dataobjects

from processing.tests.TestData import lines


class SchematizationTest(unittest.TestCase):

    def test_simplification(self):
        outputs = processing.runalg('schematizationprovider:topologypreservingsimplifier', lines(), '2000', None)
        output = outputs['OUTPUT']
        layer = dataobjects.getObjectFromUri(output, True)
        fields = layer.pendingFields()
        expectednames = ['ID', 'LINE_NUM_A', 'LINE_ST_A']
        names = [str(f.name()) for f in fields]
        self.assertEqual(expectednames, names)
        features = processing.features(layer)
        self.assertEqual(5, len(features))
        feature = features.next()
        attrs = feature.attributes()
        expectedvalues = ['NULL', 'NULL', 'NULL']
        values = [str(attr) for attr in attrs]
        self.assertEqual(expectedvalues, values)


def suite():
    suite = unittest.makeSuite(SchematizationTest, 'test')
    return suite


def runtests():
    result = unittest.TestResult()
    testsuite = suite()
    testsuite.run(result)
    return result
