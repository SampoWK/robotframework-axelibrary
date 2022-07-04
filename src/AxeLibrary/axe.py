import json
from .version import VERSION
from axe_selenium_python import Axe
from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import keyword, library
from robot.api import logger
from dominate.tags import table, tbody, tr, th, td, colgroup, col, pre, code


@library(scope='GLOBAL', version=VERSION)
class AxeLibrary():

    def __init__(self):
        self.axe_instance = None
        self.results = None

    @keyword
    def run_accessibility_tests(self, result_file, axe_js_path=None, context=None, options=None):
        """
        Executes accessibility tests in current page by injecting axe-core javascript and write results into `result_file` (json). Return result statisitics

        |  = Attribute =  |  = Description =  |
        | result_file     |  File to store accessibility test results (.json). Ex: google.json  |
        | axe_script_url  |  axe.js file path.  |
        | context         |  Defines the scope of the analysis - the part of the DOM that you would like to analyze. This will typically be the document or a specific selector such as class name, ID, selector, etc.  |
        | options         |  Set of options that change how axe.run works, including what rules will run. See: https://github.com/dequelabs/axe-core/blob/master/doc/API.md#options-parameter |
        """
        # get webdriver instance
        seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
        webdriver = seleniumlib.driver
        # create axe instance
        if axe_js_path:
            self.axe_instance = Axe(webdriver, axe_js_path)
        else:
            self.axe_instance = Axe(webdriver)
        # inject axe-core javascript into current page
        self.axe_instance.inject()
        # run axe accessibility validations
        self.results = self.axe_instance.run(context, options)
        # write results to specified file
        self.axe_instance.write_results(self.results, result_file)
        # generate json
        result_dict = {"inapplicable": len(self.results["inapplicable"]), "incomplete": len(self.results["incomplete"]),
                       "passes": len(self.results["passes"]), "violations": len(self.results["violations"])}
        logger.info(result_dict)
        # return result
        return result_dict

    @keyword
    def get_json_accessibility_result(self):
        """
        Return accessibility test result in Json format. Need to be used after `Run Accessibility Tests` keyword
        """
        axe_result = json.dumps(self.results, indent=3)
        logger.info(axe_result)
        return axe_result

    @keyword
    def accessibility_issues_log(self, type='violations'):
        """
        Inserts readable accessibility result into `log.html` based on given `type`. Need to be used after `Run Accessibility Tests` keyword

        |  = Attribute =  |  = Description =  |
        | Type            |  `violations`, `incomplete` are two supported values  |
        """
        results_by_type = self.results[type]
        result_obj = {}
        id = 1
        results_table = table(class_name='messages info-message')

        col_group = colgroup()
        col_group.add(col(style='width:5%;'))
        col_group.add(col(style='width:15%;'))
        col_group.add(col(style='width:25%;'))
        col_group.add(col(style='width:25%;'))
        results_table.add(col_group)

        table_body = tbody()
        heading_row = tr(style='text-align: left;')
        heading_row.add(th('ID#', style='padding: 1em;'))
        heading_row.add(th('LOCATOR', style='padding: 1em;'))
        heading_row.add(th('HTML', style='padding: 1em;'))
        heading_row.add(th('ISSUE', style='padding: 1em;'))
        table_body.add(heading_row)

        for result in results_by_type:
            for node in result['nodes']:
                table_row = tr(style='text-align: left;')
                table_row.add(td(str(id).strip(),
                                 style='padding: 1em;')
                              )                  # ID#
                table_row.add(
                    td(str(node['target'][0]).strip(), style='padding: 1em;'))   # LOCATOR
                table_row.add(
                    td(pre(code(str(node['html']).strip()),
                           style='overflow:auto;\
                            word-wrap:normal;\
                            background-color:#626264;\
                            border-radius:0.3em;\
                            min-height:4em;\
                            color: white;\
                            margin-block-start:0;\
                            margin-block-end:0;\
                            padding: 0.5em;'), style='padding: 0em;'))   # HTML
                table_row.add(
                    td(str(result['help']).strip(), style='padding: 1em;'))      # ISSUE

                table_body.add(table_row)
                id += 1

        results_table.add(table_body)

        logger.info(str(results_table), html=True)

        if len(self.results["violations"]):
            BuiltIn().fail('Found accessibility issues!')
