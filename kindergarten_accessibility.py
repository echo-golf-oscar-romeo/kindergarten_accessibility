"""
Model exported as python.
Name : kindergarten_egor
Group : egor
With QGIS : 32001
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFileDestination
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Kindergarten_egor(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('livinghousescentoids', 'living_houses_centoids', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('kindergartencentroids', 'kindergarten_centroids', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('bufferradius', 'buffer_radius', type=QgsProcessingParameterNumber.Integer, minValue=1, defaultValue=300))
        self.addParameter(QgsProcessingParameterFileDestination('Spreadsheet', 'spreadsheet', fileFilter='Microsoft Excel (*.xlsx);;Open Document Spreadsheet (*.ods)', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Intersection_raw', 'intersection_raw', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': parameters['bufferradius'],
            'END_CAP_STYLE': 0,  # Round
            'INPUT': parameters['kindergartencentroids'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 15,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Join attributes by location
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['Buffer']['OUTPUT'],
            'JOIN': parameters['livinghousescentoids'],
            'JOIN_FIELDS': [''],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [1],  # contains
            'PREFIX': 'j_',
            'OUTPUT': parameters['Intersection_raw']
        }
        outputs['JoinAttributesByLocation'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Intersection_raw'] = outputs['JoinAttributesByLocation']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Export to spreadsheet
        alg_params = {
            'FORMATTED_VALUES': False,
            'LAYERS': outputs['JoinAttributesByLocation']['OUTPUT'],
            'OVERWRITE': True,
            'USE_ALIAS': False,
            'OUTPUT': parameters['Spreadsheet']
        }
        outputs['ExportToSpreadsheet'] = processing.run('native:exporttospreadsheet', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Spreadsheet'] = outputs['ExportToSpreadsheet']['OUTPUT']
        return results

    def name(self):
        return 'kindergarten_egor'

    def displayName(self):
        return 'kindergarten_egor'

    def group(self):
        return 'egor'

    def groupId(self):
        return 'egor'

    def createInstance(self):
        return Kindergarten_egor()
