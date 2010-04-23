# -*- coding: utf-8 -*-
#
# django-zodb - using Django and ZODB together
#
# Copyright (c) 2009, Triveos Tecnologia Ltda.
# See COPYING for license
#

try:
    import coverage
except ImportError:
    coverage = None

from django.conf import settings
from django.test.simple import run_tests as django_test_runner

def test_runner_with_coverage(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    coverage_enabled = coverage and hasattr(settings, 'COVERAGE_MODULES')

    if coverage_enabled:
        coverage.use_cache(0)
        coverage.start()

    test_results = django_test_runner(test_labels, verbosity, interactive, extra_tests)

    if coverage_enabled:
        coverage.stop()
        coverage_modules = []
        for module in settings.COVERAGE_MODULES:
            coverage_modules.append(__import__(module, globals(), locals(), ['']))
        coverage.report(coverage_modules, show_missing=1)

    return test_results
